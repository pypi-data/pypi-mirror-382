import os

CWD = os.getcwd()
PWD = os.path.dirname(os.path.dirname(__file__))

BUILD_FOLDER_PATH = os.path.join(CWD, ".blazetest")
DOCKER_FILE_PATH = os.path.join(BUILD_FOLDER_PATH, "Dockerfile")

PROJECT_CONFIG_TOML = os.path.join(CWD, "blazetest.toml")

TESTS_PATH = os.path.join(CWD, "tests")
SESSION_RESULT_FILEPATH = os.path.join(CWD, "blazetest-report.json")

DEFAULT_ENCODING = os.environ.get("DEFAULT_ENCODING", "utf-8")

MAX_LAMBDA_WORKERS = 1000
TESTS_RETRY_MAX_NUMBER = 10

SUPPORTED_PYTHON_VERSIONS = ["3.7", "3.8", "3.9"]

LOKI_URL = "https://189245:{loki_api_key}@logs-prod3.grafana.net/loki/api/v1/push"
LOKI_USER = os.getenv("LOKI_USER", "189245")
LOKI_API_KEY = os.getenv("LOKI_API_KEY")
LOKI_HOST = os.getenv("LOKI_HOST", "logs-prod3.grafana.net")

PRODUCT_ID = 18031

# TODO: How to retrieve those in a secure way?
ACCESS_TOKEN = (
    "WyIzMzI3NjE2MSIsIjlSMlR0SERTTldJcTBEWU9tRjB5bmRwWXVMcHZia2tPSFNwV2VJRmgiXQ=="
)
RSA_PUB_KEY = (
    "<RSAKeyValue><Modulus>5TFzvx1Ygenf7BJYxliBFkcKSDebrxVTUteai/xjHP/"
    "Tmrx2z5h5vJRkQlg6vxecbLDj7g+TAvZssEVj5D1VVtur2Od1Fdqs49m0dA+QdGB"
    "v5DXt9YeqJLW/JpciMom79HcOeIvJDTHJcQssCXKLxGnQkTpMIpB22hTOuJTcj1b"
    "mLManR6mQYX2k/BZ/XkC2l61TbKaOnKww3BrX8+b2ImT89VeN0znxIEwBUla78C6"
    "pDJTkKDPZPeHItHk9gTBx9CkCCfMdzidVxwiMFvXM7PSBWSFKn2JPO5+gawJbV+0"
    "nH95890EL80dl/OH/K5O+CYTaHrKJ+zUcY7MxLqsmCw==</Modulus><Exponent>"
    "AQAB</Exponent></RSAKeyValue>"
)

EXECUTABLE_FILES = [
    "tests_runner_handler/__init__.py",
    "tests_runner_handler/handler.py",
    "scripts/install_dependencies.sh",
]
