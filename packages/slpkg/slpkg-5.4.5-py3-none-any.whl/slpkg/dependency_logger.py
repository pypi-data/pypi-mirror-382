#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
from typing import Any

from slpkg.config import config_load
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class DependencyLogger:  # pylint: disable=[R0903]
    """Manages the logging of package dependencies to a JSON file."""

    def __init__(self) -> None:
        logger.debug("Initializing DependencyLogger.")
        self.deps_log_file = config_load.deps_log_file
        self.utils = Utilities()
        logger.debug("DependencyLogger initialized. Log file: %s", self.deps_log_file)

    def write_deps_log(self, name: str, resolved_requires: tuple[str, ...]) -> None:
        """Create or update the dependency log file with installed packages and their resolved dependencies.

        Args:
            name (str): The name of the package whose dependencies are being logged.
            resolved_requires (tuple[str, ...]): A tuple of the resolved dependencies for the package.
                                                  These are the dependencies that were actually installed
                                                  along with the package.
        """
        logger.info("Writing dependency log for package: '%s' with %d resolved dependencies.", name, len(resolved_requires))
        deps_logs: dict[str, Any] = {}
        deps: dict[str, list[str]] = {}
        installed_requires: list[str] = []

        # Filter the resolved dependencies to only include those that are actually installed.
        # This ensures the log reflects the current state of installed dependencies.
        for require in resolved_requires:
            if self.utils.is_package_installed(require):
                installed_requires.append(require)
                logger.debug("Dependency '%s' for '%s' is installed and will be logged.", require, name)
            else:
                logger.debug("Dependency '%s' for '%s' is not installed, skipping from log.", require, name)

        deps[name] = installed_requires

        # Read existing log file if it exists, then update and write back.
        if self.deps_log_file.is_file():
            try:
                deps_logs = self.utils.read_json_file(self.deps_log_file)
                logger.debug("Existing dependency log loaded from %s.", self.deps_log_file)
                if not isinstance(deps_logs, dict):
                    logger.warning("Existing dependency log is not a dictionary. Overwriting.")
                    deps_logs = {}  # Reset if content is malformed.
            except Exception as e:  # pylint: disable=[W0718]
                logger.error("Failed to read existing dependency log from '%s': %s. Starting with empty log.", self.deps_log_file, e)
                deps_logs = {}  # Start fresh if reading fails.

        deps_logs.update(deps)  # Update with the new package's dependencies.

        try:
            self.deps_log_file.write_text(json.dumps(deps_logs, indent=4), encoding='utf-8')
            logger.info("Dependency log for '%s' successfully written to: %s", name, self.deps_log_file)
        except IOError as e:
            logger.error("Failed to write dependency log to '%s': %s", self.deps_log_file, e)
        except Exception as e:  # # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while writing dependency log for '%s': %s", name, e, exc_info=True)
