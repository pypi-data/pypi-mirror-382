import pytest  # type: ignore[import]

# noinspection PyUnresolvedReferences
from nhs_aws_helpers.fixtures import *  # noqa: F403
from tests.utils import temp_env_vars


@pytest.fixture(scope="session", autouse=True)
def autouse():
    with temp_env_vars(
        AWS_ENDPOINT_URL="http://localhost:4566",
        AWS_ACCESS_KEY_ID="dummy_access_key",
        AWS_SECRET_ACCESS_KEY="dummy_secret_key",
    ):
        yield
