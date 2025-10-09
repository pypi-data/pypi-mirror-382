#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging  # Import the logging module

from slpkg.config import config_load
from slpkg.utilities import Utilities
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class Cleanings:  # pylint: disable=[R0903,R0902]
    """Cleans the logs from packages."""

    def __init__(self) -> None:
        logger.debug("Initializing Cleanings module.")
        self.tmp_slpkg = config_load.tmp_slpkg
        self.build_path = config_load.build_path
        self.prog_name = config_load.prog_name
        self.bold = config_load.bold
        self.red = config_load.red
        self.endc = config_load.endc

        self.view = View()
        self.utils = Utilities()
        logger.debug("Cleanings module initialized. tmp_slpkg: %s, build_path: %s", self.tmp_slpkg, self.build_path)

    def tmp(self) -> None:
        """Delete files and folders in /tmp/slpkg/ folder."""
        logger.info("Starting deletion of local data in %s.", self.tmp_slpkg)
        print('Deleting of local data:\n')

        found_files_to_delete = False
        for file in self.tmp_slpkg.rglob('*'):
            found_files_to_delete = True
            print(f'{self.red}{self.endc} {file}')
            logger.debug("File found for deletion: %s", file)

        if not found_files_to_delete:
            logger.info("No files or folders found to delete in %s.", self.tmp_slpkg)
            print("No files or folders to delete.\n")  # Inform user if nothing to delete.
            return  # Exit if nothing to delete.

        print(f"\n{self.prog_name}: {self.bold}{self.red}WARNING{self.endc}: All the files and "
              f"folders will delete!")
        logger.warning("User warned about deletion of all files/folders in %s.", self.tmp_slpkg)

        self.view.question()  # Ask user for confirmation.
        logger.info("User confirmed deletion of local data.")

        try:
            self.utils.remove_folder_if_exists(self.tmp_slpkg)
            logger.info("Successfully removed folder: %s", self.tmp_slpkg)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to remove folder '%s': %s", self.tmp_slpkg, e, exc_info=True)
            print(f"{self.red}Error{self.endc}: Failed to remove {self.tmp_slpkg}\n")

        try:
            self.utils.create_directory(self.build_path)
            logger.info("Successfully created build directory: %s", self.build_path)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to create build directory '%s': %s", self.build_path, e, exc_info=True)
            print(f"{self.red}Error{self.endc}: Failed to create {self.build_path}\n")

        print('Successfully cleared!\n')
        logger.info("Local data clearing process completed.")
