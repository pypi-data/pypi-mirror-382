from abc import ABC
import logging
import os

import docker
from tqdm import tqdm

from blazetest.core.utils.command_executor import CommandExecutor
from blazetest.core.utils.exceptions import DepotTokenNotProvided, ImagePushError

logger = logging.getLogger(__name__)


class BuildTool(ABC):
    EXECUTABLE = None

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        browser_type: str = "chrome",
        browser_version: str = "latest",
        install_browser: bool = True,
        install_allure: bool = False,
        build_backend: str = "docker",
        selenium_version: str = "4.36.0",
        *args,
        **kwargs,
    ):
        self.project_context = project_context
        self.docker_file_path = docker_file_path
        self.image_uri = image_uri
        self.build_platform = build_platform
        self.browser_type = browser_type
        self.browser_version = browser_version
        self.install_browser = "true" if install_browser else "false"
        self.install_allure = "true" if install_allure else "false"
        self.build_backend = build_backend
        self.selenium_version = selenium_version

    def login(self, username: str, password: str, registry: str):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError

    def build_and_push(self):
        raise NotImplementedError

    def execute(self, command: str, arguments: dict, allowed_return_codes=None) -> int:
        if allowed_return_codes is None:
            allowed_return_codes = [0]

        command_executor = CommandExecutor(
            executable=self.EXECUTABLE,
            command=command,
            arguments=arguments,
        )
        command_result = command_executor.execute_command(
            allowed_return_codes=allowed_return_codes
        )
        return command_result


class DepotBuildTool(BuildTool):
    """
    Uses depot.dev to build and push images to a remote repository.
    """

    EXECUTABLE = "depot"  # TODO: would executable work correctly?
    BUILD_COMMAND = "build"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        depot_token: str = None,
        depot_project_id: str = None,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )
        self.depot_token = depot_token
        if self.depot_token is None:
            self.depot_token = os.getenv("DEPOT_TOKEN")
            if self.depot_token is None:
                raise DepotTokenNotProvided(
                    "Depot token not provided. "
                    "Please provide it using --depot-token CLI argument or DEPOT_TOKEN environment variable."
                )
        self.depot_project_id = depot_project_id

    def build_and_push(self):
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            "--token": self.depot_token,
            "--push": None,
            "--provenance": "false",
            f"--build-arg BROWSER_TYPE={self.browser_type}": None,
            f"--build-arg BROWSER_VERSION={self.browser_version}": None,
            f"--build-arg INSTALL_BROWSER={self.install_browser}": None,
            f"--build-arg INSTALL_ALLURE={self.install_allure}": None,
            f"--build-arg BUILD_BACKEND={self.build_backend}": None,
            f"--build-arg SELENIUM_VERSION={self.selenium_version}": None,
            self.project_context: None,
        }

        if self.depot_project_id:
            args["--project"] = self.depot_project_id

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def login(self, username: str, password: str, registry: str = None):
        client = docker.from_env()
        client.login(username=username, password=password, registry=registry)


class NamespaceBuildTool(BuildTool):
    """
    Uses Namespace.so to build and push images to a remote repository.
    Namespace provides fast, cloud-based Docker builds with automatic caching.
    """

    EXECUTABLE = "nsc"  # Namespace CLI
    BUILD_COMMAND = "build"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        namespace_token: str = None,
        namespace_workspace: str = None,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )
        self.namespace_token = namespace_token
        if self.namespace_token is None:
            self.namespace_token = os.getenv("NSC_TOKEN")
            if self.namespace_token is None:
                raise Exception(
                    "Namespace token not provided. "
                    "Please provide it using --namespace-token CLI argument, "
                    "NSC_TOKEN environment variable, or in blazetest.toml [build.namespace] section."
                )
        self.namespace_workspace = namespace_workspace
        if self.namespace_workspace is None:
            self.namespace_workspace = os.getenv("NSC_WORKSPACE")

    def build_and_push(self):
        """
        Build and push image using Namespace.so CLI.
        Command: nsc build --tag <uri> --file <dockerfile> --platform <platform> --push .
        """
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            "--push": None,
            f"--build-arg BROWSER_TYPE={self.browser_type}": None,
            f"--build-arg BROWSER_VERSION={self.browser_version}": None,
            f"--build-arg INSTALL_BROWSER={self.install_browser}": None,
            f"--build-arg INSTALL_ALLURE={self.install_allure}": None,
            f"--build-arg BUILD_BACKEND={self.build_backend}": None,
            f"--build-arg SELENIUM_VERSION={self.selenium_version}": None,
            self.project_context: None,
        }

        # Add workspace if specified
        if self.namespace_workspace:
            args["--workspace"] = self.namespace_workspace

        # Set token as environment variable for nsc CLI
        if self.namespace_token:
            os.environ["NSC_TOKEN"] = self.namespace_token

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def login(self, username: str, password: str, registry: str = None):
        """Use Docker client to login to container registry"""
        client = docker.from_env()
        client.login(username=username, password=password, registry=registry)


