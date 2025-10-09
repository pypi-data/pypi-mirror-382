#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import os
from multiprocessing import Process, Queue
from pathlib import Path
from typing import Optional, Union

from urllib3 import PoolManager, ProxyManager, make_headers
from urllib3.exceptions import HTTPError, NewConnectionError

from slpkg.config import config_load
from slpkg.progress_bar import ProgressBar
from slpkg.repo_info import RepoInfo
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.imprint import Imprint

logger = logging.getLogger(__name__)


class CheckUpdates:  # pylint: disable=[R0902]
    """Checks for changes in the ChangeLog files."""

    def __init__(self, options: dict[str, bool], repository: str) -> None:
        logger.debug("Initializing CheckUpdates module with options: %s, repository: %s", options, repository)
        self.options = options
        self.repository = repository

        # Configuration settings for urllib3 and proxy.
        self.urllib_timeout = config_load.urllib_timeout
        self.proxy_username = config_load.proxy_username
        self.proxy_password = config_load.proxy_password
        self.proxy_address = config_load.proxy_address
        self.urllib_retries = config_load.urllib_retries
        self.urllib_redirect = config_load.urllib_redirect
        # Initialize colors.
        self.green = config_load.green
        self.red = config_load.red
        self.yellow = config_load.yellow
        self.endc = config_load.endc

        # Initialize dependent utility classes.
        self.utils = Utilities()
        self.progress = ProgressBar()
        self.repos = Repositories()
        self.repo_info = RepoInfo(options, repository)
        self.imp = Imprint()

        # Internal state variables for comparison results and errors.
        self.compare: dict[str, bool] = {}  # Stores repo_name: True if update available, False otherwise.
        self.error_connected: list[str] = []  # Stores URLs that failed to connect.

        # Initialize urllib3 PoolManager (or ProxyManager if proxy is configured)
        # This needs to be set up based on proxy configuration.
        self.http: Union[PoolManager, ProxyManager]
        if self.proxy_address.startswith('http'):
            self.http = ProxyManager(self.proxy_address)
            logger.debug("Initialized HTTP ProxyManager for address: %s", self.proxy_address)
        elif self.proxy_address.startswith('socks'):
            try:
                from urllib3.contrib.socks import \
                    SOCKSProxyManager  # pylint: disable=[C0415]
                self.http = SOCKSProxyManager(self.proxy_address)
                logger.debug("Initialized SOCKS ProxyManager for address: %s", self.proxy_address)
            except (ModuleNotFoundError, ImportError):
                logger.error("PySocks module not found for SOCKS proxy. Falling back to direct connection.")
                self.http = PoolManager(timeout=self.urllib_timeout)
        else:
            self.http = PoolManager(timeout=self.urllib_timeout)
            logger.debug("Initialized PoolManager for direct connection.")

        # Default headers for proxy authentication, if applicable
        self.proxy_default_headers = make_headers(
            proxy_basic_auth=f'{self.proxy_username}:{self.proxy_password}')

        # Options from constructor
        self.option_for_repository: Union[bool, str] = options.get('option_repository', False)
        self.option_for_check: bool = options.get('option_check', False)
        logger.debug("CheckUpdates initialized. Proxy address: '%s', Option for repository: %s, Option for check: %s",
                     self.proxy_address, self.option_for_repository, self.option_for_check)

    def check_the_repositories(self, queue: Optional[Queue]) -> None:  # type: ignore
        """Save checks to a dictionary.

        Args:
            queue (Optional[Queue]): Puts attributes to the queue.
        """
        logger.info("Starting repository checks. Queue provided: %s", queue is not None)
        if self.option_for_repository:
            logger.debug("Checking single repository: %s", self.repository)
            self.save_the_compares(self.repository)
        else:
            logger.debug("Checking all enabled repositories.")
            for repo, enable_data in self.repos.repositories.items():
                if enable_data['enable']:
                    self.save_the_compares(repo)
                else:
                    logger.debug("Repository '%s' is disabled. Skipping check.", repo)

        if queue is not None:
            logger.debug("Putting compare and error_connected data into the queue.")
            queue.put(self.compare)
            queue.put(self.error_connected)
        logger.info("Repository checks completed.")

    def save_the_compares(self, repo: str) -> None:
        """Save compares to a dictionary.

        Args:
            repo (str): Repository name.
        """
        logger.debug("Saving comparison status for repository: %s", repo)
        local_chg_txt: Path = Path(
            self.repos.repositories[repo]['path'],
            self.repos.repositories[repo]['changelog_txt']
        )

        repo_chg_txt: str = (
            f"{self.repos.repositories[repo]['mirror_changelog']}"
            f"{self.repos.repositories[repo]['changelog_txt']}"
        )
        repo_data_file: Path = Path(self.repos.repositories[repo]['path'],
                                    self.repos.data_json)

        logger.debug("Local changelog path: %s, Remote changelog URL: %s, Repo data file: %s",
                     local_chg_txt, repo_chg_txt, repo_data_file)

        if not repo_data_file.is_file():
            # If data.json does not exist, assume update is needed (first time sync or corrupted).
            self.compare[repo] = True
            logger.info("Repository '%s' data file not found. Marking for update.", repo)
        else:
            self.compare[repo] = self.compare_the_changelogs(
                local_chg_txt, repo_chg_txt)
            logger.info("Comparison result for '%s': %s", repo, self.compare[repo])

    def compare_the_changelogs(self, local_chg_txt: Path, repo_chg_txt: str) -> bool:
        """Compare the two ChangeLog files for changes.

        Args:
            local_chg_txt (Path): Path to the local ChangeLog file.
            repo_chg_txt (str): Mirror or remote ChangeLog file.

        Returns:
            bool: True if remote ChangeLog is newer/different, False otherwise.

        Raises:
            SystemExit: For keyboard interrupt during network request.
        """
        logger.debug("Comparing local changelog '%s' with remote changelog '%s'.", local_chg_txt, repo_chg_txt)
        local_size: int = 0
        repo_size: int = 0

        # Get local changelog file size.
        if local_chg_txt.is_file():
            local_size = int(os.stat(local_chg_txt).st_size)
            logger.debug("Local changelog file size: %d bytes.", local_size)
        else:
            logger.debug("Local changelog file '%s' does not exist. Assuming remote is newer.", local_chg_txt)
            # If local file doesn't exist, it's always an update.
            return True

        try:  # Get repository changelog file size from remote.
            logger.debug("Fetching remote changelog header from: %s", repo_chg_txt)
            # Use 'HEAD' request to get headers without downloading full content
            repo_response = self.http.request(
                'HEAD', repo_chg_txt,
                retries=self.urllib_retries,
                redirect=self.urllib_redirect,
                headers=self.proxy_default_headers if self.proxy_address else None  # Pass proxy headers if proxy is used.
            )
            # Manual check for HTTP status codes (4xx or 5xx)
            if 400 <= repo_response.status < 600:
                logger.error("HTTP error fetching remote changelog '%s': Status Code %s", repo_chg_txt, repo_response.status)
                self.error_connected.append(repo_chg_txt)
                return False  # Cannot compare if connection fails, assume no update for now (or handle as error).

            content_length_header = repo_response.headers.get('content-length', 0)
            repo_size = int(content_length_header) if content_length_header else 0
            logger.debug("Remote changelog file size: %d bytes (from Content-Length header).", repo_size)
        except KeyboardInterrupt as e:
            logger.warning("KeyboardInterrupt during remote changelog fetch. Exiting.", exc_info=True)
            raise SystemExit(1) from e
        except (HTTPError, NewConnectionError) as e:
            logger.error("Connection error or HTTP error fetching remote changelog '%s': %s", repo_chg_txt, e)
            self.error_connected.append(repo_chg_txt)
            return False  # Cannot compare if connection fails, assume no update for now (or handle as error).
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred fetching remote changelog '%s': %s", repo_chg_txt, e, exc_info=True)
            self.error_connected.append(repo_chg_txt)
            return False

        if repo_size == 0:
            logger.warning("Remote changelog size is 0 for '%s'. Assuming no update or empty file.", repo_chg_txt)
            return False  # If remote size is 0, consider it not updated or empty.

        result = local_size != repo_size
        logger.debug("Changelog comparison result: local_size=%d, repo_size=%d, different=%s", local_size, repo_size, result)
        return result

    def check_for_error_connected(self) -> None:
        """Check for error connected and prints a message."""
        if self.error_connected:
            logger.warning("Detected connection errors for mirrors: %s", self.error_connected)
            print(f'\n{self.red}Failed connected to the mirrors:{self.endc}')
            print('-' * 32)
            for repo_url in self.error_connected:
                print(f'{self.red}>{self.endc} {repo_url}')
            print()
        else:
            logger.debug("No connection errors detected.")

    # They would only be needed if proxy settings could change mid-execution or if http object needed re-initialization.
    def set_http_proxy_server(self) -> None:
        """Set for HTTP proxy server."""
        logger.debug("Setting HTTP proxy server to: %s", self.proxy_address)
        self.http = ProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def set_socks_proxy_server(self) -> None:
        """Set for a SOCKS proxy server."""
        logger.debug("Setting SOCKS proxy server to: %s", self.proxy_address)
        try:  # Try to import PySocks if it's installed.
            from urllib3.contrib.socks import \
                SOCKSProxyManager  # pylint: disable=[C0415]
            self.http = SOCKSProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)
        except (ModuleNotFoundError, ImportError) as error:
            logger.error("PySocks module not found. Cannot set SOCKS proxy. Error: %s", error)
            print(error)

    def view_messages(self) -> None:
        """Print for update messages."""
        logger.info("Preparing update messages for display.")
        repo_for_update: list[str] = []
        for repo, comp in self.compare.items():
            if comp:
                repo_for_update.append(repo)

        if repo_for_update:
            logger.info("Found %d repositories with available updates: %s", len(repo_for_update), repo_for_update)
            last_updates: dict[str, dict[str, str]] = self.repo_info.repo_information()

            print(f"\n{self.green}There are new updates available for the "
                  f"repositories:{self.endc}\n")

            # Calculate max length for repository names for alignment
            repo_length: int = 0
            if repo_for_update:  # Ensure list is not empty before calling max.
                repo_length = max(len(name) for name in repo_for_update)

            for repo in repo_for_update:
                last_updated: str = 'None'
                if last_updates.get(repo):
                    last_updated = last_updates[repo].get('last_updated', 'None')

                print(f'> {self.green}{repo:<{repo_length}}{self.endc} Last Updated: '
                      f"'{last_updated}'")
                logger.debug("Displayed update message for repo '%s': Last Updated: '%s'", repo, last_updated)
            if not self.option_for_check:
                print()
        else:
            logger.info("No updated packages since the last check.")
            print(f'\n{self.yellow}No updated packages since the last check.{self.endc}\n')

        if self.option_for_check:
            print()

    def updates(self) -> dict[str, bool]:
        """Call methods in parallel with the progress tool or without.

        Returns:
            dict: Dictionary of compares (repo_name: bool indicating update available).
        """
        logger.info("Starting 'updates' method to check repositories.")
        message: str = 'Checking for news, please wait'
        queue: Queue = Queue()  # type: ignore # Queue for inter-process communication

        # Starting multiprocessing for checks and progress bar
        process_1 = Process(target=self.check_the_repositories, args=(queue,))
        process_2 = Process(target=self.progress.progress_bar, args=(message,))
        logger.debug("Created multiprocessing processes for checks and progress bar.")

        process_1.start()
        process_2.start()
        logger.debug("Started processes.")

        # Wait until process 1 (repository checks) finishes.
        process_1.join()
        logger.debug("Process 1 (check_the_repositories) finished.")

        process_2.terminate()
        logger.debug("Process 2 (progress_bar) terminated.")
        # Clear the progress bar line and show 'Done' message.
        print(f'\r{message}... {self.imp.done} ', end='')
        logger.info("Progress bar cleared and 'Done' message displayed.")

        # Retrieve results from the queue
        self.compare = queue.get()
        self.error_connected = queue.get()
        logger.debug("Retrieved comparison results and connection errors from queue.")

        # Reset cursor to normal after progress bar.
        print('\x1b[?25h')
        logger.debug("Terminal cursor reset to normal.")

        self.check_for_error_connected()  # Display any connection errors.
        self.view_messages()  # Display update messages.
        logger.info("Updates check completed. Returning comparison results.")
        return self.compare
