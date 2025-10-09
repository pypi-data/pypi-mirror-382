import json
import logging
import os
from typing import List, Dict

import boto3
import pytest
import xml.etree.ElementTree as ET

PWD = os.path.dirname(__file__)
logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        format="%(process)d-%(levelname)s-%(message)s", level=logging.INFO
    )


class S3Upload:
    def __init__(self, region):
        self.client = boto3.client(
            "s3",
            region_name=region,
        )

    def upload_file_to_s3_bucket(
        self,
        filepath: str,
        timestamp: str,
        s3_bucket: str,
        session_uuid: str,
        retry: bool,
    ) -> str:
        filename = os.path.basename(filepath)
        dst_folder = os.path.join(session_uuid, f"{timestamp}/target/junitxml")
        dst_filepath = os.path.join(dst_folder, filename)

        if retry:
            dst_filepath = os.path.join(dst_folder, f"flaky-{filename}")

        try:
            with open(filepath, "rb") as f:
                self.client.put_object(
                    Body=f,
                    Bucket=s3_bucket,
                    Key=dst_filepath,
                )
        except FileNotFoundError as err:
            logger.error(f"Seems like the test was not properly executed: {err}")
            raise err

        return dst_filepath


def execute_tests(args: List[str]):
    return pytest.main(args)


def upload_allure_results(
    s3_client,
    allure_dir: str,
    session_uuid: str,
    s3_bucket: str,
    timestamp: str,
    retry: bool,
) -> List[str]:
    """Upload all Allure result files to S3."""
    uploaded_paths = []

    if not os.path.exists(allure_dir):
        logger.warning(f"Allure results directory not found: {allure_dir}")
        return uploaded_paths

    # Upload all JSON files from allure-results directory
    for filename in os.listdir(allure_dir):
        filepath = os.path.join(allure_dir, filename)
        if not os.path.isfile(filepath):
            continue

        # Construct S3 path
        dst_folder = os.path.join(session_uuid, f"{timestamp}/target/allure-results")
        if retry:
            dst_folder = os.path.join(
                session_uuid, f"{timestamp}/target/allure-results-flaky"
            )
        dst_filepath = os.path.join(dst_folder, filename)

        try:
            with open(filepath, "rb") as f:
                s3_client.put_object(
                    Body=f,
                    Bucket=s3_bucket,
                    Key=dst_filepath,
                )
            uploaded_paths.append(dst_filepath)
            logger.debug(f"Uploaded Allure result: {dst_filepath}")
        except Exception as e:
            logger.error(f"Failed to upload Allure result {filename}: {str(e)}")

    return uploaded_paths


def parse_junit_xml(
    xml_file_path: str, s3_path: str, node_ids: List[str]
) -> List[Dict]:
    tree = ET.parse(xml_file_path)

    root = tree.getroot()
    test_results = []

    for testcase in root.iter("testcase"):
        classname = testcase.get("classname")
        name = testcase.get("name")
        node_id = f"{classname}::{name}"

        if testcase.find("failure") is not None:
            result = "failure"
        elif testcase.find("error") is not None:
            result = "error"
        elif testcase.find("skipped") is not None:
            result = "skipped"
        else:
            result = "passed"

        pytest_node_id = node_id
        for _node_id in node_ids:
            node = _node_id.split("::")
            function_name = node.pop()
            function_path = ".".join(node).replace(".py", "").replace("/", ".")

            if function_name == name and function_path == classname:
                pytest_node_id = _node_id

        test_result = {
            "node_id": pytest_node_id,
            "test_result": result,
            "report_path": s3_path,
        }
        test_results.append(test_result)

    return test_results


def run_tests(event, context=None) -> Dict:  # noqa
    setup_logging()

    pytest_args: List[str] = event["pytest_args"]
    node_ids: List[str] = event["node_ids"]
    report_path: str = event["report_path"]
    region: str = event["region"]
    session_uuid: str = event["session_uuid"]
    timestamp: str = event["start_timestamp"]
    retry: bool = event["retry"]

    s3 = S3Upload(region=region)
    s3_bucket = os.environ.get("S3_BUCKET")

    logger.info(f"Invoking tests: {node_ids} with pytest args: {pytest_args}")

    # Generate both JUnit XML (for backward compatibility) and Allure results
    allure_results_dir = "/tmp/allure-results"
    os.makedirs(allure_results_dir, exist_ok=True)

    args = [
        *node_ids,
        f"--junitxml={report_path}",
        f"--alluredir={allure_results_dir}",
    ] + pytest_args

    execute_tests(args=args)

    # Upload JUnit XML report
    s3_path = s3.upload_file_to_s3_bucket(
        filepath=report_path,
        session_uuid=session_uuid,
        s3_bucket=s3_bucket,
        timestamp=timestamp,
        retry=retry,
    )

    # Upload Allure results directory (all JSON files)
    allure_s3_paths = upload_allure_results(
        s3_client=s3.client,
        allure_dir=allure_results_dir,
        session_uuid=session_uuid,
        s3_bucket=s3_bucket,
        timestamp=timestamp,
        retry=retry,
    )
    logger.info(f"Uploaded {len(allure_s3_paths)} Allure result files")

    test_results = parse_junit_xml(
        xml_file_path=report_path, s3_path=s3_path, node_ids=node_ids
    )

    logger.info(f"Test result: {test_results}")

    response = {
        "statusCode": 200,
        "body": json.dumps(test_results),
    }

    return response
