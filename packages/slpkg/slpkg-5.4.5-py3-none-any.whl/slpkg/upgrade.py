#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import platform
import shutil
from pathlib import Path
from typing import Generator, Optional, Union, cast

from packaging.version import InvalidVersion, parse

from slpkg.config import config_load
from slpkg.load_data import LoadData
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Upgrade:  # pylint: disable=[R0902]
    """Upgrade the installed packages."""

    def __init__(self, repository: Optional[str], data: Optional[Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]]]) -> None:
        logger.debug("Initializing Upgrade module with repository: %s, data present: %s", repository, bool(data))
        self.repository = cast(str, repository)  # Informs mypy that it will NOT be None.
        self.data = cast(Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]], data)

        self.log_packages = config_load.log_packages
        self.kernel_version = config_load.kernel_version
        self.package_method = config_load.package_method
        self.downgrade_packages = config_load.downgrade_packages
        self.grey = config_load.grey
        self.yellow = config_load.yellow
        self.red = config_load.red
        self.green = config_load.green
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()
        self.load_data = LoadData()

        self.id: int = 0
        self.log_id: int = 0
        self.sum_upgrade: int = 0
        self.sum_removed: int = 0
        self.sum_added: int = 0
        self.installed_packages: list[Path] = []

        self.kernel_ver: str = platform.uname()[2]
        self.columns, self.rows = shutil.get_terminal_size()
        logger.debug("Upgrade module initialized. Kernel version: %s, Terminal size: %sx%s", self.kernel_ver, self.columns, self.rows)

    def _load_installed_packages(self, repository: str) -> None:
        """Load installed packages from /var/log/packages or based on repository tags.

        Args:
            repository (str): Repository name (e.g., 'slackware', 'slackware64-extra').
        """
        logger.debug("Loading installed packages for repository: %s", repository)
        if repository == self.repos.slack_repo_name:
            extra_repo: dict[str, dict[str, str]] = {}

            extra_data_file: Path = Path(self.repos.repositories[self.repos.slack_extra_repo_name]['path'],
                                         self.repos.data_json)

            if self.repos.repositories[self.repos.slack_extra_repo_name]['enable'] and extra_data_file.is_file():
                logger.debug("Slackware extra repository enabled and data file exists: %s", extra_data_file)
                extra_repo = self.load_data.load(self.repos.slack_extra_repo_name, message=False)
            else:
                logger.debug("Slackware extra repository not enabled or data file not found: %s", extra_data_file)

            installed: dict[str, str] = self.utils.all_installed()

            for name, package in installed.items():
                tag: str = self.utils.split_package(package)['tag']
                if not tag:  # Add only Slackware original packages that have not package tag.
                    if extra_repo.get(name):  # Avoid installed packages from extra repository.
                        extra_package: str = extra_repo[name]['package']
                        if extra_package[:-4] != package:
                            logger.debug("Adding Slackware original package '%s' (not matching extra repo) to installed list.", package)
                            self.installed_packages.append(Path(package))
                    else:
                        self.installed_packages.append(Path(package))
        else:
            repo_tag: str = self.repos.repositories[repository]['repo_tag']
            logger.debug("Loading installed packages with repository tag '%s' for '%s'.", repo_tag, repository)
            self.installed_packages = list(self.log_packages.glob(f'*{repo_tag}'))
        logger.info("Loaded %d installed packages for repository '%s'.", len(self.installed_packages), repository)

    def packages(self) -> Generator[str, str, str]:
        """Generate upgradeable, removable, and new packages based on repository data.

        This method acts as a generator, yielding package names with a suffix
        indicating their status ('_Removed.' or '_Added.') or just the name for upgradeable.
        """
        logger.debug("Starting package generation for upgrade/removal/addition.")
        # Load installed packages relevant to the current repository context.
        self._load_installed_packages(self.repository)

        # Iterate through loaded installed packages to find upgradeable ones.
        for inst in self.installed_packages:
            name: str = self.utils.split_package(inst.name)['name']

            if self.is_package_upgradeable(inst.name):
                logger.info("Found upgradeable package: %s", name)
                yield name

            if self.repository in self.repos.remove_packages:
                # If the installed package's name is not found in the current repository's data,
                # it means it's no longer offered by this repo and might be a candidate for removal.
                if name not in self.data.keys():
                    logger.info("Package '%s' found for removal (not in repository data).", name)
                    yield f'{name}_Removed.'

        # Check for new packages in the repository.
        if self.repository in self.repos.new_packages:
            # logger.debug("Checking for new packages in repository: %s", self.repository)
            # Get only the names of all installed packages for efficient lookup.
            all_installed: dict[str, str] = self.utils.all_installed()
            for name in self.data.keys():
                # If a package from the repository is not currently installed.
                if name not in all_installed:
                    logger.info("New package '%s' found for addition (not currently installed).", name)
                    yield f'{name}_Added.'

        logger.debug("Finished generating packages.")
        # Return an empty string to satisfy type hint for Generator,
        # as generators implicitly return None when exhausted.
        return ""

    def is_package_upgradeable(self, installed: str) -> bool:  # pylint: disable=[R0911]
        """Determine if an installed package is upgradeable based on repository data.

        Args:
            installed (str): Full name of the installed package (e.g., 'foo-1.0-x86_64-1.t?z').

        Returns:
            bool: True if the package is upgradeable, False otherwise.
        """
        inst_name: str = self.utils.split_package(installed)['name']
        logger.debug("Checking upgradeability for installed package: %s (name: %s)", installed, inst_name)

        # Check if repository data exists for the installed package's name.
        if self.data.get(inst_name):
            repo_version: str = self.data[inst_name]['version']  # type: ignore
            repo_build: str = self.data[inst_name]['build']  # type: ignore
            logger.debug("Repository data found for '%s': Version=%s, Build=%s", inst_name, repo_version, repo_build)

            inst_version: str = self.utils.split_package(installed)['version']

            # Adjust installed version if kernel_version flag is set and it matches current kernel.
            if self.kernel_version and inst_version.endswith(f'_{self.kernel_ver}'):
                original_inst_version = inst_version  # Store original for logging
                original_installed = installed  # Store original for logging
                inst_version = inst_version.replace(f'_{self.kernel_ver}', '')
                installed = installed.replace(f'_{self.kernel_ver}', '')  # Update 'installed' for subsequent split_package calls
                logger.debug("Adjusted installed package '%s' (original version '%s') for kernel version comparison: new version='%s', new package name='%s'", original_installed, original_inst_version, inst_version, installed)

            inst_build: str = self.utils.split_package(installed)['build']
            logger.debug("Installed package '%s' details: Version=%s, Build=%s", inst_name, inst_version, inst_build)

            # Compare packages based on the 'package_method' configuration.
            if self.package_method:
                repo_package: str = self.data[inst_name]['package'][:-4]  # type: ignore
                logger.debug("Using package method for comparison. Installed: %s, Repo: %s", installed, repo_package)
                if installed != repo_package:
                    logger.info("Package '%s' is upgradeable (package method: full names differ).", inst_name)
                    return True

            else:  # Using version parsing method (packaging.version.parse).
                try:
                    parsed_repo_version = parse(repo_version)
                    parsed_inst_version = parse(inst_version)
                    logger.debug("Comparing versions using parse() for '%s': Repo=%s, Installed=%s", inst_name, parsed_repo_version, parsed_inst_version)

                    # Check for newer version.
                    if parse(repo_version) > parse(inst_version):
                        logger.info("Package '%s' is upgradeable (repo version '%s' > installed version '%s').", inst_name, repo_version, inst_version)
                        return True

                    # Check for same version but newer build.
                    if parse(repo_version) == parse(inst_version) and int(repo_build) > int(inst_build):
                        logger.info("Package '%s' is upgradeable (same version, repo build '%s' > installed build '%s').", inst_name, repo_build, inst_build)
                        return True

                    # Check for downgrade if enabled.
                    if self.downgrade_packages and (parse(repo_version) < parse(inst_version)):
                        logger.info("Package '%s' is downgradeable (repo version '%s' < installed version '%s') and downgrade is enabled.", inst_name, repo_version, inst_version)
                        return True
                except InvalidVersion as err:
                    # Fallback to string comparison if version parsing fails (e.g., malformed version string).
                    logger.warning("Invalid version format encountered for '%s' (installed: %s, repo: %s). Falling back to string comparison. Error: %s",
                                   inst_name, installed, self.data[inst_name]['package'], err)
                    if repo_version > inst_version:  # Try to compare the strings.
                        logger.info("Package '%s' is upgradeable (string comparison fallback: repo version '%s' > installed version '%s').", inst_name, repo_version, inst_version)
                        return True
                    if repo_version == inst_version and int(repo_build) > int(inst_build):
                        logger.info("Package '%s' is upgradeable (string comparison fallback: same version, repo build '%s' > installed build '%s').", inst_name, repo_build, inst_build)
                        return True
                    logger.debug("Package '%s' is not upgradeable/downgradeable based on string comparison fallback.", inst_name)
        else:
            logger.debug("No repository data found for package '%s'. Not upgradeable.", inst_name)

        return False

    def check_packages(self) -> None:
        """Check all configured repositories for upgradeable, removable, and new packages.
        Populates internal counters and 'found_packages' dictionary.
        """
        logger.info("Starting check for upgradeable, removable, and new packages.")
        repo_data: dict[str, dict[str, dict[str, str]]] = {}
        found_packages: dict[int, dict[str, str]] = {}

        # Determine which repositories to check based on 'self.repository'.
        if self.repository == '*':
            repo_data = self.data  # type: ignore  # Assuming self.data is the full multi-repo dict here.
            logger.debug("Checking all repositories as '*' was specified.")
        else:
            repo_data[self.repository] = self.data  # type: ignore  # Assuming self.data is single repo dict here.
            logger.debug("Checking specific repository: %s", self.repository)

        for repo, data in repo_data.items():
            logger.debug("Processing repository '%s' for checks.", repo)
            self._load_installed_packages(repo)

            for installed in sorted(self.installed_packages):
                name: str = self.utils.split_package(installed.name)['name']
                logger.debug("Evaluating installed package '%s' from repository '%s'.", installed.name, repo)

                # Check if the installed package exists in the current repository's data.
                if data.get(name):
                    # Temporarily set self.data to the current repository's data for is_package_upgradeable.
                    # This is important because is_package_upgradeable uses self.data.
                    self.data = data

                    if self.is_package_upgradeable(installed.name):
                        self.id += 1
                        self.sum_upgrade += 1

                        # Get package details for logging and storing in found_packages.
                        inst_version: str = self.utils.split_package(installed.name)['version']
                        inst_build: str = self.utils.split_package(installed.name)['build']
                        repo_version: str = data[name]['version']
                        repo_build: str = data[name]['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': repo,
                            'type': 'upgrade'
                        }
                        logger.debug("Package '%s' identified for upgrade (installed: %s-%s, repo: %s-%s).",
                                     name, inst_version, inst_build, repo_version, repo_build)

                # Check if the repository is configured to handle removals.
                if repo in self.repos.remove_packages:
                    tag: str = self.utils.split_package(installed.name)['tag']
                    # A package is a candidate for removal if it has no tag AND is not in the current repo's data.
                    if not tag and name not in data.keys():
                        self.id += 1
                        self.sum_removed += 1
                        inst_version = self.utils.split_package(installed.name)['version']
                        inst_build = self.utils.split_package(installed.name)['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': '',
                            'repo_build': '',
                            'repo': repo,
                            'type': 'remove'
                        }
                        logger.debug("Package '%s' identified for removal (installed: %s-%s, no repo counterpart, no tag).",
                                     name, inst_version, inst_build)

            # Check for new packages in the current repository.
            if repo in self.repos.new_packages:
                logger.debug("Checking for new packages in repository '%s'.", repo)
                all_installed_names = self.utils.all_installed().keys()  # Get just keys for faster lookup.
                for name in data.keys():  # Get just keys for faster lookup
                    if name not in all_installed_names:  # If the package is not currently installed
                        self.id += 1
                        self.sum_added += 1
                        repo_version = data[name]['version']
                        repo_build = data[name]['build']

                        found_packages[self.id] = {
                            'name': name,
                            'inst_version': '',  # No installed version for new packages
                            'inst_build': '',  # No installed build for new packages
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': repo,
                            'type': 'add'
                        }
                        logger.debug("New package '%s' identified for addition (repo: %s-%s).",
                                     name, repo_version, repo_build)

        # Call the private method to display results to the console.
        self._results(found_packages)
        # Log summary of findings after displaying.
        logger.info("Finished checking packages. Total found: %d (Upgrade: %d, Removed: %d, Added: %d)",
                    len(found_packages), self.sum_upgrade, self.sum_removed, self.sum_added)

    def _results(self, found_packages: dict[int, dict[str, str]]) -> None:
        """Print the results of checking to the console.

        Args:
            found_packages (dict[int, dict[str, str]]): Dictionary of packages found for
                                                         upgrade, removal, or addition.

        Raises:
            SystemExit: Exits the application with status 0 after displaying results.
        """
        logger.debug("Displaying results of package check to console.")
        if found_packages:
            print()

            name_alignment: int = 18
            if self.columns > 80:
                name_alignment = (self.columns - 80) + 18

            title: str = (f"{'packages':<{name_alignment}} {'Repository':<15} {'Build':<6} {'Installed':<15} "
                          f"{'Build':<5} {'Repo':>15}")
            print(len(title) * '=')
            print(title)
            print(len(title) * '=')

            for data in found_packages.values():
                name: str = data['name']
                repo_version: str = data['repo_version']
                repo_build: str = data['repo_build']
                inst_version: str = data['inst_version']
                inst_build: str = data['inst_build']
                repo: str = data['repo']
                mode: str = data['type']

                # Truncate long names/versions for display.
                if len(name) > name_alignment:
                    name = f'{name[:name_alignment - 4]}...'
                if len(inst_version) > 15:
                    inst_version = f"{inst_version[:11]}..."
                if len(repo_version) > 15:
                    repo_version = f"{repo_version[:11]}..."

                # Assign colors based on package type
                color: str = self.yellow
                if mode == 'remove':
                    color = self.red
                if mode == 'add':
                    color = self.green

                # Print formatted package information to console.
                print(f"{color}{name:<{name_alignment}}{self.endc} {repo_version:<15} "
                      f"{repo_build:<6} {inst_version:<15} "
                      f"{inst_build:<5} {repo:>15}")

            print(len(title) * '=')
            print(f'{self.grey}Total packages: {self.sum_upgrade} upgraded, '
                  f'{self.sum_removed} removed and {self.sum_added} added.{self.endc}\n')
            logger.info("Results displayed to console: %d upgraded, %d removed, %d added.", self.sum_upgrade, self.sum_removed, self.sum_added)

        else:
            print('\nEverything is up-to-date!\n')
            logger.info("No packages found for upgrade, removal, or addition. Displayed 'Everything is up-to-date!' message.")

        raise SystemExit(0)
