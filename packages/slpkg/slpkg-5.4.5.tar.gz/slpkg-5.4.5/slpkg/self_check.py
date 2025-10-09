#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import re
from typing import Any, Union

import requests
from packaging.version import InvalidVersion
from packaging.version import Version as Version_parse
from packaging.version import parse as parse_version

from slpkg.config import config_load
from slpkg.views.version import Version

logger = logging.getLogger(__name__)

# Constants for the script
PYPROJECT_URL = 'https://gitlab.com/dslackw/slpkg/-/raw/master/pyproject.toml'
VERSION_PREFIX = 'version'  # The prefix used for version lines in the pyproject file


def get_installed_version() -> str:
    """
    Retrieves the locally installed version of the software.
    Assumes the 'Version' class is available and functional.
    If 'Version' is not found, it logs an error and returns a default low version.
    """
    try:
        # Replace this with your actual method to get the installed version.
        # For example, if you have a __version__ attribute in your main module:
        # from your_package import __version__
        # return __version__

        # If 'Version' class from 'slpkg.views.version' is indeed used:
        ver = Version()
        return ver.version
    except NameError:
        logger.error("The 'Version' class is not defined. Please ensure 'from slpkg.views.version import Version' is correct.")
        return "0.0.0"  # Return a default low version to allow updates if class is missing


def get_repo_latest_version(url: str) -> Union[Any, None]:  # pylint: disable=[R0911]
    """
    Fetches the latest version from the repository's pyproject file.

    Args:
        url (str): The URL to the pyproject.toml file.

    Returns:
        str | None: The latest version string if found, otherwise None.
    """
    try:
        # Make a GET request with a timeout to prevent indefinite waiting
        response = requests.get(url, timeout=10)
        # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        response.raise_for_status()

        # Define the regex pattern for "version = "X.Y.Z""
        version_pattern = re.compile(r'version = "(\d+\.\d+\.\d+)"')

        # Search for the first line that starts with the defined VERSION_PREFIX
        for line in response.text.splitlines():
            match = version_pattern.search(line)
            if match:
                return match.group(1)

        logger.warning("No version found with the specified prefix.")
        return None

    except requests.exceptions.Timeout:
        logger.error("The request timed out after 10 seconds while trying to reach the URL: %s", url)
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to the URL: %s. Check your internet connection or the URL.", url)
        return None
    except requests.exceptions.HTTPError as e:
        # Log specific HTTP errors (e.g., 404 Not Found, 403 Forbidden)
        logger.error("HTTP error occurred while accessing %s: %s - %s", url, e.response.status_code, e.response.reason)
        return None
    except requests.exceptions.RequestException as e:
        # Catch any other request-related exceptions not caught by more specific requests exceptions
        logger.error("An unexpected request error occurred while accessing %s: %s", url, e)
        return None


def check_self_update() -> None:
    """
    Checks for a newer version of the software and informs the user.
    """
    green: str = config_load.green
    cyan: str = config_load.cyan
    yellow: str = config_load.yellow
    endc: str = config_load.endc
    parsed_installed: Version_parse = parse_version('0.0.0')
    parsed_repo: Version_parse = parse_version('0.0.0')

    installed_version_str = get_installed_version()
    repo_version_str = get_repo_latest_version(PYPROJECT_URL)

    # If we couldn't determine the repository's latest version, we can't proceed
    if not repo_version_str:
        logger.info("Could not determine the latest version from the repository. Update check aborted.")
        return

    try:
        # Parse version strings into comparable version objects
        parsed_installed = parse_version(installed_version_str)
        parsed_repo = parse_version(repo_version_str)
    except InvalidVersion as e:
        # Catch general exceptions during version parsing (e.g., InvalidVersion)
        logger.error("Failed to parse versions '%s' or '%s': %s. Please ensure valid version strings.",
                     installed_version_str, repo_version_str, e)

    # Compare the parsed versions
    if parsed_repo > parsed_installed:
        print(f"Update available: Version {green}{parsed_repo}{endc} is newer than your current {yellow}{parsed_installed}{endc}.")
        print(f"Please visit the install page: '{cyan}https://dslackw.gitlab.io/slpkg/install{endc}'")
    else:
        print(f"Current version ({green}{parsed_installed}{endc}) is up to date. No new updates found.")
