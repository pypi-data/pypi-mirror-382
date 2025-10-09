#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import shutil
import time
from pathlib import Path

from slpkg.config import config_load
from slpkg.downloader import Downloader
from slpkg.errors import Errors
from slpkg.gpg_verify import GPGVerify
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class DownloadOnly:  # pylint: disable=[R0902]
    """Download only the sources or packages."""

    def __init__(self, directory: str, options: dict[str, bool], data: dict[str, dict[str, str]], repository: str) -> None:
        logger.debug("Initializing DownloadOnly module with directory: '%s', repository: '%s', options: %s",
                     directory, repository, options)
        self.directory: Path = Path(directory)
        self.options = options
        self.data = data
        self.repository = repository

        self.gpg_verification = config_load.gpg_verification
        self.is_64bit = config_load.is_64bit()

        self.view = View(options, repository, data)
        self.download = Downloader(options)
        self.repos = Repositories()
        self.utils = Utilities()
        self.imp = Imprint()
        self.errors = Errors()
        self.gpg = GPGVerify()

        self.urls: dict[str, tuple[list[str], Path]] = {}
        self.asc_files: list[Path] = []
        self.count_sources: int = 0
        logger.debug("DownloadOnly initialized. GPG verification: %s, Is 64-bit: %s", self.gpg_verification, self.is_64bit)

    def packages(self, packages: list[str]) -> None:
        """Download the packages.

        Args:
            packages (list[str]): List of packages.
        """
        logger.info("Starting package download process for packages: %s", packages)
        if not self.directory.is_dir():
            logger.critical("Download directory '%s' does not exist. Raising error.", self.directory)
            self.errors.message(f"Path '{self.directory}' does not exist", 1)
        else:
            logger.debug("Download directory '%s' exists.", self.directory)

        packages = self.utils.apply_package_pattern(self.data, packages)
        logger.debug("Packages after applying patterns: %s", packages)

        self.view.download_packages(packages, self.directory)
        logger.debug("Displayed download packages view.")
        self.view.question()
        logger.info("User confirmed package download.")
        start: float = time.time()

        print('\rPrepare sources for downloading... ', end='')
        logger.debug("Preparing sources for downloading.")
        for pkg in packages:
            logger.debug("Processing package '%s' for source preparation.", pkg)
            if self.repository in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                self.save_slackbuild_sources(pkg)
                self.copy_slackbuild_scripts(pkg)
                logger.debug("Handled SlackBuild sources and scripts for '%s'.", pkg)
            else:
                self.save_binary_sources(pkg)
                logger.debug("Handled binary sources for '%s'.", pkg)

        print(self.imp.done)
        logger.info("Source preparation completed.")
        self.download_the_sources()

        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)
        logger.info("Package download process completed in %.2f seconds.", elapsed_time)

    def save_binary_sources(self, name: str) -> None:
        """Assign for binary repositories.

        Args:
            name (str): Package name.
        """
        logger.debug("Saving binary sources for package: '%s'.", name)
        package: str = self.data[name]['package']
        mirror: str = self.data[name]['mirror']
        location: str = self.data[name]['location']

        # Main package URL
        url: list[str] = [f'{mirror}{location}/{package}']
        self.count_sources += len(url)
        self.urls[name] = (url, self.directory)
        logger.debug("Added main package URL '%s' to download list.", url[0])

        # ASC file URL and local path for GPG verification
        if self.gpg_verification:
            asc_url: list[str] = [f'{mirror}{location}/{package}.asc']
            asc_file_path: Path = Path(self.directory, f'{package}.asc')
            self.urls[f'{name}_asc'] = (asc_url, self.directory)  # Use a unique key for ASC file.
            self.asc_files.append(asc_file_path)
            logger.debug("Added ASC file URL '%s' and path '%s' for GPG verification.", asc_url[0], asc_file_path)

    def save_slackbuild_sources(self, name: str) -> None:
        """Assign for sbo repositories.

        Args:
            name (str): SBo name.
        """
        logger.debug("Saving SlackBuild sources for package: '%s'.", name)
        sources: list[str] = []
        if self.is_64bit and self.data[name].get('download64'):
            sources = list(self.data[name]['download64'])
            logger.debug("Using 64-bit download sources for '%s': %s", name, sources)
        else:
            sources = list(self.data[name]['download'])
            logger.debug("Using default download sources for '%s': %s", name, sources)

        self.count_sources += len(sources)
        self.urls[name] = (sources, Path(self.directory, name))
        logger.debug("Added SlackBuild source URLs for '%s' to download list.", name)

        # GPG verification for SBo (Ponce is handled differently in gpg_verify)
        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            location: str = self.data[name]['location']
            # Construct the URL for the .asc file from the SBo mirror
            sbo_mirror = self.repos.repositories[self.repos.sbo_repo_name]['mirror_packages']  # Use packages mirror for consistency.
            asc_url: list[str] = [f'{sbo_mirror}{location}/{name}{self.repos.sbo_repo_tar_suffix}.asc']

            # Construct the path where the .asc file will be downloaded
            asc_file_path: Path = Path(self.directory, f'{name}{self.repos.sbo_repo_tar_suffix}.asc')

            self.urls[f'{name}_sbo_asc'] = (asc_url, self.directory)  # Use a unique key for SBo ASC file.
            self.asc_files.append(asc_file_path)
            logger.debug("Added SBo ASC file URL '%s' and path '%s' for GPG verification.", asc_url[0], asc_file_path)

    def copy_slackbuild_scripts(self, name: str) -> None:
        """Copy slackbuilds from local repository to download path.

        Args:
            name (str): SBo name.
        """
        logger.debug("Copying SlackBuild scripts for '%s'.", name)
        repo_path_package: Path = Path(self.repos.repositories[self.repository]['path'],
                                       self.data[name]['location'], name)
        target_directory: Path = Path(self.directory, name)
        if not target_directory.is_dir():
            try:
                shutil.copytree(repo_path_package, target_directory)
                logger.info("Copied SlackBuild scripts from '%s' to '%s'.", repo_path_package, target_directory)
            except shutil.Error as e:
                logger.error("Failed to copy SlackBuild scripts for '%s' from '%s' to '%s': %s",
                             name, repo_path_package, target_directory, e)
            except Exception as e:  # pylint: disable=[W0718]
                logger.critical("An unexpected error occurred while copying SlackBuild scripts for '%s': %s", name, e, exc_info=True)
        else:
            logger.debug("Target directory '%s' already exists for SlackBuild scripts. Skipping copy.", target_directory)

    def download_the_sources(self) -> None:
        """Download the sources."""
        logger.info("Initiating download of all collected sources.")
        if self.urls:
            print(f'Started to download total ({self.count_sources}) sources:\n')
            self.download.download(self.urls, repo_data=[self.repository, self.data[list(self.urls.keys())[0]]['location']])  # Pass repo_data for fallback logic.
            logger.info("All sources downloaded. Proceeding to GPG verification.")
            self.gpg_verify()
        else:
            logger.info("No URLs collected for download. Skipping download and GPG verification.")

    def gpg_verify(self) -> None:
        """Verify files with GPG."""
        logger.debug("Starting GPG verification process.")
        # GPG verification is performed if enabled and if the repository is not Ponce.
        # Ponce typically does not have GPG signed packages in the same way SBo does.
        if self.gpg_verification and self.repository != self.repos.ponce_repo_name:
            if self.asc_files:
                logger.info("GPG verification enabled and ASC files found. Calling GPGVerify.")
                self.gpg.verify(self.asc_files)
            else:
                logger.info("GPG verification enabled, but no ASC files were collected for verification.")
        else:
            logger.info("GPG verification skipped: GPG verification is disabled or repository is '%s'.", self.repository)
