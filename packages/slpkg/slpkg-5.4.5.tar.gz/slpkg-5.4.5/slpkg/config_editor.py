#!/usr/bin/python3
# -*- coding: utf-8 -*-


import ast
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import tomlkit

from slpkg.config import config_load
from slpkg.dialog_box import DialogBox
from slpkg.errors import Errors

logger = logging.getLogger(__name__)


class FormConfigs:  # pylint: disable=[R0902]
    """Edit slpkg.toml config file with dialog utility."""

    def __init__(self, options: dict[str, bool]) -> None:
        logger.debug("Initializing FormConfigs module with options: %s", options)
        self.dialog = config_load.dialog
        self.etc_path = config_load.etc_path
        self.prog_name = config_load.prog_name
        self.config = config_load.config
        self.editor = config_load.editor

        self.dialogbox = DialogBox()
        self.errors = Errors()

        self.original_configs: dict[str, dict[str, Any]] = {}  # Will hold the full TOML structure.
        self.config_file: Path = Path(self.etc_path, f'{self.prog_name}.toml')
        self.option_for_edit: bool = options.get('option_edit', False)
        logger.debug("FormConfigs initialized. Dialog enabled: %s, Option for direct edit: %s, Config file: %s, Config editor: %s",
                     self.dialog, self.option_for_edit, self.config_file, self.editor)

    def run(self) -> None:
        """Choose tool to edit the configuration file."""
        logger.info("Starting configuration file editing process.")
        if self.dialog:
            logger.debug("Dialog utility is enabled.")
            if self.option_for_edit:
                logger.info("Option --edit is enabled. Calling external editor first.")
                self.editor_config()  # User wants to edit with external editor first.
            logger.info("Calling dialog_edit for interactive form.")
            self.dialog_edit()  # Then present the dialog form.
        else:
            logger.info("Dialog utility is disabled. Calling external editor only.")
            self.editor_config()  # Only use external editor.

    def editor_config(self) -> None:
        """Edit slpkg.toml configuration file with system EDITOR"""
        editor = self.editor
        if not editor:
            editor = os.environ.get('EDITOR', '')
        if not editor:
            logger.error("No editor configured or found in environment. Cannot open external editor for changelog.")
            print("Error: No editor configured or found. Cannot open editor.")
            sys.exit(1)

        command = [editor, str(self.config_file)]  # Ensure Path object is converted to string.
        logger.info("Opening configuration file '%s' with external editor: '%s'", self.config_file, editor)
        try:
            subprocess.run(command, check=True)  # check=True will raise CalledProcessError on non-zero exit codes.
            logger.info("External editor exited successfully.")
        except subprocess.CalledProcessError as e:
            logger.error("External editor command failed with exit code %s: %s", e.returncode, e, exc_info=True)
            self.errors.message(f"External editor failed with exit code {e.returncode}", exit_status=e.returncode)
        except FileNotFoundError:
            logger.error("External editor '%s' not found. Please ensure it is installed and in your PATH.", editor, exc_info=True)
            self.errors.message(f"External editor '{editor}' not found.", exit_status=1)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while opening external editor: %s", e, exc_info=True)
            self.errors.message(f"An unexpected error occurred with editor: {e}", exit_status=1)

        sys.exit(0)

    def dialog_edit(self) -> None:
        """Read and write the configuration file using dialog form."""
        logger.info("Preparing dialog form for editing configuration file: %s", self.config_file)
        elements: list[Any] = []
        height: int = 0
        width: int = 0
        form_height: int = 0
        text: str = f'Edit the configuration file: {self.config_file}'
        title: str = ' Configuration File '

        # Creating the elements for the dialog form.
        # self.config holds the 'CONFIGS' table from the TOML file.
        for i, (key, value) in enumerate(self.config.items(), start=1):
            display_value = str(value)
            if isinstance(value, bool):  # Convert booleans to 'true'/'false' strings for dialog.
                display_value = 'true' if value else 'false'

            # elements format: (tag, row, col, default_value, field_row, field_col, field_length, input_max_length, help_text, help_text_label)
            elements.extend(
                [(key, i, 1, display_value, i, 21, 47, 200, '0x0', f'Config: {key} = {display_value}')]
            )
            logger.debug("Added dialog element for key '%s' with value '%s'.", key, display_value)

        logger.debug("Calling dialogbox.mixedform with %d elements.", len(elements))
        code, tags = self.dialogbox.mixedform(text, title, elements, height, width, form_height)

        os.system('clear')  # Clear terminal after dialog exits.
        logger.debug("Dialogbox exited with code: '%s', returned tags: %s", code, tags)

        if code == 'help':  # Dialog returns 'help' string for help button
            logger.info("User requested help from dialog. Displaying textbox with config file content.")
            self.help()
        elif code == 'ok':  # Dialog returns 'ok' string for OK button
            logger.info("User confirmed changes in dialog. Writing new configurations.")
            self.write_configs(tags)
        else:
            logger.info("Dialog was cancelled or returned an unexpected code ('%s'). No changes written.", code)

    def help(self) -> None:
        """Load the configuration file on a text box."""
        logger.info("Displaying help textbox for config file: %s", self.config_file)
        # The textbox method displays the content of the file.
        self.dialogbox.textbox(str(self.config_file), 40, 60)
        logger.debug("Textbox closed. Returning to dialog_edit.")
        self.dialog_edit()  # Return to the dialog form after help is viewed.

    def read_configs(self) -> None:
        """Read the original config file into self.original_configs."""
        logger.debug("Reading original config file: %s", self.config_file)
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.original_configs = tomlkit.parse(file.read())
            logger.info("Successfully read original config file.")
        except FileNotFoundError:
            logger.error("Original config file '%s' not found during read_configs. Cannot proceed.", self.config_file)
            self.errors.message(f"Configuration file '{self.config_file}' not found.", exit_status=1)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("Error reading original config file '%s': %s", self.config_file, e, exc_info=True)
            self.errors.message(f"Error reading configuration file: {e}", exit_status=1)

    def write_configs(self, tags: list[str]) -> None:
        """Write new configs to the file.

        Args:
            tags (list[str]): User new configs (values from the dialog form).
        """
        logger.info("Writing new configurations to file: %s. Received tags: %s", self.config_file, tags)
        self.read_configs()  # Ensure original_configs is loaded.

        # Iterate through the keys in the 'CONFIGS' section of the original TOML structure
        # and update them with the new values from 'tags'.
        # The order of keys in self.original_configs['CONFIGS'] must match the order of 'tags'.
        for key, new_value_str in zip(self.original_configs['CONFIGS'].keys(), tags):
            logger.debug("Processing config key '%s' with new string value '%s'.", key, new_value_str)

            new_value: Any = new_value_str  # Start with the string value.

            # Attempt to convert string values to their appropriate Python types
            if new_value_str.lower() == 'true':
                new_value = True
            elif new_value_str.lower() == 'false':
                new_value = False
            elif re.match(r"^-?\d+(\.\d+)?$", new_value_str):  # Check for int or float pattern.
                if new_value_str.isdigit() or (new_value_str.startswith('-') and new_value_str[1:].isdigit()):
                    new_value = int(new_value_str)
                else:
                    new_value = float(new_value_str)
            elif re.match(r'^\s*\[.*\]\s*$', new_value_str):  # Check for list pattern.
                try:
                    new_value = ast.literal_eval(new_value_str)
                    if not isinstance(new_value, list):  # Ensure it's actually a list after eval.
                        raise ValueError("Evaluated value is not a list.")
                except (SyntaxError, ValueError, TypeError) as e:
                    logger.error("Error parsing list value for key '%s': '%s'. Error: %s", key, new_value_str, e, exc_info=True)
                    self.errors.message(f"Error parsing config file for key '{key}'. Invalid list format: '{new_value_str}'", 1)

            # Update the value in the TOML document object
            self.original_configs['CONFIGS'][key] = new_value
            logger.debug("Updated config '%s' to Python value: %s (type: %s)", key, new_value, type(new_value))

        # Write the updated TOML document back to the file
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                file.write(tomlkit.dumps(self.original_configs))
            logger.info("Successfully wrote new configurations to file: %s", self.config_file)
        except IOError as e:
            logger.critical("Failed to write configuration file '%s': %s", self.config_file, e, exc_info=True)
            self.errors.message(f"Error writing configuration file: {e}", exit_status=1)
