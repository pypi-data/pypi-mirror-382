#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import shutil
import sys
import termios
import tty
from typing import Set, Union

from slpkg.config import config_load
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class TerminalSelector:  # pylint: disable=[R0902,R0903]
    """
    A class for interactive multi-selection in the terminal using arrow keys and spacebar.
    Supports Unix-like systems only.
    """

    def __init__(self, items: list[str], title: str, data: dict[str, dict[str, str]], is_upgrade: bool, initial_selection: Union[list[int], str, None] = None) -> None:  # pylint: disable=[R0912,R0913,R0915,R0917]
        """
        Initializes the TerminalSelector with a list of items and an optional initial selection.

        Args:
            initial_selection (list | str): Initial selection string or list of integers.
            items (list): A list of strings to be displayed and selected.
            title (str): The title of the operation.
            data (dict[str, dict[str, str]]): The data of the packages.
            is_upgrade (bool): Whether the command is for upgrade.
        """
        logger.debug("Initializing TerminalSelector with title: '%s', %d items, is_upgrade: %s, initial_selection: %s",
                     title, len(items), is_upgrade, initial_selection)
        self.data = data
        self.is_upgrade = is_upgrade
        self.title = title.strip()
        self.initial_selection = initial_selection

        self.terminal_selector = config_load.terminal_selector
        self.bold = config_load.bold
        self.back_white = config_load.back_white
        self.back_grey = config_load.back_grey
        self.grey = config_load.grey
        self.red = config_load.red
        self.yellow = config_load.yellow
        self.green = config_load.green
        self.black = config_load.black
        self.hg = f"{self.back_white}{self.black}"
        self.endc = config_load.endc
        self.colors = config_load.colors
        self.columns, self.rows = shutil.get_terminal_size()

        self.utils = Utilities()

        # Validate input items list.
        if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
            logger.error("TypeError: Items must be a list of strings. Received: %s", type(items))
            raise TypeError("Items must be a list of strings.")

        if not items:
            self._items: list[str] = []
            logger.info("TerminalSelector initialized with an empty list of items.")
        else:
            self._items = items
            logger.debug("TerminalSelector initialized with %d items.", len(self._items))

        self._selected_indices: Set[int] = set()
        self._current_selection_index: int = 0
        self._num_items = len(self._items)

        # Handle empty _items list for max() to prevent ValueError.
        if self._num_items > 0:
            self.longest_name: int = len(max(self._items, key=len))
            logger.debug("Calculated longest item name length: %d", self.longest_name)
        else:
            self.longest_name = 0
            logger.debug("No items, longest_name set to 0.")

        # --- Handle initial_selection ---
        if initial_selection == "all":
            self._selected_indices = set(range(self._num_items))
            logger.debug("Initial selection set to 'all' (%d items selected).", len(self._selected_indices))
        elif isinstance(initial_selection, list):
            # Validate indices and add to selected_indices.
            initial_count = 0
            for i, status_flag in enumerate(initial_selection[:self._num_items]):
                if status_flag == 1:
                    self._selected_indices.add(i)
                    initial_count += 1
            logger.debug("Initial selection set from list (%d items selected).", initial_count)
        else:
            logger.debug("No initial selection or 'none' specified. Selection starts empty.")

        # --- Viewport state for scrolling ---
        # Lines for title, instructions, and possibly a bottom border.
        # This determines the actual area for selectable items.
        self._header_lines: int = 2  # Increased to accommodate "Use arrows..." and "Enter..." instructions.
        self._footer_lines: int = 1  # A line at the bottom for prompt/padding.
        self._rows_for_items: int = self.rows - self._header_lines - self._footer_lines

        # Ensure we always have at least one line for items, even on very small terminals
        if self._rows_for_items <= 0:
            self._rows_for_items = 1
            # Adjust header lines if terminal is extremely small and cannot fit defaults
            self._header_lines = max(0, self.rows - self._footer_lines - self._rows_for_items)

        # The index of the first item currently visible at the top of the item display area
        self._top_visible_index: int = 0
        logger.debug("Viewport configured: Total rows: %d, Header lines: %d, Footer lines: %d, Rows for items: %d",
                     self.rows, self._header_lines, self._footer_lines, self._rows_for_items)

    def _repo_pkg_version(self, package: str) -> str:
        """Returns the package version of the repository package.

        Args:
            package: The name of the package.

        Returns:
            Repository package version.
        """
        version: str = self.data.get(package, {}).get("version", "")
        logger.debug("Repo package version for '%s': %s", package, version)
        return version

    def _installed_pkg_name(self, package: str) -> str:
        """Returns the name of the installed package.

        Args:
            package: The name of the package.

        Returns:
            Name of the installed package.
        """
        installed: str = self.utils.is_package_installed(package)
        logger.debug("Installed package name for '%s': %s", package, installed)
        return installed

    def _installed_pkg_version(self, package: str) -> str:
        """Returns the installed version of the package.

        Args:
            package: The name of the package.

        Returns:
            Version of the package.
        """
        package_name: str = self._installed_pkg_name(package)
        if package_name:
            version: str = self.utils.split_package(package_name)["version"]
            logger.debug("Installed package version for '%s': %s", package, version)
            return version
        logger.debug("Installed package name not found for '%s', returning empty version.", package)
        return ""

    def _repo_pkg_build(self, package: str) -> str:
        """Returns the build number of the repository package.

        Args:
            package: The name of the package.

        Returns:
            The build number.
        """
        build: str = self.data.get(package, {}).get("build", "")
        logger.debug("Repo package build for '%s': %s", package, build)
        return build

    def _installed_pkg_build(self, package: str) -> str:
        """Returns the build number of installed package.

        Args:
            package: The name of the package.

        Returns:
            Build number of installed package.
        """
        installed: str = self._installed_pkg_name(package)
        if installed:
            build: str = self.utils.split_package(installed)["build"]
            # logger.debug("Installed package build for "%s": %s", package, build)
            return build
        logger.debug("Installed package name not found for '%s', returning empty build.", package)
        return ""

    @staticmethod
    def _get_char() -> str:
        """Reads a single character from stdin without waiting for Enter."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def _move_cursor_to(row: int, col: int) -> None:
        """Moves the cursor to a specific row and column (1-indexed)."""
        sys.stdout.write(f"\033[{row};{col}H")
        sys.stdout.flush()
        logger.debug("Moved cursor to R%d C%d", row, col)

    @staticmethod
    def _erase_line() -> None:
        """Erases the current line from the cursor position to the end."""
        sys.stdout.write("\033[K")
        sys.stdout.flush()
        logger.debug("Erased current line.")

    @staticmethod
    def _hide_cursor() -> None:
        """Hides the terminal cursor using ANSI escape codes."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        logger.debug("Hid terminal cursor.")

    @staticmethod
    def _show_cursor() -> None:
        """Shows the terminal cursor using ANSI escape codes."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        logger.debug("Showed terminal cursor.")

    @staticmethod
    def _clear_screen() -> None:
        """Clears the entire terminal screen and moves cursor to home position."""
        sys.stdout.write("\033[2J")  # Clear screen
        sys.stdout.write("\033[H")  # Move cursor to home (top-left)
        sys.stdout.flush()
        logger.debug("Cleared terminal screen and moved cursor to home.")

    def _print_instructions(self) -> None:
        """Prints the title and instructions at the top of the terminal."""
        self._move_cursor_to(1, 1)
        self._erase_line()
        gr = self.grey
        bg = f"{self.back_grey}{gr}"
        ec = self.endc
        message_length: int = 74  # instructions_message length without ASCII escape colour codes.
        balance_length: int = self.columns - message_length
        instructions_message: str = f"{bg}Press {ec}{gr}[SPACE]{bg}, {ec}{gr}[TAB]{bg} for multi-selection and {ec}{gr}[ENTER]{bg} to select and accept.{' ' * balance_length}{ec}"
        sys.stdout.write(instructions_message)

        self._move_cursor_to(2, 1)
        self._erase_line()
        sys.stdout.write(f"{self.bold}{self.title}:{self.endc}")
        sys.stdout.flush()
        logger.debug("Printed terminal selector instructions.")

    def _render_item_line(self, item_index: int, screen_row_offset: int, is_current_selection: bool) -> None:  # pylint: disable=[R0914]
        """
        Renders a single item line on the specified terminal row, applying highlight if needed.

        Args:
            item_index: The index of the item in the self._items list.
            screen_row_offset: The offset from the start of the item display area (0-indexed).
                               e.g., if it"s the first item displayed, offset is 0.
            is_current_selection: True if this item is currently highlighted by the cursor.
        """
        if item_index < 0 or item_index >= self._num_items:
            logger.warning("Attempted to render out-of-bounds item_index: %d", item_index)
            return

        item_display = self._items[item_index]
        is_selected = item_index in self._selected_indices

        prefix = f"{self.red}>{self.endc}" if is_current_selection else " "
        pick: str = f"{self.yellow}*{self.endc}"
        if not self.colors:  # Use ">" prefix only if colors are off
            prefix = ">" if is_current_selection else " "
        checkbox: str = f" [{pick}]" if is_selected else " [ ]"

        display_string_item = ""
        if self.is_upgrade:
            arrow: str = " -> "
            installed_version: str = self._installed_pkg_version(item_display)
            repo_pkg_version: str = self._repo_pkg_version(item_display)
            repo_build: str = f"({self._repo_pkg_build(item_display)})"
            installed_build: str = f" ({self._installed_pkg_build(item_display)})"

            if not installed_version:
                installed_version = f"{self.green}<- Add{self.endc} New Package "
                installed_build = ""
                repo_pkg_version = ""
                repo_build = ""
                arrow = ""

            inst_package_display: str = ""
            if installed_version:
                inst_package_display = f"{installed_version}{installed_build}{arrow}"

            # Use longest_name for dynamic padding, and apply highlight color if applicable
            pkg_name_formatted = f"{item_display:<{self.longest_name}}"
            if self.colors and is_current_selection:
                pkg_name_formatted = f"{self.hg}{pkg_name_formatted}{self.endc}"

            display_string_item = (f"{prefix}{checkbox} {pkg_name_formatted} {inst_package_display}"
                                   f"{self.yellow}{repo_pkg_version} {repo_build}{self.endc}")
        else:
            pkg_name_formatted = item_display
            if self.colors and is_current_selection:
                pkg_name_formatted = f"{self.hg}{pkg_name_formatted}{self.endc}"
            display_string_item = f"{prefix}{checkbox} {pkg_name_formatted}"

        target_row = self._header_lines + screen_row_offset + 1  # +1 because terminal rows are 1-indexed.
        self._move_cursor_to(target_row, 1)  # Move to start of line.
        self._erase_line()  # Clear anything previously on this line.
        sys.stdout.write(display_string_item)
        sys.stdout.flush()
        logger.debug("Rendered item %d at screen row %d: %s", item_index, screen_row_offset, display_string_item.strip())

    def _render_viewport(self) -> None:
        """
        Clears the item display area and redraws all visible items
        based on _top_visible_index and _current_selection_index.
        """
        logger.debug("Rendering viewport. Top visible index: %d, Current selection index: %d",
                     self._top_visible_index, self._current_selection_index)

        # Clear the entire display area for items
        for r in range(self._rows_for_items):
            self._move_cursor_to(self._header_lines + r + 1, 1)
            self._erase_line()

        # Render each visible item
        for r in range(self._rows_for_items):
            item_index = self._top_visible_index + r
            if item_index < self._num_items:
                is_current_selection = item_index == self._current_selection_index
                self._render_item_line(item_index, r, is_current_selection)
            else:
                # If there are fewer items than available rows, stop rendering.
                # The _erase_line() above already cleared these empty rows.
                break

        # Position the cursor at the currently selected item"s line on screen
        if self._num_items > 0:
            cursor_row_in_viewport = self._current_selection_index - self._top_visible_index
            self._move_cursor_to(self._header_lines + cursor_row_in_viewport + 1, 1)
        sys.stdout.flush()
        logger.debug("Viewport rendering complete.")

    def select(self) -> list[str]:  # pylint: disable=[R0912,R0914,R0915]
        """
        Starts the interactive selection process.

        Returns:
            list: A list of selected items (strings), or an empty list if nothing was selected
                  or the process was cancelled.
        """
        logger.info("Starting interactive terminal selection.")
        if not self._items:
            logger.info("No items to select. Returning empty list.")
            return []

        if not self.terminal_selector or len(self._items) < 2:
            logger.info("Terminal selector disabled or less than 2 items (%d). Returning initial selection.", len(self._items))
            # Logic for non-interactive mode should mirror the original
            if self.initial_selection == "all":
                return self._items
            if isinstance(self.initial_selection, list):
                # Return items corresponding to initial selected indices
                return [self._items[i] for i in sorted(list(self._selected_indices))]
            return []  # "none" or default to empty

        self._hide_cursor()
        self._clear_screen()  # Clear entire screen at start.
        logger.debug("Cursor hidden and screen cleared for interactive selection.")

        final_selection: list[str] = []

        try:  # pylint: disable=[R1702]
            self._print_instructions()  # Print title and fixed instructions.
            self._render_viewport()  # Initial drawing of the items viewport.

            while True:
                char: str = self._get_char()
                logger.debug("Received input character: %s (repr: %r)", char, char)

                old_selection_index = self._current_selection_index
                old_top_visible_index = self._top_visible_index
                redraw_full_viewport = False  # Flag to indicate if entire viewport needs redrawing.

                if char == "\x1b":  # ASCII escape sequence start for arrow/page keys
                    char += self._get_char()  # Read "["
                    char += self._get_char()  # Read "A", "B", "C", "D", "5", "6" etc.
                    logger.debug("Detected ANSI escape sequence: %s", char)

                    if char == "\x1b[A":  # Up arrow
                        if self._current_selection_index > 0:
                            self._current_selection_index -= 1
                            # If new selection goes above current viewport top, scroll up
                            if self._current_selection_index < self._top_visible_index:
                                self._top_visible_index = self._current_selection_index
                                redraw_full_viewport = True
                        logger.debug("Moved up. New index: %d, Top visible: %d", self._current_selection_index, self._top_visible_index)

                    elif char == "\x1b[B":  # Down arrow
                        if self._current_selection_index < self._num_items - 1:
                            self._current_selection_index += 1
                            # If new selection goes below current viewport bottom, scroll down
                            if self._current_selection_index >= self._top_visible_index + self._rows_for_items:
                                self._top_visible_index += 1
                                redraw_full_viewport = True
                        logger.debug("Moved down. New index: %d, Top visible: %d", self._current_selection_index, self._top_visible_index)

                    elif char == "\x1b[5":  # Page Up
                        self._current_selection_index = max(0, self._current_selection_index - self._rows_for_items)
                        self._top_visible_index = max(0, self._top_visible_index - self._rows_for_items)
                        redraw_full_viewport = True
                        logger.debug("Page Up. New index: %d, Top visible: %d", self._current_selection_index, self._top_visible_index)

                    elif char == "\x1b[6":  # Page Down
                        self._current_selection_index = min(self._num_items - 1, self._current_selection_index + self._rows_for_items)
                        # Adjust top_visible_index to ensure selected item is visible
                        if self._current_selection_index >= self._top_visible_index + self._rows_for_items:
                            self._top_visible_index = self._current_selection_index - (self._rows_for_items - 1)
                        # Ensure top_visible_index doesn"t go out of bounds at the end of the list
                        self._top_visible_index = min(self._top_visible_index, max(0, self._num_items - self._rows_for_items))

                        redraw_full_viewport = True
                        logger.debug("Page Down. New index: %d, Top visible: %d", self._current_selection_index, self._top_visible_index)

                    # --- Redraw logic after cursor movement ---
                    if redraw_full_viewport:
                        self._render_viewport()

                    elif old_selection_index != self._current_selection_index:
                        # Only selection changed within the current viewport,
                        # redraw only the two affected lines for efficiency.
                        # First, un-highlight the old line.
                        old_screen_row_offset = old_selection_index - old_top_visible_index
                        self._render_item_line(old_selection_index, old_screen_row_offset, False)
                        # Then, highlight the new line
                        new_screen_row_offset = self._current_selection_index - self._top_visible_index
                        self._render_item_line(self._current_selection_index, new_screen_row_offset, True)
                        # Reposition cursor to the new highlighted item"s screen position.
                        self._move_cursor_to(self._header_lines + new_screen_row_offset + 1, 1)
                        sys.stdout.flush()

                elif char == " ":  # Spacebar for select/deselect
                    if self._current_selection_index in self._selected_indices:
                        self._selected_indices.remove(self._current_selection_index)
                        logger.info("Deselected item at index %d: '%s'", self._current_selection_index, self._items[self._current_selection_index])
                    else:
                        self._selected_indices.add(self._current_selection_index)
                        logger.info("Selected item at index %d: '%s'", self._current_selection_index, self._items[self._current_selection_index])
                    # Redraw the current line to show the checkbox change (it will also re-apply highlight).
                    current_screen_row_offset = self._current_selection_index - self._top_visible_index
                    self._render_item_line(self._current_selection_index, current_screen_row_offset, True)
                    # Ensure cursor is back at the start of the line for current selection.
                    self._move_cursor_to(self._header_lines + current_screen_row_offset + 1, 1)
                    sys.stdout.flush()

                elif char == "\t":  # Tab key for select/deselect all
                    if len(self._selected_indices) == self._num_items:
                        # If all are selected, deselect all
                        self._selected_indices.clear()
                        logger.info("Deselected all items using Tab key.")
                    else:
                        # Otherwise, select all
                        self._selected_indices = set(range(self._num_items))
                        logger.info("Selected all items using Tab key.")
                    self._render_viewport()  # Redraw entire viewport to update all checkboxes

                elif char in ("\r", "\n"):  # Enter key to finalize selection.
                    logger.info("Enter key pressed. Finalizing selection.")
                    # Move cursor to a clear line below the list
                    self._move_cursor_to(self._header_lines + self._rows_for_items + self._footer_lines + 1, 1)
                    self._erase_line()  # Clear any leftover text on the final line.
                    print("")  # New line for clean prompt after selector exits.

                    final_selection = [self._items[i] for i in sorted(self._selected_indices)]
                    logger.info("Selection finalized. %d items selected: %s", len(final_selection), final_selection)
                    break  # Exit the loop

                elif char in ("\x03", "q", "Q"):  # Ctrl+C or q for quit.
                    exit_code: int = 1
                    logger.info("Selection cancelled by user (key: %r).", char)
                    # Move cursor to a clear line below the list
                    self._move_cursor_to(self._header_lines + self._rows_for_items + self._footer_lines + 1, 1)
                    self._erase_line()
                    print("\nSelection cancelled.")
                    if char in ("q", "Q"):
                        exit_code = 0
                    sys.exit(exit_code)  # Exit the script with an error code for cancellation.

        finally:
            self._show_cursor()  # Always show cursor when done.
            self._clear_screen()  # Clear the screen completely on exit to restore terminal state.
            logger.debug("Cursor shown and screen cleared after interactive selection.")

        return final_selection
