import hashlib
import logging
import os
import platform
import shutil
import uuid
from pathlib import Path
from typing import List, Any, Optional

from blazetest.core.config import (
    BUILD_FOLDER_PATH,
    PWD,
    EXECUTABLE_FILES,
    CWD,
)

logger = logging.getLogger(__name__)

FILTER_ALL = "all"
FILTER_FAILED = "failed"
FILTER_FLAKY = "flaky"

LOGS_ENABLED = "enabled"
LOGS_DISABLED = "disabled"

SETUP_TOOL_AWS = "aws"


def parse_tags(tags: str = None) -> dict:
    """
    Parses tags from CLI in the format of 'key1=value1,key2=value2' into a dictionary

    :param tags: string of tags from CLI in the format of 'key1=value1,key2=value2'
    :return: dictionary of tags in the format of {'key1': 'value1', 'key2': 'value2'}
    """
    tags_d = {}

    if tags:
        tag_values = tags.split(",")

        for tag_value in tag_values:
            tag = tag_value.split("=")

            if len(tag) != 2:
                continue

            tags_d[tag[0]] = tag[1]

    return tags_d


def combine_tags(
    config_tags: Any, session_uuid: str, tags: Optional[str] = None
) -> dict:
    """
    Combines tags from CLI, config file and adds session UUID as a tag into one dictionary

    :param tags: string of tags from CLI in the format of 'key1=value1,key2=value2'
    :param config_tags: tags from BlazetestConfig object
    :param session_uuid: string of session UUID
    :return: dictionary with all tags in one dictionary
    """
    tags = parse_tags(tags)
    tags.update(dict(config_tags))
    tags["blazetest:uuid"] = session_uuid
    return tags


def generate_uuid() -> str:
    return str(uuid.uuid4())[:8]


