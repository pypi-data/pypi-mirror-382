from abc import ABC, abstractmethod
import logging

from blazetest.core.cloud.aws.ecr import create_ecr_repository, get_ecr_login_token
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
        tags: dict,
        debug: bool,
        enable_cache: bool = True,
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
        self.tags = tags
        self.debug = debug
        self.build_backend = build_backend
        self.enable_cache = enable_cache

    @abstractmethod
    def deploy(self) -> str:
        """
        Deploy infrastructure and return qualified function name.

        Returns:
            str: Version-qualified Lambda function name for safe concurrent execution
        """
        pass


def log_pulumi_event(event: str):
    logger.info(event)


class AWSInfraSetup(InfraSetupTool):
    """
    Uses specified build backend and deploys artifacts using boto3 to AWS.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def deploy(self) -> str:
        """
        Deploy infrastructure and return qualified function name.

        Returns:
            str: Version-qualified Lambda function name for safe concurrent execution
        """
        env_vars = {}

        # TODO: Inject the AWS related resource classes / function in constructor or as a parameter
        repo_info = create_ecr_repository(
            aws_region=self.aws_region,
            ecr_repository_prefix=self.ecr_repository_prefix,
            tags=self.tags,
        )

        image_uri = self.build_and_push_image(
            repo_info=repo_info,
            build_backend=self.build_backend,
            enable_cache=self.enable_cache,
        )

        workflow = AWSWorkflow(
            aws_region=self.aws_region,
            resource_prefix=self.resource_prefix,
            s3_bucket_name=self.s3_bucket_name,
            env_vars=env_vars,
            tags=self.tags,
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
        self, repo_info: dict, build_backend: str = "depot", enable_cache: bool = True
    ):
        image_uri = f"{repo_info['repositoryUri']}:{self.session_uuid}"

        image_build_push = ImageBuildPush(
            backend=build_backend,
            project_context=CWD,
            docker_file_path=DOCKER_FILE_PATH,
            image_uri=image_uri,
            build_platform="linux/amd64",
            enable_cache=enable_cache,
        )

        # TODO: check if it works in the CI/CD pipeline
        username, password = get_ecr_login_token(aws_region=self.aws_region)
        image_build_push.login(
            username=username,
            password=password,
            registry=repo_info["repositoryUri"],
        )
        logger.info("Logged in")

        image_build_push.build()
        logger.info("Built image successfully")

        image_build_push.push()
        logger.info("Pushed image to ECR successfully")

        return image_uri
