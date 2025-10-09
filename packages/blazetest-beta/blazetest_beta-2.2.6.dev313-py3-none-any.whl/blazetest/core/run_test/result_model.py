import json
import logging
import time

from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, List, Tuple, Dict, Union

from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.utils.logging_config import ColoredOutput
from blazetest.core.cloud.aws.s3_manager import S3Manager
from blazetest.core.utils.utils import parse_tags

logger = logging.getLogger(__name__)


@dataclass
class JUnitXMLReport:
    test_node_id: str
    report_path: str
    test_result: str


@dataclass
class InvocationResult:
    passed_tests_count: int
    failed_tests_count: int
    error_tests_count: int
    skipped_tests_count: int

    failed_tests_node_ids: List[str]
    pytest_duration: float

    junit_xml_reports_paths: List[JUnitXMLReport]

    @classmethod
    def parse(
        cls, results: List[Tuple[str, Dict]], start_time: float
    ) -> "InvocationResult":
        tests_passed = 0
        tests_skipped = 0
        tests_error = 0

        failed_tests = []
        junitxml_reports_paths = []

        for node_id, invocation_result in results:
            if invocation_result["test_result"] == "passed":
                tests_passed += 1
            elif invocation_result["test_result"] == "skipped":
                tests_skipped += 1
            else:
                if invocation_result["test_result"] == "error":
                    tests_error += 1
                failed_tests.append(node_id)

            junitxml_reports_paths.append(
                JUnitXMLReport(
                    test_node_id=node_id,
                    report_path=invocation_result["report_path"],
                    test_result=invocation_result["test_result"],
                )
            )

        return cls(
            passed_tests_count=tests_passed,
            failed_tests_count=len(failed_tests),
            failed_tests_node_ids=failed_tests,
            error_tests_count=tests_error,
            skipped_tests_count=tests_skipped,
            pytest_duration=time.time() - start_time,
            junit_xml_reports_paths=junitxml_reports_paths,
        )


@dataclass
class ReportMergeResult:
    final_report_path: str
    flake_report_path: str

    passed: int
    failed: int
    flaky: int

    passed_ids: List[str]
    failed_ids: List[str]
    flaky_ids: List[str]


