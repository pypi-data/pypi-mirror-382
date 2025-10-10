"""
Utility module for generating AWS Console links for resources.
"""

from urllib.parse import quote


def get_lambda_console_url(function_name: str, region: str) -> str:
    """Generate AWS Console URL for Lambda function."""
    return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{function_name}"


def get_ecr_repository_console_url(repository_name: str, region: str) -> str:
    """Generate AWS Console URL for ECR repository."""
    return f"https://{region}.console.aws.amazon.com/ecr/repositories/private/{repository_name}?region={region}"


def get_ecr_image_console_url(repository_name: str, image_tag: str, region: str) -> str:
    """Generate AWS Console URL for specific ECR image."""
    return f"https://{region}.console.aws.amazon.com/ecr/repositories/private/{repository_name}/_/image/{image_tag}/details?region={region}"


def get_s3_bucket_console_url(bucket_name: str, region: str) -> str:
    """Generate AWS Console URL for S3 bucket."""
    return f"https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}?region={region}"


def get_s3_object_console_url(bucket_name: str, object_key: str, region: str) -> str:
    """Generate AWS Console URL for S3 object."""
    encoded_key = quote(object_key, safe="")
    return f"https://s3.console.aws.amazon.com/s3/object/{bucket_name}?region={region}&prefix={encoded_key}"


def get_cloudwatch_logs_console_url(log_group: str, region: str) -> str:
    """Generate AWS Console URL for CloudWatch Logs."""
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/{quote(log_group, safe='')}"


def get_region_console_url(region: str) -> str:
    """Generate AWS Console URL for a specific region."""
    return f"https://{region}.console.aws.amazon.com/console/home?region={region}"
