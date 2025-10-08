import logging
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from xml.dom.minidom import parseString

import junitparser
from junitparser import JUnitXml, TestCase, Properties, Property
from xml.etree import ElementTree
from tqdm import tqdm

from blazetest.core.config import CWD
from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.run_test.result_model import JUnitXMLReport, ReportMergeResult
from blazetest.core.utils.logging_config import ColoredOutput
from blazetest.core.utils.exceptions import ReportNotAvailable, ReportNotUploaded
from blazetest.core.utils.allure_utils import generate_allure_report
from blazetest.core.utils.html_report import generate_html_report

logger = logging.getLogger(__name__)


class ReportMerger:
    """
    Merges reports from S3 Bucket into one file and saves back to the bucket.
    """

    FILE_ENCODING = "utf-8"

    flake_detected: bool = False

    FINAL_REPORT_FILEPATH = (
        "{timestamp}/target/merged/test-session-{resource_prefix}.xml"
    )
    FLAKE_REPORT_FILEPATH = (
        "{timestamp}/target/flake/test-session-{resource_prefix}.xml"
    )

    def __init__(
        self,
        resource_prefix: str,
        region: str,
        s3_bucket_name: str = None,
        config: BlazetestConfig = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        role_arn: str = None,
        profile: str = None,
    ):
        # Configure AWS Session Manager
        from blazetest.core.cloud.aws.session import AWSSessionManager
        from botocore.config import Config

        session_mgr = AWSSessionManager()
        session_mgr.configure(
            region=region,
            access_key_id=aws_access_key_id,
            secret_access_key=aws_secret_access_key,
            session_token=aws_session_token,
            role_arn=role_arn,
            profile=profile,
        )

        # Get S3 client with high concurrency configuration
        boto_config = Config(
            max_pool_connections=50,  # Support up to 50 concurrent connections
            retries={
                "max_attempts": 3,
                "mode": "adaptive",
            },  # Adaptive retry for transient errors
        )

        self.s3_client = session_mgr.get_client("s3", config=boto_config)
        self.s3_bucket_name = s3_bucket_name
        self.resource_prefix = resource_prefix
        self.config = config

    def set_s3_bucket_name(self, s3_bucket_name: str) -> None:
        self.s3_bucket_name = s3_bucket_name

    def merge_reports(
        self, reports: List[JUnitXMLReport], timestamp: str
    ) -> ReportMergeResult:
        print(
            f"\n* Downloading {len(reports)} test reports "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )
        tests_results = self.get_test_results_by_node_id(reports)
        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")

        print(
            f"* Merging test reports into single JUnitXML test report "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )
        merge_result = self.get_final_reports(tests_results)
        print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")

        final_report_filepath = self.FINAL_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )
        flake_report_filepath = self.FLAKE_REPORT_FILEPATH.format(
            timestamp=timestamp, resource_prefix=self.resource_prefix
        )

        reports = [
            (merge_result["final_report"], final_report_filepath),
            (merge_result["flake_report"], flake_report_filepath),
        ]

        artifacts_dir = CWD
        if self.config.general.artifacts_dir:
            artifacts_dir = os.path.join(CWD, self.config.general.artifacts_dir)

        # Generate JUnit XML reports if enabled
        if self.config.general.reporting.should_generate_xml():
            print(
                f"* Uploading merged JUnitXML test report to S3 bucket "
                f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
                end="",
            )
            for report, report_path in reports:
                self.__upload_report(
                    body=self.formatted_xml_string(report),
                    path=report_path,
                )

                # Save JUnit XML locally
                with open(
                    os.path.join(artifacts_dir, report_path.replace("/", "-")), "w"
                ) as f:
                    f.write(self.formatted_xml_string(report))

            print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}\n")
        else:
            logger.info("JUnit XML report generation disabled by configuration")

        # Generate simple HTML report if enabled
        if self.config.general.reporting.should_generate_html():
            print(
                f"* Generating HTML test report "
                f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
                end="",
            )
            for report, report_path in reports:
                # Generate HTML from JUnit XML
                html_content = generate_html_report(
                    junit_xml=report, title=f"BlazeTest Report - {self.resource_prefix}"
                )

                # Save HTML locally
                html_filename = report_path.replace("/", "-").replace(".xml", ".html")
                html_path = os.path.join(artifacts_dir, html_filename)
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

                logger.info(f"HTML report saved: {html_path}")

            print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")
            print(
                f"📊 HTML Report: {artifacts_dir}/{final_report_filepath.replace('/', '-').replace('.xml', '.html')}\n"
            )
        else:
            logger.info("HTML report generation disabled by configuration")

        # Generate Allure report if enabled
        if self.config.general.reporting.should_generate_allure():
            self.__download_and_generate_allure_report(timestamp, artifacts_dir)
        else:
            logger.info("Allure report generation disabled by configuration")

        return ReportMergeResult(
            final_report_path=final_report_filepath,
            flake_report_path=flake_report_filepath,
            passed=merge_result["passed"],
            flaky=merge_result["flaky"],
            failed=merge_result["failed"],
            passed_ids=merge_result["passed_ids"],
            flaky_ids=merge_result["flaky_ids"],
            failed_ids=merge_result["failed_ids"],
        )

    def get_test_results_by_node_id(
        self, reports: List[JUnitXMLReport]
    ) -> Dict[str, dict]:
        """
        Downloads and processes test reports in parallel for faster execution.

        For 600 tests:
        - Sequential: ~60 seconds
        - Parallel (50 workers): ~5-10 seconds
        """
        tests_results = defaultdict(lambda: defaultdict(list))

        # Download reports in parallel using ThreadPoolExecutor
        max_workers = min(50, len(reports))  # Up to 50 concurrent S3 downloads

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_report = {
                executor.submit(self.__download_and_parse_report, report): report
                for report in reports
            }

            # Process completed downloads with progress bar
            with tqdm(
                total=len(reports),
                desc="Downloading reports",
                unit="report",
                leave=False,
            ) as pbar:
                for future in as_completed(future_to_report):
                    report = future_to_report[future]
                    try:
                        test_case, result_type = future.result()
                        tests_results[report.test_node_id][result_type].append(
                            test_case
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to process report for {report.test_node_id}: {str(e)}"
                        )
                    finally:
                        pbar.update(1)

        return tests_results

    def __download_and_parse_report(
        self, report: JUnitXMLReport
    ) -> Tuple[TestCase, str]:
        """
        Downloads a single report from S3 and extracts the test case.
        Returns (TestCase, result_type) tuple for parallel processing.
        """
        report_data = self.__download_report(report.report_path)
        junit_report = junitparser.JUnitXml.fromstring(report_data)

        test_case = self.__get_test_case(junit_report, report.test_node_id)

        # Determine result type
        if report.test_result == "passed":
            result_type = "passed"
        elif report.test_result == "skipped":
            result_type = "skipped"
        else:
            result_type = "failed"

        return test_case, result_type

    @staticmethod
    def __get_test_case(junit_report: JUnitXml, node_id: str) -> TestCase:
        """
        Extracts a specific test case from a JUnit XML report by node ID.
        """
        for test_suites in junit_report:
            for test_case in test_suites:
                if test_case.classname and test_case.name:
                    case_node_id = f"{test_case.classname}.{test_case.name}"
                    normalized_node_id = (
                        node_id.replace(".py", "").replace("/", ".").replace("::", ".")
                    )
                    if case_node_id == normalized_node_id:
                        return test_case
        raise ValueError(f"Test case with node_id: {node_id} not found")

    @staticmethod
    def formatted_xml_string(junit_xml: JUnitXml) -> str:
        xml_str = junit_xml.tostring()
        root = ElementTree.fromstring(xml_str)
        rough_string = ElementTree.tostring(root, encoding="utf-8")
        re_parsed = parseString(rough_string)
        return re_parsed.toprettyxml(indent="  ")

    def get_final_reports(self, tests_results: Dict[str, dict]) -> Dict:
        final_report = junitparser.JUnitXml()
        flake_report = junitparser.JUnitXml()

        final_testsuite = junitparser.TestSuite()
        flake_testsuite = junitparser.TestSuite()

        passed, flaky, failed, skipped = 0, 0, 0, 0
        passed_ids, flaky_ids, failed_ids, skipped_ids = [], [], [], []

        for node_id in tests_results:
            test_result = tests_results[node_id]

            if len(test_result["failed"]) == 0 and len(test_result["skipped"]) == 0:
                final_testsuite.add_testcase(test_result["passed"][0])

                passed += 1
                passed_ids.append(node_id)
                continue

            elif len(test_result["passed"]) > 0:
                flake_test_case = self.get_test_case_with_flake_property(
                    test_result=test_result
                )
                flake_testsuite.add_testcase(flake_test_case)

                if self.config.general.flaky.remove_flakes is False:
                    final_testsuite.add_testcase(flake_test_case)
                    flaky += 1

                    flaky_ids.append(node_id)
                    failed_ids.append(node_id)
                else:
                    failed += 1
                    failed_ids.append(node_id)

                self.flake_detected = True

            elif len(test_result["skipped"]) > 0:
                skipped += 1
                skipped_ids.append(node_id)

            else:
                final_testsuite.add_testcase(test_result["failed"][0])

                failed += 1
                failed_ids.append(node_id)

        final_report.add_testsuite(final_testsuite)
        flake_report.add_testsuite(flake_testsuite)

        return {
            "final_report": final_report,
            "flake_report": flake_report,
            "passed": passed,
            "passed_ids": passed_ids,
            "flaky": flaky,
            "flaky_ids": flaky_ids,
            "failed": failed,
            "failed_ids": failed_ids,
            "skipped": skipped,
            "skipped_ids": skipped_ids,
        }

    @staticmethod
    def get_test_case_with_flake_property(test_result: dict) -> TestCase:
        test_case: TestCase = test_result["passed"][0]
        tests_count = len(test_result["passed"]) + len(test_result["failed"])

        is_flake = Property("flake", "true")
        flake_rate = Property(
            "flake_rate", f"{len(test_result['passed'])}/{tests_count}"
        )

        properties = Properties()
        properties.add_property(is_flake)
        properties.add_property(flake_rate)

        test_case.append(properties)
        return test_case

    def __download_report(self, report_path: str) -> str:
        try:
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket_name, Key=report_path
            )
            report_data = response["Body"].read().decode(self.FILE_ENCODING)
            return report_data
        except Exception as e:
            raise ReportNotAvailable(
                f"Error downloading report {report_path}: {str(e)}"
            )

    def __upload_report(self, body: str, path: str) -> None:
        try:
            self.s3_client.put_object(Body=body, Bucket=self.s3_bucket_name, Key=path)
        except Exception as e:
            raise ReportNotUploaded(f"Error uploading report {path} to S3: {str(e)}")

    def __download_and_generate_allure_report(
        self, timestamp: str, artifacts_dir: str
    ) -> None:
        """Download Allure results from S3 and generate Allure HTML report."""
        print(
            f"* Downloading Allure results and generating report "
            f"{ColoredOutput.GREEN.value}...{ColoredOutput.RESET.value} ",
            end="",
        )

        try:
            # Create temporary directory for Allure results
            allure_results_dir = os.path.join(artifacts_dir, "allure-results")
            allure_report_dir = os.path.join(artifacts_dir, "allure-report")

            os.makedirs(allure_results_dir, exist_ok=True)

            # List all Allure result files from S3
            prefix = f"{timestamp}/target/allure-results/"
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket_name, Prefix=prefix
                )

                if "Contents" not in response:
                    logger.warning("No Allure results found in S3")
                    print(
                        f"{ColoredOutput.YELLOW.value}No Allure results found{ColoredOutput.RESET.value}"
                    )
                    return

                # Download all Allure result files in parallel
                allure_files = [obj["Key"] for obj in response["Contents"]]
                logger.info(f"Found {len(allure_files)} Allure result files in S3")

                def download_allure_file(s3_key: str) -> None:
                    filename = os.path.basename(s3_key)
                    local_path = os.path.join(allure_results_dir, filename)
                    response = self.s3_client.get_object(
                        Bucket=self.s3_bucket_name, Key=s3_key
                    )
                    with open(local_path, "wb") as f:
                        f.write(response["Body"].read())

                # Download files in parallel
                with ThreadPoolExecutor(max_workers=50) as executor:
                    futures = [
                        executor.submit(download_allure_file, s3_key)
                        for s3_key in allure_files
                    ]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"Failed to download Allure file: {str(e)}")

                logger.info(f"Downloaded {len(allure_files)} Allure result files")

                # Generate Allure HTML report
                success = generate_allure_report(
                    allure_results_dir=allure_results_dir,
                    allure_report_dir=allure_report_dir,
                    clean=True,
                )

                if success:
                    print(f"{ColoredOutput.GREEN.value}Done{ColoredOutput.RESET.value}")
                    logger.info(
                        f"Allure report generated: {allure_report_dir}/index.html"
                    )
                    print(f"\n🎯 Allure Report: {allure_report_dir}/index.html\n")
                else:
                    print(
                        f"{ColoredOutput.YELLOW.value}Failed to generate Allure report{ColoredOutput.RESET.value}"
                    )
                    logger.warning(
                        "Allure report generation failed. Make sure Allure CLI is installed."
                    )
                    logger.info("Install Allure: npm install -g allure-commandline")

            except Exception as e:
                logger.error(f"Error listing Allure results from S3: {str(e)}")
                print(f"{ColoredOutput.RED.value}Error{ColoredOutput.RESET.value}")

        except Exception as e:
            logger.error(f"Error downloading Allure results: {str(e)}")
            print(f"{ColoredOutput.RED.value}Error{ColoredOutput.RESET.value}")
