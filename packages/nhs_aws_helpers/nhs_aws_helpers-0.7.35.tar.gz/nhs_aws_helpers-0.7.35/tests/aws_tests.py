import json
import logging
import os
from typing import Any, Literal, TypedDict, cast
from uuid import uuid4

import pytest
from botocore.config import Config
from botocore.exceptions import ClientError
from mypy_boto3_s3.service_resource import Bucket, ObjectSummary, ObjectVersion
from pytest_httpserver import HTTPServer

from nhs_aws_helpers import (
    assumed_credentials,
    dynamodb_retry_backoff,
    iam_client,
    post_create_client,
    register_config_default,
    register_retry_handler,
    s3_build_uri,
    s3_client,
    s3_delete_keys,
    s3_get_all_keys,
    s3_list_folders,
    s3_ls,
    s3_resource,
    s3_upload_multipart_from_copy,
    transaction_cancellation_reasons,
)
from nhs_aws_helpers.common import MiB
from tests.utils import temp_env_vars


@pytest.mark.parametrize(
    ("error", "expected_reasons"),
    [
        (
            {
                "Message": "Transaction cancelled, [eeek] reasons [None, ConditionalCheckFailed, None, None, None]",
                "Code": "TransactionCanceledException",
            },
            ["None", "ConditionalCheckFailed", "None", "None", "None"],
        ),
        ({"Message": "Transaction cancelled, [eeek] specific reasons []", "Code": "TransactionCanceledException"}, []),
        ({"Message": "Transaction cancelled, [eeek] specific reasons []", "Code": "Another"}, []),
    ],
)
def test_transaction_cancellation_reasons(error, expected_reasons):
    reasons = transaction_cancellation_reasons(ClientError({"Error": error}, "TransactWriteItems"))
    assert reasons == expected_reasons


def test_ddb_retries_all_fail():
    calls: list[Any] = []

    @dynamodb_retry_backoff(max_retries=2)
    def fail_me():
        nonlocal calls
        calls.append(None)
        raise ClientError(operation_name="dummy_op", error_response={"Error": {"Code": "ThrottlingException"}})

    with pytest.raises(ClientError) as ex:
        fail_me()

    assert str(ex.value) == "An error occurred (ThrottlingException) when calling the dummy_op operation: Unknown"
    assert len(calls) == 3


def test_s3_delete_keys_all(temp_s3_bucket: Bucket):
    keys = [str(key) for key in range(1003)]

    for key in keys:
        temp_s3_bucket.put_object(Key=key, Body=f"Some data {uuid4().hex}".encode())

    deleted_keys = s3_delete_keys(keys, temp_s3_bucket.name)

    remaining_keys = list(s3_get_all_keys(temp_s3_bucket.name, ""))

    assert len(deleted_keys) == len(keys)
    assert set(deleted_keys) == set(keys)
    assert len(remaining_keys) == 0


def test_s3_delete_keys_partial(temp_s3_bucket: Bucket):
    keys = [str(key) for key in range(1003)]

    for key in keys:
        temp_s3_bucket.put_object(Key=key, Body=f"Some data {uuid4().hex}".encode())

    leaving_keys = [keys.pop(i) for i in (1002, 456, 3)]

    deleted_keys = s3_delete_keys(keys, temp_s3_bucket.name)

    remaining_keys = list(s3_get_all_keys(temp_s3_bucket.name, ""))

    assert len(deleted_keys) == len(keys)
    assert set(deleted_keys) == set(keys)
    assert len(remaining_keys) == len(leaving_keys)
    assert set(remaining_keys) == set(leaving_keys)


@pytest.mark.parametrize(
    "keys",
    [(), ("a",), ("a/b",), ("a/b", "a/c")],
)
def test_s3_get_all_keys(temp_s3_bucket: Bucket, keys: list[str]):
    for key in keys:
        temp_s3_bucket.put_object(Key=key, Body=f"Some data {uuid4().hex}".encode())

    result_keys = list(s3_get_all_keys(temp_s3_bucket.name, ""))

    assert len(result_keys) == len(keys)
    assert set(result_keys) == set(keys)


@pytest.mark.parametrize(
    "keys",
    [(), ("a",), ("a/b",), ("a/b", "a/c")],
)
def test_s3_get_all_keys_under_prefix(temp_s3_bucket: Bucket, keys: list[str]):
    expected_folder = uuid4().hex

    # Keys that shouldn't be included
    for key in ("x", "y/z"):
        temp_s3_bucket.put_object(Key=key, Body=f"Some data {uuid4().hex}".encode())

    for key in keys:
        temp_s3_bucket.put_object(Key=f"{expected_folder}/{key}", Body=f"Some data {uuid4().hex}".encode())

    result_keys = list(s3_get_all_keys(temp_s3_bucket.name, expected_folder))

    assert len(result_keys) == len(keys)
    assert set(result_keys) == {f"{expected_folder}/{key}" for key in keys}


