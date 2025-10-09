#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import subprocess
from pathlib import Path

from slpkg.config import config_load
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class GPGVerify:  # pylint: disable=[R0903]
    """GPG verify files."""

    def __init__(self) -> None:
        logger.debug("Initializing GPGVerify class.")
        self.gpg_verification = config_load.gpg_verification
        self.red = config_load.red
        self.endc = config_load.endc

        self.view = View()
        self.view_process = ViewProcess()
        logger.debug("GPGVerify class initialized. GPG verification enabled: %s", self.gpg_verification)

    def verify(self, asc_files: list[Path]) -> None:
        """Verify files with gpg tool.

        Args:
            asc_files (list[Path]): List of files.
        """
        if self.gpg_verification:
            logger.info("GPG verification is enabled. Starting verification process for %d files.", len(asc_files))
            output: dict[str, int] = {}
            gpg_command: str = 'gpg --verify'
            self.view_process.message('Verify files with GPG')
            logger.debug("Displaying 'Verify files with GPG' message.")

            for file in asc_files:
                logger.debug("Verifying file: %s using command: '%s %s'", file, gpg_command, file)
                # Using shell=True for consistency with other subprocess calls in the project.
                # For security-sensitive applications, consider shell=False and passing arguments as a list.
                try:
                    with subprocess.Popen(f'{gpg_command} {file}', shell=True, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, text=True, encoding='utf-8') as process:
                        process.wait()
                        # Read the output from stdout and then strip it.
                        stdout_output = process.stdout.read() if process.stdout else ""
                        output[file.name] = process.returncode
                        logger.debug("Verification for '%s' completed with return code: %d. Output: %s",
                                     file.name, process.returncode, stdout_output.strip())
                except Exception as e:  # pylint: disable=[W0718]
                    logger.error("Error during GPG verification of file '%s': %s", file.name, e, exc_info=True)
                    output[file.name] = -1  # Indicate an internal error.

            all_zero = all(value == 0 for value in output.values())
            if all_zero:
                self.view_process.done()
                logger.info("All GPG files verified successfully.")
            else:
                self.view_process.failed()
                logger.warning("GPG verification failed for one or more files.")
                for filename, code in output.items():
                    if code != 0:
                        print(f"{self.red}Error{self.endc} {code}: {filename}")
                        logger.error("GPG verification failed for file '%s' with exit code: %d.", filename, code)
                print()  # Add a newline for console formatting.
                logger.critical("GPG verification failed. Prompting user for action, which may lead to application exit.")
                self.view.question()
        else:
            logger.info("GPG verification is disabled in configuration. Skipping file verification.")
