from blazetest.core.container_image.tools import (
    DockerBuildTool,
    DepotBuildTool,
    NamespaceBuildTool,
    RemoteBuildTool,
    BuildTool,
    DockerCloudBuildTool,
)

backends: dict[str, type[BuildTool]] = {
    "docker": DockerBuildTool,
    "docker-cloud": DockerCloudBuildTool,
    "depot": DepotBuildTool,
    "namespace": NamespaceBuildTool,
    "remote": RemoteBuildTool,
}


class ImageBuildPush:
    def __init__(
        self,
        project_context: str,
        docker_file_path: str,
        image_uri: str,
        build_platform: str,
        backend="depot",
        enable_cache: bool = True,
        *args,
        **kwargs,
    ):
        """
        ImageBuildPusher is a class that builds and pushes images to a remote repository using supported backends.
        Supported backends: "docker" (local), "depot" (depot.dev), "namespace" (namespace.so), "docker-cloud".

        Example usage:
            ```
            image_build_pusher = ImageBuildPush(
                project_context=".",
                docker_file_path="Dockerfile",
                image_uri="123456789.dkr.ecr.us-west-2.amazonaws.com/blazetest",
                build_platform="linux/amd64",
                backend="depot",
                depot_token="depot_token",
                depot_project_id="depot_project_id",
                enable_cache=True,
            )
            image_build_push.login()
            image_build_push.build_and_push()
            ```

        Args:
            project_context: The path to the project context.
            docker_file_path: The path to the Dockerfile.
            image_uri: The URI of the remote repository.
            build_platform: The platform to build the image for.
            backend: The backend to use for building and pushing the image.
            enable_cache: Whether to enable Docker BuildKit caching (for docker backend).
        """
        # Only pass enable_cache to backends that support it (docker)
        backend_kwargs = {
            "project_context": project_context,
            "docker_file_path": docker_file_path,
            "image_uri": image_uri,
            "build_platform": build_platform,
            "build_backend": backend,
            **kwargs,
        }

        if backend == "docker":
            backend_kwargs["enable_cache"] = enable_cache

        self.backend = backends[backend](*args, **backend_kwargs)

    def login(self, username: str, password: str, registry: str):
        self.backend.login(username, password, registry)

    def build(self):
        self.backend.build()

    def push(self):
        self.backend.push()