@dataclass
class TestSessionResult:
    uuid: str

    lambda_function_name: str
    s3_bucket: str

    tests_count: int
    tests_passed: int

    failed_tests_count: int
    flaky_tests_count: int

    pytest_duration: float

    failed_tests_ids: List[str] = field(default_factory=lambda: [])
    flaky_tests_ids: List[str] = field(default_factory=lambda: [])

    start_timestamp: str = None
    end_timestamp: str = None

    tags: str = None

    junit_report_path: str = None
    flake_report_path: str = None

    config: Union[BlazetestConfig, dict] = None

    rerun_uuid: str = None
    flake_detected: bool = False

    def set_uuid(self, uuid: str):
        self.uuid = uuid

    def set_rerun_uuid(self, rerun_uuid: str):
        self.rerun_uuid = rerun_uuid

    def set_tags(self, tags: str):
        self.tags = tags

    def log_results(self, failed_test_retry_enabled: bool = False):
        minutes = int(self.pytest_duration // 60)
        seconds = int(self.pytest_duration % 60)
        duration_str = (
            f"{minutes} min {seconds} seconds" if minutes > 0 else f"{seconds} seconds"
        )

        logger.info(f"Tests duration: {duration_str}")
        logger.info(
            f"Failed tests: {self.tests_count - self.tests_passed} out of {self.tests_count}"
        )

        if len(self.failed_tests_ids) > 0:
            print("{:-^50}".format(f"{self.failed_tests_count} FAILED TESTS"))
            for failed_test_id in self.failed_tests_ids:
                print(
                    f"- {ColoredOutput.RED.value}[{failed_test_id}]{ColoredOutput.RESET.value}"
                )

        # If the configuration was set to retry the tests that have failed and license has this feature
        # failed_test_retry is by default 0
        if (
            self.flaky_tests_count > 0
            and failed_test_retry_enabled
            and self.config.general.flaky.remove_flakes is False
        ):
            print("{:-^50}".format(f"{self.flaky_tests_count} FLAKY TESTS"))
            for flaky_test_id in self.flaky_tests_ids:
                print(
                    f"- {ColoredOutput.YELLOW.value}[{flaky_test_id}]{ColoredOutput.RESET.value}"
                )

    def get_tabular_data(self) -> list:
        return [
            self.uuid,
            self.rerun_uuid if self.rerun_uuid else "-",
            (
                self.config["cloud"]["aws"]["resource_prefix"]
                if "cloud" in self.config
                else "-"
            ),
            self.__get_normalized_timestamp(),
            f"{self.tests_passed}/{self.tests_count}",
            self.tags if self.tags else "-",
        ]

    def __get_normalized_timestamp(self) -> str:
        return datetime.strptime(self.start_timestamp, "%Y-%m-%d_%H-%M-%S").strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class TestSessionResultManager:
    BLAZETEST_REPORT_FILEPATH = "reports/blazetest-report.json"

    def __init__(
        self,
        s3_manager: S3Manager = None,
        config: BlazetestConfig = None,
    ):
        self.s3_manager = s3_manager
        self.config = config

    def load(self) -> List[TestSessionResult]:
        """
        Load the results from an S3 bucket file.

        Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key of the file in the S3 bucket.
        """
        results = self.s3_manager.get_json_object(self.BLAZETEST_REPORT_FILEPATH)

        if results is None:
            logger.warning("Could not find the BlazeTest report file in S3 bucket.")
            return []

        if len(results) == 0:
            logger.debug("BlazeTest report is empty")
            return []

        session_results = []
        for result in results:
            session_results.append(TestSessionResult(**result))

        session_results = list(
            sorted(session_results, key=lambda x: x.start_timestamp, reverse=True)
        )
        return session_results

    def append_results_to_json(self, test_session_result: TestSessionResult) -> None:
        """
        Appends the results to a json file in the specified S3 bucket.
        The file is created in the bucket if it does not exist.

        Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key of the file in the S3 bucket.
        """
        results = self.s3_manager.get_json_object(self.BLAZETEST_REPORT_FILEPATH)

        if results is None:
            # If the report does not exist, we create a new report file
            results = []

        result_dict = asdict(test_session_result)
        results.append(result_dict)

        updated_file_content = json.dumps(results, indent=4)

        uploaded = self.s3_manager.put_object(
            key=self.BLAZETEST_REPORT_FILEPATH,
            body=updated_file_content,
        )

        if uploaded:
            logger.info("Test session results have been appended to file in S3 bucket.")
        else:
            logger.error(
                "Internal error. Could not append test session results to file in S3 bucket."
            )

    def get_latest_test_session_result(self) -> Optional["TestSessionResult"]:
        """
        Gets latest test session result from the json file ("blazetest-report.json") in the project root.
        Returns the dataclass object of the latest test session result.
        """
        results = self.load()
        if not results:
            return None
        results = [result for result in results if result.rerun_uuid is None]
        latest_result = max(results, key=lambda x: x.start_timestamp)
        return latest_result

    def get_test_session_by_uuid(self, uuid: str) -> Optional["TestSessionResult"]:
        """
        Gets test session result from the json file ("blazetest-report.json") in the project root.
        Returns the dataclass object of the test session result.
        """
        results = self.load()

        if not results:
            return None

        results = [
            result
            for result in results
            if result.uuid == uuid and result.rerun_uuid is None
        ]

        if not results:
            return None

        return results[0]

    def get_test_session_results(
        self,
        tags: str,
        include: str = "all",
        uuid: str = None,
    ) -> List["TestSessionResult"]:
        """
        Gets all test session results from the json file ("blazetest-report.json") in the project root.
        Returns the list of dataclass objects of the test session results.
        """
        results = self.load()
        if not results:
            return []

        if include == "runs":
            results = [result for result in results if result.rerun_uuid is None]
        elif include == "reruns":
            results = [result for result in results if result.rerun_uuid is not None]

        if tags:
            results = self.__filter_by_tag(results, tags=tags)

        if uuid:
            results = [result for result in results if result.uuid == uuid]

        return results

    @classmethod
    def __filter_by_tag(
        cls, results: List["TestSessionResult"], tags: str
    ) -> List["TestSessionResult"]:
        """
        Tags are given in the format of tag1=value1,tag2=value2
        If any matches found for the tag, it is added to the list of results.
        """
        requested_tag_dict = parse_tags(tags)

        filtered_results = []
        for result in results:
            if result.tags is None:
                continue
            for key, value in requested_tag_dict.items():
                tag_dict = parse_tags(result.tags)
                if key in tag_dict and tag_dict[key] == value:
                    filtered_results.append(result)

        return filtered_results
