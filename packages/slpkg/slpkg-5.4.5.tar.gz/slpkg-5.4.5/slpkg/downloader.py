#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import threading
from multiprocessing import Process
from pathlib import Path
from typing import Any, Callable, Union
from urllib.parse import unquote, urlparse

from slpkg.config import config_load
from slpkg.errors import Errors
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.utilities import Utilities
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class Downloader:  # pylint: disable=[R0902]
    """Download the sources using external tools."""

    def __init__(self, options: dict[str, bool]) -> None:
        logger.debug("Initializing Downloader class with options: %s", options)
        self.options = options

        self.downloader = config_load.downloader
        self.maximum_parallel = config_load.maximum_parallel
        self.parallel_downloads = config_load.parallel_downloads

        self.wget_options = config_load.wget_options
        self.curl_options = config_load.curl_options
        self.aria2_options = config_load.aria2_options
        self.lftp_get_options = config_load.lftp_get_options
        self.red = config_load.red
        self.endc = config_load.endc

        self.errors = Errors()
        self.utils = Utilities()
        self.multi_process = MultiProcess(options)
        self.views = View(options)
        self.repos = Repositories()

        self.filename: str = ''
        self.repo_data: list[str] = []  # Used for sbo/ponce fallback mirror logic.
        self.downloader_command: str = ''
        self.downloader_tools: dict[str, Callable[[str, Path], None]] = {
            'wget': self.set_wget_downloader,
            'wget2': self.set_wget_downloader,  # wget2 uses similar options to wget for this purpose.
            'curl': self.set_curl_downloader,
            'aria2c': self.set_aria2_downloader,
            'lftp': self.set_lftp_downloader
        }

        # Semaphore to control the number of concurrent threads/processes for parallel downloads.
        # Ensure maximum_parallel is an int before passing to BoundedSemaphore.
        self.semaphore = threading.BoundedSemaphore(int(self.maximum_parallel))
        logger.debug("Downloader class initialized. Configured downloader: '%s', Parallel downloads: %s, Max parallel: %d",
                     self.downloader, self.parallel_downloads, self.maximum_parallel)

    def download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]],
                 repo_data: Union[list[str], None] = None) -> None:
        """Start the process for downloading.

        Args:
            sources (Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]):
                A dictionary where keys are repository names and values are tuples containing:
                - A list of URLs (for source files) or a tuple of URLs (for binary repo files like changelog, packages, checksums).
                - The Path where the files should be saved.
            repo_data (Union[list[str], None], optional):
                Optional list containing repository-specific data (e.g., [repo_name, location] for SBo).
                Used for fallback mirror logic. Defaults to None.
        """
        logger.info("Initiating download process. Parallel mode: %s", self.parallel_downloads)
        if repo_data is not None:
            self.repo_data = repo_data
            logger.debug("Repository data provided for download: %s", self.repo_data)

        if self.parallel_downloads:
            logger.debug("Calling parallel_download method.")
            self.parallel_download(sources)
        else:
            logger.debug("Calling normal_download method.")
            self.normal_download(sources)
        logger.info("Download process completed.")

    def parallel_download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]) -> None:
        """Download sources with parallel mode.

        Args:
            sources (Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]):
                A dictionary where keys are repository names and values are tuples containing:
                - A list of URLs (for source files) or a tuple of URLs (for binary repo files like changelog, packages, checksums).
                - The Path where the files should be saved.
        """
        logger.info("Starting parallel download for %d source sets.", len(sources))
        processes: list[Any] = []
        for urls_or_tuple, path in sources.values():
            # Ensure urls_or_tuple is iterable (list or tuple)
            urls_to_process = urls_or_tuple if isinstance(urls_or_tuple, (list, tuple)) else [urls_or_tuple]

            for url in urls_to_process:
                logger.debug("Acquiring semaphore for URL: %s", url)
                with self.semaphore:  # This ensures only 'maximum_parallel' processes run concurrently
                    proc = Process(target=self.tools, args=(url, path))
                    processes.append(proc)
                    proc.start()
                    logger.debug("Started new process for download: %s", url)

        logger.info("Waiting for all %d parallel download processes to complete.", len(processes))
        for process in processes:
            process.join()
        logger.info("All parallel download processes finished.")

    def normal_download(self, sources: Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]) -> None:
        """Download sources with normal mode (sequential).

        Args:
            sources (Union[dict[str, tuple[list[str], Path]], dict[str, tuple[tuple[str, str, str], Path]]]):
                A dictionary where keys are repository names and values are tuples containing:
                - A list of URLs (for source files) or a tuple of URLs (for binary repo files like changelog, packages, checksums).
                - The Path where the files should be saved.
        """
        logger.info("Starting normal (sequential) download for %d source sets.", len(sources))
        for urls_or_tuple, path in sources.values():
            # Ensure urls_or_tuple is iterable (list or tuple)
            urls_to_process = urls_or_tuple if isinstance(urls_or_tuple, (list, tuple)) else [urls_or_tuple]

            for url in urls_to_process:
                logger.debug("Downloading sequentially: %s to %s", url, path)
                self.tools(url, path)
        logger.info("Normal download process finished.")

    def tools(self, url: str, path: Path) -> None:
        """Run the selected downloader tool.

        Extracts filename, sets up the downloader command, executes it, and checks if downloaded.

        Args:
            url (str): The URL link to download.
            path (Path): Path to save the downloaded file.
        """
        logger.info("Preparing to download URL: '%s' to path: '%s'", url, path)
        url_parse_result = urlparse(url)
        self.filename = unquote(Path(url_parse_result.path).name)
        logger.debug("Extracted filename: '%s' from URL: '%s'", self.filename, url)

        try:
            # Select and set the appropriate downloader command based on configuration.
            downloader_func = self.downloader_tools.get(self.downloader)
            if downloader_func:
                downloader_func(url, path)
                logger.debug("Downloader command set: '%s'", self.downloader_command)
            else:
                # This case should ideally be caught during initialization or config validation.
                logger.critical("Configured downloader '%s' is not supported. Exiting.", self.downloader)
                self.errors.message(f"Downloader '{self.downloader}' not supported", exit_status=1)

        except KeyError:  # This block might be redundant if .get() is used with check, but kept for safety.
            logger.critical("KeyError: Configured downloader '%s' not found in downloader_tools map. Exiting.", self.downloader)
            self.errors.message(f"Downloader '{self.downloader}' not supported", exit_status=1)

        # Execute the downloader command. multi_process.process handles the subprocess execution.
        logger.info("Executing download command: '%s'", self.downloader_command)
        self.multi_process.process(self.downloader_command)
        logger.info("Download command execution finished. Checking if file was downloaded.")

        # Verify if the file was successfully downloaded.
        self.check_if_downloaded(path)
        logger.debug("Checked download status for '%s'.", self.filename)

    def set_wget_downloader(self, url: str, path: Path) -> None:
        """Set command for wget tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'{self.downloader} {self.wget_options} --directory-prefix={path} "{url}"'
        logger.debug("Wget command set: %s", self.downloader_command)

    def set_curl_downloader(self, url: str, path: Path) -> None:
        """Set command for curl tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = (f'{self.downloader} {self.curl_options} "{url}" '
                                   f'--output {path}/{self.filename}')
        logger.debug("Curl command set: %s", self.downloader_command)

    def set_aria2_downloader(self, url: str, path: Path) -> None:
        """Set command for aria2c tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'aria2c {self.aria2_options} --dir={path} "{url}"'
        logger.debug("Aria2c command set: %s", self.downloader_command)

    def set_lftp_downloader(self, url: str, path: Path) -> None:
        """Set command for lftp tool.

        Args:
            url (str): URL link.
            path (Path): Path to save.
        """
        self.downloader_command = f'{self.downloader} {self.lftp_get_options} {url} -o {path}'
        logger.debug("LFTP command set: %s", self.downloader_command)

    def check_if_downloaded(self, path: Path) -> None:
        """Check if the file was successfully downloaded.
        If not, attempts to re-download from sbosrcarch_mirror if applicable.
        """
        path_file: Path = Path(path, self.filename)
        logger.debug("Checking if downloaded file exists: %s", path_file)

        if not path_file.exists():
            logger.warning("File '%s' was not found after initial download attempt.", self.filename)

            if self._can_attempt_sbosrcarch_fallback():
                fallback_url = self._construct_sbosrcarch_url(path)
                logger.info("Attempting re-download from SBoSrcArch mirror: '%s' using configured downloader.", fallback_url)

                # Set the downloader command for the fallback URL.
                downloader_func = self.downloader_tools.get(self.downloader)
                if downloader_func:
                    downloader_func(fallback_url, path)
                    logger.debug("Fallback downloader command set: '%s'", self.downloader_command)
                    # Execute the fallback download directly using multi_process.process.
                    self.multi_process.process(self.downloader_command)
                    logger.info("Fallback download command execution finished.")
                else:
                    logger.critical("Configured downloader '%s' is not supported for fallback. Cannot attempt re-download.", self.downloader)
                    self._handle_download_failure(self.filename, fallback_url)
                    return  # Exit early if downloader not supported for fallback.

                # Re-check if file exists after the fallback attempt.
                if not path_file.exists():
                    logger.error("File '%s' still not found after fallback download attempt.", self.filename)
                    self._handle_download_failure(self.filename, fallback_url)
                else:
                    logger.info("File '%s' successfully downloaded via fallback.", self.filename)
            else:
                logger.debug("SBoSrcArch mirror not enabled or repo_data insufficient for fallback. Skipping fallback attempt.")
                self._handle_download_failure(self.filename, "N/A")
        else:
            logger.info("File '%s' successfully downloaded to '%s'.", self.filename, path_file)

    def _can_attempt_sbosrcarch_fallback(self) -> bool:
        """Determines if a fallback download from sbosrcarch_mirror is applicable."""
        is_sbo_or_ponce_repo = len(self.repo_data) > 1 and str(self.repo_data[0]) in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]

        can_fallback = bool(self.repos.sbosrcarch_mirror and is_sbo_or_ponce_repo)
        logger.debug("Can attempt SBoSrcArch fallback: %s (Mirror enabled: %s, Is SBo/Ponce repo: %s)",
                     can_fallback, bool(self.repos.sbosrcarch_mirror), is_sbo_or_ponce_repo)
        return can_fallback

    def _construct_sbosrcarch_url(self, path: Path) -> str:
        """Constructs the fallback URL for sbosrcarch_mirror."""
        location = str(self.repo_data[1])
        sbo_dir = str(path).rsplit('/', maxsplit=1)[-1]
        fallback_url = f"{self.repos.sbosrcarch_mirror}{location}/{sbo_dir}/{self.filename}"
        logger.debug("Constructed SBoSrcArch fallback URL: %s", fallback_url)
        return fallback_url

    def _handle_download_failure(self, filename: str, url_attempted: str) -> None:
        """Handles the final failure of a download, printing a message and prompting the user."""
        logger.critical("Final download failure for file '%s'. Attempted URL: '%s'. Prompting user for action.", filename, url_attempted)
        print(f"\n{self.red}Failed{self.endc}: Download the file: '{filename}'\n")
        self.views.question()
