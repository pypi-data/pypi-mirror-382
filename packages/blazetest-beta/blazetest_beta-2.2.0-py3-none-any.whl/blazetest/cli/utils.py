import logging

from blazetest.core.license.manager import LicenseManager
from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.utils.exceptions import (
    LicenseNotValid,
    LicenseExpired,
    LicenseNotSpecified,
)

logger = logging.getLogger(__name__)


def check_license(license_key, license_file, config: BlazetestConfig) -> tuple:
    try:
        licence_manager = LicenseManager(
            license_key=license_key,
            license_file=license_file,
            config_license_key=config.general.license.license_key,
            config_license_file=config.general.license.license_file,
        )
        expiration_date = licence_manager.check_license()
    except (LicenseNotSpecified, LicenseExpired, LicenseNotValid) as e:
        logger.error(e)
        return None, None

    logger.info(f"License expiration date: {expiration_date}")

    flaky_enabled = False
    if licence_manager.flaky_test_retry:
        logger.info("Flaky test retry feature is on")
        if config.general.flaky.failure_retry_attempts > 0:
            flaky_enabled = True
    else:
        if config.general.flaky.failure_retry_attempts > 0:
            logger.warning(
                "Flaky test retry feature is not available within this license"
            )

    return expiration_date, flaky_enabled


EXIT_SUCCESS = 1
EXIT_FAILURE = 0
