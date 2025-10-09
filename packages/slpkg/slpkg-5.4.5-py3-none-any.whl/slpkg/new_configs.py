#!/usr/bin/python3
# -*- coding: utf-8 -*-


import argparse
import difflib
import logging
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

import tomlkit
from tomlkit import items

# --- Logging Setup for new_configs.py ---
# This script always runs as root.
log_file: Path = Path('/var/log/slpkg/new_configs.log')
slpkg_toml_path: Path = Path('/etc/slpkg/slpkg.toml')

# Ensure the parent directory for the log file exists.
log_file.parent.mkdir(parents=True, exist_ok=True)

# Determine LOGGING_LEVEL from slpkg.toml
CONFIGURED_LOGGING_LEVEL = logging.INFO  # Default fallback level.

try:
    if slpkg_toml_path.exists():
        with open(slpkg_toml_path, 'r', encoding='utf-8') as f:
            config_data = tomlkit.parse(f.read())

        # Check if 'CONFIGS' exists and is a Table (for mypy type inference).
        if 'CONFIGS' in config_data and isinstance(config_data['CONFIGS'], items.Table):
            configs_table = config_data['CONFIGS']  # Assign to a variable with a known type.
            if 'LOGGING_LEVEL' in configs_table:
                LEVEL_STR = str(configs_table['LOGGING_LEVEL']).upper()
                # Convert string level to logging level constant
                LEVEL_INT = getattr(logging, LEVEL_STR, None)
                if isinstance(LEVEL_INT, int):
                    CONFIGURED_LOGGING_LEVEL = LEVEL_INT
except Exception as e:  # pylint: disable=[W0718]
    # Catch any parsing errors and fall back to default
    print(f"Error parsing {slpkg_toml_path} for logging level: {e}. Using default INFO for logging.", file=sys.stderr)
    CONFIGURED_LOGGING_LEVEL = logging.INFO

# Initialize Logging Configuration using basicConfig
# This will log to the determined file path, at the level read from slpkg.toml, and append to it.
logging.basicConfig(
    filename=log_file,
    level=CONFIGURED_LOGGING_LEVEL,  # Use the level read from TOML or default.
    format='%(levelname)s: %(asctime)s - %(name)s - %(funcName)s - %(message)s',
    filemode='a'  # Append to the log file each time the script runs.
)

# Get a logger instance for this module after basicConfig is set up.
logger = logging.getLogger(__name__)

logger.info("new_configs.py script started. Logging initialized.")
logger.debug("Log file path: %s", log_file)
logger.info("Logging level set to: %s (from %s)", logging.getLevelName(CONFIGURED_LOGGING_LEVEL), slpkg_toml_path)
# --- End of Logging Setup ---


