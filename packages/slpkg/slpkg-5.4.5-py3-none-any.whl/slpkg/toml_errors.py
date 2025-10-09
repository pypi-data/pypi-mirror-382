#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TomlErrors:  # pylint: disable=[R0903]
    """Raise an error message for toml files."""

    def __init__(self) -> None:
        self.prog_name: str = 'slpkg'
        logger.debug("TomlErrors module initialized.")

    def raise_toml_error_message(self, error: str, toml_file: Path) -> None:
        """General error message for toml configs files, prints to console and logs.

        Args:
            error (str): Description of the error.
            toml_file (Path): Path to the TOML file where the error occurred.

        Raises:
            SystemExit: Exits the application with status 1.
        """
        logger.error("TOML configuration error in file '%s': %s", toml_file, error)
        print(f"\n{self.prog_name}: Error: {error}: in the configuration\n"
              f"file '{toml_file}', edit the file and check for errors,\n"
              f"or if you have upgraded the '{self.prog_name}' maybe you need to run:\n"
              f"\n   $ slpkg_new-configs\n")
