#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging  # Import the logging module
import shutil
import time
from pathlib import Path
from typing import Any, Union

import requests

from slpkg.config import config_load
from slpkg.load_data import LoadData
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class RepoInfo:  # pylint: disable=[R0902]
    """View information about repositories."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        logger.debug("Initializing RepoInfo module with options: %s, repository: %s", options, repository)
        self.repository = repository

        # Console colors (not for logging, but part of class attributes)
        self.cyan = config_load.cyan
        self.green = config_load.green
        self.red = config_load.red
        self.grey = config_load.grey
        self.endc = config_load.endc

        self.load_data = LoadData()
        self.utils = Utilities()
        self.repos = Repositories()
        self.columns, self.rows = shutil.get_terminal_size()

        # Calculate alignment for console output based on terminal size
        self.name_alignment: int = self.columns - 61
        self.name_alignment = max(self.name_alignment, 1)  # Ensure minimum 1

        self.mirror_alignment: int = self.columns - 32
        self.mirror_alignment = max(self.mirror_alignment, 1)  # Ensure minimum 1

        self.enabled: int = 0
        self.total_packages: int = 0
        self.repo_data: dict[str, dict[str, str]] = {}
        self.dates: dict[str, Any] = {}
        self.mirrors_score: dict[str, int] = {}

        self.option_for_repository: Union[bool, str] = options.get('option_repository', False)
        self.option_for_fetch: bool = options.get('option_fetch', False)
        logger.debug("RepoInfo initialized. Single repository option: %s, Fetch option: %s",
                     self.option_for_repository, self.option_for_fetch)

    def info(self) -> None:
        """Print information about repositories."""
        logger.info("Starting repository information display. Fetch option: %s", self.option_for_fetch)
        if self.option_for_fetch:
            logger.debug("Fetch option enabled. Displaying mirror scores.")
            self.view_the_score_title()

            if self.option_for_repository:
                logger.debug("Fetching speed for single repository: %s", self.repository)
                mirror: str = self.repos.repositories[self.repository]['mirror_changelog']
                self.enabled += 1  # Count of enabled repos for summary
                self.check_mirror_speed(self.repository, mirror)
                self.view_summary_of_repository()
            else:
                logger.debug("Fetching speed for all enabled repositories.")
                for repo, data in self.repos.repositories.items():
                    if data['enable']:
                        mirror = data['mirror_changelog']
                        self.enabled += 1
                        self.check_mirror_speed(repo, mirror)
                self.view_summary_of_all_repositories()
        else:
            logger.debug("Fetch option disabled. Displaying repository information.")
            self.load_repo_data()
            self.view_the_title()

            if self.option_for_repository:
                logger.debug("Displaying information for single repository: %s", self.repository)
                self.view_the_repository_information()
            else:
                logger.debug("Displaying information for all repositories.")
                self.view_the_repositories_information()
        logger.info("Repository information display completed.")

    def check_mirror_speed(self, repo: str, url: str) -> None:
        """Check mirrors speed.

        Args:
            repo (str): Name of the repository.
            url (str): The repository mirror.
        """
        logger.debug("Checking mirror speed for repository '%s' at URL: %s", repo, url)

        # Adjust URL if it's a Git repository for SBo/Ponce
        if repo in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
            git_repos: dict[str, str] = {
                self.repos.sbo_repo_name: self.repos.sbo_git_mirror,
                self.repos.ponce_repo_name: self.repos.ponce_git_mirror,
            }
            if git_repos[repo].endswith('git'):
                url = git_repos[repo]
                logger.debug("Adjusted mirror URL for Git repository '%s' to: %s", repo, url)

        url_view = url
        url_length = 45 + (self.columns - 80)
        if url_length < len(url):
            url_view = f'{url[:url_length]}...'
            logger.debug("Truncated URL for display: %s", url_view)

        try:
            start_time: float = time.time()  # Record the start time.
            response = requests.get(url, timeout=10)  # 10-second timeout.
            end_time: float = time.time()  # Record the end time.

            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx).

            if response.status_code == 200:
                response_time = int((end_time - start_time) * 1000)  # Convert to milliseconds.
                self.mirrors_score[repo] = response_time
                print(f"{repo:<19}{url_view:<{self.mirror_alignment}}"
                      f"{response_time:>9} ms")
                logger.info("Mirror speed check successful for '%s': %d ms (URL: %s)", repo, response_time, url)
            else:
                # This block might be redundant due to raise_for_status, but kept for explicit status code logging
                print(f"{self.red}{repo:<19}{self.endc}{url_view:<{self.mirror_alignment}}{self.red}"
                      f"{response.status_code:>12}{self.endc}")
                logger.warning("Mirror speed check for '%s' returned status code: %d (URL: %s)", repo, response.status_code, url)
        except requests.exceptions.Timeout:
            error_message = "Timeout"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment}}{self.red}{error_message:>12}{self.endc}")
            logger.error("Mirror speed check timed out for '%s' (URL: %s)", repo, url)
        except requests.exceptions.ConnectionError:
            error_message = "Connection Error"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment}}{self.red}{error_message:>12}{self.endc}")
            logger.error("Mirror speed check connection error for '%s' (URL: %s)", repo, url)
        except requests.RequestException as e:
            # Catch other request-related errors (e.g., HTTPError from raise_for_status)
            error_message = f"HTTP {e.response.status_code}" if e.response else "Request Error"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment}}{self.red}{error_message:>12}{self.endc}")
            logger.error("Mirror speed check failed for '%s' with request exception: %s (URL: %s)", repo, e, url)
        except Exception as e:  # pylint: disable=[W0703]
            url_length = 45 + (self.columns - 80)
            if url_length < len(url):
                url_view = f'{url[:url_length - 3]}...'  # Adjust truncation for '...'
            error_message = "Unknown Error"
            print(f"{repo:<19}{url_view:<{self.mirror_alignment - 1}}{self.red}{error_message}{self.endc}")
            logger.critical("Mirror speed check encountered an unexpected error for '%s': %s (URL: %s)", repo, e, url, exc_info=True)

    def load_repo_data(self) -> None:
        """Load repository data."""
        logger.debug("Loading repository data.")
        self.dates = self.repo_information()
        logger.debug("Loaded repository update dates: %s", self.dates)
        if self.option_for_repository:
            self.repo_data = self.load_data.load(self.repository)
            logger.info("Loaded data for single repository: %s (Packages: %d)", self.repository, len(self.repo_data))
        else:
            self.repo_data = self.load_data.load('*')  # Load data for all enabled repos
            logger.info("Loaded data for all enabled repositories (Total packages across all: %d)", sum(len(d) for d in self.repo_data.values()))

    def repo_information(self) -> dict[str, dict[str, str]]:
        """Load repository information from JSON file.

        Returns:
            dict[str, dict[str, str]]: Json data file.
        """
        repo_info_json: Path = Path(f'{self.repos.repositories_path}', self.repos.repos_information)
        logger.debug("Checking for repository information JSON file: %s", repo_info_json)
        if repo_info_json.is_file():
            # The original code had a redundant Path() call here. Removed.
            data = self.utils.read_json_file(repo_info_json)
            logger.info("Successfully read repository information from: %s", repo_info_json)
            return data
        logger.warning("Repository information JSON file not found: %s. Returning empty dictionary.", repo_info_json)
        return {}

    def view_the_score_title(self) -> None:
        """Print the title for mirror score display."""
        title: str = 'Fetching mirrors, please wait...'
        print(f'{title}\n')
        print('=' * (self.columns - 1))
        print(f"{'Name:':<19}{'Mirror:':<{self.mirror_alignment}}{'Score:':>12}")
        print('=' * (self.columns - 1))
        logger.debug("Displayed mirror score title and headers.")

    def view_the_title(self) -> None:
        """Print the title for general repository information display."""
        title: str = 'repositories information:'.title()
        if self.option_for_repository:
            title = 'repository information:'.title()
        print(f'\n{title}')
        print('=' * (self.columns - 1))
        print(f"{'Name:':<{self.name_alignment}}{'Status:':<14}{'Last Updated:':<34}{'Packages:':>12}")
        print('=' * (self.columns - 1))
        logger.debug("Displayed repository information title and headers. Title: '%s'", title)

    def view_the_repository_information(self) -> None:
        """Print the information for a single repository."""
        logger.debug("Preparing to display information for single repository: %s", self.repository)
        args: dict[str, Any] = {
            'repo': self.repository,
            'date': 'None',
            'count': 0,
            'color': self.red,
            'status': 'Disable'
        }

        if self.dates.get(self.repository):
            args['date'] = self.dates[self.repository].get('last_updated', 'None')
            logger.debug("Last updated date for '%s': %s", self.repository, args['date'])

        if self.repos.repositories[self.repository]['enable']:
            self.enabled += 1
            args['status'] = 'Enabled'
            args['color'] = self.green
            args['count'] = len(self.repo_data)
            self.total_packages += len(self.repo_data)
            logger.debug("Repository '%s' is enabled. Package count: %d", self.repository, args['count'])
        else:
            logger.debug("Repository '%s' is disabled.", self.repository)

        self.view_the_line_information(args)
        self.view_summary_of_repository()
        logger.debug("Finished displaying information for single repository: %s", self.repository)

    def view_the_repositories_information(self) -> None:
        """Print the information for all repositories."""
        logger.debug("Preparing to display information for all repositories.")
        for repo, conf in self.repos.repositories.items():
            args: dict[str, Any] = {
                'repo': repo,
                'date': 'None',
                'count': 0,
                'color': self.red,
                'status': 'Disable'
            }

            if self.dates.get(repo):
                args['date'] = self.dates[repo].get('last_updated', 'None')
                logger.debug("Last updated date for '%s': %s", repo, args['date'])

            if conf['enable']:
                self.enabled += 1
                args['status'] = 'Enabled'
                args['color'] = self.green
                # Access count from the loaded all_repo_data for this specific repo.
                if repo in self.repo_data and isinstance(self.repo_data[repo], dict):
                    args['count'] = len(self.repo_data[repo])
                    self.total_packages += len(self.repo_data[repo])
                    logger.debug("Repository '%s' is enabled. Package count: %d", repo, args['count'])
                else:
                    logger.warning("Enabled repository '%s' has no loaded data or unexpected data type. Package count set to 0.", repo)
                    args['count'] = 0  # Default to 0 if data not found/valid
            else:
                logger.debug("Repository '%s' is disabled.", repo)

            self.view_the_line_information(args)
        self.view_summary_of_all_repositories()
        logger.debug("Finished displaying information for all repositories.")

    def view_the_line_information(self, args: dict[str, Any]) -> None:
        """Print a single row of repository information.

        Args:
            args (dict[str, Any]): Arguments for printing, including repo name, status, date, and count.
        """
        repository_display_name: str = args['repo']
        repo_color: str = ''
        if args['repo'] == self.repos.default_repository:
            repo_color = self.cyan
            repository_display_name = f"{args['repo']} *"
            logger.debug("Repository '%s' is default, applying cyan color and '*' suffix.", args['repo'])

        # Print the formatted line to console
        print(f"{repo_color}{repository_display_name:<{self.name_alignment}}{self.endc}{args['color']}{args['status']:<14}"
              f"{self.endc}{args['date']:<34}{args['count']:>12}")
        logger.debug("Printed line for repo '%s': Status='%s', Date='%s', Count='%s'",
                     args['repo'], args['status'], args['date'], args['count'])

    def view_summary_of_repository(self) -> None:
        """Print the summary for a single repository."""
        print('=' * (self.columns - 1))
        if self.option_for_fetch:
            # Ensure self.mirrors_score[self.repository] exists before accessing.
            score = self.mirrors_score.get(self.repository, 0)  # Default to 0 if not found.
            print(f"{self.grey}Score {score} ms for repository "
                  f"'{self.repository}'.\n{self.endc}")
            logger.info("Summary for single repository '%s': Score %d ms.", self.repository, score)
        else:
            print(f"{self.grey}Total {self.total_packages} packages available from the "
                  f"'{self.repository}' repository.\n{self.endc}")
            logger.info("Summary for single repository '%s': Total packages %d.", self.repository, self.total_packages)

    def view_summary_of_all_repositories(self) -> None:
        """Print the total summary of all repositories."""
        print('=' * (self.columns - 1))
        if self.option_for_fetch and self.mirrors_score:
            slower_mirror: str = max(self.mirrors_score, key=lambda key: self.mirrors_score[key])
            fastest_mirror: str = min(self.mirrors_score, key=lambda key: self.mirrors_score[key])

            print(f"{self.grey}Fastest mirror is '{fastest_mirror}' and "
                  f"slower mirror is '{slower_mirror}'.\n{self.endc}")
            logger.info("Summary for all mirrors: Fastest '%s', Slower '%s'.", fastest_mirror, slower_mirror)
        else:
            print(f"{self.grey}Total of {self.enabled}/{len(self.repos.repositories)} "
                  f"repositories are enabled with {self.total_packages} packages available.\n"
                  f"* Default repository is '{self.repos.default_repository}'.\n{self.endc}")
            logger.info("Summary for all repositories: %d/%d enabled, %d packages. Default: '%s'.",
                        self.enabled, len(self.repos.repositories), self.total_packages, self.repos.default_repository)
