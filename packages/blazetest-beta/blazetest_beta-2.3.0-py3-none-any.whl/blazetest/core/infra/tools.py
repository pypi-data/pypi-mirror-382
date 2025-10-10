from abc import ABC, abstractmethod
import logging

from blazetest.core.cloud.aws.ecr import (
    create_ecr_repository,
    get_ecr_login_token,
    check_image_exists,
)
from blazetest.core.config import CWD, LOKI_HOST, LOKI_USER, DOCKER_FILE_PATH
from blazetest.core.cloud.aws.workflow import AWSWorkflow
from blazetest.core.container_image.base import ImageBuildPush

logger = logging.getLogger(__name__)


class InfraSetupTool(ABC):
    def __init__(
        self,
        session_uuid: str,
        aws_region: str,
        resource_prefix: str,
        s3_bucket_name: str,
        ecr_repository_prefix: str,
        lambda_function_timeout: int,
        lambda_function_memory_size: int,
        loki_api_key: str,
        build_backend: str,
        depot_token: str,
        depot_project_id: str,
        namespace_token: str,
        namespace_workspace: str,
        tags: dict,
        debug: bool,
        enable_cache: bool = True,
        browser_type: str = "chrome",
        browser_version: str = "latest",
        install_browser: bool = True,
        install_allure: bool = False,
        selenium_version: str = "4.36.0",
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        aws_role_arn: str = None,
        aws_profile: str = None,
    ):
        self.session_uuid = session_uuid
        self.aws_region = aws_region
        self.resource_prefix = resource_prefix
        self.s3_bucket_name = s3_bucket_name
        self.ecr_repository_prefix = ecr_repository_prefix
        self.lambda_function_timeout = lambda_function_timeout
        self.lambda_function_memory_size = lambda_function_memory_size
        self.loki_api_key = loki_api_key
        self.depot_token = depot_token
        self.depot_project_id = depot_project_id
        self.namespace_token = namespace_token
        self.namespace_workspace = namespace_workspace
        self.tags = tags
        self.debug = debug
        self.build_backend = build_backend
        self.enable_cache = enable_cache
        self.browser_type = browser_type
        self.browser_version = browser_version
        self.install_browser = install_browser
        self.install_allure = install_allure
        self.selenium_version = selenium_version
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_session_token = aws_session_token
        self.aws_role_arn = aws_role_arn
        self.aws_profile = aws_profile

    @abstractmethod
    def deploy(
        self, content_hash: str, dependencies_hash: str, force_rebuild: bool = False
    ) -> str:
        """
        Deploy infrastructure and return qualified function name.

        Args:
            content_hash: Hash of project content to use as image tag
            dependencies_hash: Hash of dependency files for smart invalidation
            force_rebuild: Force rebuild even if cached image exists

        Returns:
            str: Version-qualified Lambda function name for safe concurrent execution
        """
        pass


