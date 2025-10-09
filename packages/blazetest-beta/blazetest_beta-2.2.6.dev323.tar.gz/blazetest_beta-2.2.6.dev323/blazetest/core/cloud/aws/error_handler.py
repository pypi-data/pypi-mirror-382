"""
AWS Error Handling Utilities.

Provides decorators and utilities for handling AWS-specific errors
with user-friendly messages and appropriate retry logic.
"""

import logging
import functools
from botocore.exceptions import (
    ClientError,
    BotoCoreError,
    NoCredentialsError,
    PartialCredentialsError,
    ProfileNotFound,
    EndpointConnectionError,
)

logger = logging.getLogger(__name__)


def handle_aws_errors(func):
    """
    Decorator to handle AWS errors with user-friendly messages.

    Catches common AWS exceptions and provides helpful error messages
    with troubleshooting steps.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoCredentialsError:
            logger.error(
                "AWS credentials not found. Please configure credentials using one of:\n"
                "1. CLI arguments: blazetest run -ak YOUR_KEY -as YOUR_SECRET\n"
                "2. Environment variables: export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...\n"
                "3. Config file: Add [cloud.aws.credentials] section in blazetest.toml\n"
                "4. AWS profile: Add 'profile = \"my-profile\"' in [cloud.aws.credentials]\n"
                "5. IAM role: Run on EC2/ECS or specify role_arn in config\n"
                "6. AWS CLI: Run 'aws configure' to set up default credentials"
            )
            raise
        except PartialCredentialsError as e:
            logger.error(
                f"Incomplete AWS credentials: {e}\n"
                "Both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required."
            )
            raise
        except ProfileNotFound as e:
            logger.error(
                f"AWS profile not found: {e}\n"
                "Available profiles are in ~/.aws/credentials\n"
                "Create a profile with: aws configure --profile <name>"
            )
            raise
        except EndpointConnectionError as e:
            logger.error(
                f"Unable to connect to AWS endpoint: {e}\n"
                "Check your internet connection and AWS region configuration."
            )
            raise
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", str(e))

            if error_code == "UnauthorizedOperation":
                logger.error(
                    f"AWS Permission Denied: {error_message}\n"
                    "Your IAM user/role lacks required permissions.\n"
                    "Required permissions are documented in: docs/iam_policy.json\n"
                    "Verify your IAM policy includes necessary actions for:\n"
                    "  - Lambda (CreateFunction, InvokeFunction, etc.)\n"
                    "  - S3 (CreateBucket, PutObject, GetObject)\n"
                    "  - ECR (CreateRepository, PutImage, GetAuthorizationToken)\n"
                    "  - IAM (CreateRole, PassRole, AttachRolePolicy)"
                )
            elif error_code == "InvalidAccessKeyId":
                logger.error(
                    "Invalid AWS Access Key ID.\n"
                    "Verify your credentials are correct and active."
                )
            elif error_code == "SignatureDoesNotMatch":
                logger.error(
                    "AWS Secret Access Key does not match the Access Key ID.\n"
                    "Verify your credentials are correct."
                )
            elif error_code == "ExpiredToken":
                logger.error(
                    "AWS session token has expired.\n"
                    "Refresh your temporary credentials or use permanent credentials."
                )
            elif error_code == "AccessDenied" or error_code == "AccessDeniedException":
                logger.error(
                    f"Access Denied: {error_message}\n"
                    "Check your IAM permissions. Required policy: docs/iam_policy.json"
                )
            elif error_code == "InvalidParameterValueException":
                logger.error(f"Invalid parameter value: {error_message}")
            elif error_code in ["ThrottlingException", "TooManyRequestsException"]:
                logger.error(
                    f"AWS API rate limit exceeded: {error_message}\n"
                    "Requests are being throttled. Wait and retry."
                )
            elif error_code == "ResourceNotFoundException":
                logger.error(f"AWS resource not found: {error_message}")
            else:
                logger.error(
                    f"AWS Error ({error_code}): {error_message}\n"
                    f"See AWS documentation for error code: {error_code}"
                )
            raise
        except BotoCoreError as e:
            logger.error(f"AWS SDK Error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while calling AWS: {e}")
            raise

    return wrapper


def get_friendly_error_message(error: ClientError) -> str:
    """
    Get a user-friendly error message for AWS ClientError.

    Args:
        error: boto3 ClientError exception

    Returns:
        User-friendly error message string
    """
    error_code = error.response.get("Error", {}).get("Code", "Unknown")
    error_message = error.response.get("Error", {}).get("Message", str(error))

    friendly_messages = {
        "UnauthorizedOperation": (
            "Permission denied. Check IAM policy (docs/iam_policy.json)"
        ),
        "InvalidAccessKeyId": "Invalid AWS Access Key ID",
        "SignatureDoesNotMatch": "AWS Secret Key does not match Access Key",
        "ExpiredToken": "AWS session token expired. Refresh credentials",
        "AccessDenied": "Access denied. Check IAM permissions",
        "ThrottlingException": "AWS API rate limit exceeded. Retry later",
        "ResourceNotFoundException": "AWS resource not found",
    }

    return friendly_messages.get(error_code, f"{error_code}: {error_message}")
