#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from typing import Any, Union, cast

from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess

logger = logging.getLogger(__name__)


class SearchPackage:  # pylint: disable=[R0902]
    """Search packages from the repositories."""

    def __init__(self, options: dict[str, bool], packages: list[str], data: Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]], repository: str) -> None:
        logger.debug("Initializing SearchPackage module with %d packages, repository: %s, options: %s",
                     len(packages), repository, options)
        self.packages = packages
        self.data = data
        self.repository = repository

        self.grey = config_load.grey
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()
        self.view_process = ViewProcess()

        self.matching: int = 0
        self.data_dict: dict[int, dict[str, str]] = {}
        self.repo_data: Union[dict[str, str], dict[str, dict[str, str]], Any] = {}
        self.all_data: Union[dict[str, dict[str, dict[str, str]]], dict[str, dict[str, str]]] = {}

        self.option_for_no_case: bool = options.get('option_no_case', False)
        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)
        self.option_for_pkg_description: bool = options.get('option_pkg_description', False)
        logger.debug("SearchPackage module initialized. Case-insensitive: %s, Show version: %s, Show description: %s",
                     self.option_for_no_case, self.option_for_pkg_version, self.option_for_pkg_description)

    def search(self) -> None:
        """Choose between searching all repositories or a specific one."""
        logger.info("Starting package search for packages: %s in repository: %s", self.packages, self.repository)
        self.view_process.message('Please wait for the results')  # Console message.
        if self.repository == '*':
            logger.debug("Searching across all enabled repositories.")
            self.search_to_all_repositories()
        else:
            logger.debug("Searching in specific repository: %s", self.repository)
            self.repo_data = self.data
            self.search_for_the_packages(self.repository)

        self.view_process.done()  # Console message
        print()  # Console formatting
        self.summary_of_searching()
        logger.info("Package search completed. Total matches found: %d", self.matching)

    def search_to_all_repositories(self) -> None:
        """Search package name to all enabled repositories."""
        logger.debug("Iterating through all repositories for search.")
        self.all_data = self.data  # self.data contains all repositories when '*' is used.
        for repo_name, repo_content in self.all_data.items():
            logger.debug("Searching in repository: %s", repo_name)
            self.repo_data = repo_content  # Set current repo's data for search_for_the_packages.
            self.search_for_the_packages(repo_name)

    def search_for_the_packages(self, repo: str) -> None:  # pylint: disable=[R0912]
        """Search for packages within a given repository and save matching data.

        Args:
            repo (str): repository name.
        """
        for package in self.packages:  # pylint: disable=[R1702]
            for name, data_pkg in sorted(self.repo_data.items()):

                if package in name or package == '*' or self.is_not_case_sensitive(package, name):
                    self.matching += 1
                    logger.debug("Match found for query '%s' in package '%s' (Repo: %s). Match count: %d",
                                 package, name, repo, self.matching)

                    installed_status: str = ''
                    is_installed_full_name: str = self.utils.is_package_installed(name)

                    # Determine if the package is installed and if it's the exact version from this repo.
                    if is_installed_full_name:
                        # For all repositories search, check against the specific repo's package name.
                        if self.repository == '*':
                            # Ensure data_pkg is a dict before accessing 'package'.
                            if isinstance(data_pkg, dict) and is_installed_full_name == data_pkg.get('package', '')[:-4]:
                                installed_status = f'[{self.green}installed{self.endc}]'
                                logger.debug("Package '%s' is installed and matches this repo's version (all repos search).", name)
                            else:
                                logger.debug("Package '%s' is installed but does not match this repo's version (all repos search).", name)

                        # For single repository search, check against the main self.data (which is the current repo's data)
                        # Cast self.data to its expected type for mypy to correctly infer string slicing is valid.
                        else:  # This 'else' implies self.repository != '*'.
                            # Explicitly cast self.data to the narrower type for mypy's understanding.
                            single_repo_data: dict[str, dict[str, str]] = cast(dict[str, dict[str, str]], self.data)
                            if is_installed_full_name == single_repo_data.get(name, {}).get('package', '')[:-4]:
                                installed_status = f'[{self.green}installed{self.endc}]'
                                logger.debug("Package '%s' is installed and matches this repo's version (single repo search).", name)
                            else:
                                logger.debug("Package '%s' is installed but does not match this repo's version (single repo search).", name)
                    else:
                        logger.debug("Package '%s' is not currently installed.", name)

                    # Store the found package's details
                    if isinstance(data_pkg, dict):  # Ensure data_pkg is a dict before accessing its keys.
                        self.data_dict[self.matching] = {
                            'repository': repo,
                            'name': name,
                            'version': data_pkg.get('version', 'N/A'),  # Use .get() for safety.
                            'installed': installed_status
                        }
                        logger.debug("Stored match: %s", self.data_dict[self.matching])
                    else:
                        logger.warning("Unexpected data_pkg format for package '%s' in repo '%s'. Expected dict, got %s. Skipping.", name, repo, type(data_pkg))

    def summary_of_searching(self) -> None:
        """Print the search results summary to the console."""
        logger.info("Generating search results summary. Total matches: %d", self.matching)
        repo_length: int = 1
        name_length: int = 1

        try:
            if self.data_dict:  # Only try max() if data_dict is not empty.
                repo_length = max(len(repo_item['repository']) for repo_item in self.data_dict.values())
                name_length = max(len(name_item['name']) + len(name_item['installed']) for name_item in self.data_dict.values())
            logger.debug("Calculated display lengths: repo_length=%d, name_length=%d", repo_length, name_length)
        except ValueError as e:
            # This ValueError would typically mean data_dict is empty, which is handled by self.matching check.
            # But it's good to log if it occurs unexpectedly.
            logger.warning("Error calculating display lengths (likely empty data_dict): %s", e)

        if self.matching:
            # Iterate and print each found package.
            for item in self.data_dict.values():
                name: str = item['name']
                package_name_display: str = f"{name} {item['installed']}"  # Combine name and installed status.

                version_display: str = ''
                if self.option_for_pkg_version:
                    version_display = item['version']
                    logger.debug("Including version '%s' for package '%s'.", version_display, name)

                repository_display: str = ''
                if self.repository == '*':  # Only show repository column if searching all repos.
                    repository_display = f"{item['repository']:<{repo_length}} : "
                    logger.debug("Including repository '%s' for package '%s'.", item['repository'], name)

                description_display: str = ''
                if self.option_for_pkg_description and self.repository != '*':
                    # Explicitly cast self.data to the single-repository data type for mypy.
                    single_repo_data: dict[str, dict[str, str]] = cast(dict[str, dict[str, str]], self.data)
                    if name in single_repo_data:
                        description_display = single_repo_data[name].get('description', 'No description available.')
                        logger.debug("Including description for package '%s': '%s'.", name, description_display)
                    else:
                        description_display = 'Description not available for this package/repo.'
                        logger.warning("Could not retrieve description for package '%s' (repo: %s). Data structure might be unexpected.", name, self.repository)
                    package_name_display = f"{name}: {item['installed']}"  # Adjust format if description is shown.

                # Print main package line to console
                print(f"{repository_display}{package_name_display:<{name_length}} {version_display}")
                if description_display:
                    # Print description line to console, colored green
                    print(f"  {self.yellow}{description_display}{self.endc}")

            # Print total summary to console
            print(f'\n{self.grey}Total found {self.matching} packages.{self.endc}')
            logger.info("Search summary displayed to console. Total matches: %d", self.matching)
        else:
            print('\nDoes not match any package.\n')
            logger.info("No packages matched the search criteria.")

    def is_not_case_sensitive(self, package_query: str, repo_package_name: str) -> bool:
        """Check for case-insensitive match.

        Args:
            package_query (str): The package name queried by the user.
            repo_package_name (str): The package name from the repository.

        Returns:
            bool: True if a case-insensitive match is found and option is enabled, False otherwise.
        """
        if self.option_for_no_case:
            # Log the case-insensitive comparison for debugging
            logger.debug("Performing case-insensitive comparison: '%s' in '%s'", package_query.lower(), repo_package_name.lower())
            return package_query.lower() in repo_package_name.lower()
        return False