class AWSInfraSetup(InfraSetupTool):
    """
    Uses specified build backend and deploys artifacts using boto3 to AWS.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def deploy(
        self, content_hash: str, dependencies_hash: str, force_rebuild: bool = False
    ) -> str:
        """
        Deploy infrastructure and return qualified function name.

        Args:
            content_hash: Hash of project content to use as image tag
            dependencies_hash: Hash of dependency files for smart invalidation
            force_rebuild: Force rebuild even if cached image exists

        Returns:
            str: Version-qualified Lambda function name for safe concurrent execution
        """
        env_vars = {}

        # TODO: Inject the AWS related resource classes / function in constructor or as a parameter
        repo_info = create_ecr_repository(
            aws_region=self.aws_region,
            ecr_repository_prefix=self.ecr_repository_prefix,
            tags=self.tags,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            role_arn=self.aws_role_arn,
            profile=self.aws_profile,
        )

        image_uri = self.build_and_push_image(
            repo_info=repo_info,
            content_hash=content_hash,
            dependencies_hash=dependencies_hash,
            build_backend=self.build_backend,
            enable_cache=self.enable_cache,
            force_rebuild=force_rebuild,
        )

        workflow = AWSWorkflow(
            aws_region=self.aws_region,
            resource_prefix=self.resource_prefix,
            s3_bucket_name=self.s3_bucket_name,
            env_vars=env_vars,
            tags=self.tags,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            role_arn=self.aws_role_arn,
            profile=self.aws_profile,
        )

        logger.info("Deploying...")
        qualified_function_name = workflow.deploy(
            image_uri=image_uri,
            function_timeout=self.lambda_function_timeout,
            memory_size=self.lambda_function_memory_size,
            loki_host=LOKI_HOST,
            loki_user=LOKI_USER,
            loki_api_key=self.loki_api_key,
        )
        logger.info("Deploying has finished")

        return qualified_function_name

    def build_and_push_image(
        self,
        repo_info: dict,
        content_hash: str,
        dependencies_hash: str,
        build_backend: str = "depot",
        enable_cache: bool = True,
        force_rebuild: bool = False,
    ):
        # Use content hash as image tag for better caching
        image_uri = f"{repo_info['repositoryUri']}:{content_hash}"
        repository_name = repo_info["repositoryUri"].split("/")[-1]

        # Check if image with this content hash already exists in ECR (unless force rebuild)
        image_exists = check_image_exists(
            aws_region=self.aws_region,
            repository_name=repository_name,
            image_tag=content_hash,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            role_arn=self.aws_role_arn,
            profile=self.aws_profile,
        )

        if not force_rebuild and image_exists:
            # Image exists with same content hash - check if dependencies changed
            from blazetest.core.cloud.aws.ecr import get_image_metadata

            stored_dependencies_hash = get_image_metadata(
                aws_region=self.aws_region,
                repository_name=repository_name,
                image_tag=content_hash,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                aws_session_token=self.aws_session_token,
                role_arn=self.aws_role_arn,
                profile=self.aws_profile,
            )

            if (
                stored_dependencies_hash
                and stored_dependencies_hash != dependencies_hash
            ):
                logger.info(
                    f"Dependencies changed (stored: {stored_dependencies_hash}, current: {dependencies_hash}). Rebuilding..."
                )
                force_rebuild = True
            else:
                logger.info(
                    f"Image with tag {content_hash} already exists in ECR. Skipping build."
                )
                logger.info(
                    "Tip: Use --force-rebuild flag if you've updated test files or dependencies."
                )
                return image_uri

        if force_rebuild:
            if image_exists:
                logger.info(
                    "Force rebuild requested (image exists but rebuilding anyway)..."
                )
            else:
                logger.info(
                    f"Force rebuild requested. Building new image with tag {content_hash}..."
                )

        logger.info(f"Building new image with tag {content_hash}...")

        image_build_push = ImageBuildPush(
            backend=build_backend,
            project_context=CWD,
            docker_file_path=DOCKER_FILE_PATH,
            image_uri=image_uri,
            build_platform="linux/amd64",
            enable_cache=enable_cache,
            browser_type=self.browser_type,
            browser_version=self.browser_version,
            install_browser=self.install_browser,
            install_allure=self.install_allure,
            selenium_version=self.selenium_version,
            dependencies_hash=dependencies_hash,
            depot_token=self.depot_token,
            depot_project_id=self.depot_project_id,
            namespace_token=self.namespace_token,
            namespace_workspace=self.namespace_workspace,
        )

        # TODO: check if it works in the CI/CD pipeline
        username, password = get_ecr_login_token(
            aws_region=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            role_arn=self.aws_role_arn,
            profile=self.aws_profile,
        )
        image_build_push.login(
            username=username,
            password=password,
            registry=repo_info["repositoryUri"],
        )
        logger.info("Logged in")

        image_build_push.build()
        logger.info("Built image successfully")
        logger.info(f"Image hash: {content_hash}")

        image_build_push.push()
        logger.info("Pushed image to ECR successfully")

        return image_uri
