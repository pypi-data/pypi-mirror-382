#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import sys
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse

import tomlkit
from tomlkit import exceptions

from slpkg.config import config_load
from slpkg.toml_errors import TomlErrors
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class RepoConfig(TypedDict, total=False):
    """
    A TypedDict class that defines the configuration for a repository.

    This class represents the structure of a repository configuration
    which includes details like the repository's enable status, file paths,
    and other repository-specific metadata.

    Attributes:
        enable (bool): A flag indicating whether the repository is enabled.
        path (Path): The path to the repository.
        mirror_packages (str): The URL to the repository's mirror packages.
        mirror_changelog (str): The URL to the repository's mirror changelog.
        slackbuilds_txt (str): The SlackBuilds text file for the repository.
        packages_txt (str): The packages text file.
        changelog_txt (str): The changelog text file.
        checksums_md5 (str): The repository's checksums MD5 file.
        repo_tag (str): The repository's tag.
        tar_suffix (str): The suffix for tarballs used in the repository.
    """
    enable: bool
    path: Path
    mirror_packages: str
    mirror_changelog: str
    slackbuilds_txt: str
    packages_txt: str
    changelog_txt: str
    checksums_md5: str
    repo_tag: str
    tar_suffix: str


class Repositories:  # pylint: disable=[R0902, R0903]
    """Repositories configurations."""

    toml_errors = TomlErrors()
    utils = Utilities()

    repositories_toml_file: Path = Path(config_load.etc_path, 'repositories.toml')
    repositories_path: Path = Path(config_load.lib_path, 'repos')

    repos_config: dict[str, dict[str, str]] = {}

    data_json: str = 'data.json'
    repos_information: Path = Path(repositories_path, 'repos_information.json')
    default_repository: str = 'sbo'

    slackbuilds_txt: str = 'SLACKBUILDS.TXT'
    packages_txt: str = 'PACKAGES.TXT'
    checksums_md5: str = 'CHECKSUMS.md5'
    changelog_txt: str = 'ChangeLog.txt'

    sbo_repo: bool = True
    sbo_repo_name: str = 'sbo'
    sbo_repo_path: Path = Path(repositories_path, sbo_repo_name)
    sbo_repo_mirror: str = ''
    sbo_repo_tag: str = '_SBo'
    sbo_repo_tar_suffix: str = '.tar.gz'
    sbo_git_mirror: str = ''

    ponce_repo: bool = False
    ponce_repo_name: str = 'ponce'
    ponce_repo_path: Path = Path(repositories_path, ponce_repo_name)
    ponce_repo_mirror: str = ''
    ponce_repo_tag: str = '_SBo'
    ponce_repo_tar_suffix: str = '.tar.gz'
    ponce_git_mirror: str = ''

    slack_repo: bool = False
    slack_repo_name: str = 'slack'
    slack_repo_path: Path = Path(repositories_path, slack_repo_name)
    slack_repo_mirror: str = ''
    slack_repo_tag: str = ''

    slack_extra_repo: bool = False
    slack_extra_repo_name: str = 'slack_extra'
    slack_extra_repo_path: Path = Path(repositories_path, slack_extra_repo_name)
    slack_extra_repo_mirror_packages: str = ''
    slack_extra_repo_mirror_changelog: str = ''
    slack_extra_repo_tag: str = ''

    slack_patches_repo: bool = False
    slack_patches_repo_name: str = 'slack_patches'
    slack_patches_repo_path: Path = Path(repositories_path, slack_patches_repo_name)
    slack_patches_repo_mirror_packages: str = ''
    slack_patches_repo_mirror_changelog: str = ''
    slack_patches_repo_tag: str = ''

    slack_testing_repo: bool = False
    slack_testing_repo_name: str = 'slack_testing'
    slack_testing_repo_path: Path = Path(repositories_path, slack_testing_repo_name)
    slack_testing_repo_mirror_packages: str = ''
    slack_testing_repo_mirror_changelog: str = ''
    slack_testing_repo_tag: str = ''

    alien_repo: bool = False
    alien_repo_name: str = 'alien'
    alien_repo_path: Path = Path(repositories_path, alien_repo_name)
    alien_repo_mirror_packages: str = ''
    alien_repo_mirror_changelog: str = ''
    alien_repo_tag: str = 'alien'

    multilib_repo: bool = False
    multilib_repo_name: str = 'multilib'
    multilib_repo_path: Path = Path(repositories_path, multilib_repo_name)
    multilib_repo_mirror_packages: str = ''
    multilib_repo_mirror_changelog: str = ''
    multilib_repo_tag: str = 'alien'

    restricted_repo: bool = False
    restricted_repo_name: str = 'restricted'
    restricted_repo_path: Path = Path(repositories_path, restricted_repo_name)
    restricted_repo_mirror_packages: str = ''
    restricted_repo_mirror_changelog: str = ''
    restricted_repo_tag: str = 'alien'

    gnome_repo: bool = False
    gnome_repo_name: str = 'gnome'
    gnome_repo_path: Path = Path(repositories_path, gnome_repo_name)
    gnome_repo_mirror: str = ''
    gnome_repo_tag: str = 'gfs'

    cosmic_repo: bool = False
    cosmic_repo_name: str = 'cosmic'
    cosmic_repo_path: Path = Path(repositories_path, cosmic_repo_name)
    cosmic_repo_mirror: str = ''
    cosmic_repo_tag: str = 'cosmic'

    msb_repo: bool = False
    msb_repo_name: str = 'msb'
    msb_repo_path: Path = Path(repositories_path, msb_repo_name)
    msb_repo_mirror_packages: str = ''
    msb_repo_mirror_changelog: str = ''
    msb_repo_tag: str = 'msb'

    csb_repo: bool = False
    csb_repo_name: str = 'csb'
    csb_repo_path: Path = Path(repositories_path, csb_repo_name)
    csb_repo_mirror: str = ''
    csb_repo_tag: str = 'csb'

    conraid_repo: bool = False
    conraid_repo_name: str = 'conraid'
    conraid_repo_path: Path = Path(repositories_path, conraid_repo_name)
    conraid_repo_mirror: str = ''
    conraid_repo_tag: str = 'cf'

    slackonly_repo: bool = False
    slackonly_repo_name: str = 'slackonly'
    slackonly_repo_path: Path = Path(repositories_path, slackonly_repo_name)
    slackonly_repo_mirror: str = ''
    slackonly_repo_tag: str = 'slonly'

    salix_repo: bool = False
    salix_repo_name: str = 'salix'
    salix_repo_path: Path = Path(repositories_path, salix_repo_name)
    salix_repo_mirror: str = ''
    salix_repo_tag: str = ''

    salix_extra_repo: bool = False
    salix_extra_repo_name: str = 'salix_extra'
    salix_extra_repo_path: Path = Path(repositories_path, salix_extra_repo_name)
    salix_extra_repo_mirror: str = ''
    salix_extra_repo_tag: str = ''

    slackel_repo: bool = False
    slackel_repo_name: str = 'slackel'
    slackel_repo_path: Path = Path(repositories_path, slackel_repo_name)
    slackel_repo_mirror: str = ''
    slackel_repo_tag: str = 'dj'

    slint_repo: bool = False
    slint_repo_name: str = 'slint'
    slint_repo_path: Path = Path(repositories_path, slint_repo_name)
    slint_repo_mirror: str = ''
    slint_repo_tag: str = 'slint'

    pprkut_repo: bool = False
    pprkut_repo_name: str = 'pprkut'
    pprkut_repo_path: Path = Path(repositories_path, pprkut_repo_name)
    pprkut_repo_mirror: str = ''
    pprkut_repo_tag: str = 'pprkut'

    slackdce_repo: bool = False
    slackdce_repo_name: str = 'slackdce'
    slackdce_repo_path: Path = Path(repositories_path, slackdce_repo_name)
    slackdce_repo_mirror: str = ''
    slackdce_repo_tag: str = 'slackdce'

    d2slack_repo: bool = False
    d2slack_repo_name: str = 'd2slack'
    d2slack_repo_path: Path = Path(repositories_path, d2slack_repo_name)
    d2slack_repo_mirror: str = ''
    d2slack_repo_tag: str = 'd2slack'

    try:
        logger.debug("Attempting to load repositories configuration from: %s", repositories_toml_file)
        if repositories_toml_file.is_file():
            with open(repositories_toml_file, 'r', encoding='utf-8') as file:
                repos_config = dict(tomlkit.parse(file.read()))
            logger.info("Successfully loaded repositories configuration from: %s", repositories_toml_file)

            default_repository = repos_config['DEFAULT']['REPOSITORY'].lower()
            logger.debug("Default repository set to: %s", default_repository)

            new_packages = repos_config['NEW_PACKAGES']['REPOSITORIES']
            remove_packages = repos_config['REMOVE_PACKAGES']['REPOSITORIES']
            logger.debug("New packages configured for repos: %s", new_packages)
            logger.debug("Remove packages configured for repos: %s", remove_packages)

            sbosrcarch_mirror = repos_config['SBOSRCARCH']['MIRROR']
            logger.debug("SBOSRCARCH mirror: %s", sbosrcarch_mirror)

            # SBO Repository
            sbo_repo = bool(repos_config['SBO']['ENABLE'])
            sbo_repo_mirror = repos_config['SBO']['MIRROR']
            sbo_branch = repos_config['SBO'].get('BRANCH', 'master')
            sbo_git_mirror = sbo_repo_mirror  # Initial assignment
            logger.debug("SBO config: Enabled=%s, Mirror=%s, Branch=%s", sbo_repo, sbo_repo_mirror, sbo_branch)
            if sbo_repo_mirror.endswith('.git'):
                parsed_url = urlparse(sbo_git_mirror)
                path_parts = parsed_url.path.strip("/").split("/")
                owner = path_parts[0]
                repository_name: str = path_parts[1].replace('.git', '')
                logger.debug("SBO Git mirror detected. Owner: %s, Repo Name: %s", owner, repository_name)

                if 'github.com' in sbo_git_mirror and Path(sbo_repo_path, '.git/').is_dir():
                    sbo_repo_mirror = f'https://raw.githubusercontent.com/{owner}/{repository_name}/{sbo_branch}/'
                    logger.debug("SBO mirror adjusted for GitHub Git clone: %s", sbo_repo_mirror)

                if 'gitlab.com' in sbo_git_mirror and Path(sbo_repo_path, '.git/').is_dir():
                    sbo_repo_mirror = f'https://gitlab.com/{owner}/{repository_name}/-/raw/{sbo_branch}/'
                    logger.debug("SBO mirror adjusted for GitLab Git clone: %s", sbo_repo_mirror)

            # PONCE Repository
            ponce_repo = bool(repos_config['PONCE']['ENABLE'])
            ponce_repo_mirror = repos_config['PONCE']['MIRROR']
            ponce_branch = repos_config['PONCE'].get('BRANCH', 'current')
            ponce_git_mirror = ponce_repo_mirror  # Initial assignment
            logger.debug("PONCE config: Enabled=%s, Mirror=%s, Branch=%s", ponce_repo, ponce_repo_mirror, ponce_branch)
            if ponce_repo_mirror.endswith('.git'):
                parsed_url = urlparse(ponce_git_mirror)
                path_parts = parsed_url.path.strip("/").split("/")
                owner = path_parts[0]
                repository_name = path_parts[1].replace('.git', '')
                logger.debug("PONCE Git mirror detected. Owner: %s, Repo Name: %s", owner, repository_name)

                if 'github.com' in ponce_git_mirror and Path(ponce_repo_path, '.git/').is_dir():
                    ponce_repo_mirror = f'https://raw.githubusercontent.com/{owner}/{repository_name}/{ponce_branch}/'
                    logger.debug("PONCE mirror adjusted for GitHub Git clone: %s", ponce_repo_mirror)

            # SLACK Repository
            slack_repo = bool(repos_config['SLACK']['ENABLE'])
            slack_repo_mirror = repos_config['SLACK']['MIRROR']
            logger.debug("SLACK config: Enabled=%s, Mirror=%s", slack_repo, slack_repo_mirror)

            # SLACK_EXTRA Repository
            slack_extra_repo = bool(repos_config['SLACK_EXTRA']['ENABLE'])
            slack_extra_repo_url = repos_config['SLACK_EXTRA']['MIRROR']
            slack_extra_repo_mirror_packages = slack_extra_repo_url
            slack_extra_repo_mirror_changelog = f"{'/'.join(slack_extra_repo_url.split('/')[:-2])}/"
            logger.debug("SLACK_EXTRA config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         slack_extra_repo, slack_extra_repo_mirror_packages, slack_extra_repo_mirror_changelog)

            # SLACK_PATCHES Repository
            slack_patches_repo = bool(repos_config['SLACK_PATCHES']['ENABLE'])
            slack_patches_repo_url = repos_config['SLACK_PATCHES']['MIRROR']
            slack_patches_repo_mirror_packages = slack_patches_repo_url
            slack_patches_repo_mirror_changelog = f"{'/'.join(slack_patches_repo_url.split('/')[:-2])}/"
            logger.debug("SLACK_PATCHES config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         slack_patches_repo, slack_patches_repo_mirror_packages, slack_patches_repo_mirror_changelog)

            # SLACK_TESTING Repository
            slack_testing_repo = bool(repos_config['SLACK_TESTING']['ENABLE'])
            slack_testing_repo_url = repos_config['SLACK_TESTING']['MIRROR']
            slack_testing_repo_mirror_packages = slack_testing_repo_url
            slack_testing_repo_mirror_changelog = f"{'/'.join(slack_testing_repo_url.split('/')[:-2])}/"
            logger.debug("SLACK_TESTING config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         slack_testing_repo, slack_testing_repo_mirror_packages, slack_testing_repo_mirror_changelog)

            # ALIEN Repository
            alien_repo = bool(repos_config['ALIEN']['ENABLE'])
            alien_repo_url = repos_config['ALIEN']['MIRROR']
            alien_repo_mirror_packages = alien_repo_url
            alien_repo_mirror_changelog = f"{'/'.join(alien_repo_url.split('/')[:-3])}/"
            logger.debug("ALIEN config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         alien_repo, alien_repo_mirror_packages, alien_repo_mirror_changelog)

            # MULTILIB Repository
            multilib_repo = bool(repos_config['MULTILIB']['ENABLE'])
            multilib_repo_url = repos_config['MULTILIB']['MIRROR']
            multilib_repo_mirror_packages = multilib_repo_url
            multilib_repo_mirror_changelog = f"{'/'.join(multilib_repo_url.split('/')[:-2])}/"
            logger.debug("MULTILIB config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         multilib_repo, multilib_repo_mirror_packages, multilib_repo_mirror_changelog)

            # RESTRICTED Repository
            restricted_repo = bool(repos_config['RESTRICTED']['ENABLE'])
            restricted_repo_url = repos_config['RESTRICTED']['MIRROR']
            restricted_repo_mirror_packages = restricted_repo_url
            restricted_repo_mirror_changelog = f"{'/'.join(restricted_repo_url.split('/')[:-3])}/"
            logger.debug("RESTRICTED config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         restricted_repo, restricted_repo_mirror_packages, restricted_repo_mirror_changelog)

            # GNOME Repository
            gnome_repo = bool(repos_config['GNOME']['ENABLE'])
            gnome_repo_mirror = repos_config['GNOME']['MIRROR']
            logger.debug("GNOME config: Enabled=%s, Mirror=%s", gnome_repo, gnome_repo_mirror)

            # COSMIC Repository
            cosmic_repo = bool(repos_config['COSMIC']['ENABLE'])
            cosmic_repo_mirror = repos_config['COSMIC']['MIRROR']
            logger.debug("COSMIC config: Enabled=%s, Mirror=%s", cosmic_repo, cosmic_repo_mirror)

            # MSB Repository
            msb_repo = bool(repos_config['MSB']['ENABLE'])
            msb_repo_url = repos_config['MSB']['MIRROR']
            msb_repo_mirror_packages = msb_repo_url
            msb_repo_mirror_changelog = f"{'/'.join(msb_repo_url.split('/')[:-4])}/"
            logger.debug("MSB config: Enabled=%s, Packages Mirror=%s, Changelog Mirror=%s",
                         msb_repo, msb_repo_mirror_packages, msb_repo_mirror_changelog)

            # CSB Repository
            csb_repo = bool(repos_config['CSB']['ENABLE'])
            csb_repo_mirror = repos_config['CSB']['MIRROR']
            logger.debug("CSB config: Enabled=%s, Mirror=%s", csb_repo, csb_repo_mirror)

            # CONRAID Repository
            conraid_repo = bool(repos_config['CONRAID']['ENABLE'])
            conraid_repo_mirror = repos_config['CONRAID']['MIRROR']
            logger.debug("CONRAID config: Enabled=%s, Mirror=%s", conraid_repo, conraid_repo_mirror)

            # SLACKONLY Repository
            slackonly_repo = bool(repos_config['SLACKONLY']['ENABLE'])
            slackonly_repo_mirror = repos_config['SLACKONLY']['MIRROR']
            logger.debug("SLACKONLY config: Enabled=%s, Mirror=%s", slackonly_repo, slackonly_repo_mirror)

            # SALIX Repository
            salix_repo = bool(repos_config['SALIX']['ENABLE'])
            salix_repo_mirror = repos_config['SALIX']['MIRROR']
            logger.debug("SALIX config: Enabled=%s, Mirror=%s", salix_repo, salix_repo_mirror)

            # SALIX_EXTRA Repository
            salix_extra_repo = bool(repos_config['SALIX_EXTRA']['ENABLE'])
            salix_extra_repo_mirror = repos_config['SALIX_EXTRA']['MIRROR']
            logger.debug("SALIX_EXTRA config: Enabled=%s, Mirror=%s", salix_extra_repo, salix_extra_repo_mirror)

            # SLACKEL Repository
            slackel_repo = bool(repos_config['SLACKEL']['ENABLE'])
            slackel_repo_mirror = repos_config['SLACKEL']['MIRROR']
            logger.debug("SLACKEL config: Enabled=%s, Mirror=%s", slackel_repo, slackel_repo_mirror)

            # SLINT Repository
            slint_repo = bool(repos_config['SLINT']['ENABLE'])
            slint_repo_mirror = repos_config['SLINT']['MIRROR']
            logger.debug("SLINT config: Enabled=%s, Mirror=%s", slint_repo, slint_repo_mirror)

            # PPRKUT Repository
            pprkut_repo = bool(repos_config['PPRKUT']['ENABLE'])
            pprkut_repo_mirror = repos_config['PPRKUT']['MIRROR']
            logger.debug("PPRKUT config: Enabled=%s, Mirror=%s", pprkut_repo, pprkut_repo_mirror)

            # SLACKDCE Repository
            slackdce_repo = bool(repos_config['SLACKDCE']['ENABLE'])
            slackdce_repo_mirror = repos_config['SLACKDCE']['MIRROR']
            logger.debug("SLACKDCE config: Enabled=%s, Mirror=%s", slackdce_repo, slackdce_repo_mirror)

            # D2SLACK Repository
            d2slack_repo = bool(repos_config['D2SLACK']['ENABLE'])
            d2slack_repo_mirror = repos_config['D2SLACK']['MIRROR']
            logger.debug("D2SLACK config: Enabled=%s, Mirror=%s", d2slack_repo, d2slack_repo_mirror)

        else:
            logger.warning("Repositories TOML file not found at: %s. Using default configurations.", repositories_toml_file)

    except (KeyError, exceptions.TOMLKitError) as error:
        # Log the critical error and then exit
        logger.critical("Failed to parse repositories TOML file '%s'. Error: %s", repositories_toml_file, error, exc_info=True)
        toml_errors.raise_toml_error_message(str(error), repositories_toml_file)
        sys.exit(1)

    # Dictionary configurations of repositories.
    # This dictionary is populated with the values read from the TOML file or defaults.
    repositories: dict[str, RepoConfig] = {
        sbo_repo_name: {
            'enable': sbo_repo,
            'path': sbo_repo_path,
            'mirror_packages': sbo_repo_mirror,
            'mirror_changelog': sbo_repo_mirror,
            'slackbuilds_txt': slackbuilds_txt,
            'changelog_txt': changelog_txt,
            'repo_tag': sbo_repo_tag,
            'tar_suffix': sbo_repo_tar_suffix},

        ponce_repo_name: {
            'enable': ponce_repo,
            'path': ponce_repo_path,
            'mirror_packages': ponce_repo_mirror,
            'mirror_changelog': ponce_repo_mirror,
            'slackbuilds_txt': slackbuilds_txt,
            'changelog_txt': changelog_txt,
            'repo_tag': ponce_repo_tag,
            'tar_suffix': ponce_repo_tar_suffix},

        slack_repo_name: {
            'enable': slack_repo,
            'path': slack_repo_path,
            'mirror_packages': slack_repo_mirror,
            'mirror_changelog': slack_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slack_repo_tag},

        slack_extra_repo_name: {
            'enable': slack_extra_repo,
            'path': slack_extra_repo_path,
            'mirror_packages': slack_extra_repo_mirror_packages,
            'mirror_changelog': slack_extra_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slack_extra_repo_tag},

        slack_patches_repo_name: {
            'enable': slack_patches_repo,
            'path': slack_patches_repo_path,
            'mirror_packages': slack_patches_repo_mirror_packages,
            'mirror_changelog': slack_patches_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slack_patches_repo_tag},

        slack_testing_repo_name: {
            'enable': slack_testing_repo,
            'path': slack_testing_repo_path,
            'mirror_packages': slack_testing_repo_mirror_packages,
            'mirror_changelog': slack_testing_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slack_testing_repo_tag},

        alien_repo_name: {
            'enable': alien_repo,
            'path': alien_repo_path,
            'mirror_packages': alien_repo_mirror_packages,
            'mirror_changelog': alien_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': alien_repo_tag},

        multilib_repo_name: {
            'enable': multilib_repo,
            'path': multilib_repo_path,
            'mirror_packages': multilib_repo_mirror_packages,
            'mirror_changelog': multilib_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': multilib_repo_tag},

        restricted_repo_name: {
            'enable': restricted_repo,
            'path': restricted_repo_path,
            'mirror_packages': restricted_repo_mirror_packages,
            'mirror_changelog': restricted_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': restricted_repo_tag},

        gnome_repo_name: {
            'enable': gnome_repo,
            'path': gnome_repo_path,
            'mirror_packages': gnome_repo_mirror,
            'mirror_changelog': gnome_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': gnome_repo_tag},

        cosmic_repo_name: {
            'enable': cosmic_repo,
            'path': cosmic_repo_path,
            'mirror_packages': cosmic_repo_mirror,
            'mirror_changelog': cosmic_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': cosmic_repo_tag},

        msb_repo_name: {
            'enable': msb_repo,
            'path': msb_repo_path,
            'mirror_packages': msb_repo_mirror_packages,
            'mirror_changelog': msb_repo_mirror_changelog,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': msb_repo_tag},

        csb_repo_name: {
            'enable': csb_repo,
            'path': csb_repo_path,
            'mirror_packages': csb_repo_mirror,
            'mirror_changelog': csb_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': csb_repo_tag},

        conraid_repo_name: {
            'enable': conraid_repo,
            'path': conraid_repo_path,
            'mirror_packages': conraid_repo_mirror,
            'mirror_changelog': conraid_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': conraid_repo_tag},

        slackonly_repo_name: {
            'enable': slackonly_repo,
            'path': slackonly_repo_path,
            'mirror_packages': slackonly_repo_mirror,
            'mirror_changelog': slackonly_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slackonly_repo_tag},

        salix_repo_name: {
            'enable': salix_repo,
            'path': salix_repo_path,
            'mirror_packages': salix_repo_mirror,
            'mirror_changelog': salix_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': salix_repo_tag},

        salix_extra_repo_name: {
            'enable': salix_extra_repo,
            'path': salix_extra_repo_path,
            'mirror_packages': salix_extra_repo_mirror,
            'mirror_changelog': salix_extra_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': salix_extra_repo_tag},

        slackel_repo_name: {
            'enable': slackel_repo,
            'path': slackel_repo_path,
            'mirror_packages': slackel_repo_mirror,
            'mirror_changelog': slackel_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slackel_repo_tag},

        slint_repo_name: {
            'enable': slint_repo,
            'path': slint_repo_path,
            'mirror_packages': slint_repo_mirror,
            'mirror_changelog': slint_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slint_repo_tag},

        pprkut_repo_name: {
            'enable': pprkut_repo,
            'path': pprkut_repo_path,
            'mirror_packages': pprkut_repo_mirror,
            'mirror_changelog': pprkut_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': pprkut_repo_tag},

        slackdce_repo_name: {
            'enable': slackdce_repo,
            'path': slackdce_repo_path,
            'mirror_packages': slackdce_repo_mirror,
            'mirror_changelog': slackdce_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': slackdce_repo_tag},

        d2slack_repo_name: {
            'enable': d2slack_repo,
            'path': d2slack_repo_path,
            'mirror_packages': d2slack_repo_mirror,
            'mirror_changelog': d2slack_repo_mirror,
            'packages_txt': packages_txt,
            'checksums_md5': checksums_md5,
            'changelog_txt': changelog_txt,
            'repo_tag': d2slack_repo_tag}
    }

    all_repos = [name.lower() for name in repos_config.keys()]
    defaults_repos = list(repositories.keys())

    diff_repos = list(set(all_repos) - set(defaults_repos))
    items_to_remove = ('default', 'new_packages', 'remove_packages', 'sbosrcarch')
    for item in items_to_remove:
        if item in diff_repos:  # Check if item exists before removing
            diff_repos.remove(item)
            logger.debug("Removed internal TOML section '%s' from diff_repos.", item)
        else:
            logger.debug("Internal TOML section '%s' not found in diff_repos (already removed or not present).", item)

    diff_repos = [name.upper() for name in diff_repos]
    logger.debug("Identified custom repositories from TOML: %s", diff_repos)

    if diff_repos:
        logger.info("Found %d custom repositories in repositories.toml. Adding them to configurations.", len(diff_repos))
        for repo_name_upper, data in repos_config.items():
            if repo_name_upper in diff_repos:
                repo_name_lower = repo_name_upper.lower()
                logger.debug("Processing custom repository '%s'.", repo_name_upper)

                mirror_packages: str = data.get('MIRROR', '')
                mirror_changelog: str = mirror_packages  # Default to mirror_packages
                if data.get('CHANGELOG'):
                    mirror_changelog = data.get('CHANGELOG', '')

                # Ensure all required keys for RepoConfig are present, even if empty defaults
                values: RepoConfig = {
                    'enable': bool(data.get('ENABLE', False)),  # Default to False if not specified
                    'path': Path(repositories_path, repo_name_lower),
                    'mirror_packages': mirror_packages,
                    'mirror_changelog': mirror_changelog,
                    'packages_txt': packages_txt,
                    'checksums_md5': checksums_md5,
                    'changelog_txt': changelog_txt,
                    'repo_tag': data.get('TAG', '')  # Use 'TAG' as per common TOML convention, default to empty string
                }
                # If 'slackbuilds_txt' or 'tar_suffix' are expected for SBo-like repos,
                # they should be retrieved with .get() as they might not be present for binary repos.
                if 'SLACKBUILDS.TXT' in data:  # Check if this key exists in the TOML section
                    values['slackbuilds_txt'] = data['SLACKBUILDS.TXT']
                if 'TAR_SUFFIX' in data:  # Check if this key exists in the TOML section
                    values['tar_suffix'] = data['TAR_SUFFIX']

                repositories[repo_name_lower] = values
                logger.info("Added custom repository '%s' with config: %s", repo_name_lower, values)
    else:
        logger.info("No custom repositories found in repositories.toml.")
