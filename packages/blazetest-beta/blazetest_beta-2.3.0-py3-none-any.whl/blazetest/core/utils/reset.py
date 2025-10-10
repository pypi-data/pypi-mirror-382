"""
Resource reset utility for BlazeTest.
This module handles deletion of all AWS resources created by BlazeTest.
"""

import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def reset_aws_resources(
    aws_region: str,
    ecr_repository_prefix: str,
    s3_bucket_prefix: str,
    lambda_function_prefix: str,
    iam_role_prefix: str,
    iam_policy_prefix: str,
) -> bool:
    """
    Delete all AWS resources created by BlazeTest.

    Args:
        aws_region: AWS region
        ecr_repository_prefix: ECR repository name prefix
        s3_bucket_prefix: S3 bucket name prefix
        lambda_function_prefix: Lambda function name prefix
        iam_role_prefix: IAM role name prefix
        iam_policy_prefix: IAM policy name prefix

    Returns:
        bool: True if reset was successful, False otherwise
    """
    logger.warning("=" * 80)
    logger.warning("WARNING: Resetting all BlazeTest AWS resources")
    logger.warning("This will delete:")
    logger.warning("  - ECR repository and all images")
    logger.warning("  - Lambda functions and all versions")
    logger.warning("  - S3 bucket contents")
    logger.warning("  - IAM roles and policies")
    logger.warning("  - Local Docker build cache")
    logger.warning("This operation CANNOT be undone!")
    logger.warning("=" * 80)

    success = True

    # 1. Delete ECR images
    try:
        logger.info(f"Deleting ECR repository: {ecr_repository_prefix}")
        _delete_ecr_repository(ecr_repository_prefix, aws_region)
    except Exception as e:
        logger.error(f"Failed to delete ECR repository: {e}")
        success = False

    # 2. Delete Lambda function
    try:
        logger.info(f"Deleting Lambda functions with prefix: {lambda_function_prefix}")
        _delete_lambda_functions(lambda_function_prefix, aws_region)
    except Exception as e:
        logger.error(f"Failed to delete Lambda functions: {e}")
        success = False

    # 3. Delete S3 bucket contents
    try:
        logger.info(f"Deleting S3 bucket contents with prefix: {s3_bucket_prefix}")
        _delete_s3_bucket_contents(s3_bucket_prefix, aws_region)
    except Exception as e:
        logger.error(f"Failed to delete S3 bucket contents: {e}")
        success = False

    # 4. Delete IAM role and policy (optional, as they may be reused)
    try:
        logger.info(f"Deleting IAM role: {iam_role_prefix}")
        _delete_iam_role(iam_role_prefix, iam_policy_prefix)
    except Exception as e:
        logger.warning(f"Could not delete IAM role (may be in use): {e}")

    # 5. Clear local Docker build cache
    try:
        logger.info("Clearing Docker build cache...")
        _clear_docker_cache()
    except Exception as e:
        logger.error(f"Failed to clear Docker cache: {e}")
        success = False

    if success:
        logger.info("✓ AWS resources reset successfully")
    else:
        logger.error("✗ Some resources could not be deleted")

    return success


