#!/usr/bin/python3
# -*- coding: utf-8 -*-

# pylint: disable=[C0302]

import argparse
import logging
import os
import re
import sys
import time
from pathlib import Path
from signal import SIG_DFL, SIGPIPE, signal
from typing import Any, Callable, NoReturn, Union

from slpkg.binaries.install import Packages
from slpkg.changelog import Changelog
from slpkg.check_updates import CheckUpdates
from slpkg.choose_packages import Choose
from slpkg.cleanings import Cleanings
from slpkg.config import config_load
from slpkg.config_editor import FormConfigs
from slpkg.dependees import Dependees
from slpkg.download_only import DownloadOnly
from slpkg.errors import Errors
from slpkg.list_installed import ListInstalled
from slpkg.load_data import LoadData
from slpkg.multi_process import MultiProcess
from slpkg.package_validator import PackageValidator
from slpkg.remove_packages import RemovePackages
from slpkg.repo_info import RepoInfo
from slpkg.repositories import Repositories
from slpkg.sbos.slackbuild import Slackbuilds
from slpkg.search import SearchPackage
from slpkg.self_check import check_self_update
from slpkg.tracking import Tracking
from slpkg.update_repositories import UpdateRepositories
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.info_package import InfoPackage
from slpkg.views.version import Version
from slpkg.views.views import View

# Ignore broken pipe errors when piping output to other commands (e.g., `slpkg list | head`).
signal(SIGPIPE, SIG_DFL)


# This option allows users to directly set the logging level to DEBUG from the command line,
# overriding any logging_level configuration specified in slpkg.toml.
if '--debug' in sys.argv[1:] or '-d' in sys.argv[1:]:
    LOGGING_LEVEL = getattr(logging, 'DEBUG', logging.INFO)
else:
    # --- Global Logging Configuration for the entire application ---
    # Determine LOGGING_LEVEL from config_load (which reads from slpkg.toml).
    # This needs to happen before config_load.update_from_args is called,
    # as update_from_args might also log.
    LOGGING_LEVEL = getattr(logging, config_load.logging_level, logging.INFO)

# Validate the retrieved logging level. If invalid, default to INFO.
if not isinstance(LOGGING_LEVEL, int):
    print(f"Warning: Invalid log level '{config_load.logging_level}' in config. Using INFO.", file=sys.stderr)
    LOGGING_LEVEL = logging.INFO

# Configure the root logger. This setup will apply to all loggers created with getLogger(__name__).
# The log file will be overwritten each time the script starts (filemode='w').
logging.basicConfig(filename=config_load.slpkg_log_file,
                    level=LOGGING_LEVEL,
                    format='%(levelname)s: %(asctime)s - %(name)s - %(funcName)s - %(message)s',
                    filemode='w')

# Initialize the logger for the main module.
logger = logging.getLogger(__name__)
logger.info("slpkg application started. Logging initialized to level: %s (file: %s)",
            logging.getLevelName(LOGGING_LEVEL), config_load.slpkg_log_file)
# --- End of Global Logging Configuration ---


