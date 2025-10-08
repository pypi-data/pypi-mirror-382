import boto3
from ephemeral_pulumi_deploy import get_config_str
from mypy_boto3_ssm import SSMClient

type WorkloadName = str
type AwsAccountId = str


def create_resource_name_safe_str(name: str) -> str:
    return (
        name.lower()
        .replace(" ", "-")
        .replace(":", "-")
        .replace("(", "-")
        .replace(")", "-")
        .replace("'", "-")
        .replace('"', "-")
        .replace("/", "-")
        .replace(chr(92), "-")  # backslash
        .replace("=", "-")
        .replace("@", "-")
        .replace(".", "-")
    )


def get_ssm_param_value(
    param_name: str, *, ssm_client: SSMClient | None = None, session: boto3.Session | None = None
) -> str:
    if session is None:
        session = boto3.Session()
    if ssm_client is None:
        ssm_client = session.client("ssm")
    param = ssm_client.get_parameter(Name=param_name)["Parameter"]
    assert "Value" in param, f"Expected 'Value' in {param}"
    return param["Value"]


def get_org_managed_ssm_param_value(param_name: str) -> str:
    org_home_region = get_config_str("proj:aws_org_home_region")
    ssm_client = boto3.client("ssm", region_name=org_home_region)
    return get_ssm_param_value(param_name, ssm_client=ssm_client)


def get_manual_artifacts_bucket_name() -> str:
    return get_org_managed_ssm_param_value("/org-managed/manual-artifacts-bucket-name")
