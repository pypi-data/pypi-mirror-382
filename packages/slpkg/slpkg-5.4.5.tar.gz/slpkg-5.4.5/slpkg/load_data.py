#!/usr/bin/python3
# -*- coding: utf-8 -*-


import json
import logging
from pathlib import Path
from typing import Any

from slpkg.blacklist import Blacklist
from slpkg.config import config_load
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess

logger = logging.getLogger(__name__)


class LoadData:  # pylint: disable=[R0902]
    """Reads data form json file and load to dictionary."""

    def __init__(self) -> None:
        logger.debug("Initializing LoadData class.")
        self.cyan = config_load.cyan
        self.green = config_load.green
        self.red = config_load.red
        self.endc = config_load.endc

        self.repos = Repositories()
        self.utils = Utilities()
        self.black = Blacklist()
        self.view_process = ViewProcess()
        logger.debug("LoadData class initialized.")

    def load(self, repository: str, message: bool = True) -> dict[str, dict[str, str]]:
        """Load data to the dictionary.

        Args:
            repository (str): Repository name.
            message (bool, optional): Prints or not progress message.

        Returns:
            dict[str, dict[str, str]]: Dictionary data.
        """
        logger.info("Attempting to load data for repository: '%s' (message display: %s).", repository, message)
        self.is_database_exist(repository)

        if message:
            self.view_process.message('Database loading')
            logger.debug("Displaying 'Database loading' message.")

        data: dict[Any, Any] = {}
        if repository == '*':
            logger.info("Loading data for all enabled repositories.")
            for repo, value in self.repos.repositories.items():
                if value['enable']:  # Check if the repository is enabled
                    json_data_file: Path = Path(value['path'], self.repos.data_json)
                    logger.debug("Reading data file for repository '%s': %s", repo, json_data_file)
                    data[repo] = self.read_data_file(json_data_file)
                else:
                    logger.debug("Skipping disabled repository: '%s'", repo)
        else:
            json_data_file = Path(self.repos.repositories[repository]['path'], self.repos.data_json)
            logger.debug("Reading data file for specific repository '%s': %s", repository, json_data_file)
            data = self.read_data_file(json_data_file)

        blacklist: tuple[str, ...] = tuple(self.black.packages())
        if blacklist:
            logger.info("Blacklist packages found. Applying blacklist filtering.")
            if repository == '*':
                logger.debug("Removing blacklist packages from all repositories.")
                data = self._remove_blacklist_from_all_repos(data)
            else:
                logger.debug("Removing blacklist packages from repository: '%s'.", repository)
                data = self._remove_blacklist_from_a_repo(data)
        else:
            logger.debug("No blacklist packages defined.")

        if message:
            self.view_process.done()
            logger.debug("Displaying 'done' message for database loading.")

        logger.info("Data loading for repository '%s' completed successfully.", repository)
        return data

    def is_database_exist(self, repository: str) -> None:
        """Check if database data.json exist.

        Args:
            repository (str): Name of repository.

        Raises:
            SystemExit: Raise exit code.
        """
        logger.info("Checking database existence for repository: '%s'.", repository)
        if repository == '*':
            logger.debug("Checking database existence for all enabled repositories.")
            for repo, value in self.repos.repositories.items():
                if value['enable']:  # Check if the repository is enabled
                    json_data_file: Path = Path(value['path'], self.repos.data_json)
                    self._error_database(json_data_file, repo)
                else:
                    logger.debug("Skipping database existence check for disabled repository: '%s'.", repo)
        else:
            json_data_file = Path(self.repos.repositories[repository]['path'], self.repos.data_json)
            self._error_database(json_data_file, repository)
        logger.debug("Database existence check completed for repository: '%s'.", repository)

    def _error_database(self, json_data_file: Path, repository: str) -> None:
        """Print error for database.

        Args:
            json_data_file (Path): Name of data.json file.
            repository (str): Name of repository.

        Raises:
            SystemExit: Raise system exit error.
        """
        logger.debug("Checking if database file exists: %s for repository: '%s'.", json_data_file, repository)
        if not json_data_file.is_file():
            logger.error("Database file not found: %s for repository '%s'.", json_data_file, repository)
            print(f'\nRepository: {repository}')
            print(f'\n{self.red}Error{self.endc}: File {json_data_file} not found!')
            print('\nNeed to update the database first, please run:\n')
            print(f"{'':>2} $ {self.green}slpkg update{self.endc}\n")
            raise SystemExit(1)
        logger.debug("Database file exists: %s for repository: '%s'.", json_data_file, repository)

    @staticmethod
    def read_data_file(file: Path) -> dict[str, str]:
        """Read JSON data from the file.

        Args:
            file (Path): Path file for reading.

        Returns:
            dict[str, str]

        Raises:
            SystemExit: Description
        """
        logger.info("Attempting to read JSON data from file: %s", file)
        json_data: dict[str, str] = {}
        try:
            json_data = json.loads(file.read_text(encoding='utf-8'))
            logger.debug("Successfully read JSON data from file: %s", file)
        except FileNotFoundError:
            logger.warning("File not found when reading data: %s. Returning empty dictionary.", file)
        except json.decoder.JSONDecodeError as e:
            logger.error("JSONDecodeError when reading file %s: %s. Returning empty dictionary.", file, e)
            print(f"{config_load.red}Error:{config_load.endc} Could not decode JSON from {file}. It might be corrupted.")
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while reading file %s: %s", file, e, exc_info=True)
            print(f"{config_load.red}Critical Error:{config_load.endc} Failed to read {file} due to an unexpected issue.")
        return json_data

    def _remove_blacklist_from_all_repos(self, data: dict[str, Any]) -> dict[str, Any]:
        """Remove blacklist packages from all repositories.

        Args:
            data (dict[str, Any]): Repository data.

        Returns:
            dict[str, Any]
        """
        logger.info("Removing blacklist packages from all repositories.")
        # Remove blacklist packages from keys.
        for name, repo in data.items():
            logger.debug("Processing repository '%s' for blacklist removal (keys).", name)
            blacklist_packages: list[str] = self.utils.ignore_packages(list(data[name].keys()))
            for pkg in blacklist_packages:
                if pkg in data[name].keys():
                    del data[name][pkg]
                    logger.debug("Removed blacklisted package '%s' from repository '%s' (key).", pkg, name)

        # Remove blacklist packages from dependencies (values).
        for name, repo in data.items():
            logger.debug("Processing repository '%s' for blacklist removal (dependencies).", name)
            # Re-evaluate blacklist_packages based on current keys, as some might have been removed
            current_repo_keys = list(data[name].keys())
            blacklist_packages = self.utils.ignore_packages(current_repo_keys)

            for pkg, dep in repo.items():
                deps: list[str] = dep.get('requires', [])
                original_deps_len = len(deps)
                deps_before_removal = list(deps)  # Store for logging.

                for blk in blacklist_packages:
                    if blk in deps:
                        deps.remove(blk)
                        logger.debug("Removed blacklisted package '%s' from dependencies of '%s' in repository '%s'.", blk, pkg, name)
                if len(deps) != original_deps_len:
                    data[name][pkg]['requires'] = deps
                    logger.debug("Updated dependencies for '%s' in '%s': from %s to %s", pkg, name, deps_before_removal, deps)
        logger.info("Blacklist removal from all repositories completed.")
        return data

    def _remove_blacklist_from_a_repo(self, data: dict[str, Any]) -> dict[str, Any]:
        """Remove blacklist from a repository.

        Args:
            data (dict[str, Any]): Repository data.

        Returns:
            dict[str, Any]
        """
        logger.info("Removing blacklist packages from a single repository.")
        blacklist_packages: list[str] = self.utils.ignore_packages(list(data.keys()))
        # Remove blacklist packages from keys.
        for pkg in blacklist_packages:
            if pkg in data.keys():
                del data[pkg]
                logger.debug("Removed blacklisted package '%s' from repository (key).", pkg)

        # Remove blacklist packages from dependencies (values).
        for pkg, dep in data.items():
            deps: list[str] = dep.get('requires', [])
            original_deps_len = len(deps)
            deps_before_removal = list(deps)  # Store for logging.

            for blk in blacklist_packages:
                if blk in deps:
                    deps.remove(blk)
                    logger.debug("Removed blacklisted package '%s' from dependencies of '%s'.", blk, pkg)
            if len(deps) != original_deps_len:
                data[pkg]['requires'] = deps
                logger.debug("Updated dependencies for '%s': from %s to %s", pkg, deps_before_removal, deps)
        logger.info("Blacklist removal from single repository completed.")
        return data
