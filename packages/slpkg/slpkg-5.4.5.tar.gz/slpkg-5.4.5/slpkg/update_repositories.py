#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import re
import subprocess
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any

from slpkg.check_updates import CheckUpdates
from slpkg.config import config_load
from slpkg.downloader import Downloader
from slpkg.install_data import InstallData
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.sbos.sbo_generate import SBoGenerate
from slpkg.utilities import Utilities
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class UpdateRepositories:  # pylint: disable=[R0902]
    """Update the local repositories."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        logger.debug("Initializing UpdateRepositories module with options: %s, repository: %s", options, repository)
        self.gpg_verification = config_load.gpg_verification
        self.ask_question = config_load.ask_question
        self.git_clone = config_load.git_clone
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc
        self.lftp_mirror_options = config_load.lftp_mirror_options

        self.view = View(options)
        self.multi_process = MultiProcess(options)
        self.repos = Repositories()
        self.utils = Utilities()
        self.data = InstallData()
        self.generate = SBoGenerate()
        self.check_updates = CheckUpdates(options, repository)
        self.download = Downloader(options)

        self.repos_for_update: dict[str, bool] = {}
        logger.debug("UpdateRepositories module initialized. GPG verification: %s, Git clone command: %s", self.gpg_verification, self.git_clone)

    def repositories(self) -> None:
        """Check and call the repositories for update."""
        logger.info("Checking for repository updates.")
        self.repos_for_update = self.check_updates.updates()

        if not any(list(self.repos_for_update.values())):
            logger.info("No repositories require update based on checksums. Asking user for force update.")
            self.view.question(message='Do you want to force update?')
            # Force update the repositories.
            for repo in self.repos_for_update:
                self.repos_for_update[repo] = True
            logger.info("All repositories marked for forced update.")
        else:
            logger.info("The following repositories require update: %s", {k: v for k, v in self.repos_for_update.items() if v})

        self.run_update()
        logger.info("Repository update process completed.")

    def import_gpg_key(self, repo: str) -> None:
        """Import the GPG KEY for a given repository.

        Args:
            repo (str): Repository name.
        """
        logger.debug("Attempting to import GPG key for repository: %s", repo)
        if self.gpg_verification:
            logger.debug("GPG verification is enabled.")
            mirror: str = self.repos.repositories[repo]['mirror_changelog']

            if repo == self.repos.sbo_repo_name:
                mirror = 'https://www.slackbuilds.org/'
                logger.debug("Adjusting GPG key mirror for SBo repository to: %s", mirror)

            gpg_key: str = f'{mirror}GPG-KEY'
            gpg_command: str = 'gpg --fetch-key'
            logger.debug("Attempting to fetch GPG key from %s using command: %s %s", gpg_key, gpg_command, gpg_key)

            try:
                process = subprocess.run(f'{gpg_command} {gpg_key}', shell=True, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, encoding='utf-8', text=True, check=True)

                logger.info("GPG key fetch attempt 1 successful for %s. Output: %s", gpg_key, process.stdout.strip())
                self._getting_gpg_print(process, mirror)
            except subprocess.CalledProcessError as e:
                logger.warning("GPG key fetch attempt 1 failed for %s. Error: %s. Output: %s", gpg_key, e, e.stdout.strip())
                # Fallback to packages mirror if changelog mirror fails.
                mirror = self.repos.repositories[repo]['mirror_packages']
                gpg_key = f'{mirror}GPG-KEY'
                logger.debug("GPG key fetch attempt 1 failed. Trying fallback mirror: %s", gpg_key)

                try:
                    process = subprocess.run(f'{gpg_command} {gpg_key}', shell=True, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT, encoding='utf-8', text=True, check=True)
                    logger.info("GPG key fetch attempt 2 successful for %s. Output: %s", gpg_key, process.stdout.strip())
                    self._getting_gpg_print(process, mirror)
                except subprocess.CalledProcessError:
                    logger.error("GPG key fetch attempt 2 failed for %s. Error: %s. Output: %s", gpg_key, e, e.stdout.strip())
                    print(f'Getting GPG key: {self.red}Failed{self.endc}')
                    self.view.question()
                    logger.critical("GPG key import failed after all attempts. Application may exit.")
        else:
            logger.info("GPG verification is disabled. Skipping GPG key import for repository: %s", repo)

    @staticmethod
    def _getting_gpg_print(process: CompletedProcess, mirror: str) -> None:  # type: ignore
        """Print the gpg mirror and log GPG key import status.

        Args:
            process: Subprocess process output.
            mirror: The GPG key mirror URL.
        """
        output: list[str | Any] = re.split(r"/|\s", process.stdout)
        if process.returncode == 0 and 'imported:' in output:
            print(f'Getting GPG key from: {mirror}\n')
            logger.info("GPG key successfully imported from: %s", mirror)
        else:
            # This case might indicate a successful run but no 'imported' message, or an unexpected output
            logger.warning("GPG key import status unclear for %s. Return code: %s, Output: %s", mirror, process.returncode, process.stdout.strip())

    def run_update(self) -> None:
        """Update the repositories by category (binary or SlackBuilds)."""
        logger.info("Starting repository update execution.")
        for repo, update in self.repos_for_update.items():
            if update:
                logger.info("Updating repository: %s", repo)
                self.view_downloading_message(repo)
                if repo in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                    logger.debug("Repository '%s' is a SlackBuilds repository. Calling update_slackbuild_repos.", repo)
                    self.update_slackbuild_repos(repo)
                else:
                    logger.debug("Repository '%s' is a binary repository. Calling update_binary_repos.", repo)
                    self.update_binary_repos(repo)
            else:
                logger.info("Skipping repository '%s' as it does not require an update.", repo)

    def view_downloading_message(self, repo: str) -> None:
        """Print the syncing message to the console.

        Args:
            repo (str): Repository name.
        """
        print(f"Syncing with the repository '{self.green}{repo}{self.endc}', please wait...\n")

    def update_binary_repos(self, repo: str) -> None:
        """Update the binary repositories by downloading changelog, packages, and checksums.

        Args:
            repo (str): Repository name.
        """
        urls: dict[str, tuple[tuple[str, str, str], Path]] = {}

        self.import_gpg_key(repo)

        # Construct URLs for changelog, packages, and checksums
        changelog: str = (f"{self.repos.repositories[repo]['mirror_changelog']}"
                          f"{self.repos.repositories[repo]['changelog_txt']}")
        packages: str = (f"{self.repos.repositories[repo]['mirror_packages']}"
                         f"{self.repos.repositories[repo]['packages_txt']}")
        checksums: str = (f"{self.repos.repositories[repo]['mirror_packages']}"
                          f"{self.repos.repositories[repo]['checksums_md5']}")

        logger.debug("Binary repo URLs: Changelog=%s, Packages=%s, Checksums=%s", changelog, packages, checksums)
        urls[repo] = ((changelog, packages, checksums), self.repos.repositories[repo]['path'])

        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['changelog_txt'])
        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['packages_txt'])
        self.utils.remove_file_if_exists(self.repos.repositories[repo]['path'],
                                         self.repos.repositories[repo]['checksums_md5'])

        # Ensure the repository directory exists.
        self.utils.create_directory(self.repos.repositories[repo]['path'])

        # Download the files.
        logger.info("Downloading repository data for %s...", repo)
        self.download.download(urls)
        self.data.install_binary_data(repo)
        logger.info("Binary data installation completed for %s.", repo)

    def update_slackbuild_repos(self, repo: str) -> None:
        """Update the SlackBuild repositories using Git or LFTP.

        Args:
            repo (str): Repository name.
        """
        logger.info("Updating SlackBuild repository: %s", repo)
        self.import_gpg_key(repo)

        mirror: str = self.repos.repositories[repo]['mirror_packages']

        git_mirror: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
            self.repos.ponce_repo_name: self.repos.ponce_git_mirror
        }

        repo_path: Path = self.repos.repositories[repo]['path']

        syncing_command: str
        if '.git' in git_mirror[repo]:
            logger.debug("Git mirror detected for '%s': %s. Removing existing folder and cloning.", repo, git_mirror[repo])
            self.utils.remove_folder_if_exists(repo_path)
            syncing_command = f'{self.git_clone} {git_mirror[repo]} {repo_path}'
        else:
            logger.debug("LFTP mirror detected for '%s': %s. Removing specific files and mirroring.", repo, mirror)
            self.utils.remove_file_if_exists(repo_path, self.repos.repositories[repo]['slackbuilds_txt'])
            self.utils.remove_file_if_exists(repo_path, self.repos.repositories[repo]['changelog_txt'])
            self.utils.create_directory(repo_path)
            syncing_command = f'lftp {self.lftp_mirror_options} {mirror} {repo_path}'

        logger.info("Executing sync command for '%s': %s", repo, syncing_command)
        self.multi_process.process(syncing_command)
        logger.info("Sync command completed for '%s'.", repo)

        # It checks if there is a SLACKBUILDS.TXT file, otherwise it's going to create one.
        slackbuilds_txt_path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['slackbuilds_txt'])
        if not slackbuilds_txt_path.is_file():
            logger.warning("SLACKBUILDS.TXT not found at '%s'. Attempting to generate it.", slackbuilds_txt_path)
            if '.git' in git_mirror[repo]:
                print()
            self.generate.slackbuild_file(self.repos.repositories[repo]['path'],
                                          self.repos.repositories[repo]['slackbuilds_txt'])
            logger.info("SLACKBUILDS.TXT generated for '%s'.", repo)
        else:
            logger.debug("SLACKBUILDS.TXT found at '%s'. No generation needed.", slackbuilds_txt_path)

        logger.info("Installing SlackBuilds data for repository: %s", repo)
        self.data.install_sbo_data(repo)
        logger.info("SlackBuilds data installation completed for %s.", repo)
