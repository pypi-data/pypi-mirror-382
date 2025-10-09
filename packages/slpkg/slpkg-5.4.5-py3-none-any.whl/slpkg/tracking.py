#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging

from slpkg.binaries.required import Required
from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.sbos.dependencies import Requires
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Tracking:  # pylint: disable=[R0902]
    """Tracking of the package dependencies."""

    def __init__(self, data: dict[str, dict[str, str]], packages: list[str], options: dict[str, bool],
                 repository: str) -> None:
        logger.debug("Initializing Tracking module for repository: %s, with %d packages and options: %s",
                     repository, len(packages), options)
        self.data = data
        self.packages = packages
        self.options = options
        self.repository = repository

        self.view_missing_deps = config_load.view_missing_deps
        self.bold = config_load.bold
        self.grey = config_load.grey
        self.red = config_load.red
        self.cyan = config_load.cyan
        self.endc = config_load.endc

        self.utils = Utilities()
        self.repos = Repositories()

        self.package_version: str = ''
        self.package_dependency_version: str = ''
        self.package_requires: list[str] = []
        self.package_line: str = ''
        self.require_line: str = ''
        self.count_requires: int = 0
        self.require_length: int = 0

        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)
        logger.debug("Tracking module initialized. View missing deps: %s, Option for package version: %s",
                     self.view_missing_deps, self.option_for_pkg_version)

    def package(self) -> None:
        """Call methods and prints the results for package dependency tracking."""
        logger.info("Starting package dependency tracking for %d packages.", len(self.packages))
        self.view_the_title()

        for package in self.packages:
            self.count_requires = 0

            self.set_the_package_line(package)
            self.set_package_requires(package)
            self.view_the_main_package()
            self.view_no_dependencies()

            for require in self.package_requires:
                self.count_requires += 1

                self.set_the_package_require_line(require)
                self.view_requires()

            self.view_summary_of_tracking(package)
        logger.info("Finished package dependency tracking for all packages.")

    def view_the_title(self) -> None:
        """Print the title and apply package patterns."""
        print("The list below shows the packages with dependencies:\n")
        logger.debug("Applying package patterns to initial package list: %s", self.packages)
        self.packages = self.utils.apply_package_pattern(self.data, self.packages)
        logger.debug("Package list after applying patterns: %s", self.packages)

    def view_the_main_package(self) -> None:
        """Print the main package name to console."""
        print(f'{self.package_line}:')
        logger.debug("Displayed main package line: %s", self.package_line)

    def view_requires(self) -> None:
        """Print a single package requirement to console."""
        print(f"{'':>2}{self.require_line}")
        logger.debug("Displayed requirement line: %s", self.require_line)

    def view_no_dependencies(self) -> None:
        """Print the message 'No dependencies' to console if applicable."""
        if not self.package_requires:
            print(f"{'':>1}No dependencies")
            logger.info("No dependencies found for current package.")
        else:
            logger.debug("Dependencies found for current package, 'No dependencies' message skipped.")

    def set_the_package_line(self, package: str) -> None:
        """Set the formatted string for the main package line.

        Args:
            package (str): Package name.
        """
        logger.debug("Setting package line for package: %s", package)
        self.package_line = f'{self.bold}{self.cyan}{package}{self.endc}'
        if self.option_for_pkg_version:
            self.set_package_version(package)
            self.package_line = f'{self.bold}{package} {self.package_version}{self.endc}'
            logger.debug("Package line with version: %s", self.package_line)
        else:
            logger.debug("Package line without version: %s", self.package_line)

    def set_the_package_require_line(self, require: str) -> None:
        """Set the formatted string for a package requirement.

        Args:
            require (str): Requirement name.
        """
        logger.debug("Setting requirement line for: %s", require)
        color: str = ''
        if require not in self.data:
            color = self.red
            logger.debug("Requirement '%s' not found in data, marking with red color.", require)

        self.require_line = f'{color}{require}{self.endc}'

        if self.option_for_pkg_version:
            self.set_package_dependency_version(require)
            self.require_line = (f'{color}{require:<{self.require_length}}{self.endc}'
                                 f'{self.package_dependency_version}')
            logger.debug("Requirement line with dependency version: %s", self.require_line)
        else:
            logger.debug("Requirement line without dependency version: %s", self.require_line)

    def set_package_dependency_version(self, require: str) -> None:
        """Set the version string for a package dependency.

        Args:
            require (str): Dependency name.
        """
        logger.debug("Setting dependency version for requirement: %s", require)
        self.package_dependency_version = f"{'':>1}(not included)"
        if self.data.get(require):
            self.package_dependency_version = (
                f"{'':>1}{self.data[require]['version']}"
            )
            logger.debug("Dependency '%s' version found: %s", require, self.package_dependency_version)
        else:
            logger.debug("Dependency '%s' version not found in data. Set to '(not included)'.", require)

    def set_package_version(self, package: str) -> None:
        """Set the main package version.

        Args:
            package (str): Package name.
        """
        logger.debug("Setting main package version for: %s", package)
        try:
            self.package_version = self.data[package]['version']
            logger.debug("Main package '%s' version set to: %s", package, self.package_version)
        except KeyError:
            logger.warning("Version data not found for main package '%s'. Setting version to empty string.", package)
            self.package_version = ''  # Ensure it's an empty string if not found.

    def set_package_requires(self, package: str) -> None:
        """Set the list of requirements for a given package.

        Args:
            package (str): Package name.
        """
        logger.debug("Resolving requirements for package: %s (repository: %s)", package, self.repository)
        if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            # Use Required for binary repositories
            self.package_requires = list(Required(self.data, package, self.options).resolve())
            logger.debug("Resolved binary requirements for '%s': %s", package, self.package_requires)
        else:
            # Use Requires for SlackBuilds repositories
            self.package_requires = list(Requires(self.data, package, self.options).resolve())
            logger.debug("Resolved SlackBuilds requirements for '%s': %s", package, self.package_requires)

        if self.package_requires:
            logger.debug("Initial requirements found for '%s': %d", package, len(self.package_requires))
            if self.view_missing_deps:
                logger.debug("view_missing_deps is enabled. Checking for missing dependencies in data.")
                # Make a copy of the original requires list from data to iterate.
                requires_from_data: list[str] = list(self.data.get(package, {}).get('requires', []))
                for req in requires_from_data:
                    if req not in self.data:  # If the required package is not in the loaded data.
                        self.package_requires.append(req)
                        logger.info("Added missing dependency '%s' for package '%s' (not found in data).", req, package)
                logger.debug("Final requirements list for '%s' after checking for missing deps: %s", package, self.package_requires)

            # Set require_length for formatting, only if there are requirements
            self.require_length = max((len(name) for name in self.package_requires), default=0)
            logger.debug("Calculated require_length for formatting: %d", self.require_length)
        else:
            logger.debug("No requirements found for package: %s", package)
            self.require_length = 0  # Ensure it's 0 if no requirements.

    def view_summary_of_tracking(self, package: str) -> None:
        """Print the summary of dependencies for a package to console.

        Args:
            package (str): Package name.
        """
        print(f'\n{self.grey}{self.count_requires} dependencies for {package}{self.endc}\n')
        logger.info("Summary for package '%s': %d dependencies found.", package, self.count_requires)
