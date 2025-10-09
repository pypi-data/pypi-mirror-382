"""
AWS configuration validators and utilities.
"""

import logging
from typing import List
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

logger = logging.getLogger(__name__)

# Cache for validated regions
_VALID_REGIONS_CACHE = None


def get_valid_aws_regions() -> List[str]:
    """
    Get list of valid AWS regions.

    Returns:
        List of valid AWS region names

    Raises:
        ClientError: If unable to fetch regions from AWS
    """
    global _VALID_REGIONS_CACHE

    if _VALID_REGIONS_CACHE is not None:
        return _VALID_REGIONS_CACHE

    try:
        # Use us-east-1 as a stable endpoint to query regions
        ec2 = boto3.client("ec2", region_name="us-east-1")
        response = ec2.describe_regions(AllRegions=False)
        regions = [region["RegionName"] for region in response["Regions"]]
        _VALID_REGIONS_CACHE = regions
        return regions
    except (ClientError, EndpointConnectionError) as e:
        logger.warning(f"Unable to fetch AWS regions: {e}")
        # Return a fallback list of common regions
        return [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ]


def validate_aws_region(region: str) -> bool:
    """
    Validate that the specified AWS region exists.

    Args:
        region: AWS region name to validate

    Returns:
        True if region is valid, False otherwise
    """
    valid_regions = get_valid_aws_regions()
    return region in valid_regions


def validate_iam_role_arn(role_arn: str) -> bool:
    """
    Validate IAM role ARN format.

    Args:
        role_arn: IAM role ARN to validate

    Returns:
        True if format is valid, False otherwise
    """
    # Basic ARN format: arn:aws:iam::account-id:role/role-name
    if not role_arn:
        return False

    parts = role_arn.split(":")
    if len(parts) != 6:
        return False

    if parts[0] != "arn":
        return False

    if parts[1] not in ["aws", "aws-cn", "aws-us-gov"]:
        return False

    if parts[2] != "iam":
        return False

    # parts[3] is empty for IAM
    if parts[4] and not parts[4].isdigit():
        return False

    # parts[5] should be role/role-name
    if not parts[5].startswith("role/"):
        return False

    return True
