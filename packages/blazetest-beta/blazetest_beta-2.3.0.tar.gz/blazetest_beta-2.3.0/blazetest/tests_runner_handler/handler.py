import json
import logging
import os
import time
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


def _patch_selenium_chrome():
    """
    Monkey-patch Selenium's Chrome WebDriver to automatically inject Lambda-compatible options.
    This ensures all Chrome instances created during test execution have the required flags.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions

        # Store original Chrome __init__
        _original_chrome_init = webdriver.Chrome.__init__

        def _patched_chrome_init(self, options=None, *args, **kwargs):
            """Patched Chrome init that injects Lambda-compatible options."""
            if options is None:
                options = ChromeOptions()

            # Lambda-required Chrome arguments with their argument prefixes for conflict detection
            lambda_args_map = {
                "--headless": "--headless=new",  # Replace old headless with new
                "--remote-debugging-port": "--remote-debugging-port=9222",
                "--user-data-dir": "--user-data-dir=/tmp/chrome-user-data",
                "--data-path": "--data-path=/tmp/chrome-data",
                "--disk-cache-dir": "--disk-cache-dir=/tmp/chrome-cache",
                "--homedir": "--homedir=/tmp",
                "--window-size": "--window-size=1920,1080",
            }

            # These args have no conflicts and should always be added
            # Note: Removed --single-process as it causes renderer connection issues in modern Chrome
            required_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--disable-software-rasterizer",
                "--disable-extensions",
                "--disable-features=VizDisplayCompositor",  # Helps with renderer crashes
                "--disable-backgrounding-occluded-windows",  # Prevents background process issues
                "--disable-renderer-backgrounding",  # Keep renderer active
                "--disable-blink-features=AutomationControlled",  # Hide webdriver detection
                "--disable-features=IsolateOrigins,site-per-process",  # Reduce process isolation overhead
            ]

            # Remove conflicting args and add Lambda-compatible versions
            existing_args = list(options.arguments)
            for prefix, lambda_arg in lambda_args_map.items():
                # Remove any existing argument with this prefix
                options.arguments[:] = [
                    arg for arg in options.arguments if not arg.startswith(prefix)
                ]
                # Add Lambda-compatible version
                options.add_argument(lambda_arg)

            # Add required args if not present
            for arg in required_args:
                if arg not in options.arguments:
                    options.add_argument(arg)

            # Log final Chrome arguments for debugging
            print(f"[BlazeTest] Chrome arguments: {options.arguments}")
            logger.info(f"Chrome arguments: {options.arguments}")

            # Call original init with modified options
            return _original_chrome_init(self, options=options, *args, **kwargs)

        # Apply the patch
        webdriver.Chrome.__init__ = _patched_chrome_init
        logger.info(
            "Successfully patched Selenium Chrome WebDriver for Lambda environment"
        )

    except ImportError:
        logger.warning("Selenium not installed, skipping Chrome patching")
    except Exception as e:
        logger.error(f"Failed to patch Selenium Chrome: {e}")


def execute_tests(args: List[str]):
    # Automatically patch Selenium to inject Lambda-compatible Chrome options
    # This ensures all Chrome instances get the required flags without user intervention
    _patch_selenium_chrome()

    # Set Lambda-optimized Chrome flags as environment variables (for backward compatibility)
    # These can be accessed in user's conftest.py via os.environ.get('CHROME_FLAGS', '').split()
    os.environ["CHROME_FLAGS"] = " ".join(
        [
            "--remote-debugging-port=9222",
            "--user-data-dir=/tmp/chrome-user-data",
            "--data-path=/tmp/chrome-data",
            "--disk-cache-dir=/tmp/chrome-cache",
            "--homedir=/tmp",
        ]
    )

    # Set Selenium-specific Chrome arguments for Lambda environment (for backward compatibility)
    # These fix "DevToolsActivePort file doesn't exist" errors
    # Users should read this in conftest.py: os.environ.get('SELENIUM_CHROME_ARGS', '').split()
    os.environ["SELENIUM_CHROME_ARGS"] = " ".join(
        [
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--single-process",
            "--disable-setuid-sandbox",
            "--disable-software-rasterizer",
            "--disable-extensions",
        ]
    )

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


def verify_s3_permissions(s3_client, s3_bucket: str, session_uuid: str) -> bool:
    """
    Verify S3 permissions before running tests to catch IAM issues early.

    This check helps detect:
    - Policy mismatches (wrong bucket name in policy)
    - IAM eventual consistency issues
    - Missing s3:PutObject permissions

    Args:
        s3_client: Boto3 S3 client
        s3_bucket: S3 bucket name
        session_uuid: Session UUID for creating test key

    Returns:
        True if permissions are verified, raises exception otherwise
    """
    # Use print() in addition to logger to ensure message appears in CloudWatch
    print("Checking S3 permissions against policy...")
    logger.info("Checking S3 permissions against policy...")

    # Wait 2 seconds to allow IAM eventual consistency
    time.sleep(2.0)

    # Create a test key to verify write permissions
    test_key = f"{session_uuid}/permission-check.txt"
    test_content = b"S3 permission verification test"

    try:
        # Attempt to write test object
        s3_client.put_object(
            Bucket=s3_bucket,
            Key=test_key,
            Body=test_content,
        )
        print(f"S3 permissions verified successfully for bucket: {s3_bucket}")
        logger.info(f"S3 permissions verified successfully for bucket: {s3_bucket}")

        # Clean up test object
        try:
            s3_client.delete_object(Bucket=s3_bucket, Key=test_key)
        except Exception as e:
            logger.warning(f"Failed to cleanup test object: {e}")

        return True

    except Exception as e:
        print(f"S3 permission check failed: {str(e)}")
        logger.error(f"S3 permission check failed: {str(e)}")
        logger.error(f"Bucket: {s3_bucket}, Key: {test_key}")
        logger.error("Please verify IAM policy allows s3:PutObject on this bucket")
        raise


def run_tests(event, context=None) -> Dict:  # noqa
    setup_logging()

    print("[BlazeTest] Starting test execution handler...")

    pytest_args: List[str] = event["pytest_args"]
    node_ids: List[str] = event["node_ids"]
    report_path: str = event["report_path"]
    region: str = event["region"]
    session_uuid: str = event["session_uuid"]
    timestamp: str = event["start_timestamp"]
    retry: bool = event["retry"]

    s3 = S3Upload(region=region)
    s3_bucket = os.environ.get("S3_BUCKET")

    print(f"[BlazeTest] S3 bucket: {s3_bucket}, Session: {session_uuid}")

    # Verify S3 permissions before running tests
    verify_s3_permissions(s3.client, s3_bucket, session_uuid)

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
