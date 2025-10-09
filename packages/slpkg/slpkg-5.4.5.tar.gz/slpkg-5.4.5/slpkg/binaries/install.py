#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import time
from collections import OrderedDict
from pathlib import Path

from slpkg.binaries.required import Required
from slpkg.checksum import Md5sum
from slpkg.choose_dependencies import ChooseDependencies
from slpkg.config import config_load
from slpkg.dependency_logger import DependencyLogger
from slpkg.dialog_box import DialogBox
from slpkg.downloader import Downloader
from slpkg.gpg_verify import GPGVerify
from slpkg.multi_process import MultiProcess
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class Packages:  # pylint: disable=[R0902]
    """Download and install packages with dependencies."""

    def __init__(self, repository: str, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool], mode: str) -> None:  # pylint: disable=[R0913, R0917]
        logger.debug("Initializing Packages module for repository: '%s', mode: '%s', with %d packages and options: %s",
                     repository, mode, len(packages), options)
        self.repository = repository
        self.data = data
        self.packages = packages
        self.options = options
        self.mode = mode

        self.tmp_slpkg = config_load.tmp_slpkg
        self.gpg_verification = config_load.gpg_verification
        self.process_log_file = config_load.process_log_file
        self.installpkg = config_load.installpkg
        self.reinstall = config_load.reinstall
        self.delete_sources = config_load.delete_sources
        self.dialog = config_load.dialog
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        self.utils = Utilities()
        self.dialogbox = DialogBox()
        self.multi_proc = MultiProcess(options)
        self.view = View(options, repository, data)
        self.view_process = ViewProcess()
        self.check_md5 = Md5sum(options)
        self.download = Downloader(options)
        self.upgrade = Upgrade(repository, data)
        self.gpg = GPGVerify()
        self.choose_package_dependencies = ChooseDependencies(repository, data, options, mode)
        self.dependency_logger = DependencyLogger()

        self.dependencies: list[str] = []
        self.install_order: list[str] = []
        self.binary_packages: list[str] = []
        self.skipped_packages: list[str] = []
        self.progress_message: str = 'Installing'

        self.option_for_reinstall: bool = options.get('option_reinstall', False)
        self.option_for_skip_installed: bool = options.get('option_skip_installed', False)

        self.packages = self.utils.apply_package_pattern(data, packages)
        logger.debug("Initial packages after pattern application: %s", self.packages)

    def execute(self) -> None:
        """Call methods in order."""
        logger.info("Starting package installation process.")
        self.creating_dependencies_list()
        if self.dependencies:
            self.view_process.message('Resolving dependencies')
            logger.debug("Dependencies list created. Resolving dependencies with user choice.")
        self.dependencies = self.choose_package_dependencies.choose(self.dependencies, self.view_process)
        logger.debug("Final dependencies after user choice: %s", self.dependencies)

        self.add_dependencies_to_install_order()
        self.clean_the_main_slackbuilds()
        self.add_main_packages_to_install_order()
        self.check_for_skipped()
        logger.debug("Install order after processing: %s", self.install_order)
        logger.debug("Skipped packages: %s", self.skipped_packages)

        self.view.install_upgrade_packages(self.packages, self.dependencies, self.mode)
        self.view.missing_dependencies(self.install_order)

        self.view.question()

        start: float = time.time()
        self.view.skipping_packages(self.skipped_packages)
        self.creating_the_package_urls_list()
        self.checksum_binary_packages()
        self.set_progress_message()
        self.install_packages()
        elapsed_time: float = time.time() - start

        self.utils.finished_time(elapsed_time)
        logger.info("Package installation process finished in %.2f seconds.", elapsed_time)

    def creating_dependencies_list(self) -> None:
        """Create the full list of dependencies."""
        logger.debug("Creating full list of dependencies.")
        for package in self.packages:
            dependencies: tuple[str, ...] = Required(self.data, package, self.options).resolve()
            for dependency in dependencies:
                self.dependencies.append(dependency)
        self.dependencies = list(OrderedDict.fromkeys(self.dependencies))  # Remove duplicates while preserving order.
        logger.debug("Full dependencies list created: %s", self.dependencies)

    def add_dependencies_to_install_order(self) -> None:
        """Add dependencies in order to install."""
        self.install_order.extend(self.dependencies)
        logger.debug("Dependencies added to install order: %s", self.install_order)

    def clean_the_main_slackbuilds(self) -> None:
        """Remove packages that already listed in dependencies."""
        initial_packages_len = len(self.packages)
        self.packages = [pkg for pkg in self.packages if pkg not in self.dependencies]
        if len(self.packages) < initial_packages_len:
            logger.debug("Removed %d main packages that were already in dependencies.", initial_packages_len - len(self.packages))
        logger.debug("Main packages after cleaning: %s", self.packages)

    def add_main_packages_to_install_order(self) -> None:
        """Add main packages in order to install."""
        self.install_order.extend(self.packages)
        logger.debug("Main packages added to install order: %s", self.install_order)

    def check_for_skipped(self) -> None:
        """Skip packages by user."""
        if self.option_for_skip_installed:
            logger.info("Option 'skip_installed' is enabled. Checking for already installed packages.")
            for name in self.install_order:
                installed: str = self.utils.is_package_installed(name)
                if installed:
                    self.skipped_packages.append(name)
                    logger.debug("Package '%s' is already installed and will be skipped.", name)

        # Remove packages from skipped packages.
        initial_install_order_len = len(self.install_order)
        self.install_order = [pkg for pkg in self.install_order if pkg not in self.skipped_packages]
        if len(self.install_order) < initial_install_order_len:
            logger.info("Removed %d packages from install order due to skipping.", initial_install_order_len - len(self.install_order))
        logger.debug("Final install order after skipping: %s", self.install_order)

    def creating_the_package_urls_list(self) -> None:
        """Prepare package urls for downloading."""
        logger.info("Preparing package URLs for downloading.")
        packages_to_download: dict[str, tuple[list[str], Path]] = {}
        asc_files: list[Path] = []
        if self.install_order:
            self.view_process.message('Prepare sources for downloading')
            for pkg in self.install_order:
                package: str = self.data[pkg]['package']
                mirror: str = self.data[pkg]['mirror']
                location: str = self.data[pkg]['location']
                url: list[str] = [f'{mirror}{location}/{package}']
                asc_url: list[str] = [f'{url[0]}.asc']  # Use url[0] to get the string from the list.
                asc_file: Path = Path(self.tmp_slpkg, f'{package}.asc')

                packages_to_download[pkg] = (url, self.tmp_slpkg)
                logger.debug("Added package '%s' to download list with URL: %s", pkg, url[0])

                if self.gpg_verification:
                    packages_to_download[f'{pkg}.asc'] = (asc_url, self.tmp_slpkg)
                    asc_files.append(asc_file)
                    logger.debug("Added GPG signature for package '%s' to download list.", pkg)

                self.binary_packages.append(package)

            self.view_process.done()
            self.download_the_binary_packages(packages_to_download)
            if self.gpg_verification:
                logger.info("GPG verification enabled. Verifying downloaded ASC files.")
                self.gpg.verify(asc_files)
            else:
                logger.info("GPG verification is disabled.")
        else:
            logger.info("No packages in install order. Skipping URL list creation and download.")

    def download_the_binary_packages(self, packages: dict[str, tuple[list[str], Path]]) -> None:
        """Download the packages.

        Args:
            packages (dict[str, tuple[list[str], Path]]): Packages for downloading.
        """
        if packages:
            logger.info("Starting download of %d binary packages.", len(packages))
            print(f'Started to download total ({len(packages)}) packages:\n')
            self.download.download(packages)
            print()
            logger.info("Binary package download completed.")
        else:
            logger.info("No binary packages to download.")

    def checksum_binary_packages(self) -> None:
        """Checksum packages."""
        logger.info("Starting checksum verification for binary packages.")
        for package in self.binary_packages:
            name: str = self.utils.split_package(Path(package).stem)['name']
            pkg_checksum: str = self.data[name]['checksum']
            logger.debug("Checking MD5 sum for package '%s' (expected: %s).", package, pkg_checksum)
            self.check_md5.md5sum(self.tmp_slpkg, package, pkg_checksum)
        logger.info("Checksum verification completed for all binary packages.")

    def install_packages(self) -> None:
        """Install the packages."""
        logger.info("Starting installation of binary packages.")
        # Remove old process.log file.
        if self.process_log_file.is_file():
            self.process_log_file.unlink()
            logger.debug("Removed old process log file: %s", self.process_log_file)

        if self.binary_packages:
            print(f'Started the processing of ({len(self.binary_packages)}) packages:\n')

            for package in self.binary_packages:
                command: str = f'{self.installpkg} {self.tmp_slpkg}/{package}'
                if self.option_for_reinstall:
                    command = f'{self.reinstall} {self.tmp_slpkg}/{package}'
                    logger.debug("Reinstall option enabled. Command for '%s': %s", package, command)
                else:
                    logger.debug("Install command for '%s': %s", package, command)

                self.multi_proc.process_and_log(command, package, self.progress_message)
                name: str = self.utils.split_package(package)['name']
                resolved_requires: tuple[str, ...] = Required(self.data, name, self.options).resolve()
                self.dependency_logger.write_deps_log(name, resolved_requires)

                if self.delete_sources:
                    self.utils.remove_file_if_exists(self.tmp_slpkg, package)
                    logger.debug("Deleted source file for package '%s'.", package)
        else:
            logger.info("No binary packages to install.")
        logger.info("Binary package installation process completed.")

    def set_progress_message(self) -> None:
        """Set message for upgrade method."""
        if self.mode == 'upgrade' or self.option_for_reinstall:
            self.progress_message = 'Upgrading'
            logger.debug("Progress message set to 'Upgrading' due to mode or reinstall option.")
        else:
            logger.debug("Progress message remains default: '%s'.", self.progress_message)
