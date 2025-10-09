import dataclasses
import re
from typing import Dict

from blazetest.core.utils.exceptions import ConfigurationValidationException


@dataclasses.dataclass
class ValidationBase:
    @staticmethod
    def get_validators() -> Dict:
        return {}

    def __post_init__(self):
        fields = dataclasses.fields(self)
        messages = []
        for field in fields:
            value = getattr(self, field.name)
            validator = self.get_validators().get(field.name)
            if not validator:
                continue

            is_valid, message = validator(value)
            if not is_valid:
                messages.append(message)

        if messages:
            raise ConfigurationValidationException(
                "Please correct following configuration errors: \n"
                + "\n".join(messages)
            )


def resource_prefix_is_valid(resource_prefix):
    if len(resource_prefix) > 96 or len(resource_prefix) < 3:
        return (
            False,
            "Resource prefix should be >=3 and 56 (64 - 8 (Session UUID length)) characters long",
        )

    pattern = r"^[a-zA-Z][a-zA-Z0-9-_]+$"
    if not re.match(pattern, resource_prefix):
        return (
            False,
            "Resource prefix does not meet the naming conventions. See "
            "https://docs.aws.amazon.com/AWSCloudFormation/"
            "latest/UserGuide/cfn-using-console-create-stack-parameters.html",
        )

    return True, ""


def ecr_repository_name_is_valid(ecr_repository_name):
    if len(ecr_repository_name) > 224 or len(ecr_repository_name) < 2:
        return (
            False,
            "ECR Repository should be >=2 and <= 248 (256 - 8 (Session UUID length)) characters long",
        )

    pattern = r"^[a-z][a-z0-9-_]+$"
    if not re.match(pattern, ecr_repository_name):
        return (
            False,
            "The ECR repository does not meet the naming conventions. See "
            "https://docs.aws.amazon.com/AmazonECR/latest/userguide/Repositories.html",
        )

    return True, ""


def s3_bucket_name_is_valid(s3_bucket_name):
    pattern = r"(?!(^xn--|.+-s3alias$))^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$"

    if re.match(pattern, s3_bucket_name):
        return True, ""
    else:
        return (
            False,
            "S3 Bucket name does not meet the naming conventions; "
            "See https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html",
        )


def lambda_function_timeout_is_valid(lambda_function_timeout):
    if lambda_function_timeout < 1 or lambda_function_timeout > 900:
        return (
            False,
            "Lambda function timeout must be between 1 and 900 seconds",
        )
    return True, ""


def lambda_function_memory_size_is_valid(lambda_function_memory_size):
    if lambda_function_memory_size < 128 or lambda_function_memory_size > 10240:
        return (
            False,
            "Lambda function memory size must be between 128 and 10240 MB",
        )
    return True, ""


def junit_results_file_link_is_valid(junit_results_file_link):
    if not junit_results_file_link:
        return True, ""

    if junit_results_file_link not in ("public", "private"):
        return (
            False,
            "junit_results_file_link must be either 'public' or 'private'",
        )
    return True, ""


def tests_per_dispatch_is_valid(tests_per_dispatch: int):
    if tests_per_dispatch < 1:
        return False, "Tests per dispatch can not be lower than 1"

    return True, ""