def test_s3_ls(temp_s3_bucket: Bucket):
    expected_folder = uuid4().hex
    temp_s3_bucket.put_object(Key=f"{expected_folder}/1/a.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_s3_bucket.put_object(Key=f"{expected_folder}/1/b.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_s3_bucket.put_object(Key=f"{expected_folder}/2/c.txt", Body=f"Some data {uuid4().hex}".encode())

    files = cast(list[ObjectSummary], list(s3_ls(s3_build_uri(temp_s3_bucket.name, expected_folder))))

    assert len(files) == 3
    assert {f.key for f in files} == {
        f"{expected_folder}/1/a.txt",
        f"{expected_folder}/1/b.txt",
        f"{expected_folder}/2/c.txt",
    }


def test_s3_ls_versioning_on_non_versioned_bucket(temp_s3_bucket: Bucket):
    expected_folder = uuid4().hex
    temp_s3_bucket.put_object(Key=f"{expected_folder}/1/a.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_s3_bucket.put_object(Key=f"{expected_folder}/1/b.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_s3_bucket.put_object(Key=f"{expected_folder}/2/c.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_s3_bucket.put_object(Key=f"{expected_folder}/2/c.txt", Body=f"Some new data {uuid4().hex}".encode())

    files = cast(list[ObjectVersion], list(s3_ls(s3_build_uri(temp_s3_bucket.name, expected_folder), versioning=True)))

    assert len(files) == 3
    assert {f.key for f in files} == {
        f"{expected_folder}/1/a.txt",
        f"{expected_folder}/1/b.txt",
        f"{expected_folder}/2/c.txt",
    }
    assert len({f.id for f in files}) == 1


def test_s3_ls_versioning(temp_versioned_s3_bucket: Bucket):
    expected_folder = uuid4().hex
    temp_versioned_s3_bucket.put_object(Key=f"{expected_folder}/1/a.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_versioned_s3_bucket.put_object(Key=f"{expected_folder}/1/b.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_versioned_s3_bucket.put_object(Key=f"{expected_folder}/2/c.txt", Body=f"Some data {uuid4().hex}".encode())
    temp_versioned_s3_bucket.put_object(Key=f"{expected_folder}/2/c.txt", Body=f"Some new data {uuid4().hex}".encode())

    files = cast(
        list[ObjectVersion], list(s3_ls(s3_build_uri(temp_versioned_s3_bucket.name, expected_folder), versioning=True))
    )

    assert len(files) == 4
    assert {f.key for f in files} == {
        f"{expected_folder}/1/a.txt",
        f"{expected_folder}/1/b.txt",
        f"{expected_folder}/2/c.txt",
    }
    assert len({f.id for f in files}) == 4


def test_s3_list_folders_root(temp_s3_bucket: Bucket):
    expected_folder = uuid4().hex

    temp_s3_bucket.put_object(Key=f"{expected_folder}/filename.txt", Body=f"Some data {uuid4().hex}".encode())

    folders = s3_list_folders(temp_s3_bucket.name, "")

    assert len(folders) == 1
    assert folders[0] == expected_folder


def test_s3_list_folders_subfolder_multiple_found(temp_s3_bucket: Bucket):
    some_body = f"Some data {uuid4().hex}".encode()
    prefix = f"{uuid4().hex}/"

    expected_folder1 = uuid4().hex
    expected_folder2 = uuid4().hex
    expected_folder3 = uuid4().hex

    temp_s3_bucket.put_object(Key=f"{prefix}{expected_folder1}/filename.txt", Body=some_body)

    temp_s3_bucket.put_object(Key=f"{prefix}{expected_folder2}/filename2.txt", Body=some_body)

    temp_s3_bucket.put_object(Key=f"{prefix}{expected_folder3}/filename2.txt", Body=some_body)

    temp_s3_bucket.put_object(Key=f"{prefix}{expected_folder3}/additional_file2.txt", Body=some_body)

    folders = s3_list_folders(temp_s3_bucket.name, prefix, page_size=2)

    assert len(folders) == 3
    assert f"{prefix}{expected_folder1}" in folders
    assert f"{prefix}{expected_folder2}" in folders
    assert f"{prefix}{expected_folder3}" in folders


@pytest.mark.parametrize(
    ("is_resource", "expected_exception_message"),
    [
        (
            True,
            "An error occurred (503) when calling the PutObject operation"
            " (reached max retries: 1): Service Unavailable",
        ),
        (
            False,
            "An error occurred (500) when calling the ListBuckets operation"
            " (reached max retries: 1): Internal Server Error",
        ),
    ],
)
def test_s3_retries(
    temp_s3_bucket: Bucket,
    httpserver: HTTPServer,
    is_resource: bool,
    expected_exception_message: str,
):
    server_port = httpserver.port

    expected_folder = uuid4().hex

    key = f"{expected_folder}/filename.txt"
    httpserver.expect_request(f"/{temp_s3_bucket.name}/{key}").respond_with_json({}, status=503)

    # Type-identical spec to match botocore's internal typing of _RetryDict
    class BotocoreRetries(TypedDict, total=False):
        total_max_attempts: int
        max_attempts: int
        mode: Literal["legacy", "standard", "adaptive"]

    config = Config(
        connect_timeout=float(os.environ.get("BOTO_CONNECT_TIMEOUT", "1")),
        read_timeout=float(os.environ.get("BOTO_READ_TIMEOUT", "1")),
        max_pool_connections=int(os.environ.get("BOTO_MAX_POOL_CONNECTIONS", "10")),
        retries=BotocoreRetries(
            mode=os.environ.get("BOTO_RETRIES_MODE", "standard"),  # type: ignore[typeddict-item]
            total_max_attempts=int(os.environ.get("BOTO_RETRIES_TOTAL_MAX_ATTEMPTS", "2")),
        ),
    )

    def _post_create_aws(boto_module: str, _: str, client):
        if boto_module != "s3":
            return
        register_retry_handler(client)

    register_config_default("s3", config)
    post_create_client(_post_create_aws)

    with (  # noqa: PT012
        pytest.raises(ClientError) as ex,
        temp_env_vars(
            # Point any new boto resources or clients at our fake endpoint
            AWS_ENDPOINT_URL=f"http://localhost:{server_port}",
        ),
    ):
        original_log_level = logging.getLogger("werkzeug").level
        try:
            # Avoid werkzeug logs cluttering our logs
            logging.getLogger("werkzeug").setLevel(logging.WARNING)
            if is_resource:
                s3_resource(config=config).Bucket(temp_s3_bucket.name).put_object(
                    Key=f"{key}", Body=f"Some data {uuid4().hex}".encode()
                )
            else:
                s3_client(config=config).list_buckets()

        finally:
            logging.getLogger("werkzeug").setLevel(original_log_level)

    assert str(ex.value) == expected_exception_message


# pylint: disable=too-many-locals
def test_s3_upload_multipart_from_copy(temp_s3_bucket: Bucket):
    uuid = uuid4().hex
    num_parts = 3
    ten_mb = b"ABCDEFGHIJ" * MiB
    chunk_size = 5 * MiB
    chunk_data = ten_mb[:chunk_size]

    part_keys = []
    for i in range(1, num_parts + 1):
        part_key = f"{uuid}_{i}"
        temp_s3_bucket.Object(part_key).put(Body=chunk_data)
        part_keys.append(part_key)

    target_object = temp_s3_bucket.Object(uuid)

    s3_upload_multipart_from_copy(target_object, part_keys)

    assert target_object.get()["ContentLength"] == num_parts * chunk_size


def test_s3_upload_multipart_from_copy_one_part_too_small(temp_s3_bucket: Bucket):
    uuid = uuid4().hex
    num_parts = 3
    ten_mb = b"ABCDEFGHIJ" * MiB

    part_keys = []
    for i in range(1, num_parts + 1):
        part_key = f"{uuid}_{i}"
        # 4, 8, 12 MB - 4 is too small
        temp_s3_bucket.Object(part_key).put(Body=ten_mb[: i * 4 * MiB])
        part_keys.append(part_key)

    target_object = temp_s3_bucket.Object(uuid)

    with pytest.raises(ClientError) as client_error:
        s3_upload_multipart_from_copy(target_object, part_keys)

    assert client_error.value.response["Error"]["Code"] == "EntityTooSmall"

    with pytest.raises(ClientError) as client_error:
        target_object.get()

    assert client_error.value.response["Error"]["Code"] == "NoSuchKey"


# pylint: disable=too-many-locals
def test_s3_upload_multipart_from_copy_missing_part_data(temp_s3_bucket: Bucket):
    uuid = uuid4().hex
    num_parts = 3
    ten_mb = b"ABCDEFGHIJ" * MiB
    chunk_size = 5 * MiB
    chunk_data = ten_mb[:chunk_size]

    part_keys = []
    for i in range(1, num_parts + 1):
        part_key = f"{uuid}_{i}"
        if i != 2:  # Don't store part 2
            temp_s3_bucket.Object(part_key).put(Body=chunk_data)
        part_keys.append(part_key)

    target_object = temp_s3_bucket.Object(uuid)

    with pytest.raises(IOError, match=f"Failed to multipart_upload {{'{uuid}_2'}} after 5 attempts"):
        s3_upload_multipart_from_copy(target_object, part_keys)

    with pytest.raises(ClientError) as client_error:
        target_object.get()

    assert client_error.value.response["Error"]["Code"] == "NoSuchKey"


def test_assumed_credentials():
    iam = iam_client()
    user_name = uuid4().hex
    role_name = uuid4().hex

    iam.create_user(UserName=user_name)

    role_arn = f"arn:aws:iam::123456789012:role/{role_name}"

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": "sts:AssumeRole", "Resource": role_arn}],
    }

    iam.put_user_policy(UserName=user_name, PolicyName="AllowAssumeRole", PolicyDocument=json.dumps(policy_document))

    creds = assumed_credentials(
        account_id="123456789012", role=role_name, sts_endpoint_url=os.environ["AWS_ENDPOINT_URL"]
    )
    assert creds["access_key"]
    assert creds["secret_key"]
    assert creds["token"]
    assert creds["expiry_time"]
