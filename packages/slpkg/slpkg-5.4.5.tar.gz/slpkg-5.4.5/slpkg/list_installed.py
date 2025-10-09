#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from pathlib import Path

from slpkg.config import config_load
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class ListInstalled:  # pylint: disable=[R0902]
    """Find the installed packages."""

    def __init__(self, options: dict[str, bool], packages: list[str]) -> None:
        logger.debug("Initializing ListInstalled module with packages: %s, options: %s", packages, options)
        self.packages = packages

        self.grey = config_load.grey
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.endc = config_load.endc
        self.log_packages = config_load.log_packages

        self.utils = Utilities()
        self.matching: list[str] = []
        self.total_size: int = 0

        self.option_for_no_case: bool = options.get('option_no_case', False)
        self.option_for_pkg_description: bool = options.get('option_pkg_description', False)
        logger.debug("ListInstalled initialized. Case-insensitive option: %s, Package description option: %s",
                     self.option_for_no_case, self.option_for_pkg_description)

    def installed(self) -> None:
        """Find the packages."""
        logger.info("Starting search for installed packages based on queries: %s", self.packages)
        self.view_title()
        all_installed_packages = self.utils.all_installed().values()
        logger.debug("Fetched all %d installed packages.", len(all_installed_packages))

        for package_query in self.packages:
            logger.debug("Processing package query: '%s'", package_query)
            for installed_package_full_name in all_installed_packages:
                if package_query in installed_package_full_name or \
                   package_query == '*' or \
                   self.is_not_case_sensitive(package_query, installed_package_full_name):
                    self.matching.append(installed_package_full_name)
                    logger.debug("Match found for query '%s': '%s'", package_query, installed_package_full_name)
                else:
                    logger.debug("No match for query '%s' with installed package '%s'.", package_query, installed_package_full_name)

        # Remove duplicates from matching list as multiple queries might find the same package
        self.matching = list(set(self.matching))
        logger.info("Finished finding packages. Total unique matches: %d", len(self.matching))
        self.view_matched_packages()

    @staticmethod
    def view_title() -> None:
        """Print the title."""
        print('The list below shows the installed packages:\n')
        logger.debug("Displayed title for installed packages list.")

    def view_matched_packages(self) -> None:
        """Print the matching packages."""
        if self.matching:  # pylint: disable=[R1702]
            logger.info("Displaying %d matching packages.", len(self.matching))
            for package_full_name in sorted(self.matching):  # Sort for consistent output.
                name: str = self.utils.split_package(package_full_name)['name']
                pkg_size: int = self.utils.count_file_size(name)
                size: str = self.utils.convert_file_sizes(pkg_size)
                self.total_size += pkg_size
                print(f'{package_full_name} ({self.green}{size}{self.endc})')
                logger.debug("Displayed package: '%s' with size '%s'.", package_full_name, size)

                if self.option_for_pkg_description:
                    logger.debug("Package description option enabled for '%s'.", package_full_name)
                    pkg_file: Path = Path(self.log_packages, package_full_name)
                    if pkg_file.is_file():
                        pkg_txt_list: list[str] = self.utils.read_text_file(pkg_file)
                        for line in pkg_txt_list:
                            # Look for the line that starts with "name: name" which usually contains the description
                            if line.startswith(f'{name}: {name}'):
                                print(f'{self.yellow}{line[(len(name) * 2) + 2:]}{self.endc}', end='')
                                logger.debug("Displayed description for '%s': '%s'", name, line[(len(name) * 2) + 2:].strip())
                                break
                        else:
                            logger.warning("No description line found in '%s' for package '%s'.", pkg_file, name)
                    else:
                        logger.warning("Package log file not found for description: %s", pkg_file)

            self.view_summary()
        else:
            print('\nDoes not match any package.\n')
            logger.info("No packages matched the search criteria.")

    def view_summary(self) -> None:
        """Print the summary."""
        print(f'\n{self.grey}Total found {len(self.matching)} packages with '
              f'{self.utils.convert_file_sizes(self.total_size)} size.{self.endc}')
        logger.info("Summary displayed: Total found %d packages with %s total size.",
                    len(self.matching), self.utils.convert_file_sizes(self.total_size))

    def is_not_case_sensitive(self, package_query: str, installed_package_name: str) -> bool:
        """Check for case-insensitive.

        Args:
            package_query (str): Package file.
            installed_package_name (str): Name of package.

        Returns:
            bool: True or False.
        """
        if self.option_for_no_case:
            logger.debug("Performing case-insensitive comparison: query='%s' (lower: '%s') in installed='%s' (lower: '%s')",
                         package_query, package_query.lower(), installed_package_name, installed_package_name.lower())
            return package_query.lower() in installed_package_name.lower()
        return False
