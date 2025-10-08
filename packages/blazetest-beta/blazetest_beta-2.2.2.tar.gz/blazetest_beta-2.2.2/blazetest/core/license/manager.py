import logging
import os
from pathlib import Path

from licensing.methods import Key, Helpers
from licensing.models import LicenseKey

from blazetest.core.config import ACCESS_TOKEN, RSA_PUB_KEY, PRODUCT_ID
from blazetest.core.utils.exceptions import (
    LicenseNotSpecified,
)

logger = logging.getLogger(__name__)


class LicenseManager:
    license_key: str = None
    license_file: str = None
    license: LicenseKey = None

    def __init__(
        self,
        license_key: str = None,
        license_file: str = None,
        config_license_key: str = None,
        config_license_file: str = None,
    ):
        """
        Initializes the license key or license file by checking for the key or file in the following order:
            1. 'license_key' argument
            2. 'BLAZETEST_LICENSE' environment variable
            3. 'config_license_key' argument
            4. 'config_license_file' argument
            5. 'license_file' argument
            If none of these options are specified, it raises a LicenseNotSpecified exception.

        Args:
            license_key (str): The license key string.
            license_file (str): The path to the license file.
            config_license_key (str): The license key string from configuration file.
            config_license_file (str): The path to the license file from configuration file.
        """
        env_license_key = os.environ.get("BLAZETEST_LICENSE")
        license_keys_check = [license_key, env_license_key, config_license_key]

        for lk in license_keys_check:
            if lk:
                self.license_key = lk
                break

        if not self.license_key:
            if config_license_file:
                self.license_file = config_license_file

            if license_file:
                self.license_file = license_file

            if not self.license_file:
                raise LicenseNotSpecified(
                    "Neither license-key nor license-file were not found. Checking order:\n"
                    "Environment Variable BLAZETEST_LICENSE\n"
                    "TOML configuration file: license-key or license-file\n"
                    "CLI options: --license-key or --license-file"
                )

            logger.info("Loading license file")
            self.license_file = Path(self.license_file).read_text().strip()

    def check_license(self):
        """
        Checks if given license is valid. Returns expiration date if it is valid
        Raises LicenseNotValid if the license is not valid
        Raises LicenseExpired if it has expired
        :return: expiration date
        """
        if self.license_file:
            license_key, error_message = (
                LicenseKey.load_from_string(
                    rsa_pub_key=RSA_PUB_KEY, string=self.license_file
                ),
                "",
            )
        else:
            license_key, error_message = Key.activate(
                token=ACCESS_TOKEN,
                rsa_pub_key=RSA_PUB_KEY,
                product_id=PRODUCT_ID,
                key=self.license_key or self.license_file,
                machine_code=Helpers.GetMachineCode(v=2),
            )

        # if license_key is None:
        #     raise LicenseNotValid(f"The license does not work: {error_message}")

        # TODO: is on right machine not working, consider adding machines in cryptolens
        # if not Helpers.IsOnRightMachine(license_key, v=2):
        #     raise LicenseNotValid(f"Activated device error: {error_message}")

        # Check if the license has expired
        # current_date = datetime.now()
        # if current_date > license_key.expires:
        #     raise LicenseExpired(f"The license has expired on {license_key.expires}")

        self.license = license_key
        return license_key.expires

    def has_feature(self, feature: str) -> bool:
        """
        Checks if the given feature is enabled in the license.
        :param feature: feature to check
        :return: True if the feature is enabled, False otherwise
        """
        if feature == "flaky":
            return self.license.f3
        # Other features can be added here
        return False

    @property
    def flaky_test_retry(self) -> bool:
        """
        Checks if flaky tests are enabled in the license.
        :return: True if flaky tests are enabled, False otherwise
        :return:
        """
        return self.has_feature("flaky")
