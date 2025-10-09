#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
import re
from pathlib import Path
from typing import Any, Union

from slpkg.config import config_load
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess

# Initialize the logger for this module.
logger = logging.getLogger(__name__)


class InstallData:
    """Installs data to the repositories path."""

    def __init__(self) -> None:
        logger.debug("Initializing InstallData class.")
        self.cpu_arch = config_load.cpu_arch
        self.package_type = config_load.package_type

        self.utils = Utilities()
        self.repos = Repositories()
        self.multi_process = MultiProcess()
        self.view_process = ViewProcess()
        logger.debug("InstallData class initialized.")

    def write_repo_info(self, changelog_file: Path, info: dict[str, Any]) -> None:
        """Write some repo information.

        Args:
            changelog_file (Path): Repository ChangeLog.txt path.
            info (dict[str, Any]): Repository information.
        """
        repo_name: str = info['repo_name']
        full_requires: bool = info['full_requires']
        last_date: str = ''
        repo_info: dict[str, Any] = {}

        logger.info("Writing repository info for '%s'. Changelog file: %s", repo_name, changelog_file)

        lines: list[str] = []
        try:
            lines = self.utils.read_text_file(changelog_file)
            logger.debug("Read %d lines from changelog file: %s", len(lines), changelog_file)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to read changelog file '%s': %s", changelog_file, e)

        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        for line in lines:
            if line.startswith(days):
                last_date = line.replace('\n', '')
                logger.debug("Found last updated date in changelog: '%s'", last_date)
                break
        else:
            logger.warning("No date found in changelog file '%s'. 'last_date' remains empty.", changelog_file)

        if self.repos.repos_information.is_file():
            try:
                repo_info = self.utils.read_json_file(self.repos.repos_information)
                logger.debug("Loaded existing repository information from: %s", self.repos.repos_information)
            except Exception as e:  # pylint: disable=[W0718]
                logger.error("Failed to read existing repository information from '%s': %s. Starting with empty info.", self.repos.repos_information, e)
                repo_info = {}  # Reset to empty if reading fails.

        repo_info[repo_name] = {
            'last_updated': last_date,
            'full_requires': full_requires
        }
        logger.debug("Updated repo_info for '%s': %s", repo_name, repo_info[repo_name])

        try:
            self.repos.repos_information.write_text(json.dumps(repo_info, indent=4), encoding='utf-8')
            logger.info("Successfully wrote repository information to: %s", self.repos.repos_information)
        except IOError as e:
            logger.error("Failed to write repository information to '%s': %s", self.repos.repos_information, e)

    def install_sbo_data(self, repo: str) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Read the SLACKBUILDS.TXT FILE and creates a json data file.

        Args:
            repo (str): repository name.
        """
        logger.info("Installing SlackBuilds data for repository: %s", repo)
        self.view_process.message(f'Updating the database for {repo}')
        logger.debug("Displaying 'Updating the database' message for SBo repo '%s'.", repo)

        data: dict[str, dict[str, Union[str, list[str]]]] = {}
        cache: list[str] = []
        sbo_tags: list[str] = [
            'SLACKBUILD NAME:',
            'SLACKBUILD LOCATION:',
            'SLACKBUILD FILES:',
            'SLACKBUILD VERSION:',
            'SLACKBUILD DOWNLOAD:',
            'SLACKBUILD DOWNLOAD_x86_64:',
            'SLACKBUILD MD5SUM:',
            'SLACKBUILD MD5SUM_x86_64:',
            'SLACKBUILD REQUIRES:',
            'SLACKBUILD SHORT DESCRIPTION:'
        ]

        slackbuilds_txt_path: Path = Path(self.repos.repositories[repo]['path'],
                                          self.repos.repositories[repo]['slackbuilds_txt'])
        slackbuilds_txt: list[str] = []
        try:
            slackbuilds_txt = slackbuilds_txt_path.read_text(encoding='utf-8').splitlines()
            logger.debug("Read %d lines from SLACKBUILDS.TXT: %s", len(slackbuilds_txt), slackbuilds_txt_path)
        except FileNotFoundError:
            logger.error("SLACKBUILDS.TXT file not found at: %s. Cannot install SBo data.", slackbuilds_txt_path)
            self.view_process.done()
            print()
            return
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to read SLACKBUILDS.TXT from '%s': %s", slackbuilds_txt_path, e)
            self.view_process.done()
            print()
            return

        for i, line in enumerate(slackbuilds_txt, 1):  # pylint: disable=[R1702]
            for tag in sbo_tags:
                if line.startswith(tag):
                    line = line.replace(tag, '').strip()
                    cache.append(line)
                    break  # Break after finding a tag to avoid processing the same line multiple times.

            # Process a block of 10 tags (11 lines including the name line).
            if (i % 11) == 0 and len(cache) == 10:  # Ensure all 10 tags are captured.
                build: str = ''
                name: str = cache[0]
                version: str = cache[3]
                location: str = cache[1].split('/')[1]
                logger.debug("Processing SBo package: %s, Version: %s, Location: %s", name, version, location)

                requires_str = cache[8].replace('%README%', '').strip()
                requires_list = requires_str.split() if requires_str else []

                data[name] = {
                    'location': location,
                    'files': cache[2].split(),
                    'version': version,
                    'download': cache[4].split(),
                    'download64': cache[5].split(),
                    'md5sum': cache[6].split(),
                    'md5sum64': cache[7].split(),
                    'requires': requires_list,
                    'description': cache[9].replace(name, '').strip()
                }

                arch: str = self.cpu_arch
                sbo_file: Path = Path(self.repos.repositories[repo]['path'], location, name, f'{name}.SlackBuild')
                if sbo_file.is_file():
                    try:
                        slackbuild_content = sbo_file.read_text(encoding='utf-8').splitlines()
                        for sbo_line in slackbuild_content:
                            if sbo_line.startswith('BUILD=$'):
                                build = ''.join(re.findall(r'\d+', sbo_line))
                                logger.debug("Found BUILD variable for '%s': %s", name, build)
                            if sbo_line.startswith('ARCH=noarch'):
                                arch = 'noarch'
                                logger.debug("Found ARCH=noarch for '%s'.", name)
                    except Exception as e:  # pylint: disable=[W0718]
                        logger.warning("Failed to read SlackBuild script '%s': %s. Using default build/arch.", sbo_file, e)
                else:
                    logger.warning("SlackBuild script not found for '%s' at '%s'. Using default build/arch.", name, sbo_file)

                data[name].update({'arch': arch})
                data[name].update({'build': build})

                # Construct package name based on detected arch and build
                package_full_name: str = f"{name}-{version}-{arch}-{build}{self.repos.repositories[repo]['repo_tag']}.tgz"
                data[name].update({'package': package_full_name})
                logger.debug("Constructed full package name for '%s': %s", name, package_full_name)

                cache = []  # reset cache after processing a package.
            elif (i % 11) == 0 and len(cache) != 10:
                logger.warning("Skipping incomplete SBo package entry at line %d. Expected 10 tags, found %d. Cache: %s", i, len(cache), cache)
                cache = []  # Reset cache even if incomplete.

        repo_info: dict[str, Any] = {
            'repo_name': repo,
            'full_requires': False  # SBo data typically doesn't have full_requires in the same way binary repos do.
        }

        path_changelog: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['changelog_txt'])
        self.write_repo_info(path_changelog, repo_info)
        logger.debug("Wrote repository info for SBo repo '%s'.", repo)

        data_file: Path = Path(self.repos.repositories[repo]['path'], self.repos.data_json)
        try:
            data_file.write_text(json.dumps(data, indent=4), encoding='utf-8')
            logger.info("Successfully wrote SBo data to JSON file: %s", data_file)
        except IOError as e:
            logger.error("Failed to write SBo data to '%s': %s", data_file, e)

        self.view_process.done()
        print()
        logger.info("SBo data installation for '%s' completed.", repo)

    def install_binary_data(self, repo: str) -> None:  # pylint: disable=[R0912,R0914,R0915]
        """Installs the data for binary repositories.

        Args:
            repo (str): Description
        """
        print()
        logger.info("Installing binary data for repository: %s", repo)
        self.view_process.message(f'Updating the database for {repo}')
        logger.debug("Displaying 'Updating the database' message for binary repo '%s'.", repo)

        slack_repos: list[str] = [self.repos.slack_patches_repo_name, self.repos.slack_extra_repo_name]

        mirror: str = self.repos.repositories[repo]['mirror_packages']
        if repo in slack_repos:
            mirror = self.repos.repositories[repo]['mirror_changelog']
            logger.debug("Adjusted mirror for Slack-like repo '%s' to changelog mirror: %s", repo, mirror)

        checksums_dict: dict[str, str] = {}
        data: dict[str, dict[str, Union[str, list[str]]]] = {}
        build: str = ''
        arch: str = ''
        requires: list[str] = []
        full_requires: bool = False
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.repositories[repo]['path'],
                                   self.repos.repositories[repo]['packages_txt'])
        path_checksums: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['checksums_md5'])

        packages_txt: list[str] = []
        checksums_md5: list[str] = []

        try:
            packages_txt = self.utils.read_text_file(path_packages)
            logger.debug("Read %d lines from PACKAGES.TXT: %s", len(packages_txt), path_packages)
        except FileNotFoundError:
            logger.error("PACKAGES.TXT file not found at: %s. Cannot install binary data.", path_packages)
            self.view_process.done()
            print()
            return
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("Failed to read PACKAGES.TXT from '%s': %s", path_packages, e)
            self.view_process.done()
            print()
            return

        try:
            checksums_md5 = self.utils.read_text_file(path_checksums)
            logger.debug("Read %d lines from CHECKSUMS.md5: %s", len(checksums_md5), path_checksums)
        except FileNotFoundError:
            logger.warning("CHECKSUMS.md5 file not found at: %s. Checksums will be marked as 'error checksum'.", path_checksums)
        except Exception as e:  # pylint: disable=[W0718]
            logger.warning("Failed to read CHECKSUMS.md5 from '%s': %s. Checksums might be affected.", path_checksums, e)

        for line in checksums_md5:
            line = line.strip()
            # Check if line ends with any of the defined package types (e.g., .tgz, .txz)
            if any(line.endswith(pkg_type) for pkg_type in self.package_type):
                parts = line.split('./')
                if len(parts) > 1:
                    file_part = parts[1].split('/')[-1].strip()
                    checksum_part = parts[0].strip()
                    checksums_dict[file_part] = checksum_part
                    logger.debug("Parsed checksum: file='%s', checksum='%s'", file_part, checksum_part)
                else:
                    logger.warning("Skipping malformed checksum line: '%s'", line)
            else:
                logger.debug("Skipping non-package checksum line: '%s'", line)

        cache: list[str] = []  # init cache

        for i, line in enumerate(packages_txt):
            if line.startswith(pkg_tag[0]):  # PACKAGE NAME:
                package = line.replace(pkg_tag[0], '').strip()
                name = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build = self.utils.split_package(package)['build']
                arch = self.utils.split_package(package)['arch']
                logger.debug("Processing package entry: %s (Name: %s, Version: %s, Build: %s, Arch: %s)", package, name, version, build, arch)

                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                    logger.debug("Found checksum for '%s': %s", package, checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')
                    logger.warning("Checksum not found for package '%s'. Marking as 'error checksum'.", package)

            elif line.startswith(pkg_tag[1]):  # PACKAGE LOCATION:
                package_location = line.replace(pkg_tag[1], '').strip()
                if repo == self.repos.slack_testing_repo_name:
                    cache.append(package_location.replace('./testing/', ''))
                else:
                    cache.append(package_location[2:])  # Do not install (.) dot
                logger.debug("Package location: %s", package_location[2:])

            elif line.startswith(pkg_tag[2]):  # PACKAGE SIZE (compressed):
                compressed_size = ''.join(re.findall(r'\d+', line))
                cache.append(compressed_size)
                logger.debug("Compressed size: %s", compressed_size)

            elif line.startswith(pkg_tag[3]):  # PACKAGE SIZE (uncompressed):
                uncompressed_size = ''.join(re.findall(r'\d+', line))
                cache.append(uncompressed_size)
                logger.debug("Uncompressed size: %s", uncompressed_size)

            elif line.startswith(pkg_tag[4]):  # PACKAGE REQUIRED:
                required = line.replace(pkg_tag[4], '').strip()
                requires = []  # Reset for each package.
                if '|' in required:
                    full_requires = True
                    deps_temp: list[str] = []
                    for req_part in required.split(','):
                        dep_options = req_part.split('|')
                        if len(dep_options) > 1:
                            deps_temp.append(dep_options[1].strip())  # Take the second option if '|' is present.
                        else:
                            deps_temp.extend([d.strip() for d in dep_options])  # Otherwise take all.
                    requires = list(set(deps_temp))  # Remove duplicates.
                    logger.debug("Full requires detected. Parsed dependencies: %s", requires)
                else:
                    requires = [r.strip() for r in required.split(',') if r.strip()]  # Split by comma and clean.
                    logger.debug("Simple requires detected. Parsed dependencies: %s", requires)

                # Ensure 'requires' is always a list, even if empty
                if not requires and required:  # If 'required' string was not empty but 'requires' list is (e.g., just spaces).
                    logger.warning("Could not parse requirements from string '%s'. Setting as empty list.", required)
                    requires = []

            elif line.startswith(pkg_tag[5]):  # PACKAGE DESCRIPTION:
                # Description is on the next line, offset by (name length * 2) + 2
                package_description = ''
                if i + 1 < len(packages_txt):
                    # Ensure 'name' is available from cache[0] before using it for slicing
                    current_name_from_cache = cache[0] if len(cache) > 0 else ''
                    if current_name_from_cache:
                        desc_start_index = (len(current_name_from_cache) * 2) + 2
                        package_description = packages_txt[i + 1][desc_start_index:].strip()
                        logger.debug("Extracted description: '%s'", package_description)

                if not package_description:
                    package_description = 'Not found'
                    logger.debug("Description not found for package. Setting to 'Not found'.")

                # Ensure description is wrapped in parentheses if it isn't already
                if not package_description.startswith('(') and not package_description.endswith(')'):
                    package_description = f'({package_description})'
                    logger.debug("Wrapped description in parentheses: '%s'", package_description)
                cache.append(package_description)

            # Check if all 9 expected items are in cache for a complete package entry.
            if len(cache) == 9:
                data[cache[0]] = {
                    'repo': repo,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',  # Not parsed from PACKAGES.TXT.
                    'suggests': '',   # Not parsed from PACKAGES.TXT.
                }
                logger.debug("Added package '%s' data to dictionary. Data: %s", cache[0], data[cache[0]])

                cache = []  # reset cache for the next package.
                requires = []  # reset requires for the next package.
                build = ''  # Reset build and arch for the next package.
                arch = ''
                full_requires = False  # Reset full_requires.

        repo_info: dict[str, Any] = {
            'repo_name': repo,
            'full_requires': full_requires  # This indicates if any package in this repo had '|' dependencies.
        }

        path_changelog: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.repositories[repo]['changelog_txt'])
        self.write_repo_info(path_changelog, repo_info)
        logger.debug("Wrote repository info for binary repo '%s'.", repo)

        data_file: Path = Path(self.repos.repositories[repo]['path'], self.repos.data_json)
        try:
            data_file.write_text(json.dumps(data, indent=4), encoding='utf-8')
            logger.info("Successfully wrote binary data to JSON file: %s", data_file)
        except IOError as e:
            logger.error("Failed to write binary data to '%s': %s", data_file, e)

        self.view_process.done()
        print()
        logger.info("Binary data installation for '%s' completed.", repo)
