#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import shutil
import subprocess
from datetime import datetime
from io import TextIOWrapper
from multiprocessing import Process
from typing import Optional

from slpkg.config import config_load
from slpkg.errors import Errors
from slpkg.progress_bar import ProgressBar
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint

logger = logging.getLogger(__name__)


class MultiProcess:  # pylint: disable=[R0902]
    """Create parallel process between progress bar and process."""

    def __init__(self, options: Optional[dict[str, bool]] = None) -> None:
        logger.debug("Initializing MultiProcess module with options: %s", options)
        self.colors = config_load.colors
        self.progress_bar = config_load.progress_bar
        self.package_type = config_load.package_type
        self.log_packages = config_load.log_packages
        self.process_log = config_load.process_log
        self.process_log_file = config_load.process_log_file
        self.red = config_load.red
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.imp = Imprint()
        self.errors = Errors()

        self.columns, self.rows = shutil.get_terminal_size()
        self.timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.head_message: str = f'Timestamp: {self.timestamp}'
        self.bottom_message: str = 'EOF - End of log file'

        if options is not None:
            self.option_for_reinstall: bool = options.get('option_reinstall', False)
            logger.debug("Option 'reinstall' set to: %s", self.option_for_reinstall)
        else:
            self.option_for_reinstall = False  # Default if no options provided.
            logger.debug("No options provided, 'reinstall' defaulted to False.")
        logger.debug("MultiProcess initialization complete. Terminal size: %sx%s, Process log file: %s", self.columns, self.rows, self.process_log_file)

    def process_and_log(self, command: str, filename: str, progress_message: str) -> None:
        """Start a multiprocessing process.

        Args:
            command (str): The command of process
            filename (str): The filename of process.
            progress_message (str): The message of progress.
        """
        logger.info("Starting process_and_log for command: '%s', filename: '%s', message: '%s'", command, filename, progress_message)
        pg_color: str = self.green
        width: int = 11   # Default width.

        if progress_message == 'Building':
            pg_color = self.yellow
            logger.debug("Progress message is 'Building', setting color to yellow.")
        elif progress_message == 'Removing':
            pg_color = self.red
            width = 9  # Adjusted width for 'Removing'.
            logger.debug("Progress message is 'Removing', setting color to red and width to 9.")

        if self.progress_bar:
            logger.debug("Progress bar is enabled. Setting up multiprocessing.")
            skip: str = f'{self.yellow}{self.imp.skipped}{self.endc}'
            done: str = f'{self.green}{self.imp.done}{self.endc}'
            failed: str = f'{self.red}{self.imp.failed}{self.endc}'
            installed: str = ''

            if filename.endswith(tuple(self.package_type)) and not self.option_for_reinstall:
                installed_package = self.log_packages.glob(filename[:-4])
                for inst in installed_package:
                    if inst.name == filename[:-4]:
                        installed = filename[:-4]
                        logger.debug("Found installed package matching filename: %s", installed)

            # Starting multiprocessing.
            process_1 = Process(target=self._run, args=(command,))
            process_2 = Process(target=self.progress.progress_bar, args=(progress_message, filename))
            logger.debug("Processes created: process_1 (command execution), process_2 (progress bar).")

            process_1.start()
            process_2.start()
            logger.debug("Processes started.")

            # Wait until process 1 finish.
            process_1.join()
            logger.debug("Process 1 (command execution) finished with exit code: %s", process_1.exitcode)

            # Terminate process 2 when process 1 finished.
            process_2.terminate()
            logger.debug("Process 2 (progress bar) terminated.")
            print(f"\r{' ' * (self.columns - 1)}", end='')  # Delete previous line.

            # Determine final status message for console
            if process_1.exitcode != 0:
                logger.error("Command '%s' failed with exit code %s.", command, process_1.exitcode)
                print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {failed}", end='')
            elif installed:
                logger.info("Command '%s' skipped (package already installed).", command)
                print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {skip}", end='')
            else:
                logger.info("Command '%s' completed successfully.", command)
                print(f"\r {pg_color}{progress_message:<{width}}{self.endc}: {filename} {done}", end='')

            # Restore the terminal cursor
            print('\x1b[?25h', self.endc)
            logger.debug("Terminal cursor restored.")
        else:
            logger.info("Progress bar is disabled. Running command directly without multiprocessing.")
            self._run(command)
        logger.info("process_and_log completed for filename: %s", filename)

    def _run(self, command: str, stdout: Optional[int] = subprocess.PIPE,
             stderr: Optional[int] = subprocess.STDOUT) -> None:
        """Build the package and write a log file.

        Args:
            command (str): The command of process
            stdout (Optional[int], optional): Captured stdout from the child process.
            stderr (Optional[int], optional): Captured stderr from the child process.

        Raises:
            SystemExit: Raise exit code.
        """
        logger.debug("Executing command in _run: '%s'", command)
        with subprocess.Popen(command, shell=True, stdout=stdout, stderr=stderr, text=True) as process:

            self._write_log_head()
            logger.debug("Log file header written to %s", self.process_log_file)

            # Write the process to the log file and to the terminal.
            if process.stdout:
                with process.stdout as output:
                    for line in output:
                        if not self.progress_bar:
                            print(line.strip())  # Print to console
                        if self.process_log:
                            with open(self.process_log_file, 'a', encoding='utf-8') as log:
                                log.write(line)  # Write to log file
            logger.debug("Command output processed (printed to console if no progress bar, written to log file if process_log enabled).")

            self._write_log_eof()
            logger.debug("Log file EOF marker written to %s", self.process_log_file)

            process.wait()  # Wait for the process to finish
            logger.debug("Command process finished with return code: %s", process.returncode)

            # If the process failed, return exit code.
            if process.returncode != 0:
                logger.error("Command '%s' failed with return code %s.", command, process.returncode)
                self._error_process()
                raise SystemExit(process.returncode)
        logger.debug("_run method completed for command: '%s'", command)

    def _error_process(self) -> None:
        """Print error message for a process."""
        logger.error("An error occurred in a process. Displaying user-facing error message.")
        if not self.progress_bar:
            message: str = 'Error occurred with process. Please check the log file.'
            print()
            print(len(message) * '=')
            print(f'{self.red}{message}{self.endc}')
            print(len(message) * '=')
            print()
        logger.debug("Error message displayed to console.")

    def _write_log_head(self) -> None:
        """Write the timestamp at the head of the log file."""
        if self.process_log:
            try:
                with open(self.process_log_file, 'a', encoding='utf-8') as log:
                    log.write(f"{len(self.head_message) * '='}\n")
                    log.write(f'{self.head_message}\n')
                    log.write(f"{len(self.head_message) * '='}\n")
                logger.debug("Log header successfully written to %s", self.process_log_file)
            except IOError as e:
                logger.critical("Failed to write log header to %s: %s", self.process_log_file, e, exc_info=True)

    def _write_log_eof(self) -> None:
        """Write the bottom of the log file."""
        if self.process_log:
            try:
                with open(self.process_log_file, 'a', encoding='utf-8') as log:
                    log.write(f"\n{len(self.bottom_message) * '='}\n")
                    log.write(f'{self.bottom_message}\n')
                    log.write(f"{len(self.bottom_message) * '='}\n\n")
                logger.debug("Log EOF marker successfully written to %s", self.process_log_file)
            except IOError as e:
                logger.critical("Failed to write log EOF marker to %s: %s", self.process_log_file, e, exc_info=True)

    @staticmethod
    def process(command: str, stderr: Optional[TextIOWrapper] = None, stdout: Optional[TextIOWrapper] = None) -> None:
        """Run a command to the shell.

        Args:
            command (str): The command of process
            stderr (Optional[TextIOWrapper], optional): Captured stderr from the child process.
            stdout (Optional[TextIOWrapper], optional): Captured stdout from the child process.

        Raises:
            SystemExit: Raise exit code.
        """
        logger.info("Running static process command: '%s'", command)
        try:
            # Using subprocess.run with check=False as the return code is handled explicitly below.
            output = subprocess.run(f'{command}', shell=True, stderr=stderr, stdout=stdout, check=False)
            logger.debug("Static process command '%s' completed with return code: %s", command, output.returncode)
        except KeyboardInterrupt as e:
            logger.warning("Static process command '%s' interrupted by user (KeyboardInterrupt).", command, exc_info=True)
            raise SystemExit(1) from e
        except Exception as e:
            logger.critical("An unexpected error occurred while running static process command '%s': %s", command, e, exc_info=True)
            raise SystemExit(1) from e

        if output.returncode != 0:
            logger.error("Static process command '%s' failed with exit code %s.", command, output.returncode)
            # Do not raise SystemExit for specific commands like wget/curl/lftp/aria2c
            # This logic is already present and maintained.
            if not command.startswith(('wget', 'wget2', 'curl', 'lftp', 'aria2c')):
                raise SystemExit(output.returncode)
        else:
            logger.info("Static process command '%s' executed successfully.", command)
