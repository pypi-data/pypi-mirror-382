#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import os
from typing import Any

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.terminal_selector import TerminalSelector
from slpkg.upgrade import Upgrade
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess

logger = logging.getLogger(__name__)


class ChooseDependencies:  # pylint: disable=[R0902,R0903]
    """
    Choose dependencies with dialog or with terminal selector.
    """

    def __init__(self, repository: str, data: dict[str, dict[str, str]], options: dict[str, bool], mode: str) -> None:
        logger.debug("Initializing ChooseDependencies module for repository: '%s', mode: '%s', options: %s",
                     repository, mode, options)
        self.repository = repository
        self.data = data
        self.mode = mode

        self.dialog = config_load.dialog

        self.upgrade = Upgrade(repository, data)
        self.utils = Utilities()
        self.dialogbox = DialogBox()

        self.option_for_reinstall: bool = options.get('option_reinstall', False)
        logger.debug("ChooseDependencies initialized. Dialog enabled: %s, Reinstall option: %s",
                     self.dialog, self.option_for_reinstall)

    def choose(self, dependencies: list[str], view_process: ViewProcess) -> list[str]:  # pylint: disable=[R0912,R0914,R0915]
        """Choose dependencies for install with dialog tool or terminal selector.

        Args:
            dependencies (list[str]): List of dependency names.
            view_process (ViewProcess): An instance of ViewProcess for displaying progress.

        Returns:
            list[str]: List of selected dependency names.
        """
        logger.info("Starting dependency selection for %d dependencies in mode: '%s'.", len(dependencies), self.mode)
        if not dependencies:
            logger.info("No dependencies provided to choose from. Returning empty list.")
            return []

        choices: list[Any] = []
        initial_selection: list[int] = []
        is_upgrade = False  # Flag to pass to TerminalSelector.
        height: int = 10
        width: int = 70
        list_height: int = 0
        title: str = ' Choose dependencies you want to install '

        for package in dependencies:
            logger.debug("Processing dependency '%s' for selection.", package)
            status: bool = True  # Default selection status for dialog/terminal selector.

            # Ensure package exists in self.data before accessing its properties.
            if package not in self.data:
                logger.warning("Dependency '%s' not found in repository data. Skipping from choices.", package)
                continue

            repo_ver: str = self.data[package]['version']
            description: str = self.data[package]['description']
            help_text: str = f'Description: {description}'
            installed: str = self.utils.is_package_installed(package)
            upgradeable: bool = self.upgrade.is_package_upgradeable(installed) if installed else False  # Only check if installed.

            # Determine initial selection status.
            if installed:
                status = False  # If already installed, default to unselected unless upgrade/reinstall.
                logger.debug("Dependency '%s' is installed. Initial status set to False.", package)

            if self.mode == 'upgrade' and upgradeable:
                status = True  # If in upgrade mode and upgradeable, select by default.
                logger.debug("Dependency '%s' is upgradeable in upgrade mode. Initial status set to True.", package)

            if self.option_for_reinstall:
                status = True  # If reinstall option is active, select by default.
                logger.debug("Reinstall option is active for '%s'. Initial status set to True.", package)

            if status:
                initial_selection.append(1)  # Selected.
            else:
                initial_selection.append(0)  # Not selected.

            choices.extend(
                [(package, repo_ver, status, help_text)]
            )
            logger.debug("Added choice for '%s': version '%s', status %s, help '%s'.", package, repo_ver, status, help_text)

        view_process.done()  # Signal completion of data preparation for view_process.
        logger.debug("View process done for dependency preparation.")

        selected_dependencies: list[str] = []  # Initialize to ensure it's always defined.

        if self.dialog:
            logger.info("Using dialogbox for dependency selection.")
            text: str = f'There are {len(choices)} dependencies:'
            code, dialog_selected_deps = self.dialogbox.checklist(text, title, height, width, list_height, choices)
            os.system('clear')  # Clear terminal after dialog exits

            # Dialogbox returns 0 for OK, 1 for Cancel/Esc.
            if code == 'ok':  # Dialog returns 'ok' string for OK button.
                selected_dependencies = dialog_selected_deps
                logger.info("Dialogbox returned %d selected dependencies.", len(selected_dependencies))
            else:
                logger.info("Dialogbox selection cancelled or returned non-OK code ('%s'). Returning empty list.", code)
                # If dialog is cancelled, return an empty list.
                selected_dependencies = []
        else:
            logger.info("Using TerminalSelector for dependency selection.")
            if self.mode == 'upgrade':
                is_upgrade = True  # Pass this flag to TerminalSelector.

            dependency_names_only = [choice[0] for choice in choices]  # Extract just the package names.

            terminal_selector = TerminalSelector(dependency_names_only, title, self.data, is_upgrade, initial_selection)
            selected_dependencies = terminal_selector.select()
            logger.info("TerminalSelector returned %d selected dependencies.", len(selected_dependencies))

        # selected_dependencies.reverse()
        return selected_dependencies
