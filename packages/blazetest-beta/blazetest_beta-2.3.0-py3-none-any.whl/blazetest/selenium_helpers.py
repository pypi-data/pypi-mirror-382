"""
Helper utilities for Selenium WebDriver in AWS Lambda environments.

Users can optionally use these helpers to get Lambda-optimized Chrome options.
"""

import os
from typing import Optional

try:
    from selenium import webdriver
except ImportError:
    webdriver = None


def get_lambda_chrome_options(
    headless: bool = True, additional_args: Optional[list] = None
):
    """
    Get Chrome options optimized for AWS Lambda environment.

    This helper provides recommended Chrome flags for running Selenium tests
    in Lambda. Users can use this in their conftest.py or test files.

    Args:
        headless: Whether to run in headless mode (default: True)
        additional_args: Additional Chrome arguments to add

    Returns:
        ChromeOptions object configured for Lambda

    Example:
        ```python
        from blazetest.selenium_helpers import get_lambda_chrome_options

        @pytest.fixture(scope="class")
        def driver(request):
            options = get_lambda_chrome_options()
            web_driver = webdriver.Chrome(options=options)
            request.cls.driver = web_driver
            yield
            web_driver.close()
        ```
    """
    if webdriver is None:
        raise ImportError(
            "selenium is not installed. Install it with: pip install selenium"
        )

    options = webdriver.ChromeOptions()

    # Core Lambda compatibility flags
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--single-process")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    # Critical for "DevToolsActivePort file doesn't exist" error
    options.add_argument("--remote-debugging-port=9222")

    # Use /tmp for all Chrome data (Lambda's writable directory)
    options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    options.add_argument("--data-path=/tmp/chrome-data")
    options.add_argument("--disk-cache-dir=/tmp/chrome-cache")
    options.add_argument("--homedir=/tmp")

    # Window size for consistent rendering
    options.add_argument("--window-size=1920,1080")

    # Headless mode
    if headless:
        options.add_argument("--headless=new")

    # Add any user-specified arguments
    if additional_args:
        for arg in additional_args:
            options.add_argument(arg)

    return options


def is_lambda_environment() -> bool:
    """
    Check if code is running in AWS Lambda environment.

    Returns:
        True if running in Lambda, False otherwise
    """
    return bool(
        os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT")
    )


def get_chrome_options(headless: bool = True, additional_args: Optional[list] = None):
    """
    Get Chrome options that automatically adapt to Lambda or local environment.

    Args:
        headless: Whether to run in headless mode (default: True)
        additional_args: Additional Chrome arguments to add

    Returns:
        ChromeOptions object configured for current environment
    """
    if is_lambda_environment():
        return get_lambda_chrome_options(
            headless=headless, additional_args=additional_args
        )
    else:
        # Local development - minimal options
        if webdriver is None:
            raise ImportError(
                "selenium is not installed. Install it with: pip install selenium"
            )

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")

        if additional_args:
            for arg in additional_args:
                options.add_argument(arg)

        return options
