#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import logging
import logging.handlers
import os

try:
    from dialog import Dialog  # type: ignore # pylint: disable=[W0611]

    DIALOG_AVAILABLE = True
except ModuleNotFoundError:
    DIALOG_AVAILABLE = False


import platform
from pathlib import Path
from typing import Any, Union

import tomlkit
from tomlkit import exceptions

from slpkg.toml_errors import TomlErrors

# Determine the path for the internal config log file based on user privileges.
if not os.geteuid() == 0:
    home_config_log_path: str = os.path.expanduser('~')
    config_log_file: Path = Path(home_config_log_path, '.local/share/slpkg/config.log')
else:
    # Define the path for the internal config log file for root.
    config_log_file = Path('/var/log/slpkg/config.log')

# Ensure the parent directory for the log file exists.
config_log_file.parent.mkdir(parents=True, exist_ok=True)

# Custom logger setup for this module.
config_logger = logging.getLogger('slpkg.config_internal')
config_logger.setLevel(logging.DEBUG)  # Set the desired logging level for this logger.

# Prevent messages from this logger from propagating to the root logger.
config_logger.propagate = False

# Create a RotatingFileHandler for the custom log file.
# It will rotate the log file when it reaches 1 MB (1024 * 1024 bytes)
# and keep up to 5 backup files.
MAX_LOG_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
BACKUP_LOG_COUNT = 3
file_handler = logging.handlers.RotatingFileHandler(
    config_log_file,
    maxBytes=MAX_LOG_SIZE_BYTES,
    backupCount=BACKUP_LOG_COUNT,
    encoding='utf-8'
)

file_handler.setLevel(logging.DEBUG)  # Set the level for this specific handler.
# Define a formatter for the log messages.
formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(name)s - %(funcName)s - %(message)s')
file_handler.setFormatter(formatter)
# Add the file handler to the custom logger.
config_logger.addHandler(file_handler)


