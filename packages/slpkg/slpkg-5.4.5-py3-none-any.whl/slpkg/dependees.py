#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from typing import Any, Generator

from slpkg.config import config_load
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Dependees:  # pylint: disable=[R0902]
    """Prints the packages that depend on."""

    def __init__(self, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool]) -> None:
        logger.debug("Initializing Dependees module with %d packages and options: %s", len(packages), options)
        self.data = data
        self.packages = packages
        self.options = options

        self.bold = config_load.bold
        self.grey = config_load.grey
        self.cyan = config_load.cyan
        self.endc = config_load.endc

        self.utils = Utilities()

        self.option_for_full_reverse: bool = options.get('option_full_reverse', False)
        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)
        logger.debug("Dependees module initialized. Full reverse option: %s, Package version option: %s",
                     self.option_for_full_reverse, self.option_for_pkg_version)

    def find(self) -> None:
        """Call the methods."""
        logger.info("Starting to find packages that depend on the specified ones.")
        print('The list below shows the packages that dependees on:\n')

        logger.debug("Applying package patterns to initial package list: %s", self.packages)
        self.packages = self.utils.apply_package_pattern(self.data, self.packages)
        logger.debug("Package list after applying patterns: %s", self.packages)

        for package in self.packages:
            logger.info("Processing package: %s", package)
            dependees: dict[str, Any] = dict(self.find_requires(package))
            logger.debug("Found %d dependees for package '%s'.", len(dependees), package)

            self.view_the_main_package(package)
            self.view_no_dependees(dependees)
            self.view_dependees(dependees)
            self.view_summary_of_dependees(dependees, package)
        logger.info("Finished finding dependees for all packages.")

    def set_the_package_version(self, package: str) -> str:
        """Set the version of the package.

        Args:
            package (str): Package name.
        """
        logger.debug("Setting package version for: %s", package)
        package_version = ''
        if self.data.get(package):
            package_version = self.data[package]['version']
            logger.debug("Version found for '%s': %s", package, package_version)
        else:
            logger.debug("No version data found for '%s'.", package)
        return package_version

    def find_requires(self, package: str) -> Generator[tuple[str, list[str]], None, None]:
        """Find requires that package dependees.

        Args:
            package (str): Package name.

        Yields:
            Generator: List of names with requires.
        """
        logger.debug("Searching for packages that depend on '%s'.", package)
        for name, data in self.data.items():
            # Ensure 'requires' key exists and is a list to prevent KeyError/TypeError
            if 'requires' in data and isinstance(data['requires'], list):
                if package in data['requires']:
                    logger.debug("Found '%s' depends on '%s'. Yielding: %s", name, package, data['requires'])
                    yield name, data['requires']
            else:
                logger.debug("Package '%s' has no 'requires' key or 'requires' is not a list. Skipping.", name)
        logger.debug("Finished searching for packages depending on '%s'.", package)

    @staticmethod
    def view_no_dependees(dependees: dict[str, Any]) -> None:
        """Print for no dependees.

        Args:
            dependees (dict[str, Any]): Packages data.
        """
        if not dependees:
            print(f"{'':>1}No dependees")
            logger.info("No dependees found for the current package.")
        else:
            logger.debug("Dependees found, 'No dependees' message skipped.")

    def view_the_main_package(self, package: str) -> None:
        """Print the main package.

        Args:
            package (str): Package name.
        """
        logger.debug("Displaying main package: %s", package)
        if self.option_for_pkg_version:
            pkgv: str = self.set_the_package_version(package)
            package = f'{package} {pkgv}'
            logger.debug("Main package with version: %s", package)
        print(f'{self.bold}{self.cyan}{package}{self.endc}:')

    def view_dependency_line(self, dependency: str) -> None:
        """Print the dependency line.

        Args:
            dependency (str): Name of dependency.
        """
        logger.debug("Displaying dependency line: %s", dependency)
        str_dependency: str = f"{'':>2}{dependency}"
        if self.option_for_full_reverse:
            str_dependency = f"{'':>2}{dependency}:"
            logger.debug("Applying full reverse formatting to dependency line.")
        print(str_dependency)

    def view_dependees(self, dependees: dict[str, Any]) -> None:
        """View packages that depend on.

        Args:
            dependees (dict): Packages data.
        """
        logger.debug("Displaying dependees list for current package.")
        name_length: int = 0
        if dependees:
            name_length = max(len(name) for name in dependees.keys())
            logger.debug("Calculated max name length for alignment: %d", name_length)

        for name, requires in dependees.items():
            dependency: str = name
            if self.option_for_pkg_version:
                pkgv: str = self.set_the_package_version(name)
                dependency = f'{name:<{name_length}} {pkgv}'
                logger.debug("Formatting dependee '%s' with version: '%s'", name, dependency)

            self.view_dependency_line(dependency)

            if self.option_for_full_reverse:
                # Ensure 'requires' is treated as list[str] for join and iteration.
                requires_list: list[str] = list(requires) if isinstance(requires, (list, tuple)) else [str(requires)]
                self.view_full_reverse(requires_list)
                logger.debug("Displaying full reverse dependencies for '%s'.", name)

    def view_full_reverse(self, requires: list[str]) -> None:
        """Print all packages.

        Args:
            requires (list[str]): Package requires.
        """
        logger.debug("Displaying full reverse requirements: %s", requires)
        requires_version: list[str] = []
        if self.option_for_pkg_version:
            for req in requires:
                pkgv: str = self.set_the_package_version(req)
                if pkgv:
                    requires_version.append(f'{req}-{pkgv}')
            print(f"{'':>4}{', '.join(requires_version)}")
            logger.debug("Full reverse requirements with versions: %s", requires_version)
        else:
            print(f"{'':>4}{', '.join(requires)}")
            logger.debug("Full reverse requirements without versions: %s", requires)

    def view_summary_of_dependees(self, dependees: dict[str, Any], package: str) -> None:
        """Print the summary.

        Args:
            dependees (dict[str, Any]): Packages data.
            package (str): Package name.
        """
        print(f'\n{self.grey}{len(dependees)} dependees for {package}{self.endc}\n')
        logger.info("Summary for package '%s': %d dependees found.", package, len(dependees))
