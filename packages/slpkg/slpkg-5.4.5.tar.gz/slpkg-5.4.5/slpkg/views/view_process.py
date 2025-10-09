#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import time
from multiprocessing import Process
from typing import Optional

from slpkg.config import config_load
from slpkg.progress_bar import ProgressBar
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint

logger = logging.getLogger(__name__)


class ViewProcess:
    """View the process messages."""

    def __init__(self) -> None:
        logger.debug("Initializing ViewProcess module.")
        self.red = config_load.red
        self.endc = config_load.endc

        self.progress = ProgressBar()
        self.utils = Utilities()
        self.imp = Imprint()

        self.bar_process: Optional[Process] = None
        logger.debug("ViewProcess module initialized.")

    def message(self, message: str) -> None:
        """Show spinner with message.

        Args:
            message (str): Message of spinner.
        """
        logger.info("Displaying progress message: '%s'", message)
        # Create a new process to run the progress bar in parallel.
        self.bar_process = Process(target=self.progress.progress_bar, args=(message,))
        self.bar_process.start()
        logger.debug("Progress bar process started for message: '%s' (PID: %s)", message, self.bar_process.pid)

    def done(self) -> None:
        """Show done message."""
        logger.info("Progress bar process indicating 'Done'.")
        time.sleep(0.1)  # Small delay to ensure visual update.
        if self.bar_process is not None:
            if self.bar_process.is_alive():
                self.bar_process.terminate()  # Terminate the progress bar process.
                self.bar_process.join()     # Wait for the process to finish termination.
                logger.debug("Progress bar process terminated and joined.")
            else:
                logger.debug("Progress bar process was already not alive.")
        else:
            logger.warning("Attempted to call 'done' but no progress bar process was active.")

        # Clear the line and print the 'Done' message.
        print(f'\b{self.imp.done}', end='')
        print('\x1b[?25h')  # Reset cursor after hiding.
        logger.info("'Done' message displayed and cursor reset.")

    def failed(self) -> None:
        """Show for failed message."""
        logger.warning("Progress bar process indicating 'Failed'.")
        time.sleep(0.1)  # Small delay to ensure visual update.
        if self.bar_process is not None:
            if self.bar_process.is_alive():
                self.bar_process.terminate()  # Terminate the progress bar process.
                self.bar_process.join()     # Wait for the process to finish termination.
                logger.debug("Progress bar process terminated and joined after failure.")
            else:
                logger.debug("Progress bar process was already not alive during failure.")
        else:
            logger.warning("Attempted to call 'failed' but no progress bar process was active.")

        # Clear the line and print the 'Failed' message with color.
        print(f'\b{self.red}{self.imp.failed}{self.endc}', end='')
        print('\x1b[?25h')  # Reset cursor after hiding.
        logger.warning("'Failed' message displayed and cursor reset.")
