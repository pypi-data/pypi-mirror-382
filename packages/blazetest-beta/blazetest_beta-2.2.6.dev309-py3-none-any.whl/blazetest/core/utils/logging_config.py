import enum
import logging
import os
import time
import uuid
from typing import Optional

import click
import logging_loki

from blazetest.core.config import LOKI_URL, CWD


class ColoredFormatter(logging.Formatter):
    start_time = time.time()
    last_time = time.time()

    def format(self, record):
        level = record.levelname
        msg = record.msg
        if level == "DEBUG":
            msg = click.style(msg, fg="blue")
        elif level == "INFO":
            msg = click.style(msg, bold=True)
        elif level == "WARNING":
            msg = click.style(msg, fg="yellow")
        elif level == "ERROR":
            msg = click.style(msg, fg="red", bold=True)
        elif level == "CRITICAL":
            msg = click.style(msg, bg="red", fg="white")

        total_time = round(time.time() - self.start_time, 2)
        op_time = round(time.time() - self.last_time, 2)

        message = f"* {msg} ({op_time}s, {total_time}s)"
        self.last_time = time.time()
        return message


def get_log_file_path(artifacts_dir: str, session_uuid: str):
    return os.path.join(
        CWD, os.path.join(artifacts_dir, f"blazetest_{session_uuid}.log")
    )


def setup_logging(
    debug: bool = False,
    stdout_enabled: bool = True,
    loki_api_key: Optional[str] = None,
    session_uuid: str = uuid.uuid4(),
    artifacts_dir: str = "",
):
    """
    Sets up basic logging.
    If stdout_enabled, stdout is shown to the user. Otherwise, saved to the file.
    If loki_api_key is provided, logs are sent to Loki.
    """
    level = logging.DEBUG if debug else logging.INFO

    handlers = []
    # TODO: debug not working well with Loki (possible reason: too many requests)
    if loki_api_key:
        logging_loki.emitter.LokiEmitter.level_tag = "level"
        handler = logging_loki.LokiHandler(
            url=LOKI_URL.format(loki_api_key=loki_api_key),
            tags={"service": "blazetest", "session_id": session_uuid},
            version="1",
        )
        handlers.append(handler)

    if stdout_enabled:
        colored_handler = logging.StreamHandler()
        colored_handler.setFormatter(ColoredFormatter())
        handlers.append(colored_handler)
        handlers.append(
            logging.FileHandler(filename=get_log_file_path(artifacts_dir, session_uuid))
        )

    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
    )


class ColoredOutput(enum.Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
