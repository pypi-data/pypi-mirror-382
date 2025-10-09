#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from pathlib import Path
from typing import Union

from slpkg.repositories import Repositories
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class InfoPackage:  # pylint: disable=[R0902]
    """View the packages' information."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        logger.debug("Initializing InfoPackage module with options: %s, repository: %s", options, repository)
        self.options = options
        self.repository = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.repository_packages: tuple[str, ...] = ()
        self.readme: list[str] = []
        self.info_file: list[str] = []
        self.repo_build_tag: str = ''
        self.mirror: str = ''
        self.homepage: str = ''
        self.maintainer: str = ''
        self.email: str = ''
        self.dependencies: str = ''
        self.repo_tar_suffix: str = ''

        self.option_for_pkg_version: bool = options.get('option_pkg_version', False)
        logger.debug("InfoPackage initialized. Option for package version: %s", self.option_for_pkg_version)

    def slackbuild(self, data: dict[str, dict[str, str]], slackbuilds: list[str]) -> None:
        """View slackbuilds information.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            slackbuilds (list[str]): List of slackbuilds.
        """
        logger.info("Displaying SlackBuilds information for packages: %s in repository: %s", slackbuilds, self.repository)
        print()

        repo_suffixes: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_tar_suffix,
            self.repos.ponce_repo_name: ''  # Ponce not have a specific suffix in this context.
        }
        git_mirrors: dict[str, str] = {
            self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
            self.repos.ponce_repo_name: self.repos.ponce_git_mirror
        }

        self.repo_tar_suffix = repo_suffixes.get(self.repository, '')
        logger.debug("Repository tar suffix for '%s': '%s'", self.repository, self.repo_tar_suffix)

        self.mirror = self.repos.repositories[self.repository]['mirror_packages']
        if '.git' in git_mirrors.get(self.repository, ''):  # Check if the current repo's git mirror contains '.git'.
            branch: str = ''
            if self.repository == self.repos.sbo_repo_name:
                branch = self.repos.sbo_branch
            elif self.repository == self.repos.ponce_repo_name:
                branch = self.repos.ponce_branch
            logger.debug("Git mirror detected for '%s'. Branch: '%s'", self.repository, branch)

            # Adjust mirror and suffix for Git repositories
            self.mirror = git_mirrors[self.repository].replace('.git', f'/tree/{branch}/')
            self.repo_tar_suffix = '/'
            logger.debug("Adjusted mirror for Git repo: '%s', new tar suffix: '%s'", self.mirror, self.repo_tar_suffix)

        self.repository_packages = tuple(data.keys())
        logger.debug("Loaded %d packages from repository data for dependency checks.", len(self.repository_packages))

        for sbo_name_query in slackbuilds:
            logger.debug("Processing SlackBuild query: '%s'", sbo_name_query)
            for name, item in data.items():
                if sbo_name_query in [name, '*']:
                    logger.info("Found matching SlackBuild: '%s'. Retrieving information.", name)

                    path_readme_file: Path = Path(self.repos.repositories[self.repository]['path'],
                                                  item['location'], name, 'README')
                    path_info_file: Path = Path(self.repos.repositories[self.repository]['path'],
                                                item['location'], name, f'{name}.info')

                    logger.debug("README path: %s, Info file path: %s", path_readme_file, path_info_file)

                    self.read_the_readme_file(path_readme_file)
                    self.read_the_info_file(path_info_file)
                    self.repo_build_tag = item.get('build', 'N/A')
                    self.assign_the_info_file_variables()
                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_slackbuild_package(name, item)
        logger.info("Finished displaying SlackBuilds information.")

    def read_the_readme_file(self, path_file: Path) -> None:
        """Read the README file.

        Args:
            path_file (Path): Path to the file.
        """
        logger.debug("Reading README file: %s", path_file)
        try:
            self.readme = self.utils.read_text_file(path_file)
            logger.info("Successfully read %d lines from README file: %s", len(self.readme), path_file)
        except FileNotFoundError:
            self.readme = ["README file not found."]
            logger.warning("README file not found at: %s", path_file)
        except Exception as e:  # pylint: disable=[W0718]
            self.readme = [f"Error reading README file: {e}"]
            logger.error("Error reading README file '%s': %s", path_file, e, exc_info=True)

    def read_the_info_file(self, path_info: Path) -> None:
        """Read the .info file.

        Args:
            path_info (Path): Path to the file.
        """
        logger.debug("Reading .info file: %s", path_info)
        try:
            self.info_file = self.utils.read_text_file(path_info)
            logger.info("Successfully read %d lines from .info file: %s", len(self.info_file), path_info)
        except FileNotFoundError:
            self.info_file = []  # Empty list if not found, as assign_the_info_file_variables handles empty list.
            logger.warning(".info file not found at: %s", path_info)
        except Exception as e:  # pylint: disable=[W0718]
            self.info_file = []
            logger.error("Error reading .info file '%s': %s", path_info, e, exc_info=True)

    def assign_the_info_file_variables(self) -> None:
        """Assign data from the .info file."""
        logger.debug("Assigning variables from .info file content.")
        self.homepage = ''
        self.maintainer = ''
        self.email = ''
        for line in self.info_file:
            if line.startswith('HOMEPAGE'):
                self.homepage = line[10:-2].strip()
                logger.debug("Assigned HOMEPAGE: '%s'", self.homepage)
            elif line.startswith('MAINTAINER'):
                self.maintainer = line[12:-2].strip()
                logger.debug("Assigned MAINTAINER: '%s'", self.maintainer)
            elif line.startswith('EMAIL'):
                self.email = line[7:-2].strip()
                logger.debug("Assigned EMAIL: '%s'", self.email)
        logger.debug("Finished assigning .info file variables.")

    def assign_dependencies(self, item: dict[str, str]) -> None:
        """Assign the package dependencies.

        Args:
            item (dict[str, str]): Data value.
        """
        requires: Union[str, list[str]] = item.get('requires', [])  # Get 'requires' list, default to empty list if not found.
        if isinstance(requires, list):
            self.dependencies = ', '.join([f'{pkg}' for pkg in requires])
            logger.debug("Assigned dependencies (without version): '%s'", self.dependencies)
        else:
            self.dependencies = "N/A"
            logger.warning("Unexpected type for 'requires' in item: %s. Expected list.", type(requires))

    def assign_dependencies_with_version(self, item: dict[str, str], data: dict[str, dict[str, str]]) -> None:
        """Assign dependencies with version.

        Args:
            item (dict[str, str]): Data value.
            data (dict[str, dict[str, str]]): Repository data.
        """
        if self.option_for_pkg_version:
            requires: Union[str, list[str]] = item.get('requires', [])
            if isinstance(requires, list):
                versioned_deps = []
                for pkg in requires:
                    # Check if pkg exists in the main data and in repository_packages for version info
                    if pkg in data and pkg in self.repository_packages:
                        versioned_deps.append(f"{pkg}-{data[pkg].get('version', 'N/A')}")
                    else:
                        versioned_deps.append(pkg)  # Add without version if not found in data.
                        logger.debug("Dependency '%s' not found in repository data or repository_packages for versioning.", pkg)
                self.dependencies = ', '.join(versioned_deps)
                logger.debug("Assigned dependencies (with version): '%s'", self.dependencies)
            else:
                self.dependencies = "N/A"
                logger.warning("Unexpected type for 'requires' in item when trying to assign with version: %s. Expected list.", type(requires))
        else:
            logger.debug("Option for package version is off. Skipping versioned dependency assignment.")

    def view_slackbuild_package(self, name: str, item: dict[str, str]) -> None:
        """Print slackbuild information.

        Args:
            name (str): Slackbuild name.
            item (dict[str, str]): Data value.
        """
        logger.info("Printing SlackBuild package details for '%s'.", name)
        # Prepare values, using .get() with default 'N/A' for robustness
        version = item.get('version', 'N/A')
        location = item.get('location', 'N/A')
        description = item.get('description', 'N/A')

        # Ensure 'download', 'md5sum', 'download64', 'md5sum64', 'files' are lists or default to empty lists.
        download_sources = ' '.join(item.get('download', []))
        md5sum_sources = ' '.join(item.get('md5sum', []))
        download64_sources = ' '.join(item.get('download64', []))
        md5sum64_sources = ' '.join(item.get('md5sum64', []))
        files_list = ' '.join(item.get('files', []))

        formatted_readme = ''
        if self.readme:
            # First line without leading spaces, subsequent lines with 17 spaces.
            formatted_readme = self.readme[0] + ''.join([f"{'':<17}{line}" for line in self.readme[1:]])
        else:
            formatted_readme = "No README content available."

        # Print to console
        print(f"{'Repository':<15}: {self.repository}\n"
              f"{'Name':<15}: {name}\n"
              f"{'Version':<15}: {version}\n"
              f"{'Build':<15}: {self.repo_build_tag}\n"
              f"{'Homepage':<15}: {self.homepage}\n"
              f"{'Download SBo':<15}: {self.mirror}{location}/{name}{self.repo_tar_suffix}\n"
              f"{'Sources':<15}: {download_sources}\n"
              f"{'Md5sum':<15}: {md5sum_sources}\n"
              f"{'Sources x86_64':<15}: {download64_sources}\n"
              f"{'Md5sum x86_64':<15}: {md5sum64_sources}\n"
              f"{'Files':<15}: {files_list}\n"
              f"{'Category':<15}: {location}\n"
              f"{'SBo url':<15}: {self.mirror}{location}/{name}/\n"
              f"{'Maintainer':<15}: {self.maintainer}\n"
              f"{'Email':<15}: {self.email}\n"
              f"{'Requires':<15}: {self.dependencies}\n"
              f"{'Description':<15}: {description}\n"
              f"{'README':<15}: {formatted_readme}")
        logger.debug("Printed SlackBuild details for '%s'.", name)

    def package(self, data: dict[str, dict[str, str]], packages: list[str]) -> None:
        """View binary packages information.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            packages (list[str]): List of packages.
        """
        logger.info("Displaying binary package information for packages: %s in repository: %s", packages, self.repository)
        print()
        self.repository_packages = tuple(data.keys())
        logger.debug("Loaded %d packages from repository data for dependency checks.", len(self.repository_packages))

        for package_query in packages:
            logger.debug("Processing binary package query: '%s'", package_query)
            for name, item in data.items():
                if package_query in [name, '*']:
                    logger.info("Found matching binary package: '%s'. Retrieving information.", name)
                    self.assign_dependencies(item)
                    self.assign_dependencies_with_version(item, data)
                    self.view_binary_package(name, item)
        logger.info("Finished displaying binary package information.")

    def view_binary_package(self, name: str, item: dict[str, str]) -> None:
        """Print binary packages information.

        Args:
            name (str): Package name.
            item (dict[str, str]): Data values.
        """
        logger.info("Printing binary package details for '%s'.", name)
        # Prepare values, using .get() with default 'N/A' for robustness
        version = item.get('version', 'N/A')
        build = item.get('build', 'N/A')
        package_file = item.get('package', 'N/A')
        mirror = item.get('mirror', 'N/A')
        location = item.get('location', 'N/A')
        checksum = item.get('checksum', 'N/A')
        size_comp = item.get('size_comp', 'N/A')
        size_uncomp = item.get('size_uncomp', 'N/A')
        conflicts = item.get('conflicts', 'N/A')
        suggests = item.get('suggests', 'N/A')
        description = item.get('description', 'N/A')

        # Construct download URL
        download_url = f"{mirror}{location}/{package_file}" if mirror != 'N/A' and location != 'N/A' and package_file != 'N/A' else 'N/A'

        # Print to console
        print(f"{'Repository':<15}: {self.repository}\n"
              f"{'Name':<15}: {name}\n"
              f"{'Version':<15}: {version}\n"
              f"{'Build':<15}: {build}\n"
              f"{'Package':<15}: {package_file}\n"
              f"{'Download':<15}: {download_url}\n"
              f"{'Md5sum':<15}: {checksum}\n"
              f"{'Mirror':<15}: {mirror}\n"
              f"{'Location':<15}: {location}\n"
              f"{'Size Comp':<15}: {size_comp} KB\n"
              f"{'Size Uncomp':<15}: {size_uncomp} KB\n"
              f"{'Requires':<15}: {self.dependencies}\n"
              f"{'Conflicts':<15}: {conflicts}\n"
              f"{'Suggests':<15}: {suggests}\n"
              f"{'Description':<15}: {description}\n")
        logger.debug("Printed binary package details for '%s'.", name)
