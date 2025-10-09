#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import shutil
from pathlib import Path
from typing import Optional, Union

from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint, PackageData

logger = logging.getLogger(__name__)


class View:  # pylint: disable=[R0902]
    """Views packages for build, install, remove or download."""

    def __init__(self, options: Optional[dict[str, bool]] = None, repository: Optional[str] = None, data: Optional[dict[str, dict[str, str]]] = None) -> None:
        logger.debug("Initializing View module with options: %s, repository: %s, data present: %s",
                     options, repository, bool(data))
        if options is None:
            options = {}
            logger.debug("Options were None, set to empty dict.")

        if repository is None:
            repository = 'None'
            logger.debug("Repository was None, set to 'None'.")

        if data is None:
            data = {}
            logger.debug("Data was None, set to empty dict.")

        self.options = options
        self.repository = repository
        self.data = data

        self.tmp_path = config_load.tmp_path
        self.package_method = config_load.package_method
        self.view_missing_deps = config_load.view_missing_deps
        self.ask_question = config_load.ask_question
        self.answer_yes = config_load.answer_yes
        # Console colors.
        self.grey = config_load.grey
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.red = config_load.red
        self.endc = config_load.endc

        self.repos = Repositories()
        self.utils = Utilities()
        self.imp = Imprint()
        self.upgrade = Upgrade(repository, data)

        self.sum_install: int = 0
        self.sum_upgrade: int = 0
        self.sum_remove: int = 0
        self.sum_size_comp: float = 0
        self.sum_size_uncomp: float = 0
        self.sum_size_remove: int = 0
        self.columns, self.rows = shutil.get_terminal_size()
        logger.debug("Terminal size: %sx%s", self.columns, self.rows)

        self.download_only: Path = Path()
        self.summary_message: str = ''
        self.mode: str = ''

        self.option_for_reinstall: bool = options.get('option_reinstall', False)
        logger.debug("View module initialized. Option for reinstall: %s", self.option_for_reinstall)

    def build_packages(self, slackbuilds: list[str], dependencies: list[str]) -> None:
        """View packages for build method.

        Args:
            slackbuilds (list[str]): Slackbuilds for build.
            dependencies (list[str]): Dependencies for build.
        """
        logger.info("Displaying packages for 'build' mode. SlackBuilds: %d, Dependencies: %d",
                    len(slackbuilds), len(dependencies))
        self.mode = 'build'
        self.imp.package_status('Building:')

        for slackbuild in slackbuilds:
            logger.debug("Processing SlackBuild for build: %s", slackbuild)
            self.imprint_build_package(slackbuild)
            self.summary(slackbuild)

        if dependencies:
            logger.info("Displaying dependencies for build.")
            self.imp.dependency_status('Building')

            for dependency in dependencies:
                logger.debug("Processing dependency for build: %s", dependency)
                self.imprint_build_package(dependency)
                self.summary(dependency)

        self.set_summary_for_build(slackbuilds + dependencies)
        print('\nProcess summary:')
        print('=' * (self.columns - 1))
        print(self.summary_message)
        logger.info("Build packages view completed. Summary: %s", self.summary_message.strip())

    def install_upgrade_packages(self, packages: list[str], dependencies: list[str], mode: str) -> None:
        """View packages for install or upgrade.

        Args:
            packages (list[str]): Packages for install.
            dependencies (list[str]): Dependencies for install.
            mode (str): Type of mode ('install' or 'upgrade').
        """
        logger.info("Displaying packages for '%s' mode. Packages: %d, Dependencies: %d",
                    mode, len(packages), len(dependencies))
        self.mode = mode
        message: str = 'Upgrading:'
        if self.mode == 'install':
            message = 'Installing:'
        logger.debug("Mode set to '%s', display message: '%s'", self.mode, message)

        dep_msg: str = message[:-1]  # Remove trailing colon for dependency message.
        self.imp.package_status(message)

        for package in packages:
            logger.debug("Processing package for %s: %s", self.mode, package)
            self.imprint_install_upgrade_package(package)
            self.summary(package)

        if dependencies:
            logger.info("Displaying dependencies for %s.", self.mode)
            self.imp.dependency_status(dep_msg)

            for dependency in dependencies:
                logger.debug("Processing dependency for %s: %s", self.mode, dependency)
                self.imprint_install_upgrade_package(dependency)
                self.summary(dependency)

        self.set_summary_for_install_and_upgrade(self.sum_install, self.sum_upgrade,
                                                 self.sum_size_comp, self.sum_size_uncomp)
        print('\nProcess summary:')
        print('=' * (self.columns - 1))
        print(self.summary_message)
        logger.info("%s packages view completed. Summary: %s", self.mode.capitalize(), self.summary_message.strip())

    def download_packages(self, packages: list[str], directory: Path) -> None:
        """View packages for download method.

        Args:
            packages (list[str]): Packages name for download.
            directory (Path): Path to download.
        """
        logger.info("Displaying packages for 'download' mode. Packages: %d, Directory: %s",
                    len(packages), directory)
        self.mode = 'download'
        self.download_only = directory
        self.imp.package_status('Downloading:')

        for package in packages:
            logger.debug("Processing package for download: %s", package)
            self.imprint_download_package(package)
            self.summary(package)

        self.set_summary_for_download(packages, self.sum_size_comp)
        print('\nProcess summary:')
        print('=' * (self.columns - 1))
        print(self.summary_message)
        logger.info("Download packages view completed. Summary: %s", self.summary_message.strip())

    def remove_packages(self, packages: list[str], dependencies: list[str]) -> None:
        """View packages for remove.

        Args:
            packages (list[str]): List of packages.
            dependencies (list[str]): List of dependencies.
        """
        logger.info("Displaying packages for 'remove' mode. Packages: %d, Dependencies: %d",
                    len(packages), len(dependencies))
        self.mode = 'remove'
        self.imp.package_status('Removing:')
        for package in packages:
            logger.debug("Processing package for removal: %s", package)
            self.imprint_remove_package(package)
            self.summary(package)

        if dependencies:
            logger.info("Displaying dependencies for removal.")
            self.imp.dependency_status('Removing')

            for dependency in dependencies:
                logger.debug("Processing dependency for removal: %s", dependency)
                self.imprint_remove_package(dependency)
                self.summary(dependency)

        self.set_summary_for_remove(self.sum_remove, self.sum_size_remove)
        print('\nProcess summary:')
        print('=' * (self.columns - 1))
        print(self.summary_message)
        logger.info("Remove packages view completed. Summary: %s", self.summary_message.strip())

    def imprint_build_package(self, package: str) -> None:
        """Draw line for build package method.

        Args:
            package (str): Package name.
        """
        logger.debug("Imprinting build package line for: %s", package)
        size: str = ''  # Size is not directly relevant for building (sources are downloaded, not binary size).
        version: str = self.data.get(package, {}).get('version', 'N/A')

        package_info = PackageData(
            package,
            version,
            size,
            self.green,  # Green indicates it's being processed/built.
            self.repository
        )

        self.imp.package_line(package_info)
        logger.debug("Build package line imprinted for: %s", package)

    def imprint_install_upgrade_package(self, package: str) -> None:
        """Draw line for install or upgrade package method.

        Args:
            package (str): Package name.
        """
        logger.debug("Imprinting install/upgrade package line for: %s", package)
        size: str = ''
        color: str = self.green  # Default color for new install.
        version: str = self.data.get(package, {}).get('version', 'N/A')
        installed: str = self.utils.is_package_installed(package)
        upgradable: bool = self.upgrade.is_package_upgradeable(installed) if installed else False

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            # For binary packages, calculate size
            size_comp: float = float(self.data.get(package, {}).get('size_comp', 0)) * 1024
            size = self.utils.convert_file_sizes(size_comp)
            logger.debug("Calculated compressed size for binary package '%s': %s", package, size)

        if installed:
            color = self.grey  # Grey if already installed and not upgradeable/reinstall.
            logger.debug("Package '%s' is installed, setting color to grey.", package)

        if upgradable:
            color = self.yellow  # Yellow if upgradeable.
            package = self.build_package_and_version(package)  # Append installed version for display.
            logger.debug("Package '%s' is upgradeable, setting color to yellow and appending version.", package)

        if installed and self.option_for_reinstall and not upgradable:
            color = self.yellow  # Yellow if reinstalling same version.
            package = self.build_package_and_version(package)  # Append installed version for display.
            logger.debug("Package '%s' is installed and reinstall option is active, setting color to yellow and appending version.", package)

        package_info = PackageData(
            package,
            version,
            size,
            color,
            self.repository
        )

        self.imp.package_line(package_info)
        logger.debug("Install/upgrade package line imprinted for: %s", package)

    def imprint_download_package(self, package: str) -> None:
        """Draw package for download method.

        Args:
            package (str): Package name.
        """
        logger.debug("Imprinting download package line for: %s", package)
        size: str = ''
        color: str = self.green  # Green indicates it's being downloaded.
        version: str = self.data.get(package, {}).get('version', 'N/A')

        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            # For binary packages, calculate size.
            size_comp: float = float(self.data.get(package, {}).get('size_comp', 0)) * 1024
            size = self.utils.convert_file_sizes(size_comp)
            logger.debug("Calculated compressed size for binary package '%s' for download: %s", package, size)

        package_info = PackageData(
            package,
            version,
            size,
            color,
            self.repository
        )

        self.imp.package_line(package_info)
        logger.debug("Download package line imprinted for: %s", package)

    def imprint_remove_package(self, package: str) -> None:
        """Draw package for remove method.

        Args:
            package (str): Package name.
        """
        logger.debug("Imprinting remove package line for: %s", package)
        count_size: int = self.utils.count_file_size(package)  # Get actual installed size.
        installed: str = self.utils.is_package_installed(package)

        version: str = 'N/A'
        repo_tag: str = 'N/A'
        if installed:  # Only parse if actually installed.
            version = self.utils.split_package(installed)['version']
            repo_tag = self.utils.split_package(installed)['tag']

        size: str = self.utils.convert_file_sizes(count_size)

        # Set repository for display based on installed package's tag
        self.repository = repo_tag.lower().replace('_', '') if repo_tag else 'unknown'
        logger.debug("Calculated size for removal '%s': %s. Installed version: %s, Repo Tag: %s", package, size, version, repo_tag)

        package_info = PackageData(
            package,
            version,
            size,
            self.red,  # Red indicates removal.
            self.repository
        )

        self.imp.package_line(package_info)
        logger.debug("Remove package line imprinted for: %s", package)

    def summary(self, package: str) -> None:
        """Count packages per method and accumulate sizes.

        Args:
            package (str): Package name.
        """
        logger.debug("Calculating summary for package '%s' in mode '%s'.", package, self.mode)
        installed: str = self.utils.is_package_installed(package)

        # Accumulate sizes for binary packages (not SBo/Ponce repos)
        # and if self.data is available for the package.
        if self.repository not in list(self.repos.repositories)[:2] and self.data.get(package):
            self.sum_size_comp += float(self.data[package].get('size_comp', 0)) * 1024
            self.sum_size_uncomp += float(self.data[package].get('size_uncomp', 0)) * 1024
            logger.debug("Accumulated sizes for binary package '%s': comp=%.2f, uncomp=%.2f",
                         package, self.sum_size_comp, self.sum_size_uncomp)

        # Accumulate size for packages being removed.
        if installed and self.mode == 'remove':
            pkg_size_for_removal = self.utils.count_file_size(package)
            self.sum_size_remove += pkg_size_for_removal
            logger.debug("Accumulated removal size for '%s': %d", package, pkg_size_for_removal)

        upgradeable: bool = False
        if self.mode != 'remove':
            upgradeable = self.upgrade.is_package_upgradeable(installed) if installed else False
            logger.debug("Package '%s' upgradeable status: %s", package, upgradeable)

        # Count packages based on mode and status.
        if not installed:
            self.sum_install += 1
            logger.debug("Counted '%s' as new install. Total installs: %d", package, self.sum_install)
        elif installed and self.option_for_reinstall:
            self.sum_upgrade += 1
            logger.debug("Counted '%s' as reinstall/upgrade. Total upgrades: %d", package, self.sum_upgrade)
        elif upgradeable:
            self.sum_upgrade += 1
            logger.debug("Counted '%s' as upgrade. Total upgrades: %d", package, self.sum_upgrade)
        elif installed and self.mode == 'remove':
            self.sum_remove += 1
            logger.debug("Counted '%s' as removal. Total removes: %d", package, self.sum_remove)
        logger.debug("Summary calculation complete for package '%s'.", package)

    def set_summary_for_build(self, packages: list[str]) -> None:
        """Set summary message for build.

        Args:
            packages (list): List of packages.
        """
        logger.debug("Setting summary message for 'build' mode.")
        self.summary_message = (
            f'{self.grey}Total {len(packages)} packages '
            f'will be build in {self.tmp_path} folder.{self.endc}')
        logger.info("Build summary message set: '%s'", self.summary_message.strip())

    def set_summary_for_install_and_upgrade(self, install: int, upgrade: int, size_comp: float, size_uncomp: float) -> None:
        """Set summary for install or upgrade.

        Args:
            install (int): Counts for installs.
            upgrade (int): Counts for upgrades.
            size_comp (float): Counts of compressed sizes.
            size_uncomp (float): Counts of uncompressed sizes.
        """
        logger.debug("Setting summary message for 'install/upgrade' mode. Installs: %d, Upgrades: %d, Comp Size: %.2f, Uncomp Size: %.2f",
                     install, upgrade, size_comp, size_uncomp)
        # upgrade_message: str = '' # This variable was declared but unused in original, removed.
        total_packages: str = (f'{self.grey}Total {install} packages will be installed and {upgrade} '
                               f'will be upgraded.')
        total_sizes: str = (f'\nAfter process {self.utils.convert_file_sizes(size_comp)} will be downloaded and '
                            f'{self.utils.convert_file_sizes(size_uncomp)} will be installed.{self.endc}')
        self.summary_message = f'{total_packages}{total_sizes}'
        logger.info("Install/Upgrade summary message set: '%s'", self.summary_message.strip())

    def set_summary_for_remove(self, remove: int, size_rmv: int) -> None:
        """Set summary for removes.

        Args:
            remove (int): Counts of removes.
            size_rmv (int): Size of removes.
        """
        logger.debug("Setting summary message for 'remove' mode. Removes: %d, Size: %d", remove, size_rmv)
        self.summary_message = (
            f'{self.grey}Total {remove} packages '
            f'will be removed and {self.utils.convert_file_sizes(size_rmv)} '
            f'of space will be freed up.{self.endc}')
        logger.info("Remove summary message set: '%s'", self.summary_message.strip())

    def set_summary_for_download(self, packages: list[str], size_comp: float) -> None:
        """Set summary for downloads.

        Args:
            packages (list[str]): List of packages.
            size_comp (float): Size of downloads.
        """
        logger.debug("Setting summary message for 'download' mode. Packages: %d, Comp Size: %.2f, Directory: %s",
                     len(packages), size_comp, self.download_only)
        self.summary_message = (
            f'{self.grey}Total {len(packages)} packages and {self.utils.convert_file_sizes(size_comp)} '
            f'will be downloaded in {self.download_only} folder.{self.endc}')
        logger.info("Download summary message set: '%s'", self.summary_message.strip())

    def build_package_and_version(self, package: str) -> str:
        """Build package and version string for display.

        Args:
            package (str): Package name.

        Returns:
            str: Package name with its installed version (e.g., 'foo-1.0').
        """
        logger.debug("Building package and version string for display for: %s", package)
        installed_package: str = self.utils.is_package_installed(package)
        version: str = 'N/A'
        if installed_package:
            version = self.utils.split_package(installed_package)['version']
            logger.debug("Found installed version '%s' for '%s'.", version, package)
        else:
            logger.warning("Package '%s' is not installed, cannot get installed version for display.", package)
        return f'{package}-{version}'

    def skipping_packages(self, packages: list[str]) -> None:
        """View skipped packages.

        Args:
            packages (list[str]): List of packages.
        """
        logger.info("Displaying skipped packages: %s", packages)
        if packages:
            print('Packages skipped by the user:\n')
            for name in packages:
                # Ensure self.data.get(name) and then .get('package') are handled safely
                package_display_name = self.data.get(name, {}).get('package', name)
                print(f"\r {self.red}{self.imp.skipped:<8}{self.endc}: {package_display_name} {' ' * 17}")
                logger.debug("Displayed skipped package: '%s'", package_display_name)
            print()
        else:
            logger.debug("No packages to display as skipped.")

    def missing_dependencies(self, packages: list[str]) -> None:
        """View for missing dependencies.

        Args:
            packages (list[str]): Name of packages.
        """
        logger.info("Checking for and displaying missing dependencies for packages: %s", packages)
        if self.view_missing_deps:
            missing_deps: dict[str, list[str]] = {}
            for package in packages:
                # Ensure 'requires' key exists and is a list.
                requires_data: Union[str, list[str]] = self.data.get(package, {}).get('requires', [])
                # Ensure requires is a list, even if it's not from .get() (though .get() handles it).
                requires: list[str] = list(requires_data) if isinstance(requires_data, list) else []
                logger.debug("Checking dependencies for '%s': %s", package, requires)

                current_missing = [req for req in requires if req not in self.data]
                if current_missing:
                    missing_deps[package] = current_missing
                    logger.warning("Found missing dependencies for '%s': %s", package, current_missing)

            if missing_deps:
                print('\nPackages with missing dependencies:')
                for pkg, deps in missing_deps.items():
                    if deps:  # Check if deps list is not empty.
                        print(f"{'':>1}{pkg} "
                              f"({len(deps)}):\n{'':>4}{self.red}{', '.join(deps)}{self.endc}")
                print()
                logger.info("Displayed packages with missing dependencies.")
            else:
                logger.debug("No packages found with missing dependencies.")
        else:
            logger.info("Option 'view_missing_deps' is disabled. Skipping missing dependencies check.")

    def question(self, message: str = 'Do you want to continue?') -> None:
        """View a question and get user input.

        Args:
            message (str, optional): Message of question.

        Raises:
            SystemExit: Raise an exit code 0 if user aborts.
        """
        logger.info("Asking user question: '%s'. Ask question enabled: %s, Answer yes enabled: %s",
                    message, self.ask_question, self.answer_yes)
        if self.ask_question:
            try:
                if self.answer_yes:
                    answer: str = 'y'
                    logger.debug("Auto-answered 'yes' to question due to config.")
                else:
                    answer = input(f'{message} [y/N] ')
                    logger.debug("User input for question: '%s'", answer)
            except (KeyboardInterrupt, EOFError) as err:
                print('\nOperation canceled by the user.')
                logger.warning("Operation cancelled by user via KeyboardInterrupt/EOFError.", exc_info=True)
                raise SystemExit(1) from err

            if answer.lower() not in ['y', 'yes']:  # pylint: disable=[R1720]
                print('Operation aborted by the user.')
                logger.info("Operation aborted by user (answered '%s').", answer)
                raise SystemExit(0)  # Exit if user explicitly says no or similar.
            else:
                logger.debug("User confirmed to continue.")
        else:
            logger.info("Skipping question as 'ask_question' is disabled. Proceeding without explicit confirmation.")
        print()
