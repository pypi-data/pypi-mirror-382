#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from pathlib import Path

from slpkg.views.view_process import ViewProcess

logger = logging.getLogger(__name__)


class SBoGenerate:
    """Generating the SLACKBUILDS.TXT file."""

    def __init__(self) -> None:
        logger.debug("Initializing SBoGenerate module.")
        self.view_process = ViewProcess()

    def slackbuild_file(self, repo_path: Path, repo_slackbuild_txt: str) -> None:  # pylint: disable=[R0914]
        """Create a SLACKBUILDS.TXT file.

        Args:
            repo_path (Path): Path to the repository.
            repo_slackbuild_txt (str): Name of the SLACKBUILDS.TXT file to create.
        """
        logger.info("Starting to generate '%s' file in '%s'.", repo_slackbuild_txt, repo_path)

        # slackbuild.info variables mapping integer keys to string prefixes.
        info_var: dict[int, str] = {
            1: 'PRGNAM=',
            2: 'VERSION=',
            3: 'HOMEPAGE=',
            4: 'DOWNLOAD=',
            5: 'MD5SUM=',
            6: 'DOWNLOAD_x86_64=',
            7: 'MD5SUM_x86_64=',
            8: 'REQUIRES=',
            9: 'MAINTAINER=',
            10: 'EMAIL='
        }
        logger.debug("Defined info_var mappings: %s", info_var)

        self.view_process.message(f'Generating the {repo_slackbuild_txt} file')  # Display progress message to user.

        try:
            with open(Path(repo_path, repo_slackbuild_txt), 'w', encoding='utf-8') as sbo:
                logger.debug("Opened '%s' for writing.", Path(repo_path, repo_slackbuild_txt))
                # Iterate through all files in the repository path to find .info files
                for path in repo_path.glob('**/*'):
                    if path.name.endswith('.info'):
                        sbo_path = Path('/'.join(str(path).split('/')[:-1]))  # Directory containing the .info file.

                        # Extract name and location from the path
                        name: str = str(path).split('/')[-2]
                        location: str = str(Path('/'.join(str(path).split('/')[-3:-1])))
                        files: str = ' '.join([file.name for file in list(sbo_path.iterdir())])  # List all files in the SlackBuild directory.
                        logger.debug("Processing SlackBuild '%s' at '%s'. Info file: %s", name, location, path)

                        # Read various fields from the .info file
                        version: str = (
                            ' '.join([var.strip() for var in self.read_info_file(
                                path, info_var[2], info_var[3])])[len(info_var[2]):].replace('"', ''))
                        logger.debug("Extracted version: '%s'", version)

                        download: str = (
                            ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                                path, info_var[4], info_var[5])])[len(info_var[4]):].replace('"', ''))
                        logger.debug("Extracted download: '%s'", download)

                        download_x86_64: str = (
                            ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                                path, info_var[6], info_var[7])])[len(info_var[6]):].replace('"', ''))
                        logger.debug("Extracted download_x86_64: '%s'", download_x86_64)

                        md5sum: str = (
                            ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                                path, info_var[5], info_var[6])])[len(info_var[5]):].replace('"', ''))
                        logger.debug("Extracted md5sum: '%s'", md5sum)

                        md5sum_x86_64: str = (
                            ' '.join([var.replace('\\', '').strip() for var in self.read_info_file(
                                path, info_var[7], info_var[8])])[len(info_var[7]):].replace('"', ''))
                        logger.debug("Extracted md5sum_x86_64: '%s'", md5sum_x86_64)

                        requires: str = (' '.join(list(self.read_info_file(
                            path, info_var[8], info_var[9])))[len(info_var[8]):].replace('"', ''))
                        logger.debug("Extracted requires: '%s'", requires)

                        short_description: str = self.read_short_description(sbo_path, name)
                        logger.debug("Extracted short description: '%s'", short_description)

                        # Write all extracted information to the SLACKBUILDS.TXT file.
                        sbo.write(f'SLACKBUILD NAME: {name}\n')
                        sbo.write(f'SLACKBUILD LOCATION: ./{location}\n')
                        sbo.write(f'SLACKBUILD FILES: {files}\n')
                        sbo.write(f'SLACKBUILD VERSION: {version}\n')
                        sbo.write(f'SLACKBUILD DOWNLOAD: {download}\n')
                        sbo.write(f'SLACKBUILD DOWNLOAD_x86_64: {download_x86_64}\n')
                        sbo.write(f'SLACKBUILD MD5SUM: {md5sum}\n')
                        sbo.write(f'SLACKBUILD MD5SUM_x86_64: {md5sum_x86_64}\n')
                        sbo.write(f'SLACKBUILD REQUIRES: {requires}\n')
                        sbo.write(f'SLACKBUILD SHORT DESCRIPTION: {short_description}\n')
                        sbo.write('\n')
                        logger.debug("Wrote entry for '%s' to SLACKBUILDS.TXT.", name)
        except IOError as e:
            logger.error("Failed to write to '%s': %s", Path(repo_path, repo_slackbuild_txt), e)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred during SLACKBUILDS.TXT generation: %s", e)

        self.view_process.done()  # Signal completion to the user.
        print()  # Add a newline for better console formatting.
        logger.info("Finished generating '%s' file.", repo_slackbuild_txt)

    @staticmethod
    def read_short_description(path: Path, name: str) -> str:
        """Return the short description from slack-desc file.

        Args:
            path (Path): Path to the SlackBuild directory.
            name (str): SlackBuild name.

        Returns:
            str: Short description extracted from the slack-desc file, or an empty string if not found.
        """
        slack_desc: Path = Path(path, 'slack-desc')
        logger.debug("Attempting to read short description from '%s' for '%s'.", slack_desc, name)
        if slack_desc.is_file():
            try:
                with open(slack_desc, 'r', encoding='utf-8') as f:
                    slack = f.readlines()

                for line in slack:
                    pattern: str = f'{name}: {name}'  # Expected pattern for the short description line.
                    if line.startswith(pattern):
                        short_desc = line[len(name) + 1:].strip()
                        logger.debug("Found short description for '%s': '%s'", name, short_desc)
                        return short_desc
                logger.warning("Short description pattern '%s' not found in '%s'.", pattern, slack_desc)
            except IOError as e:
                logger.error("Failed to read slack-desc file '%s': %s", slack_desc, e)
            except Exception as e:  # pylint: disable=[W0718]
                logger.critical("An unexpected error occurred while reading slack-desc for '%s': %s", name, e)
        else:
            logger.warning("slack-desc file not found at '%s'. Cannot read short description.", slack_desc)
        return ''

    @staticmethod
    def read_info_file(info_file: Path, start: str, stop: str) -> list[str]:
        """Read the .info file and return the lines between two specified variable prefixes.

        Args:
            info_file (Path): Path to the .info file.
            start (str): The variable prefix to start reading from (inclusive).
            stop (str): The variable prefix to stop reading at (exclusive).

        Returns:
            list[str]: A list of lines found between the start and stop variables.
        """
        begin = end = 0
        logger.debug("Reading info file '%s' from '%s' to '%s'.", info_file, start, stop)
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = f.read().splitlines()

            for index, line in enumerate(info):
                if line.startswith(start):
                    begin = index
                    logger.debug("Found start variable '%s' at line %d.", start, index)
                if line.startswith(stop):
                    end = index
                    logger.debug("Found stop variable '%s' at line %d.", stop, index)
                    break

            if begin >= end and end != 0:  # pylint: disable=[R1705] # Handle cases where start is after stop or stop is not found.
                logger.warning("Start variable '%s' (%d) is not before stop variable '%s' (%d) in '%s'. Returning empty list.", start, begin, stop, end, info_file)
                return []
            elif end == 0 and start != '':  # If stop not found, read till end of file from start.
                logger.warning("Stop variable '%s' not found in '%s'. Reading from '%s' to end of file.", stop, info_file, start)
                return info[begin:]

            result = info[begin:end]
            logger.debug("Extracted lines from '%s': %s", info_file, result)
            return result
        except IOError as e:
            logger.error("Failed to read info file '%s': %s", info_file, e)
        except Exception as e:  # pylint: disable=[W0718]
            logger.critical("An unexpected error occurred while reading info file '%s': %s", info_file, e)
        return []
