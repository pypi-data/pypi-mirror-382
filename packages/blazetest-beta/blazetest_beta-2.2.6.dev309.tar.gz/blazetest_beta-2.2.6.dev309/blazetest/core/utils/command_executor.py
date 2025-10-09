import logging
import subprocess
import sys
from typing import List, Dict

from blazetest.core.utils.exceptions import CommandExecutionException

logger = logging.getLogger(__name__)


class CommandExecutor:
    def __init__(self, executable: str, command: str, arguments: Dict):
        """
        :param executable:
            Executable service or module, for example: sam
        :param command:
            Command for the executable, for example: sam build
        :param arguments:
            Arguments needed to be added to the command
        """
        self.executable = executable
        self.command = command
        self.arguments: List = self.__join_arguments(arguments=arguments)

    def execute_command(self, allowed_return_codes=None) -> int:
        if allowed_return_codes is None:
            allowed_return_codes = [0]

        logger.debug(
            f"Command: {self.executable} {self.command} {' '.join(self.arguments)}"
        )
        try:
            # TODO: is it secure to use check_call()?
            subprocess.check_call(
                [
                    self.executable,
                    self.command,
                ]
                + self.arguments,
                stdout=sys.stdout,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as process:
            if process.returncode not in allowed_return_codes:
                logger.error(
                    f"{self.executable} error with return code {process.returncode}"
                )
                raise CommandExecutionException(
                    f"{self.executable} error with return code {process.returncode}"
                )
        return 0

    @staticmethod
    def __join_arguments(arguments: Dict) -> List:
        arguments_list = []
        for arg_key in arguments:
            arg_value = arguments[arg_key]

            arguments_list.append(arg_key)
            if arg_value is not None:
                arguments_list.append(arg_value)

        return arguments_list
