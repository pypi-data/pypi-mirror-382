#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging  # Import the logging module
import os
import shutil
from typing import Any, Optional, Union

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.terminal_selector import TerminalSelector
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Choose:  # pylint: disable=[R0902]
    """
    Choose packages with dialog or with terminal selector.
    """

    def __init__(self, options: dict[str, bool], repository: Optional[str] = '') -> None:
        logger.debug("Initializing Choose module with repository: '%s', options: %s", repository, options)
        self.repository = repository
        self.options = options

        self.dialog = config_load.dialog
        self.bold = config_load.bold
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc

        self.utils = Utilities()
        self.dialogbox = DialogBox()

        self.choices: list[tuple[Any, ...]] = []
        self.height: int = 10
        self.width: int = 70
        self.list_height: int = 0
        self.ordered: bool = True  # Default value, can be overridden by method call.
        self.columns, self.rows = shutil.get_terminal_size()
        self.match_packages: list[str] = []  # Stores package names that match search criteria.

        self.option_for_select_packages: bool = options.get('option_select', False)
        logger.debug("Choose module initialized. Dialog enabled: %s, Option for select packages: %s",
                     self.dialog, self.option_for_select_packages)

    def packages(self, data: dict[str, dict[str, str]], packages: list[str], method: str, ordered: bool = True) -> list[str]:
        """Call methods to choosing packages via dialog tool.

        Args:
            data (dict[str, dict[str, str]]): Repository data.
            packages (list[str]): List of packages.
            method (str): Type of method (e.g., 'remove', 'upgrade', 'install').
            ordered (bool, optional): Set True for ordered. Defaults to True.

        Returns:
            list[str]: Name of packages selected by the user.

        Raises:
            SystemExit: Exit code 0 if user cancels selection.
        """
        logger.info("Starting package selection for method: '%s', %d initial packages.", method, len(packages))
        title: str = f' Choose packages you want to {method} '
        is_upgrade = False

        # Populate self.choices and self.match_packages based on the method
        if method in ('remove', 'list_installed'):
            logger.debug("Method is '%s'. Calling choose_from_installed.", method)
            self.choose_from_installed(packages)
        elif method == 'upgrade':
            title = f' Choose packages you want to {method} or add '
            is_upgrade = True
            logger.debug("Method is 'upgrade'. Calling choose_for_upgraded.")
            self.choose_for_upgraded(data, packages)
        else:
            logger.debug("Method is '%s'. Calling choose_for_others.", method)
            self.choose_for_others(data, packages)

        if not self.choices:
            logger.info("No choices generated for selection. Returning original packages list.")
            return packages  # If no choices, return the original list of packages.

        selected_packages: list[str] = []  # Initialize to ensure it's always defined.

        if self.dialog:
            logger.info("Using dialogbox for package selection.")

            if ordered:
                self.choices = sorted(self.choices)
                logger.debug("Packages sorted: %s", packages)

            text: str = f'There are {len(self.choices)} packages:'
            code, packages_from_dialog = self.dialogbox.checklist(text, title, self.height, self.width,
                                                                  self.list_height, self.choices)
            os.system('clear')  # Clear terminal after dialog exits.

            if code == 'cancel' or not packages_from_dialog:  # 'cancel' is a string from dialog.
                logger.info("Dialogbox selection cancelled or no packages selected. Exiting.")
                raise SystemExit(0)

            selected_packages = packages_from_dialog
            logger.info("Dialogbox returned %d selected packages.", len(selected_packages))
        else:
            logger.info("Using TerminalSelector for package selection.")
            initial_selection: Union[str, None] = 'all'

            if ordered:
                self.match_packages = sorted(self.match_packages)
                logger.debug("Packages sorted: %s", self.match_packages)

            if self.option_for_select_packages:  # If --select option is used, start with no selection.
                initial_selection = None
                logger.debug("Option --select enabled, initial TerminalSelector selection set to None.")

            terminal_selector = TerminalSelector(self.match_packages, title, data, is_upgrade, initial_selection=initial_selection)
            selected_packages = terminal_selector.select()
            logger.info("TerminalSelector returned %d selected packages.", len(selected_packages))

        return selected_packages

    def choose_from_installed(self, packages: list[str]) -> None:
        """Choose installed packages for remove or find.

        Args:
            packages (list[str]): Name of packages.
        """
        logger.debug("Choosing from installed packages for removal/find. Input packages: %s", packages)
        all_installed_packages = self.utils.all_installed()  # {name: full_package_name}.

        for pkg_name_from_installed, full_installed_package in all_installed_packages.items():
            version: str = self.utils.split_package(full_installed_package)['version']

            for pkg_query in sorted(packages):  # Iterate through user-specified packages/patterns.
                # Check if the installed package name matches the query or if it's a wildcard search
                if pkg_query in pkg_name_from_installed or pkg_query == '*':
                    if pkg_name_from_installed not in self.match_packages:  # Avoid duplicates.
                        self.match_packages.append(pkg_name_from_installed)
                        # Format for dialog/selector: (tag, item_name, status, description)
                        self.choices.extend([(pkg_name_from_installed, version, False, f'Package: {full_installed_package}')])
                        logger.debug("Added installed package '%s' (version: %s) to choices.", pkg_name_from_installed, version)
                    else:
                        logger.debug("Installed package '%s' already in choices. Skipping duplicate.", pkg_name_from_installed)
        logger.debug("Finished choosing from installed packages. Total choices: %d", len(self.choices))

    def choose_for_upgraded(self, data: dict[str, dict[str, str]], packages: list[str]) -> None:
        """Choose packages that they will going to upgrade.

        Args:
            data (dict[str, dict[str, str]]): Data of repository.
            packages (list[str]): Name of packages.
        """
        logger.debug("Choosing packages for upgrade. Input packages: %s", packages)
        for package_name in packages:
            inst_package_full_name: str = self.utils.is_package_installed(package_name)

            # Ensure data[package_name] exists before accessing
            if package_name not in data:
                logger.warning("Package '%s' not found in repository data for upgrade selection. Skipping.", package_name)
                continue

            repo_ver: str = data[package_name]['version']
            repo_build_tag: str = data[package_name]['build']

            if not inst_package_full_name:
                # This is a new package to be added
                new_package_full_name: str = data[package_name]['package']
                self.match_packages.append(package_name)
                self.choices.extend(
                    [(package_name, ' <- \\Z1Add\\Zn New Package ', True,  # \\Z1Add\\Zn is dialog color code.
                      f'Add new package -> {new_package_full_name} Build: {repo_build_tag}')])
                logger.debug("Added new package '%s' to upgrade choices.", package_name)
            else:
                # This is an existing package to be upgraded
                inst_package_version: str = self.utils.split_package(inst_package_full_name)['version']
                inst_package_build: str = self.utils.split_package(inst_package_full_name)['build']

                self.match_packages.append(package_name)
                self.choices.extend(
                    [(package_name, f' {inst_package_version} -> \\Z3\\Zb{repo_ver}\\Zn ', True,  # \\Z3\\Zb is dialog color .
                      f'Installed: {package_name}-{inst_package_version} Build: {inst_package_build} -> '
                      f'Available: {repo_ver} Build: {repo_build_tag}')])
                logger.debug("Added upgradeable package '%s' to upgrade choices (Installed: %s, Repo: %s).",
                             package_name, inst_package_version, repo_ver)
        logger.debug("Finished choosing packages for upgrade. Total choices: %d", len(self.choices))

    def choose_for_others(self, data: dict[str, dict[str, Any]], packages: list[str]) -> None:  # pylint: disable=[R0912]
        """Choose packages for others methods like install, tracking etc.

        Args:
            data (dict[str, dict[str, Any]]): Repository data (can be multi-repo or single-repo data).
            packages (list[str]): Name of packages.
        """
        logger.debug("Choosing packages for other methods (install/tracking). Input packages: %s", packages)
        if self.repository == '*':  # pylint: disable=[R1702]
            logger.debug("Operating in multi-repository mode ('*').")
            for pkg_query in sorted(packages):
                for repo_name, repo_data in data.items():  # data is dict of repos.
                    for package_name, pkg_details in repo_data.items():  # pkg_details is dict for a package.
                        if pkg_query in package_name or pkg_query == '*':
                            version: str = pkg_details.get('version', 'N/A')  # Use .get() for safety.
                            if package_name not in self.match_packages:  # Avoid duplicates.
                                self.match_packages.append(package_name)
                                self.choices.extend([(package_name, version, False, f'Package: {package_name}-{version} > {repo_name}')])
                                logger.debug("Added multi-repo choice for '%s' (version: %s, repo: %s).", package_name, version, repo_name)
                            else:
                                logger.debug("Multi-repo package '%s' already in choices. Skipping duplicate.", package_name)
        else:
            logger.debug("Operating in single-repository mode ('%s').", self.repository)
            # In single-repo mode, 'data' is already the specific repository's data.
            single_repo_data: dict[str, Any] = data  # Cast for clarity.
            for pkg_query in sorted(packages):
                for package_name, pkg_details in single_repo_data.items():
                    if pkg_query in package_name or pkg_query == '*':
                        version = pkg_details.get('version', 'N/A')  # Use .get() for safety.
                        if package_name not in self.match_packages:  # Avoid duplicates.
                            self.match_packages.append(package_name)
                            self.choices.extend([(package_name, version, False, f'Package: {package_name}-{version} > {self.repository}')])
                            logger.debug("Added single-repo choice for '%s' (version: %s, repo: %s).", package_name, version, self.repository)
                        else:
                            logger.debug("Single-repo package '%s' already in choices. Skipping duplicate.", package_name)
        logger.debug("Finished choosing packages for other methods. Total choices: %d", len(self.choices))
