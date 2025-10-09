#!/usr/bin/python3
# -*- coding: utf-8 -*-


from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote

from slpkg.config import config_load
from slpkg.errors import Errors
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class Md5sum:
    """Checksum the file sources."""

    def __init__(self, options: dict[str, bool]) -> None:
        logger.debug("Initializing Md5sum module with options: %s", options)
        self.checksum_md5 = config_load.checksum_md5
        self.red = config_load.red
        self.endc = config_load.endc

        self.errors = Errors()
        self.view = View(options)
        logger.debug("Md5sum initialized. MD5 checksum enabled: %s", self.checksum_md5)

    def md5sum(self, path: Union[str, Path], source: str, checksum: str) -> None:
        """Checksum the source file.

        Args:
            path (Union[str, Path]): Path to source file.
            source (str): Source file URL or name.
            checksum (str): Expected MD5 checksum.
        """
        if self.checksum_md5:
            source_file = unquote(source)  # Decode URL-encoded characters.
            name = Path(source_file).name  # Extract filename from source (handles URLs or just names).
            filename = Path(path, name)  # Construct full path to the downloaded file.

            logger.info("Performing MD5 checksum for file: '%s' (Expected checksum: '%s').", filename, checksum)

            md5_bytes: Optional[bytes] = self.read_binary_file(filename)
            if md5_bytes is None:  # read_binary_file raises SystemExit on FileNotFoundError, so None should not be reached in normal flow.
                logger.error("Failed to read binary file '%s' for checksum. Skipping MD5 check.", filename)
                return

            file_check: str = hashlib.md5(md5_bytes).hexdigest()
            # Ensure checksum is a string, remove any potential list wrapper if it comes from an unexpected format.
            checksum_str = "".join(checksum) if isinstance(checksum, (list, tuple)) else checksum

            logger.debug("Calculated MD5: '%s', Expected MD5: '%s'.", file_check, checksum_str)

            if file_check != checksum_str:
                logger.warning("MD5 checksum mismatch for '%s'. Expected: '%s', Found: '%s'.", name, checksum_str, file_check)
                colors_length: int = len(f'{self.red}{self.endc}')
                failed_message: str = f"{self.red}FAILED{self.endc}: MD5SUM check for {name}"
                print('=' * (len(failed_message) - colors_length))
                print(failed_message)
                print('-' * (len(failed_message) - colors_length))
                print(f'Expected: {checksum_str}')
                print(f'Found: {file_check}')
                print('-' * (len(failed_message) - colors_length))
                print()
                self.view.question()
            else:
                logger.info("MD5 checksum successful for '%s'.", name)
        else:
            logger.info("MD5 checksum verification is disabled. Skipping check for '%s'.", Path(source).name)

    def read_binary_file(self, filename: Path) -> bytes:
        """Read the file source in binary mode.

        Args:
            filename (Path): Path to the file.

        Returns:
            bytes: Binary content of the file.

        Raises:
            SystemExit: If the file is not found.
        """
        logger.debug("Attempting to read binary file: %s", filename)
        try:
            with open(filename, 'rb') as file:
                content = file.read()
            logger.debug("Successfully read binary file: %s (Size: %d bytes).", filename, len(content))
            return content
        except FileNotFoundError:
            logger.critical("FileNotFoundError: Binary file '%s' not found during checksum verification. Raising error.", filename)
            self.errors.message(f"No such file or directory: '{filename}'", exit_status=20)
            # This return is technically unreachable because message calls sys.exit(1)
            # but it's kept for mypy's type checking.
            return b''
        except IOError as e:
            logger.critical("IOError: Failed to read binary file '%s': %s", filename, e, exc_info=True)
            self.errors.message(f"Error reading file '{filename}': {e}", exit_status=1)
            return b''
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while reading binary file '%s': %s", filename, e, exc_info=True)
            self.errors.message(f"An unexpected error occurred while reading file '{filename}': {e}", exit_status=1)
            return b''
