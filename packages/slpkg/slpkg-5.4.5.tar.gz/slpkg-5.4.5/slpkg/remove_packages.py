#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

from slpkg.choose_packages import Choose
from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.multi_process import MultiProcess
from slpkg.terminal_selector import TerminalSelector
from slpkg.utilities import Utilities
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class RemovePackages:  # pylint: disable=[R0902]
    """Remove installed packages with dependencies."""

    def __init__(self, packages: list[str], options: dict[str, bool]) -> None:
        logger.debug("Initializing RemovePackages module with packages: %s, options: %s", packages, options)
        self.packages = packages

        self.process_log_file = config_load.process_log_file
        self.deps_log_file = config_load.deps_log_file
        self.removepkg = config_load.removepkg
        self.dialog = config_load.dialog
        self.ask_question = config_load.ask_question
        self.red = config_load.red
        self.grey = config_load.grey
        self.endc = config_load.endc
        self.answer_yes = config_load.answer_yes

        self.dialogbox = DialogBox()
        self.utils = Utilities()
        self.multi_proc = MultiProcess(options)
        self.view = View(options=options)
        self.choose_packages = Choose(options)

        self.deps_log: dict[str, Any] = {}
        self.packages_for_remove: list[str] = []
        self.dependencies: list[str] = []
        self.found_dependent_packages: dict[str, str] = {}

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)
        logger.debug("RemovePackages initialized. Resolve off: %s, Dialog enabled: %s", self.option_for_resolve_off, self.dialog)

    def remove(self, upgrade: bool = False) -> None:
        """Remove packages.

        Args:
            upgrade (bool, optional): Is packages comes from upgrade method.
        """
        logger.info("Starting package removal process. Upgrade context: %s", upgrade)
        if not self.option_for_resolve_off:
            self.deps_log = self.utils.read_json_file(self.deps_log_file)
            logger.debug("Loaded dependency log from %s.", self.deps_log_file)
        else:
            logger.info("Dependency resolution is off. Skipping deps_log loading.")

        if upgrade:
            logger.debug("Packages are from upgrade. Asking user to choose packages for removal.")
            self.packages = self.choose_packages_for_remove(self.packages, upgrade)
            logger.info("User selected %d packages for removal from upgrade list.", len(self.packages))

        if self.packages:
            logger.info("Proceeding with removal for initial packages: %s", self.packages)
            self.add_packages_for_remove()
            self.remove_doubles_dependencies()

            if not self.option_for_resolve_off:
                logger.debug("Resolving dependencies for removal.")
                self.dependencies = self.choose_packages_for_remove(self.dependencies)
                logger.info("User selected %d dependencies for removal.", len(self.dependencies))
            else:
                logger.info("Dependency resolution is off. Skipping dependency selection.")

            self.add_installed_dependencies_to_remove()
            logger.debug("Final list of packages to remove: %s", self.packages_for_remove)

            self.view.remove_packages(self.packages, self.dependencies)  # Display to user.
            self.find_dependent()

            answer: str = 'y'
            if upgrade:
                answer = self.remove_question()
                logger.debug("Answer for upgrade removal question: %s", answer)
            else:
                # view.question() handles user input and exits on N or Ctrl+C.
                self.view.question()

            if answer.lower() == 'y':
                start: float = time.time()
                self.remove_packages()
                elapsed_time: float = time.time() - start
                self.utils.finished_time(elapsed_time)
                logger.info("Package removal process completed in %.2f seconds.", elapsed_time)
            else:
                logger.info("Package removal cancelled by user.")
        else:
            logger.info("No packages selected for removal. Exiting removal process.")

    def add_packages_for_remove(self) -> None:
        """Add packages specified by the user and their direct dependencies (if installed) to the removal list."""
        logger.debug("Adding initial packages and their direct dependencies to removal list.")
        for package in self.packages:
            installed: str = self.utils.is_package_installed(package)
            if installed:
                self.packages_for_remove.append(installed)
                logger.debug("Added user-specified package '%s' (installed as '%s') to removal list.", package, installed)
            else:
                logger.warning("User-specified package '%s' is not installed. Skipping.", package)

            if not self.option_for_resolve_off and self.deps_log.get(package):
                dependencies: list[str] = self.deps_log[package]
                logger.debug("Found %d direct dependencies for '%s': %s", len(dependencies), package, dependencies)
                for dep in dependencies:
                    # Add dependency if installed and not already in the main packages list (to avoid duplicates/re-prompts).
                    if self.utils.is_package_installed(dep) and dep not in self.packages:
                        self.dependencies.append(dep)
                        logger.debug("Added dependency '%s' to dependencies list for removal.", dep)
                    else:
                        logger.debug("Skipping dependency '%s': not installed or already in main packages list.", dep)
            elif self.option_for_resolve_off:
                logger.debug("Dependency resolution is off, skipping direct dependency lookup for '%s'.", package)
            else:
                logger.debug("No dependency log found for '%s'.", package)

    def find_dependent(self) -> None:
        """Find packages that depend on packages in the removal list, and warn the user."""
        logger.debug("Searching for packages dependent on those marked for removal.")
        for package_to_remove_full_name in self.packages_for_remove:
            name_to_remove: str = self.utils.split_package(package_to_remove_full_name)['name']
            logger.debug("Checking for dependents of '%s'.", name_to_remove)
            for pkg_name_in_deps_log, deps_list in self.deps_log.items():
                # Check if the package being removed is a dependency of another installed package.
                if name_to_remove in deps_list and \
                   pkg_name_in_deps_log not in self.packages and \
                   pkg_name_in_deps_log not in self.dependencies:

                    installed_dependent_pkg_full_name: str = self.utils.is_package_installed(pkg_name_in_deps_log)
                    if installed_dependent_pkg_full_name:
                        version: str = self.utils.split_package(installed_dependent_pkg_full_name)['version']
                        self.found_dependent_packages[pkg_name_in_deps_log] = version
                        logger.warning("Found installed package '%s' (version %s) depends on '%s', which is being removed.",
                                       pkg_name_in_deps_log, version, name_to_remove)
                    else:
                        logger.debug("Package '%s' depends on '%s' but is not currently installed.", pkg_name_in_deps_log, name_to_remove)
                else:
                    logger.debug("Package '%s' does not depend on '%s' or is already in removal lists.", pkg_name_in_deps_log, name_to_remove)

        if self.found_dependent_packages:
            dependent_packages: list[str] = list(set(self.found_dependent_packages))  # Use set for uniqueness.
            logger.warning("Found %d extra dependent packages that will be affected by this removal: %s",
                           len(dependent_packages), dependent_packages)
            print(f'\n{self.red}Warning: {self.endc}found extra ({len(dependent_packages)}) dependent packages:')
            for pkg, ver in self.found_dependent_packages.items():
                print(f"{'':>2}{pkg} {self.grey}{ver}{self.endc}")
            print('')
        else:
            logger.info("No extra dependent packages found for the packages to be removed.")

    def remove_doubles_dependencies(self) -> None:
        """Remove duplicate package names from the dependencies list."""
        initial_len = len(self.dependencies)
        self.dependencies = list(set(self.dependencies))
        if len(self.dependencies) < initial_len:
            logger.debug("Removed duplicate dependencies. Reduced from %d to %d.", initial_len, len(self.dependencies))
        else:
            logger.debug("No duplicate dependencies found.")

    def add_installed_dependencies_to_remove(self) -> None:
        """Add the full installed package names of resolved dependencies to the main removal list."""
        logger.debug("Adding installed dependencies to the main removal list.")
        for dep_name in self.dependencies:
            installed: str = self.utils.is_package_installed(dep_name)
            if installed:
                if installed not in self.packages_for_remove:  # Avoid adding duplicates.
                    self.packages_for_remove.append(installed)
                    logger.debug("Added installed dependency '%s' to final removal list.", installed)
                else:
                    logger.debug("Installed dependency '%s' already in final removal list. Skipping.", installed)
            else:
                logger.warning("Dependency '%s' was found in deps_log but is not installed. Skipping from removal.", dep_name)

    def remove_packages(self) -> None:
        """Execute the removal of packages using the 'removepkg' command."""
        logger.info("Executing removal of %d packages.", len(self.packages_for_remove))
        # Remove old process.log file.
        if self.process_log_file.is_file():
            self.process_log_file.unlink()
            logger.debug("Removed old process log file: %s", self.process_log_file)

        print(f'Started of removing total ({len(self.packages_for_remove)}) packages:\n')
        for package_full_name in self.packages_for_remove:
            command: str = f'{self.removepkg} {package_full_name}'
            progress_message: str = 'Removing'
            logger.info("Attempting to remove package: '%s' with command: '%s'", package_full_name, command)

            # multi_proc.process_and_log handles execution and logging of the command output.
            self.multi_proc.process_and_log(command, package_full_name, progress_message)

            name: str = self.utils.split_package(package_full_name)['name']
            if name in self.deps_log.keys():
                self.deps_log.pop(name)
                logger.debug("Removed '%s' from dependency log after successful removal.", name)
            else:
                logger.debug("Package '%s' not found in dependency log, no need to pop.", name)

        # Write updated dependency log back to file
        try:
            self.deps_log_file.write_text(json.dumps(self.deps_log, indent=4), encoding='utf-8')
            logger.info("Updated dependency log written to: %s", self.deps_log_file)
        except IOError as e:
            logger.error("Failed to write updated dependency log to '%s': %s", self.deps_log_file, e)

    def choose_packages_for_remove(self, packages: list[str], upgrade: bool = False) -> list[str]:  # pylint: disable=[R0914]
        """Choose packages via dialog utility or terminal selector.

        Args:
            packages (list[str]): List of package names to choose from.
            upgrade (bool, optional): Indicates if selection is for upgrade context. Defaults to False.

        Returns:
            list[str]: List of selected package names.
        """
        logger.debug("Entering choose_packages_for_remove for packages: %s, upgrade context: %s", packages, upgrade)
        if not packages:
            logger.info("No packages provided to choose from. Returning empty list.")
            return []

        height: int = 10
        width: int = 70
        list_height: int = 0
        choices: list[Any] = []  # List of tuples for dialog/selector.

        for package_name in packages:
            installed_package_full_name: str = self.utils.is_package_installed(package_name)
            if installed_package_full_name:
                installed_version: str = self.utils.split_package(installed_package_full_name)['version']
                # Format: (tag, item_name, status, description) for dialog.
                choices.append((package_name, installed_version, True, f'Package: {installed_package_full_name}'))
                logger.debug("Added choice for '%s': version '%s'", package_name, installed_version)
            else:
                logger.warning("Package '%s' not installed, skipping from selection choices.", package_name)

        # Determine title and text after choices are populated
        title: str = ' Choose dependencies you want to remove '
        text: str = f'There are {len(choices)} dependencies:'
        if upgrade:
            title = ' Choose packages you want to remove '
            text = f'There are {len(choices)} packages:'
        logger.debug("Selection dialog/selector title: '%s', text: '%s'", title, text)

        selected_packages: list[str] = []
        if self.dialog:
            logger.info("Using dialogbox for package selection.")
            if len(packages) < 2:
                return packages
            code, packages_from_dialog = self.dialogbox.checklist(text, title, height, width, list_height, choices)  # pylint: disable=[W0612]
            os.system('clear')  # Clear terminal after dialog.
            if code == 'ok':
                selected_packages = packages_from_dialog
                logger.info("Dialogbox returned packages: %s", selected_packages)
            else:
                logger.info("Dialogbox cancelled or returned non-zero code (%d). No packages selected.", code)
        else:
            package_names_only = [choice[0] for choice in choices]  # Extract just the package names.
            logger.info("Using TerminalSelector for package selection with %d items.", len(package_names_only))
            terminal_selector = TerminalSelector(package_names_only, title, data={}, is_upgrade=False, initial_selection='all')
            selected_packages = terminal_selector.select()
            logger.info("Terminal selector returned packages: %s", selected_packages)

        return selected_packages

    def remove_question(self) -> str:
        """Question about removing packages for upgrade method.

        Returns:
            str: Answer 'y' or 'n'.
        """
        logger.debug("Asking removal confirmation question for upgrade.")
        answer: str = 'n'
        if self.ask_question:
            try:
                if self.answer_yes:
                    answer = 'y'
                    logger.info("Auto-answering 'yes' to removal question due to config.")
                else:
                    answer = input('\nDo you want to remove these packages? [y/N] ')
                    logger.info("User answered removal question: '%s'", answer)
            except (KeyboardInterrupt, EOFError) as err:
                print('\nOperation canceled by the user.')
                logger.warning("Removal operation cancelled by user via KeyboardInterrupt/EOFError.", exc_info=True)
                raise SystemExit(1) from err
        else:
            logger.info("Skipping removal question as 'ask_question' is disabled. Defaulting to 'n' (unless answer_yes is true).")

        return answer
