#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import sys

from slpkg.config import config_load
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class PackageValidator:
    """Validates packages before proceeding."""

    def __init__(self) -> None:
        logger.debug("Initializing PackageValidator module.")
        self.red = config_load.red
        self.endc = config_load.endc
        self.utils = Utilities()
        logger.debug("PackageValidator module initialized.")

    def is_package_exists(self, packages: list[str], data: dict[str, dict[str, str]]) -> None:
        """Check if the package exist if not prints a message.

        Args:
            packages (list[str]): List of packages.
            data (dict[str, dict[str, str]]): Repository data.
        """
        logger.info("Checking if packages exist in repository data: %s", packages)
        not_packages: list[str] = []

        for pkg in packages:
            # Check if the package is not found in the data and is not a wildcard '*'
            if not data.get(pkg) and pkg != '*':
                not_packages.append(pkg)
                logger.warning("Package '%s' not found in repository data.", pkg)
            else:
                logger.debug("Package '%s' found or is a wildcard.", pkg)

        if not_packages:
            error_message = f"Unable to find a match: {', '.join(not_packages)}"
            print(f"{self.red}Error{self.endc}: {error_message}")
            logger.critical("Exiting: %s", error_message)
            sys.exit(1)
        else:
            logger.info("All specified packages exist in repository data or are wildcards.")

    def is_package_installed(self, packages: list[str]) -> None:
        """Check for installed packages and prints message if not.

        Args:
            packages (list[str]): List of packages.
        """
        logger.info("Checking if packages are installed: %s", packages)
        not_found: list[str] = []

        for pkg in packages:
            if not self.utils.is_package_installed(pkg):
                not_found.append(pkg)
                logger.warning("Package '%s' is not installed.", pkg)
            else:
                logger.debug("Package '%s' is installed.", pkg)

        if not_found:
            error_message = f"Unable to find a match: {', '.join(not_found)}"
            print(f"{self.red}Error{self.endc}: {error_message}")
            logger.critical("Exiting: %s", error_message)
            sys.exit(1)
        else:
            logger.info("All specified packages are installed.")
