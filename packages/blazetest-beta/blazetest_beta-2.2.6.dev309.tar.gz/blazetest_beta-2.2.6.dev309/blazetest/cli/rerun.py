import logging
import sys
from typing import Optional

import click
from art import text2art

from blazetest.cli.base import cli
from blazetest.cli.utils import check_license, EXIT_FAILURE, EXIT_SUCCESS
from blazetest.core.project_config.project_config import ProjectConfiguration
from blazetest.core.run_test.runner_facade import TestRunner
from blazetest.core.run_test.result_model import (
    TestSessionResult,
    TestSessionResultManager,
)
from blazetest.core.utils.exceptions import (
    NoTestsToRun,
    ConfigurationValidationException,
)
from blazetest.core.utils.logging_config import setup_logging
from blazetest.core.cloud.aws.s3_manager import S3Manager
from blazetest.core.utils.utils import (
    generate_uuid,
    set_environment_variables,
    FILTER_ALL,
    FILTER_FAILED,
    FILTER_FLAKY,
    create_artifacts_dir,
)

logger = logging.getLogger(__name__)


@cli.command()
@click.option(
    "-ri",
    "--runid",
    help="Blazetest session UUID to rerun.",
    required=True,
)
@click.option(
    "-config",
    "--config-path",
    help="Configuration path to the TOML file for the CLI. "
    "If not specified -> searches the project's root folder for the file blazetest.toml. "
    "If not found -> raises an error.",
)
@click.option(
    "-ak",
    "--aws-access-key-id",
    help="AWS Access Key ID which is used to deploy artifacts.",
)
@click.option(
    "-as",
    "--aws-secret-access-key",
    help="AWS Secret Access Key which is used to deploy artifacts.",
)
@click.option(
    "-k",
    "--license-key",
    help="License key for Blazetest CLI. Either --license-key or --license-file should be specified."
    "License key has a higher priority if both are specified.",
)
@click.option(
    "-l",
    "--license-file",
    help="License file for Blazetest CLI. Either --license-key or --license-file should be specified."
    "License file has a lower priority if both are specified.",
)
@click.option(
    "-lo",
    "--logs",
    default="enabled",
    type=click.Choice(["enabled", "disabled"]),
    help="Default is enabled. When logs are enabled, they are shown in the console stdout. "
    "When they are set to disabled, the logs are not shown during CLI execution, but saved to blazetest.log, "
    "which will be located in the project's root.",
)
@click.option(
    "-lk",
    "--loki",
    help="Loki API Key. If provided, logs are sent to the Loki",
)
@click.option(
    "-s",
    "--status",
    default=FILTER_ALL,
    type=click.Choice([FILTER_ALL, FILTER_FAILED, FILTER_FLAKY]),
    help="Filter which kind of tests to rerun (all, failed)",
)
@click.option("-de", "--debug", is_flag=True, help="Enables debugging output.")
def rerun(
    runid: str,
    config_path: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    license_key: str,
    license_file: str,
    logs: str,
    loki: str,
    status: str,
    debug: bool,
):
    """
    Reruns the session specified with --uuid option.
    """
    print(text2art("BlazeTest"))
    rerun_uuid = generate_uuid()

    try:
        config = ProjectConfiguration.from_toml_file(config_path)
    except ConfigurationValidationException as err:
        logger.error(err)
        sys.exit(EXIT_FAILURE)

    if config.general.artifacts_dir != "":
        create_artifacts_dir(config.general.artifacts_dir)

    setup_logging(
        debug=debug,
        stdout_enabled=logs == "enabled",
        loki_api_key=loki,
        session_uuid=rerun_uuid,
        artifacts_dir=config.general.artifacts_dir,
    )

    expiration_date, flaky_enabled = check_license(license_key, license_file, config)
    if expiration_date is None:
        return

    logger.info(f"Rerunning session with UUID: {runid}")
    logger.info(f"Rerun UUID: {rerun_uuid}")

    s3_manager = S3Manager(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_config=config.cloud.aws,
    )

    s3_bucket_name = s3_manager.find_s3_bucket()
    if s3_bucket_name is None:
        logger.error("S3 Bucket with previous sessions not found")
        return

    test_session_result_manager = TestSessionResultManager(
        config=config,
        s3_manager=s3_manager,
    )

    test_session: TestSessionResult = (
        test_session_result_manager.get_test_session_by_uuid(uuid=runid)
    )
    if test_session is None:
        logger.error(f"Session with UUID {runid} not found")
        return

    # TODO: this results in inability to be able to be forward compatible with new version of the configuration made
    # by user. Can we use the new config?
    config = ProjectConfiguration.get_dataclass_from_dict(test_session.config)

    test_runner = TestRunner(
        config=config,
        uuid=runid,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    try:
        test_runner.collect_tests(
            test_filter=status,
            test_session=test_session,
        )
    except NoTestsToRun as e:
        logger.error(e)
        return

    set_environment_variables(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    test_runner.set_s3_bucket_name(s3_bucket_name)
    test_runner.set_tests_result_manager(test_session_result_manager)

    test_session_result: Optional[TestSessionResult] = test_runner.run_tests(
        flaky_test_retry_enabled=flaky_enabled,
        rerun=True,
    )

    if test_session_result is not None:
        test_session_result.log_results(failed_test_retry_enabled=flaky_enabled)
        test_session_result.set_uuid(runid)
        test_session_result.set_rerun_uuid(rerun_uuid)
        test_session_result_manager.append_results_to_json(test_session_result)

        if test_session_result.failed_tests_count > 0:
            sys.exit(EXIT_FAILURE)

        if (
            config.general.flaky.fail_on_flake is True
            and test_session_result.flake_detected
        ):
            sys.exit(EXIT_FAILURE)

        sys.exit(EXIT_SUCCESS)

    sys.exit(EXIT_FAILURE)
