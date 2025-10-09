#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import shutil
from dataclasses import dataclass

from slpkg.config import config_load

logger = logging.getLogger(__name__)


@dataclass
class PackageData:
    """
    Represents the package with its characteristics.

    Attributes:
        package (str): The name of the package.
        version (str): The package version.
        size (str): The size of the package (e.g., "10MB").
        color (str): A color code for displaying the package.
        repo (str): The repository where the package is located.
    """
    package: str
    version: str
    size: str
    color: str
    repo: str


class Imprint:  # pylint: disable=[R0902]
    """Managing the ASCII characters."""

    def __init__(self) -> None:  # pylint: disable=[R0915]
        logger.debug("Initializing Imprint module.")
        self.bold = config_load.bold
        self.cyan = config_load.cyan
        self.endc = config_load.endc

        self.columns, self.rows = shutil.get_terminal_size()
        self.package_alignment: int = self.columns - 56
        self.version_alignment: int = 31
        self.size_alignment: int = 9
        self.repo_alignment: int = 14

        # Ensure package_alignment is at least 1 to prevent negative values in f-strings.
        self.package_alignment = max(self.package_alignment, 1)
        logger.debug("Terminal size: %sx%s. Calculated alignments: package=%d, version=%d, size=%d, repo=%d",
                     self.columns, self.rows, self.package_alignment, self.version_alignment,
                     self.size_alignment, self.repo_alignment)

        self.bullet: str = '-'
        self.done: str = 'Done'
        self.failed: str = 'Failed'
        self.skipped: str = 'Skipped'
        logger.debug("Imprint module initialized.")

    def package_status(self, mode: str) -> None:
        """Print the package status header to console.

        Args:
            mode (str): The mode of operation (e.g., "Upgrade", "Install").
        """
        logger.info("Displaying package status header for mode: '%s'.", mode)
        print('=' * (self.columns - 1))
        # This print statement formats and displays the header for package status.
        print(f"{self.bold}{self.cyan}{'Package':<{self.package_alignment}} {'Version':<{self.version_alignment}}{'Size':<{self.size_alignment}}{'Repository':>{self.repo_alignment}}{self.endc}")
        print('=' * (self.columns - 1))
        print(f'{self.bold}{mode}{self.endc}')
        logger.debug("Package status header displayed for mode '%s'.", mode)

    def package_line(self, pkg: PackageData) -> None:
        """Draw a single package line with its characteristics to console.

        Args:
            pkg (PackageData): An instance of PackageData containing package characteristics.
        """
        logger.debug("Drawing package line for: %s (version: %s, size: %s, repo: %s)", pkg.package, pkg.version, pkg.size, pkg.repo)

        # Create mutable copies for truncation
        display_version = pkg.version
        display_package = pkg.package

        # Truncate version string if it's too long for alignment
        if len(display_version) >= (self.version_alignment - 5):
            display_version = f'{display_version[:self.version_alignment - 5]}...'
            logger.debug("Truncated version from '%s' to '%s'.", pkg.version, display_version)

        # Truncate package name string if it's too long for alignment
        if len(display_package) >= (self.package_alignment - 4):
            display_package = f'{display_package[:self.package_alignment - 4]}...'
            logger.debug("Truncated package name from '%s' to '%s'.", pkg.package, display_package)

        # Print the formatted package line to console.
        print(f"{'':>1}{pkg.color}{display_package:<{self.package_alignment}}{self.endc}"
              f"{display_version:<{self.version_alignment}}{self.endc}{pkg.size:<{self.size_alignment}}"
              f"{pkg.repo:>{self.repo_alignment}}")
        logger.debug("Package line displayed for '%s'.", pkg.package)

    def dependency_status(self, mode: str) -> None:
        """Draw the dependency status header to console.

        Args:
            mode (str): The mode for dependencies (e.g., "Missing", "Installed").
        """
        logger.info("Displaying dependency status header for mode: '%s'.", mode)
        # This print statement formats and displays the header for dependency status.
        print(f"{self.bold}{mode} dependencies:{self.endc}")
        logger.debug("Dependency status header displayed for mode '%s'.", mode)