def _delete_ecr_repository(repository_name: str, region: str):
    """Delete ECR repository and all its images."""
    try:
        # List all images
        result = subprocess.run(
            [
                "aws",
                "ecr",
                "list-images",
                "--repository-name",
                repository_name,
                "--region",
                region,
                "--query",
                "imageIds[*]",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        if result.stdout.strip() != "[]":
            # Delete all images
            subprocess.run(
                [
                    "aws",
                    "ecr",
                    "batch-delete-image",
                    "--repository-name",
                    repository_name,
                    "--region",
                    region,
                    "--image-ids",
                    result.stdout.strip(),
                ],
                capture_output=True,
                check=False,  # Don't fail if some images can't be deleted
            )
            logger.info(f"✓ Deleted all images from ECR repository: {repository_name}")
        else:
            logger.info(f"ECR repository {repository_name} is already empty")

    except subprocess.CalledProcessError as e:
        if "RepositoryNotFoundException" in e.stderr:
            logger.info(f"ECR repository {repository_name} does not exist")
        else:
            raise


def _delete_lambda_functions(function_prefix: str, region: str):
    """Delete Lambda functions with given prefix."""
    try:
        # List Lambda functions
        result = subprocess.run(
            [
                "aws",
                "lambda",
                "list-functions",
                "--region",
                region,
                "--query",
                f"Functions[?starts_with(FunctionName, `{function_prefix}`)].FunctionName",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        functions = json.loads(result.stdout)

        for function_name in functions:
            logger.info(f"Deleting Lambda function: {function_name}")

            # Delete all versions first
            versions_result = subprocess.run(
                [
                    "aws",
                    "lambda",
                    "list-versions-by-function",
                    "--function-name",
                    function_name,
                    "--region",
                    region,
                    "--query",
                    "Versions[].Version",
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            versions = json.loads(versions_result.stdout)
            for version in versions:
                if version != "$LATEST":
                    try:
                        subprocess.run(
                            [
                                "aws",
                                "lambda",
                                "delete-function",
                                "--function-name",
                                function_name,
                                "--qualifier",
                                version,
                                "--region",
                                region,
                            ],
                            capture_output=True,
                            check=False,
                        )
                    except Exception:
                        pass  # Continue even if version deletion fails

            # Delete the function itself
            subprocess.run(
                [
                    "aws",
                    "lambda",
                    "delete-function",
                    "--function-name",
                    function_name,
                    "--region",
                    region,
                ],
                capture_output=True,
                check=True,
            )
            logger.info(f"✓ Deleted Lambda function: {function_name}")

    except subprocess.CalledProcessError as e:
        if "ResourceNotFoundException" not in e.stderr:
            raise


def _delete_s3_bucket_contents(bucket_prefix: str, region: str):
    """Delete all contents from S3 buckets with given prefix."""
    try:
        # List buckets
        result = subprocess.run(
            [
                "aws",
                "s3api",
                "list-buckets",
                "--query",
                f"Buckets[?starts_with(Name, `{bucket_prefix}`)].Name",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        buckets = json.loads(result.stdout)

        for bucket_name in buckets:
            logger.info(f"Deleting contents of S3 bucket: {bucket_name}")
            subprocess.run(
                [
                    "aws",
                    "s3",
                    "rm",
                    f"s3://{bucket_name}",
                    "--recursive",
                    "--region",
                    region,
                ],
                capture_output=True,
                check=False,  # Don't fail if bucket is already empty
            )
            logger.info(f"✓ Deleted contents of S3 bucket: {bucket_name}")

    except subprocess.CalledProcessError:
        logger.warning("Could not delete S3 bucket contents")


def _delete_iam_role(role_name: str, policy_name: str):
    """Delete IAM role and associated policy."""
    try:
        # Detach policy from role
        subprocess.run(
            [
                "aws",
                "iam",
                "detach-role-policy",
                "--role-name",
                role_name,
                "--policy-arn",
                f"arn:aws:iam::*:policy/{policy_name}",
            ],
            capture_output=True,
            check=False,
        )

        # Delete policy
        subprocess.run(
            [
                "aws",
                "iam",
                "delete-policy",
                "--policy-arn",
                f"arn:aws:iam::*:policy/{policy_name}",
            ],
            capture_output=True,
            check=False,
        )

        # Delete role
        subprocess.run(
            ["aws", "iam", "delete-role", "--role-name", role_name],
            capture_output=True,
            check=False,
        )

        logger.info("✓ Deleted IAM role and policy")
    except Exception:
        pass  # IAM deletion is optional


def _clear_docker_cache():
    """Clear Docker build cache."""
    try:
        result = subprocess.run(
            ["docker", "builder", "prune", "-af"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("✓ Docker build cache cleared")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Could not clear Docker cache: {e}")
