#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Changelog:  # pylint: disable=[R0902]

    """Manages and prints changelog information for specified repositories.

    This class handles the retrieval and display of changelog entries.
    It allows filtering changelog content based on a user-provided query
    and includes terminal-based pagination for large outputs.
    """

    def __init__(self, options: dict[str, bool], repository: str, query: str) -> None:
        logger.debug("Initializing Changelog module with options: %s, repository: %s, query: '%s'",
                     options, repository, query)
        self.options = options
        self.repository = repository
        self.query = query

        self.editor = config_load.editor
        self.pager = config_load.pager
        logger.debug("Pager string: %s, and editor: %s from config.", self.pager, self.editor)

        self.repos = Repositories()
        self.utils = Utilities()
        self.columns, self.rows = shutil.get_terminal_size()
        logger.debug("Terminal size: %sx%s", self.columns, self.rows)

        self.repo_path: Path = self.repos.repositories[self.repository]['path']
        self.changelog_txt: str = self.repos.repositories[self.repository]['changelog_txt']
        self.changelog_file: Path = Path(self.repo_path, self.changelog_txt)
        logger.debug("Changelog file path: %s", self.changelog_file)

        self.option_for_pager: bool = options.get('option_pager', False)
        self.option_for_edit: bool = options.get('option_edit', False)
        logger.debug("Option for edit enabled: %s, Option for pager enabled: %s", self.option_for_edit, self.option_for_pager)

    def run(self) -> None:
        """Run changelog methods"""
        logger.info("Changelog run method called. Option for edit: %s", self.option_for_edit)
        if self.option_for_edit:
            self.edit_changelog()
        else:
            self.display_changelog()

    def display_changelog(self) -> None:
        """Prints repository changelog."""
        logger.info("Displaying changelog for repository '%s' with query: '%s'. Pager enabled: %s",
                    self.repository, self.query, self.option_for_pager)
        day_pattern = re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b', re.IGNORECASE)
        # Console colors.
        green: str = config_load.green
        endc: str = config_load.endc

        try:
            # Read changelog file line by line.
            lines = self.utils.read_text_file(self.changelog_file)
            logger.debug("Read %d lines from changelog file: %s", len(lines), self.changelog_file)

            if self.option_for_pager:
                # If the pager option is enabled, pipe output to the configured pager.
                pager_command = self.pager.split()
                logger.debug("Using pager command: %s", pager_command)

                # Start a subprocess to the pager using a 'with' statement for proper resource management.
                # stdin=subprocess.PIPE allows us to write to the pager's input.
                # text=True ensures proper handling of text (str) and encoding.
                # encoding='utf-8' specifies the character encoding for the stream.
                with subprocess.Popen(pager_command, stdin=subprocess.PIPE, text=True, encoding='utf-8') as process:
                    if process.stdin is None:
                        logger.error("Pager process stdin is unexpectedly None. Cannot write to pager.")
                        raise IOError("Failed to open stdin pipe for pager process.")

                    for line_from_file in lines:
                        # Case-insensitive query match.
                        if self.query.lower() in line_from_file.lower():
                            display_line = line_from_file  # Use a mutable variable for display.

                            # Apply green color for date lines.
                            if day_pattern.search(line_from_file):
                                display_line = f'{green}{display_line}{endc}'
                                logger.debug("Applied green color to date line: '%s'", line_from_file.strip())

                            # Write the formatted line to the standard input of the pager process.
                            process.stdin.write(display_line)
                            logger.debug("Wrote line to pager's stdin: '%s'", display_line.strip())

                    # Close the stdin of the pager process. This signals EOF (End Of File) to the pager,
                    # so it knows there's no more input coming and can display the content.
                    process.stdin.close()
                    logger.debug("Closed pager's stdin.")

                    # The 'with' statement for Popen handles waiting for the process to terminate
                    # and cleaning up resources. We keep process.wait() explicitly for clarity
                    # and to ensure the script waits for the pager to finish before exiting.
                    process.wait()
                    logger.info("Pager process exited. Finished displaying changelog.")
            else:
                logger.debug("Pager not enabled. Printing directly to stdout.")
                for line_from_file in lines:
                    # Case-insensitive query match.
                    if self.query.lower() in line_from_file.lower():
                        display_line = line_from_file
                        if day_pattern.search(line_from_file):
                            display_line = f'{green}{display_line}{endc}'
                        sys.stdout.write(display_line)
                logger.info("Finished displaying changelog directly to stdout.")

        except FileNotFoundError:
            logger.error("Changelog file not found: %s", self.changelog_file)
            print(f"Error: Changelog file not found at '{self.changelog_file}'")
            sys.exit(1)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while displaying changelog: %s", e, exc_info=True)
            print(f"Error: An unexpected error occurred: {e}")
            sys.exit(1)

    def edit_changelog(self) -> None:
        """Edit changelog file with system editor."""
        editor = self.editor
        if not editor:
            editor = os.environ.get('EDITOR', '')
        if not editor:
            logger.error("No editor configured or found in environment. Cannot open external editor for changelog.")
            print("Error: No editor configured or found. Cannot open editor.")
            sys.exit(1)

        command = [editor, str(self.changelog_file)]
        logger.info("Opening changelog file '%s' with external editor: '%s'", self.changelog_file, editor)
        try:
            subprocess.run(command, check=True)  # check=True will raise CalledProcessError on non-zero exit codes.
            logger.info("External editor exited successfully after editing changelog.")
        except subprocess.CalledProcessError as e:
            logger.error("External editor command failed with exit code %s: %s", e.returncode, e, exc_info=True)
            print(f"Error: External editor failed with exit code {e.returncode}")
            sys.exit(e.returncode)
        except FileNotFoundError:
            logger.error("External editor '%s' not found. Please ensure it is installed and in your PATH.", editor, exc_info=True)
            print(f"Error: External editor '{editor}' not found. Please ensure it is installed and in your PATH.")
            sys.exit(1)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while opening external editor for changelog: %s", e, exc_info=True)
            print(f"Error: An unexpected error occurred with editor: {e}")
            sys.exit(1)

        sys.exit(0)