def extract_selenium_version(project_dir: str = None) -> str:
    """
    Extract Selenium version from user's dependency files.
    This allows BlazeTest to use the same Selenium version as the user's tests.

    :param project_dir: Project directory (defaults to CWD)
    :return: Selenium version string (e.g., "4.36.0") or default "4.36.0" if not found
    """
    import re

    if project_dir is None:
        project_dir = CWD

    project_path = Path(project_dir)

    # Try requirements.txt first (most common)
    requirements_file = project_path / "requirements.txt"
    if requirements_file.exists():
        content = requirements_file.read_text()
        # Match patterns like: selenium==4.36.0, selenium>=4.6.0, selenium~=4.36
        match = re.search(
            r"selenium\s*[=~><!]+\s*([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
            content,
            re.IGNORECASE,
        )
        if match:
            version = match.group(1)
            # If it's a range like >=4.6.0, use the minimum version
            return version

    # Try pyproject.toml (Poetry)
    pyproject_file = project_path / "pyproject.toml"
    if pyproject_file.exists():
        content = pyproject_file.read_text()
        # Match patterns in [tool.poetry.dependencies] section
        # selenium = "^4.36.0" or selenium = ">=4.6.0"
        match = re.search(
            r'selenium\s*=\s*["\'][\^~><=]*([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            content,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)

    # Try Pipfile
    pipfile = project_path / "Pipfile"
    if pipfile.exists():
        content = pipfile.read_text()
        # Match patterns like: selenium = "==4.36.0" or selenium = "*"
        match = re.search(
            r'selenium\s*=\s*["\'][\^~><=]*([0-9]+\.[0-9]+(?:\.[0-9]+)?)',
            content,
            re.IGNORECASE,
        )
        if match:
            return match.group(1)

    # Default to 4.36.0 if not found
    return "4.36.0"


def compute_dependencies_hash(project_dir: str = None) -> str:
    """
    Compute a hash of just the dependency files (requirements.txt, etc).
    This is used to detect when dependencies change even if content hash is same.

    :param project_dir: Project directory (defaults to CWD)
    :return: 8-character hex hash of dependency files
    """
    if project_dir is None:
        project_dir = CWD

    hasher = hashlib.sha256()

    # Only hash dependency files
    dep_files = [
        "requirements.txt",
        "pyproject.toml",
        "poetry.lock",
        "Pipfile",
        "Pipfile.lock",
    ]

    for dep_file in dep_files:
        file_path = Path(project_dir) / dep_file
        if file_path.exists():
            hasher.update(dep_file.encode("utf-8"))
            hasher.update(file_path.read_bytes())

    return hasher.hexdigest()[:8]


def compute_project_hash(project_dir: str = None, config: Any = None) -> str:
    """
    Compute a hash of the project content to detect changes.
    This hash is used to determine if a Docker image needs to be rebuilt.

    :param project_dir: Project directory to hash (defaults to CWD)
    :param config: Project configuration object (optional)
    :return: 8-character hex hash of project content
    """
    if project_dir is None:
        project_dir = CWD

    hasher = hashlib.sha256()

    # Hash configuration settings that affect the image
    if config and hasattr(config, "aws"):
        # Hash Python version, browser settings, etc.
        hash_items = [
            str(get_python_version()),
            str(getattr(config.aws, "browser_type", "chrome")),
            str(getattr(config.aws, "browser_version", "latest")),
            str(getattr(config.aws, "install_browser", True)),
            str(getattr(config.aws, "install_allure", False)),
        ]
        for item in hash_items:
            hasher.update(item.encode("utf-8"))

    # Hash all Python files, requirements files, and test files
    patterns = [
        "**/*.py",
        "**/requirements*.txt",
        "**/pyproject.toml",
        "**/poetry.lock",
        "**/Pipfile",
        "**/Pipfile.lock",
        "**/pytest.ini",
        "**/.blazetest.toml",
    ]

    files_to_hash = []
    for pattern in patterns:
        files_to_hash.extend(sorted(Path(project_dir).glob(pattern)))

    # Sort files for consistent hashing
    for file_path in sorted(files_to_hash):
        try:
            # Skip .blazetest directory (generated), venv, .git, etc.
            if any(
                part in file_path.parts
                for part in [
                    ".blazetest",
                    "venv",
                    ".venv",
                    ".git",
                    "__pycache__",
                    ".pytest_cache",
                    "node_modules",
                ]
            ):
                continue

            # Hash relative path and file content
            rel_path = file_path.relative_to(project_dir)
            hasher.update(str(rel_path).encode("utf-8"))

            # Hash file content
            with open(file_path, "rb") as f:
                hasher.update(f.read())
        except (OSError, PermissionError):
            # Skip files we can't read
            pass

    # Return first 8 chars of hex digest
    return hasher.hexdigest()[:8]


def get_python_version() -> str:
    """
    Gets current Python version

    :return: string in the format of: '3.8', '3.7'
    """
    return ".".join(list(platform.python_version_tuple()[:2]))


def remove_junit_report_path(pytest_args: List[str]) -> List[str]:
    """Remove the `--junitxml` argument from a list of pytest arguments.

    :param pytest_args: List of pytest arguments.
    :return: List of pytest arguments with the `--junitxml` argument removed.
    """
    return [arg for arg in pytest_args if not arg.startswith("--junitxml")]


def set_environment_variables(
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_region: str = None,
):
    """Set AWS credentials as environment variables.

    :param aws_access_key_id: AWS access key ID.
    :param aws_secret_access_key: AWS secret access key.
    :param aws_region: AWS region.
    """
    if aws_access_key_id:
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id

    if aws_secret_access_key:
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key

    if aws_region:
        os.environ["AWS_DEFAULT_REGION"] = aws_region


def insert_python_version(dockerfile_path, python_version):
    """
    Inserts an indicated Python version to the Dockerfile variable PYTHON_VERSION

    :param dockerfile_path: Path to the Dockerfile
    :param python_version: Python version in the format '3.8'
    """
    with open(dockerfile_path, "r") as f:
        lines = f.read()

    # Replace only the default value in ARG PYTHON_VERSION=X.X, not the variable name itself
    lines = lines.replace(
        "ARG PYTHON_VERSION=3.9", f"ARG PYTHON_VERSION={python_version}"
    )
    with open(dockerfile_path, "w") as f:
        f.write(lines)


def create_artifacts_dir(artifacts_dir: str) -> None:
    """
    Create an artifacts directory in current working directory (CWD)

    :param artifacts_dir: Path to the artifacts directory
    """
    Path(os.path.join(CWD, artifacts_dir)).mkdir(parents=True, exist_ok=True)


# TODO: optimize function to be more readable and more efficient
def create_build_folder(remote_logging_enabled: bool) -> None:
    """
    Create a build folder and copy necessary files to it.

    Files located in .blazetest folder:
    - Dockerfile
    - scripts
        - install_dependencies.sh
    - tests_runner_handler
        - __init__.py
        - tests_runner_handler.py
    """
    # Remove existing build folder to ensure fresh copy of templates
    if os.path.exists(BUILD_FOLDER_PATH):
        shutil.rmtree(BUILD_FOLDER_PATH)

    # Create build folder and necessary subdirectories (scripts and tests_runner_handler)
    Path(BUILD_FOLDER_PATH).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(BUILD_FOLDER_PATH, "scripts")).mkdir(
        parents=True,
        exist_ok=True,
    )
    Path(os.path.join(BUILD_FOLDER_PATH, "tests_runner_handler")).mkdir(
        parents=True,
        exist_ok=True,
    )

    # Create list of source-destination file pairs for the files in EXECUTABLE_FILES
    src_dst_pairs = [
        (os.path.join(PWD, file), os.path.join(BUILD_FOLDER_PATH, file))
        for file in EXECUTABLE_FILES
    ]

    for src, dst in src_dst_pairs:
        shutil.copyfile(src=src, dst=dst)

    dockerfile = "RemoteLogging.Dockerfile" if remote_logging_enabled else "Dockerfile"

    shutil.copyfile(
        src=os.path.join(PWD, dockerfile),
        dst=os.path.join(BUILD_FOLDER_PATH, "Dockerfile"),
    )

    insert_python_version(
        dockerfile_path=os.path.join(BUILD_FOLDER_PATH, "Dockerfile"),
        python_version=get_python_version(),
    )

    logger.info("Successfully created build folder")


def print_table(data):
    max_lengths = [max(map(len, col)) for col in zip(*data)]

    for row in data:
        print("   ".join(word.ljust(length) for word, length in zip(row, max_lengths)))


def get_n_node_ids(node_ids: List[Any], items_per_sublist: int) -> List[List[Any]]:
    if items_per_sublist <= 0:
        raise ValueError("The value of items per sublist cannot be lower than 1")

    bin_size = max(len(node_ids) // items_per_sublist, 1)
    if len(node_ids) % items_per_sublist > 0 and len(node_ids) > items_per_sublist:
        bin_size += 1

    result = [[] for _ in range(bin_size)]

    for i, node_id in enumerate(node_ids):
        index = i // items_per_sublist
        result[index].append(node_id)

    return result


def flatten(elements: List[List[Any]]) -> List[Any]:
    result = []
    for li in elements:
        for element in li:
            result.append(element)
    return result
