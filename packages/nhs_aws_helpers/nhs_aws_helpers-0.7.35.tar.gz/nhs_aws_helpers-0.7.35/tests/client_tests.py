from nhs_aws_helpers import ecs_client, healthlake_client, iam_client, sts_client


def test_sts_client():
    client = sts_client()
    assert client.meta.service_model.service_id == "STS"


def test_healthlake_client():
    client = healthlake_client()
    assert client.meta.service_model.service_id == "HealthLake"


def test_ecs_client():
    client = ecs_client()
    assert client.meta.service_model.service_id == "ECS"


def test_iam_client():
    client = iam_client()
    assert client.meta.service_model.service_id == "IAM"
