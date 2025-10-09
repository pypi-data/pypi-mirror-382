import logging
from typing import Optional
import sys

import click
from art import text2art

from blazetest import __version__
from blazetest.cli.base import cli
from blazetest.cli.utils import check_license, EXIT_SUCCESS, EXIT_FAILURE
from blazetest.core.infra.base import InfraSetup
from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.project_config.project_config import ProjectConfiguration
from blazetest.core.run_test.runner_facade import TestRunner
from blazetest.core.run_test.result_model import (
    TestSessionResult,
    TestSessionResultManager,
)
from blazetest.core.utils.exceptions import (
    NoTestsToRun,
    ReportNotMerged,
    ConfigurationValidationException,
)
from blazetest.core.utils.logging_config import setup_logging
from blazetest.core.cloud.aws.s3_manager import S3Manager
from blazetest.core.utils.utils import (
    create_build_folder,
    generate_uuid,
    set_environment_variables,
    combine_tags,
    LOGS_ENABLED,
    LOGS_DISABLED,
    SETUP_TOOL_AWS,
    create_artifacts_dir,
)

logger = logging.getLogger(__name__)


@cli.command()
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
    "-at",
    "--aws-session-token",
    help="AWS Session Token for temporary credentials (optional).",
)
@click.option(
    "-ar",
    "--aws-role-arn",
    help="AWS IAM Role ARN to assume (recommended for CI/CD).",
)
@click.option(
    "-ap",
    "--aws-profile",
    help="AWS Profile name from ~/.aws/credentials (recommended for local development).",
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
    "-t",
    "--tags",
    help="Tags specified for the AWS Lambda function. The tags will be attached to created Lambda function instance.",
)
@click.option(
    "-lo",
    "--logs",
    default=LOGS_ENABLED,
    type=click.Choice([LOGS_ENABLED, LOGS_DISABLED]),
    help="Default is enabled. When logs are enabled, they are shown in the console stdout. "
    "When they are set to disabled, the logs are not shown during CLI execution, but saved to blazetest.log, "
    "which will be located in the project's root.",
)
@click.option(
    "-rl",
    "--remote-logs",
    help="If provided, logs are sent to the remote logging system. Default is Loki",
)
@click.option(
    "-dt",
    "--depot-token",
    help="Depot token for the depot.dev. If not provided, it will be taken from the DEPOT_TOKEN environment variable.",
)
@click.option(
    "-dp",
    "--depot-project-id",
    help="Depot project ID for the depot.dev. "
    "If not provided, it will be taken from the DEPOT_PROJECT_ID environment variable.",
)
@click.option(
    "-nt",
    "--namespace-token",
    help="Namespace token for namespace.so. If not provided, it will be taken from the NSC_TOKEN environment variable.",
)
@click.option(
    "-nw",
    "--namespace-workspace",
    help="Namespace workspace for namespace.so. "
    "If not provided, it will be taken from the NSC_WORKSPACE environment variable.",
)
@click.option("-de", "--debug", is_flag=True, help="Enables debugging output.")
def run(
    config_path: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_session_token: str,
    aws_role_arn: str,
    aws_profile: str,
    license_key: str,
    license_file: str,
    tags: str,
    logs: str,
    remote_logs: str,
    depot_token: str,
    depot_project_id: str,
    namespace_token: str,
    namespace_workspace: str,
    debug: bool,
):
    """
    Runs tests using the PyTest library and parallel Lambda functions.
    """
    print(text2art("BlazeTest"))
    print(f"Version: {__version__}\n")
    session_uuid = generate_uuid()

    # Get project configuration from Blazetest TOML
    try:
        config = ProjectConfiguration.from_toml_file(config_path)
    except ConfigurationValidationException as err:
        logger.error(err)
        sys.exit(EXIT_FAILURE)

    if config.general.artifacts_dir != "":
        create_artifacts_dir(config.general.artifacts_dir)

    setup_logging(
        debug=debug,
        stdout_enabled=logs == LOGS_ENABLED,
        loki_api_key=remote_logs,
        session_uuid=session_uuid,
        artifacts_dir=config.general.artifacts_dir,
    )

    logger.info(f"Session UUID: {session_uuid}")

    expiration_date, flaky_enabled = check_license(license_key, license_file, config)
    if expiration_date is None:
        return

    # AWS Credentials Priority: CLI args > config file > env vars
    final_aws_access_key_id = (
        aws_access_key_id or config.cloud.aws.credentials.access_key_id
    )
    final_aws_secret_access_key = (
        aws_secret_access_key or config.cloud.aws.credentials.secret_access_key
    )
    final_aws_session_token = (
        aws_session_token or config.cloud.aws.credentials.session_token
    )
    final_aws_role_arn = aws_role_arn or config.cloud.aws.credentials.role_arn
    final_aws_profile = aws_profile or config.cloud.aws.credentials.profile

    test_runner = TestRunner(
        config=config,
        uuid=session_uuid,
        aws_access_key_id=final_aws_access_key_id,
        aws_secret_access_key=final_aws_secret_access_key,
        aws_session_token=final_aws_session_token,
        role_arn=final_aws_role_arn,
        profile=final_aws_profile,
    )

    try:
        test_runner.collect_tests()
    except NoTestsToRun as e:
        logger.error(e)
        return

    set_environment_variables(
        aws_access_key_id=final_aws_access_key_id,
        aws_secret_access_key=final_aws_secret_access_key,
    )

    all_tags = combine_tags(
        tags=tags, config_tags=config.cloud.aws.tags, session_uuid=session_uuid
    )

    s3_manager = S3Manager(
        aws_config=config.cloud.aws,
        aws_access_key_id=final_aws_access_key_id,
        aws_secret_access_key=final_aws_secret_access_key,
    )
    s3_bucket_name = s3_manager.find_or_create_s3_bucket(tags=all_tags)

    # Deploy and get version-qualified function name for safe concurrent execution
    # Priority: CLI args > config file > env vars (handled in tools.py)
    final_depot_token = depot_token or config.build.depot.token
    final_depot_project_id = depot_project_id or config.build.depot.project_id
    final_namespace_token = namespace_token or config.build.namespace.token
    final_namespace_workspace = namespace_workspace or config.build.namespace.workspace

    qualified_function_name = deploy(
        config=config,
        s3_bucket_name=s3_bucket_name,
        session_uuid=session_uuid,
        tags=all_tags,
        debug=debug,
        remote_logging_api_key=remote_logs,
        depot_token=final_depot_token,
        depot_project_id=final_depot_project_id,
        namespace_token=final_namespace_token,
        namespace_workspace=final_namespace_workspace,
        aws_access_key_id=final_aws_access_key_id,
        aws_secret_access_key=final_aws_secret_access_key,
        aws_session_token=final_aws_session_token,
        aws_role_arn=final_aws_role_arn,
        aws_profile=final_aws_profile,
    )

    test_session_result_manager = TestSessionResultManager(
        config=config,
        s3_manager=s3_manager,
    )

    test_runner.set_tests_result_manager(test_session_result_manager)
    test_runner.set_s3_bucket_name(s3_bucket_name)
    # Set the version-qualified function name directly to avoid lookup and ensure correct version
    test_runner.function_name = qualified_function_name
    logger.info(f"Using Lambda function version: {qualified_function_name}")

    try:
        test_session_result: Optional[TestSessionResult] = test_runner.run_tests(
            flaky_test_retry_enabled=flaky_enabled,
        )
    except ReportNotMerged as err:
        logger.error(err)
        sys.exit(EXIT_FAILURE)

    if test_session_result is not None:
        test_session_result.log_results(failed_test_retry_enabled=flaky_enabled)
        test_session_result.set_tags(tags if tags else None)
        test_session_result.set_uuid(session_uuid)
        test_session_result_manager.append_results_to_json(test_session_result)

        if test_session_result.failed_tests_count > 0 or (
            config.general.flaky.fail_on_flake is True
            and test_session_result.flake_detected
        ):
            sys.exit(EXIT_FAILURE)

    sys.exit(EXIT_SUCCESS)


