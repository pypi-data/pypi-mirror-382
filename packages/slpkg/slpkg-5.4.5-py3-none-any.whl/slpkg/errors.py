#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging

from slpkg.config import config_load

logger = logging.getLogger(__name__)


class Errors:  # pylint: disable=[R0903]
    """Raise an error message."""

    def __init__(self) -> None:
        logger.debug("Initializing Errors class.")
        self.prog_name = config_load.prog_name
        self.red = config_load.red
        self.endc = config_load.endc
        logger.debug("Errors class initialized with program name: %s", self.prog_name)

    def message(self, message: str, exit_status: int) -> None:
        """General method to raise an error message and exit.

        Logs the error message at a critical level before printing to console and exiting.

        Args:
            message (str): String message to display and log.
            exit_status (int): Exit status code for the application.

        Raises:
            SystemExit: Exits the application with the specified status code.
        """
        # Log the error message at a critical level.
        # This ensures that even if the program exits, the error is recorded in the log file.
        logger.critical("Application exiting with error (status %d): %s", exit_status, message)

        # Print the error message to the console for immediate user feedback.
        print(f"\n{self.prog_name}: {self.red}Error{self.endc}: {message}\n")

        # Raise SystemExit to terminate the program.
        raise SystemExit(exit_status)
