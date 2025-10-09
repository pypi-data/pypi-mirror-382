#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import json
import logging
import os
import re
import shutil
import time
from collections.abc import Generator
from pathlib import Path

from slpkg.blacklist import Blacklist
from slpkg.config import config_load
from slpkg.errors import Errors

logger = logging.getLogger(__name__)


class Utilities:
    """List of utilities."""

    def __init__(self) -> None:
        self.log_packages = config_load.log_packages
        self.build_path = config_load.build_path

        self.black = Blacklist()
        self.errors = Errors()

    def is_package_installed(self, name: str) -> str:
        """Return the installed package binary.

        Args:
            name (str): Package name.

        Returns:
            str: Full package name.
        """
        logger.debug("Checking if package '%s' is installed...", name)
        installed_package: Generator[Path] = self.log_packages.glob(f'{name}*')

        for installed in installed_package:
            inst_name: str = self.split_package(installed.name)['name']
            if inst_name == name and inst_name not in self.ignore_packages([inst_name]):
                return installed.name
        logger.debug("Package '%s' not found as installed.", name)
        return ''

    def all_installed(self) -> dict[str, str]:
        """Return all installed packages from /var/log/packages folder.

        Returns:
            dict[str, str]: All installed packages and names.
        """
        logger.info("Scanning for all installed packages in '%s'...", self.log_packages)
        installed_packages: dict[str, str] = {}

        for file in self.log_packages.glob('*'):
            name: str = self.split_package(file.name)['name']

            if not name.startswith('.'):
                installed_packages[name] = file.name

        logger.debug("Found %d initial installed packages.", len(installed_packages))

        blacklist_packages: list[str] = self.ignore_packages(list(installed_packages.keys()))
        if blacklist_packages:
            for black in blacklist_packages:
                if black in installed_packages:
                    del installed_packages[black]
                    logger.debug("Removed blacklisted package '%s' from installed list.", black)

        logger.info("Finished scanning. Total installed packages (excluding blacklisted): %d", len(installed_packages))
        return installed_packages

    @staticmethod
    def remove_file_if_exists(path: Path, file: str) -> None:
        """Remove the old files.

        Args:
            path (Path): Path to the file.
            file (str): File name.
        """
        archive: Path = Path(path, file)
        if archive.is_file():
            try:
                archive.unlink()
                logger.info("Successfully removed file: '%s'", archive)
            except OSError as e:
                logger.error("Failed to remove file '%s': %s", archive, e, exc_info=True)
        else:
            logger.debug("File '%s' does not exist, no removal needed.", archive)

    @staticmethod
    def remove_folder_if_exists(folder: Path) -> None:
        """Remove the folder if exists.

        Args:
            folder (Path): Path to the folder.
        """
        if folder.exists():
            try:
                shutil.rmtree(folder)
                logger.info("Successfully removed folder: '%s'", folder)
            except OSError as e:
                logger.error("Failed to remove folder '%s': %s", folder, e, exc_info=True)
        else:
            logger.debug("Folder '%s' does not exist, no removal needed.", folder)

    @staticmethod
    def create_directory(directory: Path) -> None:
        """Create folder like mkdir -p.

        Args:
            directory (Path): Path to folder.
        """
        if not directory.is_dir():
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info("Created directory: '%s'", directory)
            except OSError as e:
                logger.error("Failed to create directory '%s': %s", directory, e, exc_info=True)
        else:
            logger.debug("Directory '%s' already exists.", directory)

    @staticmethod
    def split_package(package: str) -> dict[str, str]:
        """Split the binary package name in name, version, arch, build and tag.

        Args:
            package (str): Full package name for splitting.

        Returns:
            dict[str, str]: Split package by name, version, arch, build and package tag.
        """
        # Initialize result with default empty values
        result: dict[str, str] = {
            'name': '',
            'version': '',
            'arch': '',
            'build': '',
            'tag': ''
        }

        if package:
            try:
                name_parts = package.split('-')
                if len(name_parts) < 4:
                    raise ValueError("Package string has too few parts after splitting by '-'")

                name = '-'.join(name_parts[:-3])
                version = ''.join(package[len(name):].split('-')[:-2])
                arch = ''.join(package[len(name + version) + 2:].split('-')[:-1])
                build_tag = name_parts[-1]
                build = ''.join(re.findall(r'\d+', build_tag[:2]))
                pkg_tag = build_tag[len(build):]

                # Update the result dictionary if splitting was successful
                result = {
                    'name': name,
                    'version': version,
                    'arch': arch,
                    'build': build,
                    'tag': pkg_tag
                }

                # Check for unexpected formats AFTER attempting to split and populate
                if not name or not version or not arch or not build:
                    logger.debug("Partially empty fields after splitting package '%s'. Result: %s", package, result)

            except (IndexError, ValueError, re.error) as e:
                logger.debug("Error splitting package '%s': %s. Returning empty result.", package, e)

        # logger.debug("Split package '%s' into: %s", package, result)
        return result

    @staticmethod
    def finished_time(elapsed_time: float) -> None:
        """Print the elapsed time.

        Args:
            elapsed_time (float): Unformatted time.
        """
        formatted_time = time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        logger.info("Operation finished. Elapsed time: %s", formatted_time)
        print('\nFinished:', formatted_time)

    def read_packages_from_file(self, file: Path) -> Generator[str]:
        """Read packages from file.

        Args:
            file (Path): Path to the file.

        Yields:
            Generator[str]: Package names.
        """
        logger.info("Reading packages from file: '%s'", file)
        try:
            with open(file, 'r', encoding='utf-8') as pkgs:
                packages: list[str] = pkgs.read().splitlines()
            logger.debug("Successfully read %d lines from '%s'.", len(packages), file)

            for package in packages:
                if package and not package.startswith('#'):
                    if '#' in package:
                        original_package = package  # Store original for logging
                        package = package.split('#')[0].strip()
                        logger.debug("Trimmed comment from package line: '%s' -> '%s'", original_package, package)
                    yield package
                else:
                    logger.debug("Skipping empty or commented line in '%s': '%s'", file, package)
        except FileNotFoundError:
            logger.error("File not found: '%s'. Raising error message.", file, exc_info=True)
            self.errors.message(f"No such file or directory: '{file}'", exit_status=20)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("An unexpected error occurred while reading '%s': %s", file, e, exc_info=True)
            self.errors.message(f"Error reading file '{file}': {e}", exit_status=21)

    def read_text_file(self, file: Path) -> list[str]:
        """Read a text file.

        Args:
            file (Path): Path to the file.

        Returns:
            list[str]: The lines in the list.
        """
        logger.info("Reading text file: '%s'", file)
        try:
            with open(file, 'r', encoding='utf-8', errors='replace') as text_file:
                lines = text_file.readlines()
                logger.debug("Successfully read %d lines from '%s'.", len(lines), file)
                return lines
        except FileNotFoundError:
            logger.error("File not found: '%s'. Raising error message.", file, exc_info=True)
            self.errors.message(f"No such file or directory: '{file}'", exit_status=20)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("An unexpected error occurred while reading text file '%s': %s", file, e, exc_info=True)
            self.errors.message(f"Error reading text file '{file}': {e}", exit_status=21)
        return []

    def count_file_size(self, name: str) -> int:
        """Count the file size.

        Read the contents files from the package file list
        and count the total installation file size in bytes.

        Args:
            name (str): The name of the package.

        Returns:
            int
        """
        count_files: int = 0
        installed: Path = Path(self.log_packages, self.is_package_installed(name))
        if installed:
            file_installed: list[str] = installed.read_text(encoding="utf-8").splitlines()
            for line in file_installed:
                file: Path = Path('/', line)
                if file.is_file():
                    try:
                        count_files += file.stat().st_size
                    except OSError as e:
                        logger.warning("Could not stat file '%s' for size calculation: %s", file, e)

        logger.info("Total counted size for '%s': %s bytes.", name, count_files)
        return count_files

    @staticmethod
    def convert_file_sizes(byte_size: float) -> str:
        """Convert bytes to kb, mb and gb.

        Args:
            byte_size (float): The file size in bytes.

        Returns:
            str
        """
        kb_size: float = byte_size / 1024
        mb_size: float = kb_size / 1024
        gb_size: float = mb_size / 1024

        if gb_size >= 1:
            return f"{gb_size:.0f} GB"
        if mb_size >= 1:
            return f"{mb_size:.0f} MB"
        if kb_size >= 1:
            return f"{kb_size:.0f} KB"

        return f"{byte_size} B"

    @staticmethod
    def apply_package_pattern(data: dict[str, dict[str, str]], packages: list[str]) -> list[str]:
        """If the '*' applied returns all the package names.

        Args:
            data (dict[str, dict[str, str]]): The repository data.
            packages (list[str]): The packages that applied.

        Returns:
            list[str]: Package names.
        """
        original_packages_len = len(packages)
        if '*' in packages:
            logger.info("'*' pattern detected. Expanding to all repository packages.")
            packages.remove('*')
            packages.extend(list(data.keys()))
            logger.info("Expanded package list from %d to %d items.", original_packages_len, len(packages))
        return packages

    @staticmethod
    def change_owner_privileges(folder: Path) -> None:
        """Change the owner privileges.

        Args:
            folder (Path): Path to the folder.
        """
        logger.info("Attempting to change ownership of folder '%s' to root:root (0:0).", folder)
        try:
            os.chown(folder, 0, 0)
            logger.debug("Successfully changed ownership of folder '%s'.", folder)
        except OSError as e:
            logger.error("Failed to change ownership of folder '%s': %s", folder, e, exc_info=True)

        for file in os.listdir(folder):
            file_path = Path(folder, file)
            try:
                os.chown(file_path, 0, 0)
                logger.debug("Successfully changed ownership of file: '%s'.", file_path)
            except OSError as e:
                logger.error("Failed to change ownership of file '%s': %s", file_path, e, exc_info=True)

    @staticmethod
    def case_insensitive_pattern_matching(packages: list[str], data: dict[str, dict[str, str]],
                                          options: dict[str, bool]) -> list[str]:
        """Case-insensitive pattern matching packages.

        Args:
            packages (list[str]): List of packages.
            data (dict[str, dict[str, str]]): Repository data.
            options (list[str]): User options.

        Returns:
            list[str]: Matched packages.
        """
        if options.get('option_no_case'):
            logger.info("Applying case-insensitive package matching.")
            repo_packages: tuple[str, ...] = tuple(data.keys())
            matched_count = 0
            for i, package in enumerate(packages):  # Iterate by index to safely remove
                found_match = False
                for pkg in repo_packages:
                    if package.lower() == pkg.lower():
                        if package != pkg:  # Only log if an actual case change happened
                            logger.debug("Matched case-insensitively: '%s' -> '%s'", package, pkg)
                        packages[i] = pkg  # Replace with the correct-cased name
                        found_match = True
                        matched_count += 1
                        break  # Found a match, move to next requested package
                if not found_match:
                    logger.debug("No case-insensitive match found for '%s' in repository data.", package)
            logger.info("Case-insensitive matching complete. %s packages adjusted for case.", matched_count)
        return packages

    def read_json_file(self, file: Path) -> dict[str, dict[str, str]]:
        """Read JSON data from the file.

        Args:
            file (Path): Path file for reading.

        Returns:
            dict[str, dict[str, str]]: Json data file.
        """
        logger.info("Attempting to read JSON data from '%s'.", file)
        json_data: dict[str, dict[str, str]] = {}
        try:
            if not file.is_file():
                logger.error("JSON file '%s' not found. Raising error message.", file)
                self.errors.message(f'{file} not found.', exit_status=1)

            json_data = json.loads(file.read_text(encoding='utf-8'))
            logger.info("Successfully read JSON data from '%s'.", file)
        except json.decoder.JSONDecodeError as e:
            logger.error("Error decoding JSON from '%s': %s", file, e, exc_info=True)
        except Exception as e:  # pylint: disable=[W0718]
            logger.error("An unexpected error occurred while reading JSON from '%s': %s", file, e, exc_info=True)
        return json_data

    def ignore_packages(self, packages: list[str]) -> list[str]:
        """Match packages using regular expression.

        Args:
            packages (list[str]): The packages to apply the pattern.

        Returns:
            list[str]
        """
        logger.debug("Checking %d packages against blacklist.", len(packages))
        matching_packages: list[str] = []
        blacklist: list[str] = self.black.packages()
        if blacklist:
            logger.debug("Blacklist loaded: %s", blacklist)
            pattern: str = '|'.join(tuple(blacklist))
            for pkg in packages:
                if re.search(pattern, pkg):
                    matching_packages.append(pkg)
                    logger.debug("Package '%s' matched blacklist pattern.", pkg)
            logger.info("Found %d packages to ignore/blacklist.", len(matching_packages))
        else:
            logger.debug("No packages in blacklist to apply.")
        return matching_packages

    def patch_slackbuild_file(self, name: str, variable_name: str, new_value: str) -> None:
        """
        Patch a specific variable in the SlackBuild script.

        Args:
            name (str): The name of the package.
            variable_name (str): The name of the variable to patch (e.g., 'VERSION', 'TAG').
            new_value (str): The new value to set for the variable.
        """
        sbo_script: Path = Path(self.build_path, name, f'{name}.SlackBuild')
        logger.debug("Attempting to patch variable '%s' in SlackBuild script: %s", variable_name, sbo_script)

        if not sbo_script.is_file() or not new_value:
            logger.debug("Skipping SlackBuild variable patch for '%s': script not found or new value is empty.", name)
            return

        lines: list[str] = self.read_text_file(sbo_script)
        patched = False
        new_lines = []

        pattern = re.compile(rf'^{re.escape(variable_name)}=.*')

        for line in lines:
            if pattern.match(line):
                if f'${{{variable_name}:-' in line:
                    new_line = f'{variable_name}=${{{variable_name}:-{new_value}}}\n'
                else:
                    new_line = f'{variable_name}={new_value}\n'

                new_lines.append(new_line)
                patched = True
                logger.debug("Patched '%s' line in '%s' to: '%s'", variable_name, sbo_script, new_line.strip())
            else:
                new_lines.append(line)

        try:
            with open(sbo_script, 'w', encoding='utf-8') as script:
                script.writelines(new_lines)

            if not patched:
                logger.warning("No '%s=' line found in '%s' to patch.", variable_name, sbo_script)
            else:
                logger.info("SlackBuild variable '%s' patched successfully for '%s'.", variable_name, name)
        except IOError as e:
            logger.error("Failed to patch SlackBuild script '%s': %s", sbo_script, e)
