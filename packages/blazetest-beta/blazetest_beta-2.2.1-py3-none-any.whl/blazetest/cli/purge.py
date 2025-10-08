import logging
import sys
from typing import List

import click
from art import text2art
from blazetest.core.cloud.aws.aws_lambda import AWSLambda
from blazetest.core.cloud.aws.ecr import (
    list_ecr_repositories_to_purge,
    batch_delete_ecr_repositories,
)

from blazetest.core.utils.utils import set_environment_variables

from blazetest.cli.base import cli
from blazetest.cli.utils import check_license, EXIT_FAILURE, EXIT_SUCCESS
from blazetest.core.project_config.project_config import ProjectConfiguration
from blazetest.core.utils.logging_config import setup_logging

logger = logging.getLogger(__name__)


@cli.command()
@click.option(
    "-ri",
    "--runid",
    help="Blazetest session UUID to purge artifacts all from.",
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
@click.option("-de", "--debug", is_flag=True, help="Enables debugging output.")
@click.option(
    "-dr",
    "--dryrun",
    is_flag=True,
    help="Lists all artifacts to delete without actual deleting.",
)
def purge(
    runid: str,
    config_path: str,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    license_key: str,
    license_file: str,
    logs: str,
    debug: bool,
    dryrun: bool,
):
    """
    Purge artifacts from the AWS account
    """
    print(text2art("BlazeTest"))

    setup_logging(
        debug=debug,
        stdout_enabled=logs == "enabled",
    )

    config = ProjectConfiguration.from_toml_file(config_path)
    expiration_date, flaky_enabled = check_license(license_key, license_file, config)
    if expiration_date is None:
        return

    set_environment_variables(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    if runid:
        logger.info(f"Purging artifacts with session UUID: {runid}")

    logger.info(
        f"Purging all artifacts which were created within: {config.general.purge.purge_time_limit} hours"
    )

    if config.general.purge.purge_exclude_tags:
        logger.info(
            f"Purging all artifacts which contain following tags: {config.general.purge.purge_exclude_tags}"
        )

    try:
        purge_artifacts(
            region_name=config.cloud.aws.region,
            run_id=runid,
            purge_time_limit=config.general.purge.purge_time_limit,
            purge_exclude_tags=config.general.purge.purge_exclude_tags,
            dryrun=dryrun,
        )
    except Exception as err:
        logger.error(f"There was an error during purge of artifacts: {err}")
        sys.exit(EXIT_FAILURE)

    # TODO: what to do with sessions that have those artifacts?

    sys.exit(EXIT_SUCCESS)


def purge_artifacts(
    region_name: str,
    run_id: str,
    purge_time_limit: int,
    purge_exclude_tags: List[str],
    dryrun: bool,
):
    """
    Purges function with specified run_id.
    If run_id, purges all the functions that are not older than the specified time limit
    and do not have the specified excluded tags.

    Args:
        region_name:
        run_id:
        purge_time_limit:
        purge_exclude_tags:

    Returns:

    """
    lambda_handler = AWSLambda(
        region=region_name,
    )

    logger.info("Getting lambda functions to delete...")
    lambda_functions_to_delete = lambda_handler.list_functions_to_purge(
        run_id=run_id,
        time_limit=purge_time_limit,
        exclude_tags=purge_exclude_tags,
    )

    logger.info("Getting ECR repositories to delete...")
    repositories_to_delete = list_ecr_repositories_to_purge(
        aws_region=region_name,
        run_id=run_id,
        time_limit=purge_time_limit,
        exclude_tags=purge_exclude_tags,
    )

    if not lambda_functions_to_delete and not repositories_to_delete:
        logger.info("No artifacts to delete.")
        return

    if dryrun:
        logger.info("List of artifacts to delete: ")
    else:
        logger.info("Are you sure you want to delete the following:")

    if repositories_to_delete:
        repositories_list = "\n- ".join(repositories_to_delete)
        logger.info(f"\n\nRepositories:\n- {repositories_list}")

    if lambda_functions_to_delete:
        functions_list = "\n- ".join(lambda_functions_to_delete)
        logger.info(f"\n\nLambda functions:\n- {functions_list}")

    if dryrun:
        return

    answer = input("\n\nType 'yes' to confirm: ")

    if answer != "yes":
        logger.info("Aborting repository deletion.")
        return

    if lambda_functions_to_delete:
        lambda_handler.batch_delete(function_names=lambda_functions_to_delete)
        logger.info("Lambda functions deleted successfully.")

    if repositories_to_delete:
        batch_delete_ecr_repositories(
            aws_region=region_name,
            repositories=repositories_to_delete,
        )
        logger.info("ECR repositories deleted successfully.")
