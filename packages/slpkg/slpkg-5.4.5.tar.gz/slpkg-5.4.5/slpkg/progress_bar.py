#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import time
from typing import Any

from slpkg.config import config_load
from slpkg.views.imprint import Imprint

logger = logging.getLogger(__name__)


class ProgressBar:  # pylint: disable=[R0902]
    """Progress spinner bar."""

    def __init__(self) -> None:
        logger.debug("Initializing ProgressBar module.")
        self.progress_spinner = config_load.progress_spinner
        self.colors = config_load.colors
        self.spinner_color = config_load.spinner_color

        self.endc = config_load.endc

        self.imp = Imprint()

        self.color = ''
        self.spinners: dict[str, Any] = {}
        self.spinners_color: dict[str, str] = {}
        self.spinner = ''
        self.bar_message = ''

        logger.debug("ProgressBar initialized with config: progress_spinner='%s', colors_enabled=%s, spinner_color='%s'",
                     self.progress_spinner, self.colors, self.spinner_color)

    def progress_bar(self, message: str, filename: str = '') -> None:
        """Create the progress bar."""
        logger.info("Starting progress bar for message: '%s', filename: '%s'", message, filename)
        self.assign_spinner_chars()
        self.set_spinner()
        self.assign_spinner_colors()
        self.set_color()
        self.set_the_spinner_message(str(filename), message)

        print('\x1b[?25l', end='')  # Hide cursor before starting.
        logger.debug("Terminal cursor hidden.")

        current_state = 0  # Index of the current state in the spinner characters.
        try:
            while True:
                # Print the current spinner frame, overwriting the previous one.
                print(f"\r{self.bar_message}{self.color}{self.spinner[current_state]}{self.endc}", end="", flush=True)
                time.sleep(0.1)  # Control animation speed
                current_state = (current_state + 1) % len(self.spinner)  # Move to the next spinner character.
        except KeyboardInterrupt as e:
            logger.warning("Progress bar interrupted by KeyboardInterrupt.", exc_info=True)
            print('\x1b[?25h', end='')  # Show cursor before exiting.
            logger.debug("Terminal cursor shown after interrupt.")
            raise SystemExit(1) from e
        finally:
            # Ensure cursor is always shown if the loop exits for any other reason.
            print('\x1b[?25h', end='')
            logger.debug("Terminal cursor shown (finally block).")
        logger.info("Progress bar stopped.")

    def assign_spinner_colors(self) -> None:
        """Assign available spinner colors."""
        self.spinners_color = {
            'green': config_load.green,
            'yellow': config_load.yellow,
            'cyan': config_load.cyan,
            'grey': config_load.grey,
            'red': config_load.red,
            'white': config_load.white
        }
        logger.debug("Spinner colors assigned: %s", list(self.spinners_color.keys()))

    def assign_spinner_chars(self) -> None:
        """Assign available spinner characters."""
        self.spinners = {
            'spinner': ('-', '\\', '|', '/'),
            'pie': ('◷', '◶', '◵', '◴'),
            'moon': ('◑', '◒', '◐', '◓'),
            'line': ('⎺', '⎻', '⎼', '⎽', '⎼', '⎻'),
            'pixel': ('⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽'),
            'ball': ('_', '.', '|', 'o'),
            'clock': ('🕛', '🕑', '🕒', '🕔', '🕧', '🕗', '🕘', '🕚')
        }
        logger.debug("Spinner character sets assigned: %s", list(self.spinners.keys()))

    def set_the_spinner_message(self, filename: str, message: str) -> None:
        """Set message to the spinner.

        Args:
            filename (str): Name of file being processed (optional).
            message (str): The base progress bar message (e.g., "Installing", "Downloading").
        """
        width: int = 11  # Default width for message alignment
        if message == 'Removing':
            width = 9  # Adjust width for 'Removing' message.

        self.bar_message = f'{message}... '  # Default message format.
        if filename:
            # If a filename is provided, format the message to include it.
            self.bar_message = f' {message:<{width}}{self.endc}: {filename} '

        logger.debug("Spinner message set to: '%s'", self.bar_message.strip())

    def set_spinner(self) -> None:
        """Set the active spinner characters based on configuration."""
        try:
            self.spinner = self.spinners[self.progress_spinner]
            logger.debug("Spinner set to '%s' characters: %s", self.progress_spinner, self.spinner)
        except KeyError:
            logger.info("Invalid progress spinner '%s' specified in config. Falling back to default 'spinner'.", self.progress_spinner)
            self.spinner = self.spinners['spinner']
            logger.debug("Spinner fallback to 'spinner' characters: %s", self.spinner)

    def set_color(self) -> None:
        """Set the spinner color based on configuration."""
        try:
            self.color = self.spinners_color[self.spinner_color]
            logger.debug("Spinner color set to '%s'.", self.spinner_color)
        except KeyError:
            logger.info("Invalid spinner color '%s' specified in config. Falling back to default color.", self.spinner_color)
            self.color = ''  # Fallback to default terminal color (white/reset).
            logger.debug("Spinner color fallback to default.")
