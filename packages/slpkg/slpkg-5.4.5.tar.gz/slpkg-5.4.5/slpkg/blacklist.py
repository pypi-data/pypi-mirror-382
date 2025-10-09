#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import sys
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit import exceptions

from slpkg.config import config_load
from slpkg.toml_errors import TomlErrors

logger = logging.getLogger(__name__)


class Blacklist:  # pylint: disable=[R0903]
    """Reads and returns the blacklist."""

    def __init__(self) -> None:
        logger.debug("Initializing Blacklist module.")
        self.etc_path = config_load.etc_path

        self.toml_errors = TomlErrors()
        self.blacklist_file_toml: Path = Path(self.etc_path, 'blacklist.toml')
        logger.debug("Blacklist module initialized. Blacklist file path: %s", self.blacklist_file_toml)

    def packages(self) -> list[str]:
        """Read the blacklist file.

        Returns:
            list[str]: Name of packages.
        """
        packages: list[str] = []
        logger.info("Attempting to read blacklist packages from: %s", self.blacklist_file_toml)

        if self.blacklist_file_toml.is_file():
            logger.debug("Blacklist file exists. Proceeding to read and parse.")
            try:
                with open(self.blacklist_file_toml, 'r', encoding='utf-8') as file:
                    black: dict[str, Any] = tomlkit.parse(file.read())
                    # Ensure 'PACKAGES' key exists and is a list.
                    if 'PACKAGES' in black and isinstance(black['PACKAGES'], list):
                        packages = list(black['PACKAGES'])
                        logger.info("Successfully loaded %d packages from blacklist.", len(packages))
                        logger.debug("Blacklisted packages: %s", packages)
                    else:
                        logger.warning("Blacklist file '%s' does not contain a 'PACKAGES' key or its value is not a list. Returning empty list.", self.blacklist_file_toml)
                        packages = []  # Ensure packages is empty if format is incorrect.
            except (KeyError, exceptions.TOMLKitError) as error:
                logger.critical("Failed to parse blacklist TOML file '%s'. Error: %s", self.blacklist_file_toml, error, exc_info=True)
                print()
                self.toml_errors.raise_toml_error_message(str(error), self.blacklist_file_toml)
                sys.exit(1)  # Exit on critical parsing error.
            except Exception as e:  # pylint: disable=[W0718]
                logger.critical("An unexpected error occurred while reading blacklist file '%s': %s", self.blacklist_file_toml, e, exc_info=True)
                print(f"\nError: An unexpected error occurred while reading blacklist file: {e}\n")
                sys.exit(1)
        else:
            logger.info("Blacklist file '%s' does not exist. Returning empty list.", self.blacklist_file_toml)

        return packages