def deploy(
    config: BlazetestConfig,
    s3_bucket_name: str,
    session_uuid: str,
    tags: dict,
    remote_logging_api_key: str,
    debug: bool,
    depot_token: str,
    depot_project_id: str,
    namespace_token: str,
    namespace_workspace: str,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
    aws_session_token: str = None,
    aws_role_arn: str = None,
    aws_profile: str = None,
):
    """
    Creates the build folder and deploys the necessary AWS resources (ECR, Lambda, and S3 bucket).
    """
    remote_logging_enabled = remote_logging_api_key is not None
    create_build_folder(remote_logging_enabled=remote_logging_enabled)
    infra_setup = InfraSetup(
        session_uuid=session_uuid,
        aws_region=config.cloud.aws.region,
        resource_prefix=config.cloud.aws.resource_prefix,
        ecr_repository_prefix=config.cloud.aws.get_ecr_repository_prefix(
            uuid=session_uuid
        ),
        lambda_function_memory_size=config.cloud.aws.lambda_function_memory_size,
        lambda_function_timeout=config.cloud.aws.lambda_function_timeout,
        s3_bucket_name=s3_bucket_name,
        tags=tags if tags else None,
        loki_api_key=remote_logging_api_key,
        setup_tool=SETUP_TOOL_AWS,
        debug=debug,
        depot_token=depot_token,
        depot_project_id=depot_project_id,
        namespace_token=namespace_token,
        namespace_workspace=namespace_workspace,
        build_backend=config.build.backend,
        enable_cache=config.build.enable_cache,
        browser_type=config.browser.type,
        browser_version=config.browser.get_browser_version(),
        install_browser=config.browser.install,
        install_allure=config.general.reporting.should_generate_allure(),
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        aws_role_arn=aws_role_arn,
        aws_profile=aws_profile,
    )
    # Deploy and get the version-qualified function name for safe concurrent execution
    qualified_function_name = infra_setup.deploy()
    return qualified_function_name