class Run:  # pylint: disable=[R0902]
    """Run main slpkg methods."""

    def __init__(self, options: dict[str, Any], repository: str) -> None:
        logger.debug("Initializing Run class with options: %s, repository: %s", options, repository)
        self.options = options
        self.repos = Repositories()

        self.repository = repository
        if not repository:
            self.repository = self.repos.default_repository
            logger.debug("No repository specified, defaulting to: %s", self.repository)
        else:
            logger.debug("Using specified repository: %s", self.repository)

        # Access config_load attributes directly as they are updated globally
        self.logging_level = config_load.logging_level
        self.prog_name = config_load.prog_name
        self.tmp_slpkg = config_load.tmp_slpkg
        self.file_list_suffix = config_load.file_list_suffix
        self.bootloader_command = config_load.bootloader_command
        self.red = config_load.red
        self.green = config_load.green
        self.endc = config_load.endc

        self.utils = Utilities()
        self.multi_process = MultiProcess(options=self.options)
        self.views = View(options=self.options)

        self.data: dict[str, dict[str, str]] = {}

        self.load_data = LoadData()

        self.pkg_validator = PackageValidator()
        self.choose = Choose(self.options, self.repository)
        logger.debug("Run class initialization complete.")

    def is_file_list_packages(self, packages: list[str]) -> list[str]:
        """Check for filelist.pkgs file.

        Args:
            packages (list[str]): List of packages.

        Returns:
            list[str]: List of packages for a file.
        """
        logger.debug("Checking if package list contains a file list: %s", packages)
        if packages and packages[0].endswith(self.file_list_suffix):
            file = Path(packages[0])
            logger.info("Detected package list file: %s", file)
            file_packages: list[str] = list(self.utils.read_packages_from_file(file))
            logger.debug("Packages read from file '%s': %s", file, file_packages)
            return file_packages
        logger.debug("Package list does not contain a file list. Returning original packages.")
        return packages

    @staticmethod
    def is_root() -> None:
        """Checking for root privileges."""
        logger.debug("Checking for root privileges.")
        if not os.geteuid() == 0:
            logger.critical("Application must be run as root. Current UID: %s", os.geteuid())
            sys.exit('Must run as root.')
        logger.debug("Root privileges confirmed.")

    def update(self) -> NoReturn:
        """Update the local repositories."""
        logger.info("Executing 'update' command.")
        self.is_root()

        if self.options.get('option_check'):
            logger.info("Running update in check mode.")
            check = CheckUpdates(self.options, self.repository)
            check.updates()
        else:
            logger.info("Starting full repository update.")
            start: float = time.time()
            update = UpdateRepositories(self.options, self.repository)
            update.repositories()
            elapsed_time: float = time.time() - start
            self.utils.finished_time(elapsed_time)
            logger.info("Repository update completed in %.2f seconds.", elapsed_time)
        sys.exit(0)

    def upgrade(self) -> NoReturn:  # pylint: disable=[R0912,R0915]
        """Upgrade the installed packages."""
        logger.info("Executing 'upgrade' command for repository: %s", self.repository)
        self.is_root()
        command: str = Run.upgrade.__name__
        removed: list[str] = []
        added: list[str] = []
        ordered: bool = True
        kernel_generic_current_package: str = self.utils.is_package_installed('kernel-generic')
        logger.debug("Current kernel-generic package: %s", kernel_generic_current_package)

        if self.options.get('option_check'):
            logger.info("Running upgrade in check mode.")
            self.data = self.load_data.load(self.repository)
            upgrade = Upgrade(self.repository, self.data)
            upgrade.check_packages()

        elif self.repository != '*':
            logger.info("Performing upgrade for specific repository: %s", self.repository)
            self.data = self.load_data.load(self.repository)
            upgrade = Upgrade(self.repository, self.data)
            packages: list[str] = list(upgrade.packages())
            logger.debug("Initial packages for upgrade: %s", packages)

            for package in packages:
                if package.endswith('_Removed.'):
                    removed.append(package.replace('_Removed.', ''))
                    logger.debug("Identified package for removal: %s", package.replace('_Removed.', ''))
                if package.endswith('_Added.'):
                    added.append(package.replace('_Added.', ''))
                    logger.debug("Identified package for addition: %s", package.replace('_Added.', ''))

            # Remove packages that not exists in the repository.
            if removed:
                logger.info("Initiating removal of %d packages.", len(removed))
                packages = [pkg for pkg in packages if not pkg.endswith('_Removed.')]
                remove = RemovePackages(removed, self.options)
                remove.remove(upgrade=True)
                logger.info("Packages removed during upgrade process.")

            if added:
                logger.info("Initiating addition of %d new packages.", len(added))
                packages = sorted([pkg for pkg in packages if not pkg.endswith('_Added.')])
                packages = added + packages
                ordered = False
                logger.debug("Combined added and upgradeable packages: %s", packages)

            packages = self.choose.packages(self.data, packages, command, ordered)
            logger.debug("Packages selected after user choice: %s", packages)

            if not packages:
                logger.info("No packages selected for upgrade. Exiting.")
                print('\nEverything is up-to-date!\n')
                sys.exit(0)

            if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                logger.info("Installing binary packages for upgrade.")
                install_bin = Packages(self.repository, self.data, packages, self.options, mode=command)
                install_bin.execute()
            else:
                logger.info("Installing SlackBuilds for upgrade.")
                install_sbo = Slackbuilds(self.repository, self.data, packages, self.options, mode=command)
                install_sbo.execute()

            self._is_kernel_upgrade(kernel_generic_current_package)

        sys.exit(0)

    def _is_kernel_upgrade(self, kernel_generic_current_package: str) -> None:
        """Compare current and installed kernel package."""
        logger.debug("Checking for kernel upgrade. Old kernel-generic: %s", kernel_generic_current_package)
        kernel_generic_new_package: str = self.utils.is_package_installed('kernel-generic')
        logger.debug("New kernel-generic package: %s", kernel_generic_new_package)
        if kernel_generic_current_package != kernel_generic_new_package:
            logger.info("Kernel-generic package has been upgraded.")
            if self.bootloader_command:
                logger.info("Bootloader command is configured: '%s'. Prompting user to run.", self.bootloader_command)
                self._bootloader_update()
            else:
                logger.info("Bootloader command not configured. Displaying manual kernel update message.")
                self._kernel_image_message()

    def _kernel_image_message(self) -> None:
        """Print a warning kernel upgrade message."""
        logger.warning("Displaying kernel upgrade warning message to user.")
        print(f"\n{self.red}Warning!{self.endc} Your kernel image looks like to have been upgraded!\n"
              "Please update the bootloader with the new parameters of the upgraded kernel.\n"
              "See: lilo, eliloconfig or grub-mkconfig -o /boot/grub/grub.cfg,\n"
              "depending on how you have your system configured.\n")

    def _bootloader_update(self) -> None:
        """Prompt user to run bootloader update command and execute it."""
        logger.info("Prompting user for bootloader update: '%s'", self.bootloader_command)
        print(f'\nYour kernel image upgraded, do you want to run this command:\n'
              f'\n{self.green}    {self.bootloader_command}{self.endc}\n')
        self.views.question()
        logger.info("User confirmed bootloader update. Executing command: '%s'", self.bootloader_command)
        self.multi_process.process(self.bootloader_command)
        logger.info("Bootloader update command executed.")

    def repo_info(self) -> NoReturn:
        """Print repositories information."""
        logger.info("Executing 'repo-info' command.")
        repo = RepoInfo(self.options, self.repository)
        repo.info()
        sys.exit(0)

    def edit_configs(self) -> NoReturn:
        """Edit configurations via dialog box."""
        logger.info("Executing 'config' command (edit configurations).")
        self.is_root()
        form_configs = FormConfigs(options=self.options)
        form_configs.run()
        logger.info("Configuration editing completed.")
        sys.exit(0)

    def clean_tmp(self) -> NoReturn:
        """Remove all files and directories from tmp."""
        logger.info("Executing 'clean-tmp' command.")
        self.is_root()
        clean = Cleanings()
        clean.tmp()
        logger.info("Temporary files cleaned.")
        sys.exit(0)

    @staticmethod
    def self_check() -> NoReturn:
        """Check for slpkg updates."""
        logger.info("Executing 'self-check' command.")
        check_self_update()
        logger.info("Self-check completed.")
        sys.exit(0)

    def build(self, packages: list[str]) -> NoReturn:
        """Build slackbuilds with dependencies without install."""
        logger.info("Executing 'build' command for packages: %s", packages)
        self.is_root()
        command: str = Run.build.__name__

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for build command (repo: %s).", self.repository)
        build_packages = self.is_file_list_packages(packages)
        build_packages = self.utils.case_insensitive_pattern_matching(build_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", build_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for build.")
            build_packages = self.choose.packages(self.data, build_packages, command, ordered=True)
            logger.debug("Packages after user selection for build: %s", build_packages)

        self.pkg_validator.is_package_exists(build_packages, self.data)
        logger.debug("Existence check passed for build packages.")

        build = Slackbuilds(
            self.repository, self.data, build_packages, self.options, mode=command
        )
        logger.info("Initiating SlackBuilds build process.")
        build.execute()
        logger.info("Build command completed.")
        sys.exit(0)

    def install(self, packages: list[str]) -> NoReturn:
        """Build and install packages with dependencies."""
        logger.info("Executing 'install' command for packages: %s", packages)
        self.is_root()
        command: str = Run.install.__name__
        kernel_generic_current_package: str = self.utils.is_package_installed('kernel-generic')
        logger.debug("Current kernel-generic package: %s", kernel_generic_current_package)

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for install command (repo: %s).", self.repository)
        install_packages = self.is_file_list_packages(packages)
        install_packages = self.utils.case_insensitive_pattern_matching(install_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", install_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for install.")
            install_packages = self.choose.packages(self.data, install_packages, command, ordered=True)
            logger.debug("Packages after user selection for install: %s", install_packages)

        self.pkg_validator.is_package_exists(install_packages, self.data)
        logger.debug("Existence check passed for install packages.")

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            logger.info("Installing binary packages.")
            install_bin = Packages(self.repository, self.data, install_packages, self.options, mode=command)
            install_bin.execute()
        else:
            logger.info("Installing SlackBuilds.")
            install_sbo = Slackbuilds(self.repository, self.data, install_packages, self.options, mode=command)
            install_sbo.execute()

        self._is_kernel_upgrade(kernel_generic_current_package)
        logger.info("Install command completed.")
        sys.exit(0)

    def remove(self, packages: list[str]) -> NoReturn:
        """Remove packages with dependencies."""
        logger.info("Executing 'remove' command for packages: %s", packages)
        self.is_root()
        command: str = Run.remove.__name__

        remove_packages: list[str] = self.is_file_list_packages(packages)
        logger.debug("Packages after file list check for remove: %s", remove_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for remove.")
            remove_packages = self.choose.packages({}, remove_packages, command, ordered=True)  # No data needed for remove choose.
            logger.debug("Packages after user selection for remove: %s", remove_packages)

        self.pkg_validator.is_package_installed(remove_packages)
        logger.debug("Installed check passed for remove packages.")

        remove = RemovePackages(remove_packages, self.options)
        logger.info("Initiating package removal process.")
        remove.remove()
        logger.info("Remove command completed.")
        sys.exit(0)

    def download(self, packages: list[str], directory: str) -> NoReturn:
        """Download only packages."""
        logger.info("Executing 'download' command for packages: %s to directory: %s", packages, directory)
        command: str = Run.download.__name__

        if not directory:
            directory = str(self.tmp_slpkg)
            logger.debug("No download directory specified, defaulting to: %s", directory)
        else:
            logger.debug("Using specified download directory: %s", directory)

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for download command (repo: %s).", self.repository)
        download_packages = self.is_file_list_packages(packages)
        download_packages = self.utils.case_insensitive_pattern_matching(download_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", download_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for download.")
            download_packages = self.choose.packages(self.data, download_packages, command, ordered=True)
            logger.debug("Packages after user selection for download: %s", download_packages)

        self.pkg_validator.is_package_exists(download_packages, self.data)
        logger.debug("Existence check passed for download packages.")

        down_only = DownloadOnly(directory, self.options, self.data, self.repository)
        logger.info("Initiating package download process.")
        down_only.packages(download_packages)
        logger.info("Download command completed.")
        sys.exit(0)

    def list_installed(self, packages: list[str]) -> NoReturn:
        """Find installed packages."""
        logger.info("Executing 'list' command for packages: %s", packages)
        command: str = Run.list_installed.__name__

        ls_packages: list[str] = self.is_file_list_packages(packages)
        logger.debug("Packages after file list check for list: %s", ls_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for list.")
            data: dict[str, dict[str, str]] = {}  # No repository data needed for installed packages.
            ls_packages = self.choose.packages(data, ls_packages, command, ordered=True)
            logger.debug("Packages after user selection for list: %s", ls_packages)

        ls = ListInstalled(self.options, ls_packages)
        logger.info("Initiating listing of installed packages.")
        ls.installed()
        logger.info("List command completed.")
        sys.exit(0)

    def info_package(self, packages: list[str]) -> NoReturn:
        """View package information."""
        logger.info("Executing 'info' command for packages: %s (repo: %s)", packages, self.repository)
        command: str = Run.info_package.__name__

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for info command (repo: %s).", self.repository)
        info_packages = self.is_file_list_packages(packages)
        info_packages = self.utils.case_insensitive_pattern_matching(info_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", info_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for info.")
            info_packages = self.choose.packages(self.data, info_packages, command, ordered=True)
            logger.debug("Packages after user selection for info: %s", info_packages)

        self.pkg_validator.is_package_exists(info_packages, self.data)
        logger.debug("Existence check passed for info packages.")

        view = InfoPackage(self.options, self.repository)

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            logger.info("Displaying binary package information.")
            view.package(self.data, info_packages)
        else:
            logger.info("Displaying SlackBuild package information.")
            view.slackbuild(self.data, info_packages)
        logger.info("Info command completed.")
        sys.exit(0)

    def search(self, packages: list[str]) -> NoReturn:
        """Search packages from the repositories."""
        logger.info("Executing 'search' command for packages: %s (repo: %s)", packages, self.repository)
        command: str = Run.search.__name__
        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for search command (repo: %s).", self.repository)

        search_packages: list[str] = self.is_file_list_packages(packages)
        logger.debug("Packages after file list check for search: %s", search_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for search.")
            search_packages = self.choose.packages(self.data, search_packages, command, ordered=True)
            logger.debug("Packages after user selection for search: %s", search_packages)

        pkgs = SearchPackage(self.options, search_packages, self.data, self.repository)
        logger.info("Initiating package search process.")
        pkgs.search()
        logger.info("Search command completed.")
        sys.exit(0)

    def dependees(self, packages: list[str]) -> NoReturn:
        """View packages that depend on other packages."""
        logger.info("Executing 'dependees' command for packages: %s (repo: %s)", packages, self.repository)
        command: str = Run.dependees.__name__

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for dependees command (repo: %s).", self.repository)
        dependees_packages = self.is_file_list_packages(packages)
        dependees_packages = self.utils.case_insensitive_pattern_matching(dependees_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", dependees_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for dependees.")
            dependees_packages = self.choose.packages(self.data, dependees_packages, command, ordered=True)
            logger.debug("Packages after user selection for dependees: %s", dependees_packages)

        self.pkg_validator.is_package_exists(dependees_packages, self.data)
        logger.debug("Existence check passed for dependees packages.")

        dependees = Dependees(self.data, dependees_packages, self.options)
        logger.info("Initiating dependees find process.")
        dependees.find()
        logger.info("Dependees command completed.")
        sys.exit(0)

    def tracking(self, packages: list[str]) -> NoReturn:
        """Tracking package dependencies."""
        logger.info("Executing 'tracking' command for packages: %s (repo: %s)", packages, self.repository)
        command: str = Run.tracking.__name__

        self.data = self.load_data.load(self.repository)
        logger.debug("Loaded repository data for tracking command (repo: %s).", self.repository)
        tracking_packages = self.is_file_list_packages(packages)
        tracking_packages = self.utils.case_insensitive_pattern_matching(tracking_packages, self.data, self.options)
        logger.debug("Packages after file list and case-insensitive matching: %s", tracking_packages)

        if self.options.get('option_select') or self.options.get('option_dialog'):
            logger.info("User selected option_select. Prompting package selection for tracking.")
            tracking_packages = self.choose.packages(self.data, tracking_packages, command, ordered=True)
            logger.debug("Packages after user selection for tracking: %s", tracking_packages)

        self.pkg_validator.is_package_exists(tracking_packages, self.data)
        logger.debug("Existence check passed for tracking packages.")

        tracking = Tracking(self.data, tracking_packages, self.options, self.repository)
        logger.info("Initiating package tracking process.")
        tracking.package()
        logger.info("Tracking command completed.")
        sys.exit(0)

    def changelog_print(self, query: str) -> NoReturn:
        """Prints repository changelog."""
        logger.info("Executing 'changelog' command for query: '%s' (repo: %s)", query, self.repository)
        changelog_manager = Changelog(options=self.options, repository=self.repository, query=query)
        changelog_manager.run()
        logger.info("Changelog command completed.")
        sys.exit(0)

    @staticmethod
    def version() -> NoReturn:
        """Print program version and exit."""
        logger.info("Executing 'version' command.")
        version = Version()
        version.view()
        logger.info("Version command completed.")
        sys.exit(0)


def check_for_repositories(repository: str, args: argparse.Namespace, parser: argparse.ArgumentParser, option_args: dict[str, Any]) -> None:
    """Manages repository rules and validation."""
    logger.debug("Checking repository rules for repository: '%s', command: '%s', options: %s", repository, args.command, option_args)
    repos = Repositories()
    repo_config = repos.repositories.get(repository)

    if repository != '*' and repository is not None and repository != '':
        if repo_config is None:
            logger.error("Repository '%s' does not exist.", repository)
            parser.error(f"Repository '{repository}' does not exist.")
        elif not repo_config.get('enable'):
            logger.error("Repository '%s' is not enabled.", repository)
            parser.error(f"Repository '{repository}' is not enabled.")

    # Special rules for '*' repository
    if repository == '*' and not (args.command == 'search' or (args.command == 'upgrade' and option_args.get('option_check'))):
        logger.error("Repository '*' is not allowed with command '%s'.", args.command)
        parser.error(f"Repository '{repository}' is not allowed with this command.")

    # Special rules for 'build' command
    if args.command == 'build' and repository and repository not in list(repos.repositories)[:2]:
        logger.error("Repository '%s' is not allowed with 'build' command.", repository)
        parser.error(f"Repository '{repository}' is not allowed with this command.")
    logger.debug("Repository rules check completed successfully.")


class CustomCommandsFormatter(argparse.RawDescriptionHelpFormatter):
    """
    Formatter that produces exactly the requested output format:
    - Main help shows: slpkg <COMMAND> [PACKAGES] [OPTIONS]
    - Command help shows: slpkg install [PACKAGE ...] [OPTIONS]
    - Clean command listing with proper indentation
    """

    def __init__(self, prog: str, indent_increment: int = 1, max_help_position: int = 26, width: Union[int, None] = None) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        # self._subcommands = ['update', 'upgrade', 'config', 'repo-info', 'clean-tmp',
        #                      'self-check', 'build', 'install', 'remove', 'download',
        #                      'list', 'info', 'search', 'dependees', 'tracking', 'version', 'changelog', 'help']
        self.custom_usage = f"{self._prog} <COMMAND> [PACKAGES] [OPTIONS]"
        logger.debug("CustomCommandsFormatter initialized.")

    def add_usage(self, usage: Union[str, None], actions: list[argparse.Action], groups: list[argparse._ArgumentGroup], prefix: Union[str, None] = None) -> None:  # type: ignore
        """Custom usage formatting that handles both main and command help"""
        if prefix is None:
            prefix = f'{config_load.bold}Usage{config_load.endc}: '

        # For the main parser's help, always use the custom usage.
        # Subcommand help will be handled by their own print_help() calls via subparsers_map.
        usage = self.custom_usage

        return super().add_usage(usage, actions, groups, prefix)  # type: ignore[arg-type]

    def _format_action(self, action: list[argparse.Action]) -> Union[str, None]:  # type: ignore
        """Remove command choices and format subcommands cleanly"""
        if isinstance(action, argparse._SubParsersAction) and action.dest == 'command':  # pylint: disable=[W0212]
            # Store original values
            orig_help = action.help
            orig_choices = action.choices

            # Temporarily modify for clean output
            action.help = None
            action.choices = None  # type: ignore

            # Get formatted string
            result = super()._format_action(action)

            # Restore original values
            action.help = orig_help
            action.choices = orig_choices

            # Remove all unwanted artifacts
            result = re.sub(r'^ *command.*\n', '', result, flags=re.MULTILINE)
            result = re.sub(r'\{.*}.*\n', '', result, flags=re.MULTILINE)
            return result

        return super()._format_action(action)  # type: ignore[arg-type]

    def _format_action_invocation(self, action: argparse.Action) -> Union[str, None]:  # type: ignore
        """Ensure consistent 10-space indentation for commands"""
        if not action.option_strings and not isinstance(action, argparse._SubParsersAction):  # pylint: disable=[W0212]
            metavar = self._format_args(action, self._get_default_metavar_for_positional(action))
            return metavar
        return super()._format_action_invocation(action)

    def format_help(self) -> str:
        """Final help text processing"""
        help_text = super().format_help()

        # Replace section headers
        help_text = help_text.replace(
            'positional arguments:',
            f'{config_load.bold}Commands:{config_load.endc}'
        )

        # Clean up any remaining artifacts
        help_text = re.sub(r'\{.*}.*\n', '', help_text)  # Remove {command1,command2} line
        help_text = re.sub(r'command\n', '', help_text)  # Remove command line

        return help_text


def main() -> None:  # pylint: disable=[R0912,R0914,R0915]
    """Main control function for argparse arguments."""
    logger.info("Main function started.")
    error = Errors()

    commands_that_use_repos = [
        'install', 'i', 'inst',
        'build', 'b', 'bld',
        'download', 'dl', 'dwn',
        'info', 'inf', 'show',
        'search', 's', 'ser',
        'dependees', 'dp', 'dps',
        'tracking', 't', 'trk',
        'update', 'u', 'upd',
        'upgrade', 'U', 'upg',
        'repo-info', 'ri', 'rinf',
        'changelog', 'a', 'chg'
    ]
    logger.debug("Commands that use repositories: %s", commands_that_use_repos)

    commands_that_use_packages = [
        'install', 'i', 'inst',
        'remove', 'R', 'rmv',
        'build', 'b', 'bld',
        'download', 'dl', 'dwn',
        'info', 'inf', 'show',
        'search', 's', 'ser',
        'list', 'l', 'lst',
        'dependees', 'dp', 'dps',
        'tracking', 't', 'trk'
    ]
    logger.debug("Commands that use packages: %s", commands_that_use_packages)

    # --- Argument Parsers for common options ---
    # Each common option gets its own parser to be reused as a parent.
    yes_parser = argparse.ArgumentParser(add_help=False)
    yes_group = yes_parser.add_argument_group()
    yes_group.add_argument('-y', '--yes', action='store_true', dest='option_yes', help='Answer Yes to all questions.')

    check_parser = argparse.ArgumentParser(add_help=False)
    check_group = check_parser.add_argument_group()
    check_group.add_argument('-c', '--check', action='store_true', dest='option_check', help='Check a procedure before you run it.')

    resolve_off_parser = argparse.ArgumentParser(add_help=False)
    resolve_off_group = resolve_off_parser.add_argument_group()
    resolve_off_group.add_argument('-O', '--resolve-off', action='store_true', dest='option_resolve_off', help='Turns off dependency resolving.')

    reinstall_parser = argparse.ArgumentParser(add_help=False)
    reinstall_group = reinstall_parser.add_argument_group()
    reinstall_group.add_argument('-r', '--reinstall', action='store_true', dest='option_reinstall', help='Upgrade packages of the same version.')

    skip_install_parser = argparse.ArgumentParser(add_help=False)
    skip_install_group = skip_install_parser.add_argument_group()
    skip_install_group.add_argument('-k', '--skip-installed', action='store_true', dest='option_skip_installed', help='Skip installed packages during the building or installation progress.')

    fetch_parser = argparse.ArgumentParser(add_help=False)
    fetch_group = fetch_parser.add_argument_group()
    fetch_group.add_argument('-f', '--fetch', action='store_true', dest='option_fetch', help='Fetch the fastest and slower mirror.')

    full_reverse_parser = argparse.ArgumentParser(add_help=False)
    full_reverse_group = full_reverse_parser.add_argument_group()
    full_reverse_group.add_argument('-E', '--full-reverse', action='store_true', dest='option_full_reverse', help='Display the full reverse dependency tree.')

    select_parser = argparse.ArgumentParser(add_help=False)
    select_group = select_parser.add_argument_group()
    select_group.add_argument('-S', '--select', action='store_true', dest='option_select', help='Matching and select packages with selector or dialog.')

    progress_bar_parser = argparse.ArgumentParser(add_help=False)
    progress_bar_group = progress_bar_parser.add_argument_group()
    progress_bar_group.add_argument('-B', '--progress-bar', action='store_true', dest='option_progress_bar', help='Display static progress bar instead of process execute.')

    pkg_version_parser = argparse.ArgumentParser(add_help=False)
    pkg_version_group = pkg_version_parser.add_argument_group()
    pkg_version_group.add_argument('-p', '--pkg-version', action='store_true', dest='option_pkg_version', help='Print the repository package version.')

    parallel_parser = argparse.ArgumentParser(add_help=False)
    parallel_group = parallel_parser.add_argument_group()
    parallel_group.add_argument('-P', '--parallel', action='store_true', dest='option_parallel', help='Enable download files in parallel.')

    no_case_parser = argparse.ArgumentParser(add_help=False)
    no_case_group = no_case_parser.add_argument_group()
    no_case_group.add_argument('-m', '--no-case', action='store_true', dest='option_no_case', help='Case-insensitive pattern matching.')

    color_parser = argparse.ArgumentParser(add_help=False)
    color_group = color_parser.add_argument_group()
    color_group.add_argument('-x', '--color', choices=['on', 'off', 'ON', 'OFF'], metavar='<ON/OFF>', dest='option_color', help='Switch on or off color output.')

    dialog_parser = argparse.ArgumentParser(add_help=False)
    dialog_group = dialog_parser.add_argument_group()
    dialog_group.add_argument('-D', '--dialog', action='store_true', dest='option_dialog', help='Enable dialog-based interface instead, terminal selector.')

    description_parser = argparse.ArgumentParser(add_help=False)
    description_group = description_parser.add_argument_group()
    description_group.add_argument('-t', '--desc', action='store_true', dest='option_pkg_description', help='Print the package description.')

    edit_parser = argparse.ArgumentParser(add_help=False)
    edit_group = edit_parser.add_argument_group()
    edit_group.add_argument('-e', '--edit', action='store_true', dest='option_edit', help="Open the file with the system's default editor.")

    edit_sbo_parser = argparse.ArgumentParser(add_help=False)
    edit_sbo_group = edit_sbo_parser.add_argument_group()
    edit_sbo_group.add_argument('-e', '--edit', metavar='NAME', dest='option_sbo_edit', help="Open a specified SBo file for editing using the system's default editor, typically before a build operation. This functionality is applicable only to SBo repositories. Use '*' to select all relevant SBo files.")

    repo_tag_parser = argparse.ArgumentParser(add_help=False)
    repo_tag_group = repo_tag_parser.add_argument_group()
    repo_tag_group.add_argument('-T', '--repo-tag', metavar='TAG', dest='option_repo_tag', help="Sets a specific repository tag (TAG) for SlackBuild scripts, used to distinguish your custom builds. Provide the desired tag value (e.g., _custom). This is typically used before a build operation and applies exclusively to SlackBuild repositories.")

    pager_parser = argparse.ArgumentParser(add_help=False)
    pager_group = pager_parser.add_argument_group()
    pager_group.add_argument('-R', '--pager', action='store_true', dest='option_pager', help='Enables viewing output through a pager.')

    repository_parser = argparse.ArgumentParser(add_help=False)
    repository_group = repository_parser.add_argument_group()
    repository_group.add_argument('-o', '--repository', metavar='<NAME>', dest='option_repository', help='Sets the active repository for package management operations. Overrides the default repository from the configuration file.')

    directory_parser = argparse.ArgumentParser(add_help=False)
    directory_group = directory_parser.add_argument_group()
    directory_group.add_argument('-z', '--directory', metavar='<PATH>', dest='option_directory', help='Download files to a specific path.')

    query_parser = argparse.ArgumentParser(add_help=False)
    query_group = query_parser.add_argument_group()
    query_group.add_argument('-q', '--query', metavar='<QUERY>', dest='option_query', help='Filter results based on a search query.')

    # debug_parser only for the command line menu,
    # the task of changing the logging level is achieved
    # at the beginning of the file through the sys.argv module.
    debug_parser = argparse.ArgumentParser(add_help=False)
    debug_group = debug_parser.add_argument_group()
    debug_group.add_argument('-d', '--debug', action='store_true', dest='option_debug', help='Sets the logging level to DEBUG.')

    # --- Main Parser ---
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog='slpkg',
        description="Description:\n  Package manager utility for Slackware Linux.",
        formatter_class=CustomCommandsFormatter,
        epilog='For command-specific help: slpkg help <COMMAND> or use manpage.',
        add_help=False
    )
    logger.debug("Main argparse parser created.")

    subparsers = parser.add_subparsers(
        dest='command',
    )
    subparsers.required = True  # Makes subcommand selection mandatory.
    logger.debug("Subparsers created and set as required.")

    # Dictionary to store references to subparsers for easy access by the 'help' command
    subparsers_map: dict[str, argparse.ArgumentParser] = {}

    # --- Subcommand Parsers ---
    # Store each subparser in the map after creation
    subparsers_map['update'] = subparsers.add_parser('update', aliases=['u', 'upd'], parents=[check_parser, color_parser, repository_parser, debug_parser], help='Sync repository database with local.')
    subparsers_map['upgrade'] = subparsers.add_parser('upgrade', aliases=['U', 'upg'], parents=[yes_parser, check_parser, resolve_off_parser, progress_bar_parser, parallel_parser, dialog_parser, color_parser, repository_parser, debug_parser],
                                                      help='Upgrade the installed packages.')
    subparsers_map['config'] = subparsers.add_parser('config', aliases=['g', 'conf'], parents=[edit_parser, dialog_parser, debug_parser], help='Edit the configuration file.')
    subparsers_map['repo-info'] = subparsers.add_parser('repo-info', aliases=['ri', 'rinf'], parents=[fetch_parser, color_parser, repository_parser, debug_parser], help='Display the repositories information.')
    subparsers_map['clean-tmp'] = subparsers.add_parser('clean-tmp', aliases=['c', 'ctmp'], parents=[debug_parser], help='Clean old downloaded packages and scripts.')
    subparsers_map['self-check'] = subparsers.add_parser('self-check', aliases=['sc', 'schk'], parents=[debug_parser], help='Checks for available slpkg updates.')

    build_parser = subparsers.add_parser('build', aliases=['b', 'bld'], parents=[yes_parser, resolve_off_parser, skip_install_parser, progress_bar_parser, parallel_parser, no_case_parser, select_parser, dialog_parser, edit_sbo_parser, repo_tag_parser, color_parser,
                                         repository_parser, debug_parser],
                                         help='Build SBo scripts without install it.')
    build_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to build.')
    subparsers_map['build'] = build_parser

    install_parser = subparsers.add_parser('install', aliases=['i', 'inst'], parents=[yes_parser, reinstall_parser, resolve_off_parser, skip_install_parser, progress_bar_parser, parallel_parser, no_case_parser,
                                           select_parser, dialog_parser, edit_sbo_parser, repo_tag_parser, color_parser, repository_parser, debug_parser],
                                           help='Build/install SBo scripts or binary packages.')
    install_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to install.')
    subparsers_map['install'] = install_parser

    remove_parser = subparsers.add_parser('remove', aliases=['R', 'rmv'], parents=[yes_parser, resolve_off_parser, select_parser, dialog_parser, progress_bar_parser, color_parser, debug_parser],
                                          help='Remove installed packages with dependencies.')
    remove_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to remove.')
    subparsers_map['remove'] = remove_parser

    download_parser = subparsers.add_parser('download', aliases=['dl', 'dwn'], parents=[yes_parser, no_case_parser, select_parser, dialog_parser, color_parser, directory_parser, repository_parser, debug_parser],
                                            help='Download only the packages without build or install.')
    download_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to download.')
    subparsers_map['download'] = download_parser

    list_parser = subparsers.add_parser('list', aliases=['l', 'lst'], parents=[no_case_parser, description_parser, select_parser, dialog_parser, color_parser, debug_parser], help='Matching and display list of the installed packages.')
    list_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to display.')
    subparsers_map['list'] = list_parser

    info_parser = subparsers.add_parser('info', aliases=['inf', 'show'], parents=[select_parser, dialog_parser, color_parser, repository_parser, debug_parser], help='Display package information by the repository.')
    info_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to display information for.')
    subparsers_map['info'] = info_parser

    search_parser = subparsers.add_parser('search', aliases=['s', 'ser'], parents=[no_case_parser, pkg_version_parser, description_parser, select_parser, dialog_parser, color_parser, repository_parser, debug_parser],
                                          help='This will match each package by the repository.')
    search_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names to search for.')
    subparsers_map['search'] = search_parser

    dependees_parser = subparsers.add_parser('dependees', aliases=['dp', 'dps'], parents=[no_case_parser, pkg_version_parser, full_reverse_parser, select_parser, dialog_parser, color_parser, repository_parser, debug_parser],
                                             help='Display packages that depend on other packages.')
    dependees_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names for dependencies.')
    subparsers_map['dependees'] = dependees_parser

    tracking_parser = subparsers.add_parser('tracking', aliases=['t', 'trk'], parents=[no_case_parser, pkg_version_parser, select_parser, dialog_parser, color_parser, repository_parser, debug_parser],
                                            help='Display and tracking the packages dependencies.')
    tracking_parser.add_argument('packages', nargs='+', metavar='PACKAGE', help='Package names for tracking.')
    subparsers_map['tracking'] = tracking_parser

    changelog_parser = subparsers.add_parser('changelog', aliases=['a', 'chg'], parents=[edit_parser, pager_parser, repository_parser, query_parser, color_parser, debug_parser], help='Display the changelog for a given repository.')
    subparsers_map['changelog'] = changelog_parser

    version_parser = subparsers.add_parser('version', aliases=['v', 'ver'], parents=[], help='Show version and exit.')
    subparsers_map['version'] = version_parser

    help_parser = subparsers.add_parser('help', aliases=['h', 'hlp'], parents=[], help='Show this help message and exit.')
    help_parser.add_argument('command_for_help', nargs='?', help='Show help for a specific command.')
    subparsers_map['help'] = help_parser  # Store reference for 'help' itself

    logger.debug("All subcommand parsers defined and stored in subparsers_map.")

    # --- Handle initial argument parsing for missing command or help ---
    # This logic is moved here before the main parse_args to handle cases where
    # a command is missing or only -h/--help is provided without a command.
    if len(sys.argv) == 1:
        logger.error("No command provided. Exiting with error and showing help message.")
        parser.error('Missing command. Use "help" for more information.')

    # Check for -h or --help without a specific command.
    # This block ensures that -h or --help do not show the full help,
    # but instead direct the user to the 'help' subcommand.
    if len(sys.argv) == 2 and any(arg == '-h' or arg == '--help' for arg in sys.argv[1:]):  # pylint: disable=[R1714]
        logger.info("'-h' or '--help' provided without a command. Directing user to 'help' subcommand.")
        parser.error('Missing command. Use "help" for more information.')

    # --- Parse arguments ---
    args: argparse.Namespace = parser.parse_args()
    logger.info("Arguments parsed: %s", args)

    # --- Update configs from argparse args. ---
    # Call the update_from_args method from config_load to apply CLI arguments to global config.
    config_load.update_from_args(args)
    logger.debug("Configuration updated from argparse arguments using config_load.update_from_args.")

    # Retrieve repository, directory, and query.
    repository = args.option_repository if hasattr(args, 'option_repository') and args.option_repository is not None else ''
    directory = args.option_directory if hasattr(args, 'option_directory') and args.option_directory is not None else '/tmp/slpkg/'
    query = args.option_query if hasattr(args, 'option_query') and args.option_query is not None else ''
    logger.debug("Extracted repository: '%s', directory: '%s', query: '%s'", repository, directory, query)

    option_args: dict[str, Any] = {
        'option_yes': getattr(args, 'option_yes', False),
        'option_check': getattr(args, 'option_check', False),
        'option_resolve_off': getattr(args, 'option_resolve_off', False),
        'option_reinstall': getattr(args, 'option_reinstall', False),
        'option_skip_installed': getattr(args, 'option_skip_installed', False),
        'option_fetch': getattr(args, 'option_fetch', False),
        'option_full_reverse': getattr(args, 'option_full_reverse', False),
        'option_select': getattr(args, 'option_select', False),
        'option_progress_bar': getattr(args, 'option_progress_bar', False),
        'option_pkg_version': getattr(args, 'option_pkg_version', False),
        'option_parallel': getattr(args, 'option_parallel', False),
        'option_no_case': getattr(args, 'option_no_case', False),
        'option_color': getattr(args, 'option_color', None),
        'option_dialog': getattr(args, 'option_dialog', False),
        'option_pkg_description': getattr(args, 'option_pkg_description', False),
        'option_edit': getattr(args, 'option_edit', False),
        'option_sbo_edit': getattr(args, 'option_sbo_edit', False),
        'option_repo_tag': getattr(args, 'option_repo_tag', None),
        'option_pager': getattr(args, 'option_pager', False),
        'option_repository': repository,  # Store the actual repository string.
        'option_directory': directory,    # Store the actual directory string.
        'option_query': query,            # Store the actual query string.
    }
    logger.debug("Extracted options dictionary: %s", option_args)

    # --- Repository validation ---
    check_for_repositories(repository, args, parser, option_args)
    logger.debug("Repository validation completed.")

    # --- Initialize Run class ---
    # Pass the full option_args dictionary to Run
    runner = Run(option_args, repository)
    logger.debug("Run class instance created.")

    # --- Command Dispatch ---
    command_map: dict[str, Callable[..., Any]] = {
        'update': runner.update, 'u': runner.update, 'upd': runner.update,
        'upgrade': runner.upgrade, 'U': runner.upgrade, 'upg': runner.upgrade,
        'config': runner.edit_configs, 'g': runner.edit_configs, 'conf': runner.edit_configs,
        'repo-info': runner.repo_info, 'ri': runner.repo_info, 'rinf': runner.repo_info,
        'clean-tmp': runner.clean_tmp, 'c': runner.clean_tmp, 'ctmp': runner.clean_tmp,
        'self-check': runner.self_check, 'sc': runner.self_check, 'schk': runner.self_check,
        'build': runner.build, 'b': runner.build, 'bld': runner.build,
        'install': runner.install, 'i': runner.install, 'inst': runner.install,
        'remove': runner.remove, 'R': runner.remove, 'rmv': runner.remove,
        'download': runner.download, 'dl': runner.download, 'dwn': runner.download,
        'list': runner.list_installed, 'l': runner.list_installed, 'lst': runner.list_installed,
        'info': runner.info_package, 'inf': runner.info_package, 'show': runner.info_package,
        'search': runner.search, 's': runner.search, 'ser': runner.search,
        'dependees': runner.dependees, 'dp': runner.dependees, 'dps': runner.dependees,
        'tracking': runner.tracking, 't': runner.tracking, 'trk': runner.tracking,
        'changelog': runner.changelog_print, 'a': runner.changelog_print, 'chg': runner.changelog_print,
        'version': runner.version, 'v': runner.version, 'ver': runner.version
    }
    logger.debug("Command map created: %s", list(command_map.keys()))

    try:
        command = args.command
        logger.info("Dispatching command: '%s'", command)

        if command in commands_that_use_packages:
            if command in ['download', 'dl', 'dwn']:
                logger.info("Dispatching 'download' command with packages: %s, directory: %s", args.packages, directory)
                runner.download(args.packages, directory)
            else:
                logger.info("Dispatching command '%s' with packages: %s", command, args.packages)
                command_map[command](args.packages)
        elif command in ['changelog', 'a', 'chg']:
            logger.info("Dispatching 'changelog' command with query: '%s'", query)
            runner.changelog_print(query)
        elif command in ['help', 'h', 'hlp']:
            logger.info("Handling 'help' command for subcommand: %s", args.command_for_help)
            # Specific handling for the 'help' command.
            if args.command_for_help:
                subcommand_to_help = args.command_for_help
                if subcommand_to_help in subparsers_map:
                    # Get the specific subparser and print its help directly.
                    subparsers_map[subcommand_to_help].print_help()
                    logger.info("Displayed help for subcommand: '%s'.", subcommand_to_help)
                else:
                    # If the requested subcommand for help does not exist.
                    parser.error(f"Unknown command '{subcommand_to_help}' for help.")
                    logger.error("Attempted to get help for unknown subcommand: '%s'.", subcommand_to_help)
            else:
                parser.print_help()  # Display general help for 'slpkg help'.
                logger.info("Displayed general help for 'slpkg help'.")
        else:
            logger.info("Dispatching command '%s' without specific package/query/directory arguments.", command)
            command_map[command]()

    except (KeyboardInterrupt, EOFError):
        logger.info("Operation cancelled by user (KeyboardInterrupt/EOFError). Exiting with status 1.")
        print('\nOperation canceled by the user.')
        sys.exit(1)
    except KeyError as e:
        logger.error('KeyError occurred during command dispatch: %s', e, exc_info=True)
        message: str = f'An internal error occurred: {e}. Check the log {config_load.slpkg_log_file} file.'
        error.message(message=message, exit_status=1)
    logger.info("Main function finished.")


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError) as err:
        logger.info("Application terminated by user (KeyboardInterrupt/EOFError) at top level. Exiting with status 1.")
        print('\nOperation canceled by the user.')
        raise SystemExit(1) from err
    except Exception as e:  # pylint: disable=[W0718]
        logger.critical('An unexpected critical error occurred at top level: %s', e, exc_info=True)
        msg: str = f'A critical error occurred: {e}. Check the log {config_load.slpkg_log_file} file.'
        print(msg, file=sys.stderr)
        sys.exit(1)
