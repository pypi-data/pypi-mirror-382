import html
import logging
import os
import platform
import shutil
import uuid
from pathlib import Path
from typing import List, Any, Optional


from junitparser.xunit2 import JUnitXml
import xml.etree.ElementTree as ET

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

    os.environ["PULUMI_CONFIG_PASSPHRASE"] = "pass"


def insert_python_version(dockerfile_path, python_version):
    """
    Inserts an indicated Python version to the Dockerfile variable PYTHON_VERSION

    :param dockerfile_path: Path to the Dockerfile
    :param python_version: Python version in the format '3.8'
    """
    with open(dockerfile_path, "r") as f:
        lines = f.read()

    lines = lines.replace("PYTHON_VERSION", python_version)
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


def xml_to_html(xml: JUnitXml):
    root = ET.fromstring(xml.tostring())

    # Create the HTML content
    html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>JUnit Test Results</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                h1 { color: #333; }
                .testsuite { margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }
                .testcase { margin: 10px 0; padding: 5px; background-color: #f4f4f4; }
                .properties { margin-top: 10px; }
                .property { margin-left: 20px; }
            </style>
        </head>
        <body>
            <h1>JUnit Test Results</h1>
        """

    # TODO: merge testsuites appropriately or use junit2html
    for testsuite in root.findall("testsuite"):
        html_content += f"""
            <div class="testsuite">
                <h2>Test Suite: {testsuite.get('name')}</h2>
                <p>Tests: {testsuite.get('tests')}, Errors: {testsuite.get('errors')},
                   Failures: {testsuite.get('failures')}, Skipped: {testsuite.get('skipped')}</p>
                <p>Time: {testsuite.get('time')} seconds</p>
                <p>Timestamp: {testsuite.get('timestamp')}</p>
                <p>Hostname: {testsuite.get('hostname')}</p>
            """

        for testcase in testsuite.findall("testcase"):
            html_content += f"""
                <div class="testcase">
                    <h3>Test Case: {testcase.get('name')}</h3>
                    <p>Classname: {testcase.get('classname')}</p>
                    <p>Time: {testcase.get('time')} seconds</p>
                </div>
                """

        properties = testsuite.find("properties")
        if properties is not None:
            html_content += "<div class='properties'><h3>Properties:</h3>"
            for prop in properties.findall("property"):
                html_content += f"""
                    <div class="property">
                        <p>{html.escape(prop.get('name'))}: {html.escape(prop.get('value'))}</p>
                    </div>
                    """
            html_content += "</div>"

        html_content += "</div>"

    html_content += "</body></html>"
    return html_content


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
