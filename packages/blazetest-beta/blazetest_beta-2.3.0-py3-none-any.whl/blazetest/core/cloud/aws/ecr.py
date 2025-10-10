import base64
import datetime
import logging
from typing import Tuple, List, Optional

from blazetest.core.cloud.aws.session import AWSSessionManager
from blazetest.core.cloud.aws.error_handler import handle_aws_errors

logger = logging.getLogger(__name__)


@handle_aws_errors
def create_ecr_repository(
    aws_region: str,
    tags: dict,
    ecr_repository_prefix: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
):
    # Configure session manager and get ECR client
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr = session_mgr.get_client("ecr")

    ecr_tags = []
    for tag in tags:
        ecr_tags.append({"Key": tag, "Value": tags[tag]})

    try:
        response = ecr.create_repository(
            repositoryName=ecr_repository_prefix, tags=ecr_tags
        )
        repository = response["repository"]
        logger.info(f"Repository '{ecr_repository_prefix}' created successfully.")
        return repository
    except ecr.exceptions.RepositoryAlreadyExistsException:
        logger.warning(f"Repository '{ecr_repository_prefix}' already exists.")
        # Fetch existing repository info
        response = ecr.describe_repositories(repositoryNames=[ecr_repository_prefix])
        repository = response["repositories"][0]
        return repository
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise e


@handle_aws_errors
def get_ecr_login_token(
    aws_region: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
) -> Tuple[str, str]:
    # Configure session manager and get ECR client
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr = session_mgr.get_client("ecr")

    response = ecr.get_authorization_token()

    auth_data = response["authorizationData"][0]
    token = auth_data["authorizationToken"]

    decoded_token = base64.b64decode(token).decode("utf-8")
    username, password = decoded_token.split(":")

    return username, password


@handle_aws_errors
def check_image_exists(
    aws_region: str,
    repository_name: str,
    image_tag: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
) -> bool:
    """
    Check if an image with the specified tag exists in ECR repository.

    :param aws_region: AWS region
    :param repository_name: ECR repository name
    :param image_tag: Image tag to check
    :return: True if image exists, False otherwise
    """
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr = session_mgr.get_client("ecr")

    try:
        response = ecr.describe_images(
            repositoryName=repository_name, imageIds=[{"imageTag": image_tag}]
        )
        return len(response.get("imageDetails", [])) > 0
    except ecr.exceptions.ImageNotFoundException:
        return False
    except ecr.exceptions.RepositoryNotFoundException:
        return False
    except Exception as e:
        logger.debug(f"Error checking if image exists: {e}")
        return False


@handle_aws_errors
def get_image_metadata(
    aws_region: str,
    repository_name: str,
    image_tag: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
) -> Optional[str]:
    """
    Get the dependencies hash stored in image manifest labels.

    :param aws_region: AWS region
    :param repository_name: ECR repository name
    :param image_tag: Image tag to check
    :return: Dependencies hash if found, None otherwise
    """
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr = session_mgr.get_client("ecr")

    try:
        # Get image manifest to read labels
        response = ecr.batch_get_image(
            repositoryName=repository_name,
            imageIds=[{"imageTag": image_tag}],
            acceptedMediaTypes=["application/vnd.docker.distribution.manifest.v1+json"],
        )

        if not response.get("images"):
            return None

        import json

        manifest = json.loads(response["images"][0]["imageManifest"])

        # Parse v1 manifest to get labels from history
        if "history" in manifest:
            for history_item in manifest["history"]:
                v1_compatibility = json.loads(history_item.get("v1Compatibility", "{}"))
                config = v1_compatibility.get("config", {})
                labels = config.get("Labels", {})

                if "blazetest.dependencies_hash" in labels:
                    return labels["blazetest.dependencies_hash"]

        return None
    except Exception as e:
        logger.debug(f"Error getting image metadata: {e}")
        return None


@handle_aws_errors
def tag_image_with_metadata(
    aws_region: str,
    repository_name: str,
    image_tag: str,
    dependencies_hash: str,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
):
    """
    Tag an ECR image with metadata (dependencies hash).
    Note: ECR doesn't support adding labels after push, so this metadata
    should be baked into the Docker image at build time via LABEL instruction.

    :param aws_region: AWS region
    :param repository_name: ECR repository name
    :param image_tag: Image tag to tag
    :param dependencies_hash: Dependencies hash to store
    """
    # Note: This function is a placeholder. The actual implementation
    # should add the LABEL to the Dockerfile at build time.
    # ECR metadata is read-only after push.
    logger.debug(
        f"Metadata should be added to image at build time: "
        f"LABEL blazetest.dependencies_hash={dependencies_hash}"
    )


@handle_aws_errors
def list_ecr_repositories_to_purge(
    aws_region: str,
    run_id: str,
    time_limit: int,
    exclude_tags: List[str],
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
) -> List[str]:
    current_time = datetime.datetime.now(datetime.timezone.utc)
    time_threshold = current_time - datetime.timedelta(hours=time_limit)

    # Configure session manager and get ECR client
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr_client = session_mgr.get_client("ecr")

    repositories_to_delete = []

    paginator = ecr_client.get_paginator("describe_repositories")
    for page in paginator.paginate():
        for repository in page["repositories"]:
            repository_name = repository["repositoryName"]
            repository_arn = repository["repositoryArn"]

            # Get the repository tags
            try:
                tags_response = ecr_client.list_tags_for_resource(
                    resourceArn=repository_arn
                )
                tags = {tag["Key"]: tag["Value"] for tag in tags_response["tags"]}
            except Exception as e:
                logger.error(
                    f"Error getting tags for repository {repository_name}: {str(e)}"
                )
                continue

            if tags.get("blazetest:uuid") is None:
                logger.debug(
                    f"Repository {repository_name} is not blazetest repository"
                )
                continue

            # Check if the repository has the specified run_id
            if run_id and tags.get("blazetest:uuid") == run_id:
                repositories_to_delete.append(repository_name)
                continue

            # Check if the repository is within the time limit
            if repository["createdAt"] < time_threshold:
                logger.debug(
                    f"Repository {repository_name} is older than the time limit: {repository['createdAt']}"
                )
                continue

            # Check if the repository has any of the excluded tags
            if exclude_tags and any(tag in tags for tag in exclude_tags):
                logger.debug(f"Repository {repository_name} has excluded tags: {tags}")
                continue

            repositories_to_delete.append(repository_name)

    return repositories_to_delete


@handle_aws_errors
def batch_delete_ecr_repositories(
    aws_region: str,
    repositories: List[str],
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    role_arn: Optional[str] = None,
    profile: Optional[str] = None,
):
    # Configure session manager and get ECR client
    session_mgr = AWSSessionManager()
    session_mgr.configure(
        region=aws_region,
        access_key_id=aws_access_key_id,
        secret_access_key=aws_secret_access_key,
        session_token=aws_session_token,
        role_arn=role_arn,
        profile=profile,
    )
    ecr_client = session_mgr.get_client("ecr")

    for repository_name in repositories:
        try:
            ecr_client.delete_repository(repositoryName=repository_name, force=True)
            logger.info(f"Deleted ECR repository: {repository_name}")
        except Exception as e:
            logger.error(f"Error deleting repository {repository_name}: {str(e)}")
