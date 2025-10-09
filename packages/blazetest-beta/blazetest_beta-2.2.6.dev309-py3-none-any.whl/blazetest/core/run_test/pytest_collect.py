import io
import logging
import sys
from typing import List

import pytest

from blazetest.core.config import CWD

logger = logging.getLogger(__name__)


class NodeIDCollector:
    node_ids: List[str] = []

    def pytest_collection_modifyitems(self, items):
        self.node_ids = [item.nodeid for item in items]


# Class for not hiding pytest output
class NullIO(io.IOBase):
    def write(self, txt):
        pass


def get_collector():
    return NodeIDCollector()


def collect_tests(pytest_args: List[str]) -> List[str]:
    # Redirect stdout to the NullIO object
    original_stdout = sys.stdout
    sys.stdout = NullIO()

    pytest_args = [f"--rootdir={CWD}", "--collect-only", "--quiet"] + pytest_args
    logger.debug(f"Collecting tests with following pytest arguments: {pytest_args}")

    collector = get_collector()
    pytest.main(pytest_args, plugins=[collector])

    sys.stdout = original_stdout
    return collector.node_ids