class NewConfigs:  # pylint: disable=[R0902]
    """Tool that manage the config files."""

    def __init__(self, no_colors: bool = False) -> None:
        logger.debug("Initializing NewConfigs instance.")
        self.etc_path: Path = Path('/etc/slpkg')
        self.slpkg_config: Path = Path(self.etc_path, 'slpkg.toml')
        self.repositories_config: Path = Path(self.etc_path, 'repositories.toml')
        self.blacklist_config: Path = Path(self.etc_path, 'blacklist.toml')
        self.slpkg_config_new: Path = Path(self.etc_path, 'slpkg.toml.new')
        self.repositories_config_new: Path = Path(self.etc_path, 'repositories.toml.new')
        self.blacklist_config_new: Path = Path(self.etc_path, 'blacklist.toml.new')
        logger.debug("Config file paths initialized.")

        self.bold: str = '\033[1m'
        self.red: str = '\x1b[91m'
        self.green: str = '\x1b[32m'
        self.bgreen: str = f'{self.bold}{self.green}'
        self.yellow: str = '\x1b[93m'
        self.byellow: str = f'{self.bold}{self.yellow}'
        self.endc: str = '\x1b[0m'

        if no_colors:
            self.set_no_colors()
            logger.info("Colors disabled via --no-colors argument.")

        self.choice = None
        logger.debug("NewConfigs initialization complete.")

    def set_no_colors(self) -> None:
        """Switch off colors."""
        logger.debug("Setting no colors.")
        self.bold = ''
        self.red = ''
        self.green = ''
        self.bgreen = ''
        self.yellow = ''
        self.byellow = ''
        self.endc = ''

    def check(self) -> None:
        """Check for .new files."""
        logger.info("Checking for NEW configuration files.")
        print('Checking for NEW configuration files...\n')

        has_new_files = (self.slpkg_config_new.is_file()
                         or self.blacklist_config_new.is_file()
                         or self.repositories_config_new.is_file())

        if has_new_files:
            logger.info("New configuration files found.")
            print('There are NEW files:\n')

            if self.slpkg_config_new.is_file():
                logger.info("Found: %s", self.slpkg_config_new)
                print(f"{self.bgreen:>12}{self.slpkg_config_new}{self.endc}")

            if self.repositories_config_new.is_file():
                logger.info("Found: %s", self.repositories_config_new)
                print(f"{self.bgreen:>12}{self.repositories_config_new}{self.endc}")

            if self.blacklist_config_new.is_file():
                logger.info("Found: %s", self.blacklist_config_new)
                print(f"{self.bgreen:>12}{self.blacklist_config_new}{self.endc}")

            print(f'\nWhat would you like to do ({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                  f'{self.byellow}R{self.endc}/{self.byellow}P{self.endc})?\n')

            print(f"{'':>2}({self.byellow}K{self.endc})eep the old files and consider '.new' files later.\n"
                  f"{'':>2}({self.byellow}O{self.endc})verwrite all old files with the new ones.\n"
                  f"{'':>5}The old files will be stored with the suffix '.orig'.\n"
                  f"{'':>2}({self.byellow}R{self.endc})emove all '.new' files.\n"
                  f"{'':>2}({self.byellow}P{self.endc})rompt K, O, R, D, V selection for every single file.\n")

            self.menu()

        else:
            logger.info("No .new files found.")
            print(f"\n{'No .new files found.':>23}\n")

    def menu(self) -> None:
        """Menu of choices."""
        choice: str = input('Choice: ')
        logger.debug("User choice: '%s'", choice)

        choice = choice.lower()

        arguments: dict[str, Callable[..., None]] = {
            'k': self.keep,
            'o': self.overwrite,
            'r': self.remove,
            'p': self.prompt
        }

        try:
            arguments[choice]()
        except KeyError:
            logger.warning("Invalid choice '%s'. Defaulting to 'Keep'.", choice)
            self.keep()

    @staticmethod
    def keep() -> None:
        """Print a message."""
        logger.info("User chose to keep existing files. No changes made.")
        print("\nNo changes were made.\n")

    def overwrite(self) -> None:
        """Copy the .new files and rename the olds to .orig."""
        logger.info("Starting overwrite process for new config files.")

        if self.slpkg_config_new.is_file():
            self.overwrite_config_file()

        if self.repositories_config_new.is_file():
            self.overwrite_repositories_file()

        if self.blacklist_config_new.is_file():
            self.overwrite_blacklist_file()

        print()  # new line - Keep for formatting console output

    def overwrite_config_file(self) -> None:
        """Copy the slpkg.toml.new file and rename the old to .orig."""
        logger.debug("Overwriting slpkg.toml with slpkg.toml.new.")
        try:
            if self.slpkg_config.is_file():
                shutil.copy(self.slpkg_config, f"{self.slpkg_config}.orig")
                logger.info("Backed up %s to %s.orig", self.slpkg_config, self.slpkg_config)
                print(f"\ncp {self.green}{self.slpkg_config}{self.endc} -> {self.slpkg_config}.orig")

            shutil.move(self.slpkg_config_new, self.slpkg_config)
            logger.info("Moved %s to %s", self.slpkg_config_new, self.slpkg_config)
            print(f"mv {self.slpkg_config_new} -> {self.green}{self.slpkg_config}{self.endc}")
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to overwrite %s: %s", self.slpkg_config, e, exc_info=True)
            print(f"{self.red}Error overwriting {self.slpkg_config}: {e}{self.endc}")

    def overwrite_repositories_file(self) -> None:
        """Copy the repositories.toml.new file and rename the old to .orig."""
        logger.debug("Overwriting repositories.toml with repositories.toml.new.")
        try:
            if self.repositories_config.is_file():
                shutil.copy(self.repositories_config, f"{self.repositories_config}.orig")
                logger.info("Backed up %s to %s.orig", self.repositories_config, self.repositories_config)
                print(f"\ncp {self.green}{self.repositories_config}{self.endc} -> {self.repositories_config}.orig")

            shutil.move(self.repositories_config_new, self.repositories_config)
            logger.info("Moved %s to %s", self.repositories_config_new, self.repositories_config)
            print(f"mv {self.repositories_config_new} -> {self.green}{self.repositories_config}{self.endc}")
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to overwrite %s: %s", self.repositories_config, e, exc_info=True)
            print(f"{self.red}Error overwriting {self.repositories_config}: {e}{self.endc}")

    def overwrite_blacklist_file(self) -> None:
        """Copy the blacklist.toml.new file and rename the old to .orig."""
        logger.debug("Overwriting blacklist.toml with blacklist.toml.new.")
        try:
            if self.blacklist_config.is_file():
                shutil.copy(self.blacklist_config, f"{self.blacklist_config}.orig")
                logger.info("Backed up %s to %s.orig", self.blacklist_config, self.blacklist_config)
                print(f"\ncp {self.green}{self.blacklist_config}{self.endc} -> {self.blacklist_config}.orig")

            shutil.move(self.blacklist_config_new, self.blacklist_config)
            logger.info("Moved %s to %s", self.blacklist_config_new, self.blacklist_config)
            print(f"mv {self.blacklist_config_new} -> {self.green}{self.blacklist_config}{self.endc}")
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to overwrite %s: %s", self.blacklist_config, e, exc_info=True)
            print(f"{self.red}Error overwriting {self.blacklist_config}: {e}{self.endc}")

    def remove(self) -> None:
        """Remove the .new files."""
        logger.info("Starting removal process for new config files.")
        print()
        self.remove_config_new_file()
        self.remove_repositories_new_file()
        self.remove_blacklist_new_file()
        print()

    def remove_config_new_file(self) -> None:
        """Remove slpkg.toml.new file."""
        logger.debug("Attempting to remove %s", self.slpkg_config_new)
        try:
            if self.slpkg_config_new.is_file():
                self.slpkg_config_new.unlink()
                logger.info("Removed file: %s", self.slpkg_config_new)
                print(f"rm {self.red}{self.slpkg_config_new}{self.endc}")
        except OSError as e:
            logger.error("Failed to remove %s: %s", self.slpkg_config_new, e, exc_info=True)
            print(f"{self.red}Error removing {self.slpkg_config_new}: {e}{self.endc}")

    def remove_repositories_new_file(self) -> None:
        """Remove repositories.toml.new file."""
        logger.debug("Attempting to remove %s", self.repositories_config_new)
        try:
            if self.repositories_config_new.is_file():
                self.repositories_config_new.unlink()
                logger.info("Removed file: %s", self.repositories_config_new)
                print(f"rm {self.red}{self.repositories_config_new}{self.endc}")
        except OSError as e:
            logger.error("Failed to remove %s: %s", self.repositories_config_new, e, exc_info=True)
            print(f"{self.red}Error removing {self.repositories_config_new}: {e}{self.endc}")

    def remove_blacklist_new_file(self) -> None:
        """Remove blacklist.toml.new file."""
        logger.debug("Attempting to remove %s", self.blacklist_config_new)
        try:
            if self.blacklist_config_new.is_file():
                self.blacklist_config_new.unlink()
                logger.info("Removed file: %s", self.blacklist_config_new)
                print(f"rm {self.red}{self.blacklist_config_new}{self.endc}")
        except OSError as e:
            logger.error("Failed to remove %s: %s", self.blacklist_config_new, e, exc_info=True)
            print(f"{self.red}Error removing {self.blacklist_config_new}: {e}{self.endc}")

    def prompt(self) -> None:
        """Prompt K, O, R selection for every single file."""
        logger.info("Starting interactive prompt for new config files.")
        print(f"\n{'':>2}({self.byellow}K{self.endc})eep, ({self.byellow}O{self.endc})verwrite, "
              f"({self.byellow}R{self.endc})emove, ({self.byellow}D{self.endc})iff, "
              f"({self.byellow}V{self.endc})imdiff\n")

        if self.slpkg_config_new.is_file():
            self.prompt_slpkg_config()

        if self.repositories_config_new.is_file():
            self.prompt_repositories_config()

        if self.blacklist_config_new.is_file():
            self.prompt_blacklist_config()

    def prompt_slpkg_config(self) -> None:
        """Prompt for slpkg.toml file."""
        logger.debug("Prompting for %s", self.slpkg_config_new)
        make: str = input(f'{self.bgreen}{self.slpkg_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')
        logger.debug("User action for %s: %s", self.slpkg_config_new, make.lower())

        if make.lower() == 'k':
            logger.info("User chose to keep %s", self.slpkg_config_new)
        elif make.lower() == 'o':
            self.overwrite_config_file()
            print()  # new line
        elif make.lower() == 'r':
            print()  # new line
            self.remove_config_new_file()
            print()  # new line
        elif make.lower() == 'd':
            self.diff_files(self.slpkg_config_new, self.slpkg_config)
            self.prompt_slpkg_config()
        elif make.lower() == 'v':
            self.vimdiff(self.slpkg_config_new, self.slpkg_config)
            self.prompt_slpkg_config()
        else:
            logger.warning("Invalid input for %s: '%s'. Keeping file by default.", self.slpkg_config_new, make)

    def prompt_repositories_config(self) -> None:
        """Prompt for repositories.toml file."""
        logger.debug("Prompting for %s", self.repositories_config_new)
        make: str = input(f'{self.bgreen}{self.repositories_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')
        logger.debug("User action for %s: %s", self.repositories_config_new, make.lower())

        if make.lower() == 'k':
            logger.info("User chose to keep %s", self.repositories_config_new)
        elif make.lower() == 'o':
            self.overwrite_repositories_file()
            print()  # new line
        elif make.lower() == 'r':
            print()  # new line
            self.remove_repositories_new_file()
            print()  # new line
        elif make.lower() == 'd':
            self.diff_files(self.repositories_config_new, self.repositories_config)
            self.prompt_repositories_config()
        elif make.lower() == 'v':
            self.vimdiff(self.repositories_config_new, self.repositories_config)
            self.prompt_repositories_config()
        else:
            logger.warning("Invalid input for %s: '%s'. Keeping file by default.", self.repositories_config_new, make)

    def prompt_blacklist_config(self) -> None:
        """Prompt for blacklist.toml file."""
        logger.debug("Prompting for %s", self.blacklist_config_new)
        make: str = input(f'{self.bgreen}{self.blacklist_config_new}{self.endc} - '
                          f'({self.byellow}K{self.endc}/{self.byellow}O{self.endc}/'
                          f'{self.byellow}R{self.endc}/{self.byellow}D{self.endc}/'
                          f'{self.byellow}V{self.endc}): ')
        logger.debug("User action for %s: %s", self.blacklist_config_new, make.lower())

        if make.lower() == 'k':
            logger.info("User chose to keep %s", self.blacklist_config_new)
        elif make.lower() == 'o':
            self.overwrite_blacklist_file()
            print()  # new line
        elif make.lower() == 'r':
            print()  # new line
            self.remove_blacklist_new_file()
            print()  # new line
        elif make.lower() == 'd':
            self.diff_files(self.blacklist_config_new, self.blacklist_config)
            self.prompt_blacklist_config()
        elif make.lower() == 'v':
            self.vimdiff(self.blacklist_config_new, self.blacklist_config)
            self.prompt_blacklist_config()
        else:
            logger.warning("Invalid input for %s: '%s'. Keeping file by default.", self.blacklist_config_new, make)

    @staticmethod
    def diff_files(file2: Path, file1: Path) -> None:
        """Diff the .new and the current file."""
        logger.info("Performing diff between %s and %s", file1, file2)
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                with open(file2, 'r', encoding='utf-8') as f2:
                    diff = difflib.context_diff(
                        f1.readlines(),
                        f2.readlines(),
                        fromfile=str(file1),
                        tofile=str(file2)
                    )
                    for line in diff:
                        print(line, end='')
            logger.info("Diff completed successfully.")
        except FileNotFoundError as e:
            logger.error("One of the files not found for diffing: %s (Files: %s, %s)", e, file1, file2, exc_info=True)
            print(f"Error: One of the files not found for diffing: {e}")

    @staticmethod
    def vimdiff(file1: Path, file2: Path) -> None:
        """Show vimdiff command.

        Args:
            file1 (Any): First file.
            file2 (Any): Second file.

        Raises:
            SystemExit: Raise exit code.
        """
        logger.info("Attempting to open vimdiff for %s and %s", file1, file2)
        try:
            # Using subprocess.run with check=True is generally safer than subprocess.call
            # It raises CalledProcessError if the command returns a non-zero exit code.
            subprocess.run(['vimdiff', str(file1), str(file2)], check=True)
            logger.info("vimdiff command executed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error("vimdiff command failed with exit code %d: %s", e.returncode, e, exc_info=True)
            print(f"Error running vimdiff: Command failed with exit code {e.returncode}")
            raise SystemExit(e.returncode) from e
        except FileNotFoundError as e:
            logger.error("vimdiff command not found. Please ensure vim is installed and in your PATH.", exc_info=True)
            print("Error: 'vimdiff' command not found. Please ensure vim is installed and in your PATH.")
            raise SystemExit(1) from e
        except Exception as e:
            logger.critical("An unexpected error occurred while running vimdiff: %s", e, exc_info=True)
            print(f"An unexpected error occurred: {e}")
            raise SystemExit(1) from e


def main() -> None:
    """Manage arguments."""
    parser = argparse.ArgumentParser(
        description='Tool to manage slpkg configuration files (.new files).',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--no-colors',
        action='store_true',
        help='Disable the output colors'
    )

    args = parser.parse_args()

    try:
        config = NewConfigs(no_colors=args.no_colors)
        config.check()
    except (KeyboardInterrupt, EOFError):
        logger.info("Operation cancelled by user (KeyboardInterrupt/EOFError).")
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:  # pylint: disable=[W0718]
        logger.critical("An unexpected error occurred in main execution: %s", e, exc_info=True)
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
