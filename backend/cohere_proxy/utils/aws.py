import os
import boto3
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session

from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
ROLE_ARN = os.getenv("BEDROCK_ASSUME_ROLE", None)


def refreshable_session(
    role_arn, session_name="AssumeRoleSession", region_name=AWS_DEFAULT_REGION
):
    sts_client = boto3.client("sts", region_name=region_name)

    def refresh():
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=900,  # 15 minutes
        )
        credentials = response["Credentials"]

        return {
            "access_key": credentials["AccessKeyId"],
            "secret_key": credentials["SecretAccessKey"],
            "token": credentials["SessionToken"],
            "expiry_time": credentials["Expiration"].isoformat(),
        }

    botocore_session = get_session()

    refreshable_credentials = RefreshableCredentials.create_from_metadata(
        metadata=refresh(), refresh_using=refresh, method="sts-assume-role"
    )

    botocore_session._credentials = refreshable_credentials
    botocore_session.set_config_variable("region", region_name)

    return boto3.Session(botocore_session=botocore_session)


retry_config = Config(
    retries={
        "max_attempts": 5,  # Maximum number of retry attempts
        "mode": "standard",  # Retry mode: 'standard' or 'adaptive'
    }
)

session = refreshable_session(ROLE_ARN)
bedrock_client = session.client("bedrock-runtime", config=retry_config)
