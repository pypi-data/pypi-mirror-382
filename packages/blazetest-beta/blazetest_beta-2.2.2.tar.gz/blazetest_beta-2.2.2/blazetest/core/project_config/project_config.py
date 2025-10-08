import logging
from typing import Dict

import toml
from dacite import from_dict, MissingValueError, WrongTypeError

from blazetest.core.config import PROJECT_CONFIG_TOML
from blazetest.core.project_config.model import BlazetestConfig
from blazetest.core.utils.exceptions import (
    ConfigurationFileNotFound,
    ConfigurationMissingValue,
    ConfigurationFieldWrongType,
)

logger = logging.getLogger(__name__)


class ProjectConfiguration:
    @classmethod
    def from_toml_file(cls, toml_file_path: str = None) -> BlazetestConfig:
        """Load configuration data from a TOML file and create a `BlazetestConfig` object.

        Args:
            toml_file_path: Path to the TOML file. If not specified, the default
                location specified by `BLAZETEST_CONFIG` will be used.

        Returns:
            A `BlazetestConfig` object created from the data in the TOML file.

        Raises:
            ConfigurationFileNotFound: If the specified TOML file does not exist.
            ConfigurationMissingValue: If required values are missing from the TOML file.
            ConfigurationFieldWrongType: If a value in the TOML file has the wrong type.
        """
        if not toml_file_path:
            logger.info(
                f"Config file location not specified. Using default location: {PROJECT_CONFIG_TOML}",
            )
            toml_file_path = PROJECT_CONFIG_TOML

        try:
            with open(toml_file_path) as f:
                data = toml.loads(f.read())
                return cls.get_dataclass_from_dict(data=data)
        except FileNotFoundError as err:
            raise ConfigurationFileNotFound(f"Configuration file does not exist: {err}")

    @classmethod
    def from_toml_string(cls, toml_string: str) -> BlazetestConfig:
        """Load configuration data from a TOML string and create a `LambdaConfig` object.

        Args:
            toml_string: TOML string containing configuration data.

        Returns:
            A `LambdaConfig` object created from the data in the TOML string.

        Raises:
            ConfigurationMissingValue: If required values are missing from the TOML string.
            ConfigurationFieldWrongType: If a value in the TOML string has the wrong type.
        """
        try:
            data = toml.loads(toml_string)
            return cls.get_dataclass_from_dict(data=data)
        except FileNotFoundError as err:
            raise ConfigurationFileNotFound(f"Configuration file does not exist: {err}")

    @staticmethod
    def get_dataclass_from_dict(data: Dict):
        """Create a `LambdaConfig` object from a dictionary.

        Args:
            data: Dictionary containing configuration data.

        Returns:
            A `LambdaConfig` object created from the data in the dictionary.

        Raises:
            ConfigurationMissingValue: If required values are missing from the dictionary.
            ConfigurationFieldWrongType: If a value in the dictionary has the wrong type.
        """
        try:
            return from_dict(data_class=BlazetestConfig, data=data)
        except MissingValueError as err:
            raise ConfigurationMissingValue(f"Blazetest configuration error: {err}")
        except WrongTypeError as err:
            raise ConfigurationFieldWrongType(f"Blazetest configuration error: {err}")
