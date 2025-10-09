import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def generate_allure_report(
    allure_results_dir: str, allure_report_dir: str, clean: bool = True
) -> bool:
    """
    Generate Allure HTML report from results directory.

    Args:
        allure_results_dir: Directory containing Allure result JSON files
        allure_report_dir: Directory where HTML report will be generated
        clean: Whether to clean previous report before generating

    Returns:
        bool: True if report generation succeeded, False otherwise
    """
    try:
        # Check if allure command is available
        if not shutil.which("allure"):
            logger.error(
                "Allure CLI not found. Install from https://docs.qameta.io/allure/"
            )
            logger.error("For quick install: npm install -g allure-commandline")
            return False

        # Check if results directory exists and has files
        if not os.path.exists(allure_results_dir):
            logger.error(f"Allure results directory not found: {allure_results_dir}")
            return False

        result_files = list(Path(allure_results_dir).glob("*-result.json"))
        if not result_files:
            logger.warning(f"No Allure result files found in {allure_results_dir}")
            return False

        logger.info(f"Found {len(result_files)} Allure result files")

        # Clean previous report if requested
        if clean and os.path.exists(allure_report_dir):
            logger.info(f"Cleaning previous report: {allure_report_dir}")
            shutil.rmtree(allure_report_dir)

        # Create report directory
        os.makedirs(allure_report_dir, exist_ok=True)

        # Generate Allure report
        logger.info(f"Generating Allure report: {allure_report_dir}")
        cmd = [
            "allure",
            "generate",
            allure_results_dir,
            "-o",
            allure_report_dir,
            "--clean" if clean else "",
        ]

        # Remove empty string if not cleaning
        cmd = [c for c in cmd if c]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            logger.error(f"Allure report generation failed: {result.stderr}")
            return False

        logger.info(
            f"Allure report generated successfully: {allure_report_dir}/index.html"
        )
        return True

    except subprocess.TimeoutExpired:
        logger.error("Allure report generation timed out after 60 seconds")
        return False
    except Exception as e:
        logger.error(f"Error generating Allure report: {str(e)}")
        return False


def get_allure_report_path(allure_report_dir: str) -> Optional[str]:
    """
    Get the path to the main Allure report HTML file.

    Args:
        allure_report_dir: Directory containing generated Allure report

    Returns:
        str: Path to index.html if exists, None otherwise
    """
    index_path = os.path.join(allure_report_dir, "index.html")
    if os.path.exists(index_path):
        return index_path
    return None


def install_allure_cli() -> bool:
    """
    Attempt to install Allure CLI using npm (if available).

    Returns:
        bool: True if installation succeeded, False otherwise
    """
    try:
        # Check if npm is available
        if not shutil.which("npm"):
            logger.error("npm not found. Cannot auto-install Allure CLI")
            logger.info(
                "Please install Allure manually: https://docs.qameta.io/allure/"
            )
            return False

        logger.info("Installing Allure CLI via npm...")
        result = subprocess.run(
            ["npm", "install", "-g", "allure-commandline"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0:
            logger.info("Allure CLI installed successfully")
            return True
        else:
            logger.error(f"Failed to install Allure CLI: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("Allure CLI installation timed out")
        return False
    except Exception as e:
        logger.error(f"Error installing Allure CLI: {str(e)}")
        return False