class DockerBuildTool(BuildTool):
    """
    This class will be used to build and push images from local Docker.
    """

    EXECUTABLE = "docker"
    BUILD_COMMAND = "build"
    PUSH_COMMAND = "push"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        enable_cache: bool = True,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )
        self.client = docker.from_env()
        self.enable_cache = enable_cache

    def login(self, username: str, password: str, registry: str):
        # TODO: not working correctly, resulting in "Your authorization token has expired. Reauthenticate.."
        self.client.login(username=username, password=password, registry=registry)

    def build_and_push(self):
        self.build()
        self.push()

    def build(self):
        # Set DOCKER_BUILDKIT for better caching and performance
        os.environ["DOCKER_BUILDKIT"] = "1"

        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            "--build-arg": f"BROWSER_TYPE={self.browser_type}",
            self.project_context: None,
        }

        # Add browser version and install flag as separate build args
        # Note: CommandExecutor will need to handle multiple --build-arg values
        if self.browser_version:
            args[f"--build-arg BROWSER_VERSION={self.browser_version}"] = None
        if self.install_browser:
            args[f"--build-arg INSTALL_BROWSER={self.install_browser}"] = None
        args[f"--build-arg INSTALL_ALLURE={self.install_allure}"] = None
        args[f"--build-arg BUILD_BACKEND={self.build_backend}"] = None
        args[f"--build-arg SELENIUM_VERSION={self.selenium_version}"] = None

        # Enable BuildKit inline cache for faster rebuilds
        if self.enable_cache:
            args["--cache-from"] = self.image_uri
            args["--build-arg BUILDKIT_INLINE_CACHE=1"] = None

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def push(self):
        # TODO: if push fails, need to handle it
        progress_bars = {}

        logger.info("Pushing an image to ECR...")
        try:
            for line in self.client.images.push(
                self.image_uri, decode=True, stream=True
            ):
                if "error" in line:
                    raise ImagePushError(f"Error pushing image: {line['error']}")

                if (
                    "progressDetail" in line
                    and "current" in line["progressDetail"]
                    and "total" in line["progressDetail"]
                ):
                    layer_id = line["id"]
                    current = line["progressDetail"]["current"]
                    total = line["progressDetail"]["total"]

                    if layer_id not in progress_bars:
                        progress_bars[layer_id] = tqdm(
                            total=total,
                            desc=f"Layer {layer_id[:8]}",
                            unit="B",
                            unit_scale=True,
                            leave=True,
                        )

                    progress_bars[layer_id].update(current - progress_bars[layer_id].n)

                elif "status" in line:
                    if line["status"] == "Pushed":
                        layer_id = line["id"]
                        if layer_id in progress_bars:
                            progress_bars[layer_id].close()
                            del progress_bars[layer_id]
                    elif line["status"].startswith("Pushing"):
                        pass

        except ImagePushError as e:
            logger.error(f"Push failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during push: {str(e)}")
            raise
        finally:
            # Close any remaining progress bars
            for bar in progress_bars.values():
                bar.close()

        print()

        logger.info("Image push completed.")


class DockerCloudBuildTool(BuildTool):
    """
    This class will be used to build and push images from Docker Cloud.
    """

    EXECUTABLE = "docker buildx"
    CREATE_COMMAND = "create"
    BUILD_COMMAND = "build"
    PUSH_COMMAND = "push"

    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
    ):
        super().__init__(
            project_context=project_context,
            docker_file_path=docker_file_path,
            image_uri=image_uri,
            build_platform=build_platform,
        )

    def login(self, username: str, password: str, registry: str):
        client = docker.from_env()
        client.login(username=username, password=password, registry=registry)

    def build_and_push(self):  # aws_username: str, aws_password: str, aws_registry: str
        self.build()
        # Login to ECR
        # self.login()
        self.push()

    def create_cloud_builder(self):
        args = {
            "--driver": "cloud",
            "--name": "builder",
        }

        return self.execute(
            command=self.CREATE_COMMAND,
            arguments=args,
        )

    def build(self):
        args = {
            "--tag": self.image_uri,
            "--file": self.docker_file_path,
            "--platform": self.build_platform,
            self.project_context: None,
        }

        return self.execute(
            command=self.BUILD_COMMAND,
            arguments=args,
        )

    def push(self):
        args = {
            self.image_uri: None,
        }

        return self.execute(
            command=self.PUSH_COMMAND,
            arguments=args,
        )


class RemoteBuildTool(BuildTool):
    """
    This class will be used to build and push images from AWS CodeBuild, Google Cloud Build, etc.
    """

    def __init__(self):
        raise NotImplementedError("RemoteBuildTool is not implemented yet.")

    def build(self):
        raise NotImplementedError

    def push(self):
        raise NotImplementedError