class Config:  # pylint: disable=[R0902, R0903]
    """Loads and holds configurations."""

    def __init__(self) -> None:  # pylint: disable=[R0915]
        # Initialize variables for error handling and architecture detection.
        config_logger.debug("Initialization of the Config module.")
        self.toml_errors = TomlErrors()
        self.cpu_arch: str = platform.machine()
        self.os_arch: str = platform.architecture()[0]
        config_logger.debug("Detected CPU architecture: %s, OS architecture: %s", self.cpu_arch, self.os_arch)

        # Program name.
        self.prog_name: str = 'slpkg'

        # Slpkg default utility paths.
        self.tmp_path: Path = Path('/tmp')
        self.tmp_slpkg: Path = Path(self.tmp_path, self.prog_name)
        self.build_path: Path = Path(self.tmp_path, self.prog_name, 'build')
        self.etc_path: Path = Path('/etc', self.prog_name)
        self.lib_path: Path = Path('/var/lib', self.prog_name)
        self.log_path: Path = Path('/var/log/', self.prog_name)
        self.log_packages: Path = Path('/var', 'log', 'packages')
        config_logger.debug("Default paths initialized: tmp_path=%s, etc_path=%s, lib_path=%s, log_path=%s",
                            self.tmp_path, self.etc_path, self.lib_path, self.log_path)

        # Slpkg log files.
        self.deps_log_file: Path = Path(self.log_path, 'deps.log')
        self.process_log_file: Path = Path(self.log_path, 'process.log')
        self.slpkg_log_file: Path = Path(self.log_path, 'slpkg.log')
        config_logger.debug("Log files paths initialized: deps_log_file=%s, process_log_file=%s, slpkg_log_file=%s",
                            self.deps_log_file, self.process_log_file, self.slpkg_log_file)

        # Answer yes always is False except user changes via argparse module.
        self.answer_yes: bool = False

        # Default configurations for slpkg.toml.
        # These are "fallback" values if not found in the TOML file or not set by argparse.
        self.logging_level: str = 'INFO'
        self.file_list_suffix: str = '.pkgs'
        self.package_type = [".tgz", ".txz"]
        self.installpkg: str = 'upgradepkg --install-new'
        self.reinstall: str = 'upgradepkg --reinstall'
        self.removepkg: str = 'removepkg'
        self.kernel_version: bool = True
        self.bootloader_command: str = ''
        self.colors: bool = True
        self.makeflags: str = '-j4'
        self.gpg_verification: bool = False
        self.checksum_md5: bool = True
        self.dialog: bool = False
        self.pager: str = 'most'
        self.editor: str = 'vim'
        self.terminal_selector: bool = True
        self.view_missing_deps: bool = False
        self.package_method: bool = False
        self.downgrade_packages: bool = False
        self.delete_sources: bool = False
        self.downloader: str = 'wget'
        self.wget_options: str = '-c -q --progress=bar:force:noscroll --show-progress'
        self.curl_options: str = ''
        self.aria2_options: str = '-c'
        self.lftp_get_options: str = '-c get -e'
        self.lftp_mirror_options: str = '-c mirror --parallel=100 --only-newer --delete'
        self.git_clone: str = 'git clone --depth 1'
        self.download_only_path: Union[Path, str] = Path(self.tmp_slpkg, '')  # Default to tmp_slpkg
        self.ask_question: bool = True
        self.parallel_downloads: bool = False
        self.maximum_parallel: int = 5
        self.progress_bar: bool = False
        self.progress_spinner: str = 'spinner'
        self.spinner_color: str = 'green'
        self.process_log: bool = True
        self.urllib_retries: bool = False
        self.urllib_redirect: bool = False
        self.urllib_timeout: float = 3.0
        self.proxy_address: str = ''
        self.proxy_username: str = ''
        self.proxy_password: str = ''
        config_logger.debug("Default configuration values initialized.")

        # Load configurations from the TOML file (before potential argparse override)
        self._load_config()
        # Apply static checks/adjustments based on loaded settings
        self._set_colors()  # Will apply colors based on self.colors (from TOML or default)
        self._create_paths()
        config_logger.debug("Config module initialization complete.")

    def _load_config(self) -> None:  # pylint: disable=[R0915,R0912]
        config_logger.debug("Loading configuration from TOML file.")
        # This map corresponds TOML keys (uppercase)
        # to the corresponding class attributes (lowercase)
        toml_to_attr_map = {
            'LOGGING_LEVEL': 'logging_level',
            'FILE_LIST_SUFFIX': 'file_list_suffix',
            'PACKAGE_TYPE': 'package_type',
            'INSTALLPKG': 'installpkg',
            'REINSTALL': 'reinstall',
            'REMOVEPKG': 'removepkg',
            'KERNEL_VERSION': 'kernel_version',
            'BOOTLOADER_COMMAND': 'bootloader_command',
            'COLORS': 'colors',
            'MAKEFLAGS': 'makeflags',
            'GPG_VERIFICATION': 'gpg_verification',
            'CHECKSUM_MD5': 'checksum_md5',
            'DIALOG': 'dialog',
            'PAGER': 'pager',
            'EDITOR': 'editor',
            'TERMINAL_SELECTOR': 'terminal_selector',
            'VIEW_MISSING_DEPS': 'view_missing_deps',
            'PACKAGE_METHOD': 'package_method',
            'DOWNGRADE_PACKAGES': 'downgrade_packages',
            'DELETE_SOURCES': 'delete_sources',
            'DOWNLOADER': 'downloader',
            'WGET_OPTIONS': 'wget_options',
            'CURL_OPTIONS': 'curl_options',
            'ARIA2_OPTIONS': 'aria2_options',
            'LFTP_GET_OPTIONS': 'lftp_get_options',
            'LFTP_MIRROR_OPTIONS': 'lftp_mirror_options',
            'GIT_CLONE': 'git_clone',
            'DOWNLOAD_ONLY_PATH': 'download_only_path',
            'ASK_QUESTION': 'ask_question',
            'PARALLEL_DOWNLOADS': 'parallel_downloads',
            'MAXIMUM_PARALLEL': 'maximum_parallel',
            'PROGRESS_BAR': 'progress_bar',
            'PROGRESS_SPINNER': 'progress_spinner',
            'SPINNER_COLOR': 'spinner_color',
            'PROCESS_LOG': 'process_log',
            'URLLIB_RETRIES': 'urllib_retries',
            'URLLIB_REDIRECT': 'urllib_redirect',
            'URLLIB_TIMEOUT': 'urllib_timeout',
            'PROXY_ADDRESS': 'proxy_address',
            'PROXY_USERNAME': 'proxy_username',
            'PROXY_PASSWORD': 'proxy_password',
        }

        # Type map for validation
        config_types = {
            'LOGGING_LEVEL': (str,),
            'FILE_LIST_SUFFIX': (str,),
            'PACKAGE_TYPE': (list,),
            'INSTALLPKG': (str,),
            'REINSTALL': (str,),
            'REMOVEPKG': (str,),
            'KERNEL_VERSION': (bool,),
            'BOOTLOADER_COMMAND': (str,),
            'COLORS': (bool,),
            'MAKEFLAGS': (str,),
            'GPG_VERIFICATION': (bool,),
            'CHECKSUM_MD5': (bool,),
            'DIALOG': (bool,),
            'PAGER': (str,),
            'EDITOR': (str,),
            'TERMINAL_SELECTOR': (bool,),
            'VIEW_MISSING_DEPS': (bool,),
            'PACKAGE_METHOD': (bool,),
            'DOWNGRADE_PACKAGES': (bool,),
            'DELETE_SOURCES': (bool,),
            'DOWNLOADER': (str,),
            'WGET_OPTIONS': (str,),
            'CURL_OPTIONS': (str,),
            'ARIA2_OPTIONS': (str,),
            'LFTP_GET_OPTIONS': (str,),
            'LFTP_MIRROR_OPTIONS': (str,),
            'GIT_CLONE': (str,),
            'DOWNLOAD_ONLY_PATH': (str, Path),
            'ASK_QUESTION': (bool,),
            'PARALLEL_DOWNLOADS': (bool,),
            'MAXIMUM_PARALLEL': (int,),
            'PROGRESS_BAR': (bool,),
            'PROGRESS_SPINNER': (str,),
            'SPINNER_COLOR': (str,),
            'PROCESS_LOG': (bool,),
            'URLLIB_RETRIES': (bool,),
            'URLLIB_REDIRECT': (bool,),
            'URLLIB_TIMEOUT': (int, float),
            'PROXY_ADDRESS': (str,),
            'PROXY_USERNAME': (str,),
            'PROXY_PASSWORD': (str,),
        }

        config_path_file: Path = Path(self.etc_path, f'{self.prog_name}.toml')
        conf: dict[str, dict[str, Any]] = {}
        toml_setting_name: str = ''
        try:
            if config_path_file.exists():
                config_logger.debug("Configuration file found at: %s", config_path_file)
                with open(config_path_file, 'r', encoding='utf-8') as file:
                    conf = tomlkit.parse(file.read())
                config_logger.info("Successfully parsed configuration file: %s", config_path_file)
            else:
                config_logger.warning("Configuration file not found at: %s. Using default settings.", config_path_file)
                # print is removed for this case as per previous request to keep console clear if not an error

            if conf and 'CONFIGS' in conf:
                self.config = conf['CONFIGS']  # Store settings from TOML
                config_logger.debug("Found 'CONFIGS' section in TOML file.")

                error_type = False
                error_key = False
                keys_not_found = []
                for toml_key, attr_name in toml_to_attr_map.items():
                    if toml_key in self.config:  # Check if key exists in TOML
                        value = self.config[toml_key]
                        expected_type = config_types[toml_key]

                        # Special handling for DOWNLOAD_ONLY_PATH: convert string to Path
                        if toml_key == 'DOWNLOAD_ONLY_PATH' and isinstance(value, str):
                            value = Path(value)
                            config_logger.debug("Converted DOWNLOAD_ONLY_PATH from string to Path: %s", value)

                        # Type checking (if it's a Union (e.g., (str, Path)), check all types)
                        # Check if the value's type is among the expected types
                        if not isinstance(value, expected_type):
                            error_type = True
                            toml_setting_name = toml_key
                            config_logger.error("Type mismatch for TOML setting '%s'. Expected %s, got %s. Value: %s",
                                                toml_key, expected_type, type(value), value)
                            break  # Exit loop on first type error

                        # If no type error, assign the value to the class attribute
                        setattr(self, attr_name, value)
                        config_logger.debug("Set config '%s' to value '%s' (from TOML).", attr_name, value)
                    else:
                        error_key = True
                        keys_not_found.append(toml_key)

                if error_key:
                    config_logger.warning("TOML setting '%s' not found in config file. Using default value.", keys_not_found)
                    print(f"Important notification: Unable to find '{', '.join(keys_not_found)}' settings in your current configurations. "
                          f"This issue may arise after an '{self.prog_name}' upgrade. To resolve this issue, please run:\n"
                          f"\n{'':>4}$ slpkg_new-configs\n"
                          "\nDefault settings are currently in use.\n")

                if error_type:  # If a type error was found, print a message
                    print(f"{self.prog_name}: Error: Setting '{toml_setting_name}' in configurations contain wrong type.\n"
                          f"Default configurations are used.\n")
                    config_logger.error("Configuration loading aborted due to type error in setting '%s'. Using default values for remaining settings.", toml_setting_name)
                else:
                    config_logger.info("All configurations from TOML file processed successfully.")
            else:
                config_logger.warning("No 'CONFIGS' section found in %s or file is empty. Using default settings.", config_path_file)

        except (KeyError, exceptions.TOMLKitError) as e:
            config_logger.critical("Failed to parse or access required key in %s. Error: %s", config_path_file, e, exc_info=True)
            self.toml_errors.raise_toml_error_message(str(e), config_path_file)
            print('The default configurations are used.\n')  # This print is user-facing, kept.
            # sys.exit(1) is handled by toml_errors.raise_toml_error_message

        # If the dialog module is not available, disable dialog regardless of TOML setting.
        if not DIALOG_AVAILABLE:
            if self.dialog:  # Only log if it was previously enabled.
                config_logger.warning("Python 'dialog' module is not available. Forcing self.dialog to False.")
            self.dialog = False
        config_logger.debug("Dialog status after check: %s", self.dialog)

    def update_from_args(self, args: argparse.Namespace) -> None:
        """
        Updates configuration settings based on parsed argparse arguments.
        This method should be called from main.py after arguments are parsed.
        """
        config_logger.debug("Updating configurations from argparse arguments: %s", args)
        if hasattr(args, 'option_color') and args.option_color is not None:  # Check for None to allow explicit --color=off.
            # argparse might pass 'on', 'off', True, False. Normalize to boolean.
            self.colors = str(args.option_color).lower() == 'on' or args.option_color is True
            self._set_colors()  # Reapply color settings if changed.
            config_logger.info("Colors updated from args to: %s", self.colors)

        if hasattr(args, 'option_dialog') and args.option_dialog is not None:
            self.dialog = args.option_dialog
            if not DIALOG_AVAILABLE:  # Ensure it respects DIALOG_AVAILABLE.
                if self.dialog:  # Only log if it's being overridden.
                    config_logger.warning("Attempted to enable dialog via argparse, but 'dialog' module is not available. Forcing self.dialog to False.")
                self.dialog = False
            config_logger.info("Dialog updated from args to: %s", self.dialog)

        if hasattr(args, 'option_parallel') and args.option_parallel is not None:
            self.parallel_downloads = args.option_parallel
            config_logger.info("Parallel downloads updated from args to: %s", self.parallel_downloads)

        if hasattr(args, 'option_progress_bar') and args.option_progress_bar is not None:
            self.progress_bar = args.option_progress_bar
            config_logger.info("Progress bar updated from args to: %s", self.progress_bar)

        if hasattr(args, 'option_yes') and args.option_yes is not None:
            self.answer_yes = args.option_yes
            config_logger.info("Answer 'yes' updated from args to: %s", self.answer_yes)
        config_logger.debug("Configuration update from argparse complete.")

    def _set_colors(self) -> None:
        config_logger.debug("Setting terminal color codes.")
        # Reset color codes
        self.back_white: str = ''
        self.back_grey = ''
        self.bold: str = ''
        self.white: str = ''
        self.black: str = ''
        self.red: str = ''
        self.green: str = ''
        self.yellow: str = ''
        self.cyan: str = ''
        self.grey: str = ''
        self.endc: str = ''

        # Apply colors only if self.colors is True
        if self.colors:
            self.back_white = '\x1b[107m'
            self.back_grey = '\x1b[48;5;234m'
            self.bold = '\x1b[1m'
            self.white = '\x1b[37m'
            self.black = '\x1b[30m'
            self.red = '\x1b[91m'
            self.green = '\x1b[32m'
            self.yellow = '\x1b[93m'
            self.cyan = '\x1b[96m'
            self.grey = '\x1b[90m'
            self.endc = '\x1b[0m'
            config_logger.debug("Terminal colors enabled and set.")
        else:
            config_logger.debug("Terminal colors disabled. Color codes are empty strings.")

    def _create_paths(self) -> None:
        config_logger.debug("Creating necessary application paths.")
        if not os.geteuid() == 0:
            home_path: str = os.path.expanduser('~')
            home_log: Path = Path(home_path, '.local', 'share', self.prog_name)
            home_log.mkdir(parents=True, exist_ok=True)
            self.slpkg_log_file = Path(home_log, 'slpkg.log')
            config_logger.info("Running as non-root. Log file redirected to user home: %s", self.slpkg_log_file)

        paths = [
            self.lib_path,
            self.etc_path,
            self.build_path,
            self.tmp_slpkg,
            self.log_path,
            # Ensure download_only_path is a Path object before adding to list
            Path(self.download_only_path) if isinstance(self.download_only_path, str) else self.download_only_path,
        ]
        for path in paths:
            try:
                if not path.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                    config_logger.debug("Created directory: %s", path)
                else:
                    config_logger.debug("Directory already exists: %s", path)
            except OSError as e:
                config_logger.error("Failed to create directory '%s': %s", path, e)
        config_logger.debug("All necessary paths checked/created.")

    def is_64bit(self) -> bool:
        """Determines the CPU and the OS architecture.

        Returns:
            bool: True if the system is 64-bit, False otherwise.
        """
        is_64 = self.cpu_arch in {'x86_64', 'amd64', 'aarch64', 'arm64', 'ia64'} and self.os_arch == '64bit'
        config_logger.debug("System architecture check: CPU='%s', OS='%s'. Is 64-bit: %s", self.cpu_arch, self.os_arch, is_64)
        return is_64


# Creating a unique instance of the Config class.
# This instance will be loaded by any module that imports 'config'.
# It contains default settings and settings from TOML (if config.toml exists in /etc/slpkg).
config_load = Config()
