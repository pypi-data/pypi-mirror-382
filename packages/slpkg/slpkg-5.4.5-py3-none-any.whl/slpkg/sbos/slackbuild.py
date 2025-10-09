#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import os
import shutil
import tempfile
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Union

from slpkg.checksum import Md5sum
from slpkg.choose_dependencies import ChooseDependencies
from slpkg.config import config_load
from slpkg.dependency_logger import DependencyLogger
from slpkg.downloader import Downloader
from slpkg.gpg_verify import GPGVerify
from slpkg.multi_process import MultiProcess
from slpkg.repositories import Repositories
from slpkg.sbos.dependencies import Requires
from slpkg.utilities import Utilities
from slpkg.views.view_process import ViewProcess
from slpkg.views.views import View

logger = logging.getLogger(__name__)


class DependencyManager:
    """
    Manages the creation and selection of SlackBuild dependencies.
    """

    def __init__(self, data: dict[str, dict[str, str]], options: dict[str, bool],  # pylint: disable=[R0913,R0917]
                 choose_dependencies_instance: ChooseDependencies,
                 view_process_instance: ViewProcess,
                 utils_instance: Utilities) -> None:
        self.data = data
        self.options = options
        self.choose_package_dependencies = choose_dependencies_instance
        self.view_process = view_process_instance
        self.utils = utils_instance
        self.dependencies: list[str] = []

    def resolve_and_select(self, slackbuilds: list[str]) -> list[str]:
        """
        Resolves dependencies for the given SlackBuilds and allows user selection.
        """
        logger.info("Creating initial dependencies list for %d slackbuilds.", len(slackbuilds))
        for slackbuild in slackbuilds:
            dependencies: tuple[str, ...] = Requires(self.data, slackbuild, self.options).resolve()
            logger.debug("Dependencies resolved for '%s': %s", slackbuild, dependencies)
            for dependency in dependencies:
                self.dependencies.append(dependency)

        self.dependencies = list(OrderedDict.fromkeys(self.dependencies))
        logger.info("Final unique dependencies list created with %d items.", len(self.dependencies))

        if self.dependencies:
            self.view_process.message('Resolving dependencies')
            logger.debug("Displaying 'Resolving dependencies' message.")

        selected_dependencies = self.choose_package_dependencies.choose(self.dependencies, self.view_process)
        logger.info("Selected dependencies after user choice: %s", selected_dependencies)
        return selected_dependencies

    def manage_build_order(self, initial_slackbuilds: list[str], selected_dependencies: list[str], option_for_skip_installed: bool) -> tuple[list[str], list[str]]:
        """
        Manages the build order by adding dependencies, cleaning main slackbuilds,
        and checking for skipped packages.

        Returns:
            tuple[list[str], list[str]]: (final_build_order, skipped_packages)
        """
        build_order: list[str] = []
        skipped_packages: list[str] = []

        build_order.extend(selected_dependencies)
        logger.debug("Added %d dependencies to the build order.", len(selected_dependencies))

        main_slackbuilds_filtered = [sbo for sbo in initial_slackbuilds if sbo not in selected_dependencies]
        build_order.extend(main_slackbuilds_filtered)
        logger.info("Final build order before skipped check: %s", build_order)

        if option_for_skip_installed:
            logger.info("Option --skip-installed is active. Checking for already installed packages to skip.")
            for name in build_order:
                if self.utils.is_package_installed(name):
                    skipped_packages.append(name)
                    logger.debug("Package '%s' is installed and will be skipped.", name)

            build_order = [pkg for pkg in build_order if pkg not in skipped_packages]
            logger.info("Removed %d packages from build order due to --skip-installed.", len(skipped_packages))
        else:
            logger.debug("Option --skip-installed is not active. No packages will be skipped based on installation status.")

        return build_order, skipped_packages


class SourcePreparer:  # pylint: disable=[R0902,R0903]
    """
    Prepares SlackBuild directories and sources for downloading and building.
    """

    def __init__(self, build_path: Path, tmp_slpkg: Path, prog_name: str, is_64bit: bool,  # pylint: disable=[R0913,R0917]
                 gpg_verification: bool, repos_instance: Repositories, utils_instance: Utilities,
                 view_process_instance: ViewProcess) -> None:
        self.build_path = build_path
        self.tmp_slpkg = tmp_slpkg
        self.prog_name = prog_name
        self.is_64bit = is_64bit
        self.gpg_verification = gpg_verification
        self.repos = repos_instance
        self.utils = utils_instance
        self.view_process = view_process_instance

    def prepare(self, build_order: list[str], data: dict[str, dict[str, str]], repository: str, tar_suffix: str) -> tuple[dict[str, tuple[list[str], Path]], list[Path], int, list[str]]:  # pylint: disable=[R0914]
        """
        Prepares SlackBuild directories and sources for downloading and building.

        Returns:
            tuple: (sources_to_download, asc_files, total_sources_count, repo_data_for_downloader)
        """
        if not build_order:
            logger.info("No SlackBuilds in build order. Skipping source preparation.")
            return {}, [], 0, []

        self.view_process.message('Prepare sources for downloading')
        logger.info("Preparing %d SlackBuilds for source downloading.", len(build_order))

        sources_to_download: dict[str, tuple[list[str], Path]] = {}
        asc_files: list[Path] = []
        total_sources_count: int = 0
        repo_data_for_downloader: list[str] = []  # This needs to be set per SlackBuild's repo data.

        for sbo in build_order:
            build_path_sbo: Path = Path(self.build_path, sbo)
            logger.debug("Preparing build directory for '%s': %s", sbo, build_path_sbo)

            self.utils.remove_folder_if_exists(build_path_sbo)
            self.utils.create_directory(build_path_sbo)

            location = data[sbo]['location']
            repo_data_for_downloader = [repository, data[sbo]['location']]
            slackbuild_script_path: Path = Path(self.build_path, sbo, f'{sbo}.SlackBuild')

            repo_package_source: Path = Path(self.repos.repositories[repository]['path'], location, sbo)
            logger.debug("Copying SlackBuild source from '%s' to '%s'.", repo_package_source, build_path_sbo)
            shutil.copytree(repo_package_source, build_path_sbo, dirs_exist_ok=True)

            os.chmod(slackbuild_script_path, 0o775)
            logger.debug("Set executable permissions for SlackBuild script: %s", slackbuild_script_path)

            sources: list[str]
            if self.is_64bit and data[sbo].get('download64'):
                sources = list(data[sbo]['download64'])
                logger.debug("Using 64-bit download sources for '%s'.", sbo)
            else:
                sources = list(data[sbo]['download'])
                logger.debug("Using default download sources for '%s'.", sbo)

            total_sources_count += len(sources)

            if self.gpg_verification and repository == self.repos.sbo_repo_name:
                asc_file: Path = Path(self.repos.repositories_path, self.repos.sbo_repo_name,
                                      location, f'{sbo}{tar_suffix}.asc')
                if asc_file.is_file():
                    asc_files.append(asc_file)
                    logger.debug("Added GPG .asc file for verification: %s", asc_file)
                else:
                    logger.warning("GPG .asc file not found for '%s' at '%s'. Skipping verification for this source.", sbo, asc_file)

            sources_to_download[sbo] = (sources, Path(self.build_path, sbo))
            logger.debug("Sources prepared for '%s': %s", sbo, sources)

        self.view_process.done()
        logger.info("Finished preparing SlackBuilds for downloading.")
        return sources_to_download, asc_files, total_sources_count, repo_data_for_downloader


class PackageBuilder:  # pylint: disable=[R0902,R0903]
    """
    Handles the building of individual SlackBuild packages.
    """

    def __init__(self, options: dict[str, Any], build_path: Path, tmp_slpkg: Path, prog_name: str,  # pylint: disable=[R0913,R0917]
                 makeflags: str, editor: str, multi_proc_instance: MultiProcess, utils_instance: Utilities, view_instance: View) -> None:
        self.options = options
        self.build_path = build_path
        self.tmp_slpkg = tmp_slpkg
        self.prog_name = prog_name
        self.makeflags = makeflags
        self.editor = editor
        self.multi_proc = multi_proc_instance
        self.utils = utils_instance
        self.view = view_instance
        self.output_env: Path = Path()
        self.yellow = config_load.yellow
        self.green = config_load.green
        self.endc = config_load.endc

    def build(self, name: str) -> Path:
        """
        Build the SlackBuild script in a temporary environment.

        Returns:
            Path: The path to the temporary output directory where the package is built.
        """
        logger.info("Building SlackBuild script for: '%s'.", name)
        self._set_makeflags()

        self.output_env = Path(tempfile.mkdtemp(dir=self.tmp_slpkg, prefix=f'{self.prog_name}.'))
        os.environ['OUTPUT'] = str(self.output_env)
        logger.debug("Created temporary output directory: %s. Set OUTPUT env var.", self.output_env)

        self._set_slackbuild_repo_tag(name)

        folder: Path = Path(self.build_path, name)
        filename: str = f'{name}.SlackBuild'
        command: str = f'{folder}/./{filename}'

        self._edit_slackbuild(name, folder)

        self.utils.change_owner_privileges(folder)
        logger.debug("Changed owner privileges for folder: %s", folder)

        progress_message: str = 'Building'
        self.multi_proc.process_and_log(command, filename, progress_message)
        logger.info("SlackBuild script for '%s' build command executed.", name)
        return self.output_env

    def _set_makeflags(self) -> None:
        """Set the MAKEFLAGS environment variable for parallel compilation."""
        os.environ['MAKEFLAGS'] = f'-j {self.makeflags}'
        logger.debug("MAKEFLAGS environment variable set to: '%s'", os.environ['MAKEFLAGS'])

    def _set_slackbuild_repo_tag(self, name: str) -> None:
        """
        Set a new repo tag to the SlackBuild variable TAG.
        If 'option_repo_tag' is provided, it will patch the TAG variable
        in the SlackBuild script for the given package 'name'.
        """
        logger.debug("Checking for 'option_repo_tag' to set repo tag for '%s'.", name)
        option_repo_tag: Union[str, None] = self.options.get('option_repo_tag')

        if option_repo_tag is not None:
            new_repo_tag: str = option_repo_tag

            if not isinstance(new_repo_tag, str):
                logger.warning("Unexpected type for 'option_repo_tag': %s. Expected string. Skipping tag patch.", type(new_repo_tag))
                return

            logger.debug("Repository tag '%s' found from options for '%s'.", new_repo_tag, name)

            try:
                self.utils.patch_slackbuild_file(name, 'TAG', new_repo_tag)
                logger.info("Successfully initiated patching of TAG with '%s' for '%s'.", new_repo_tag, name)
            except Exception as e:  # pylint: disable=[W0718]
                logger.error("Failed to patch TAG for '%s' with value '%s': %s", name, new_repo_tag, e, exc_info=True)
        else:
            logger.debug("No 'option_repo_tag' provided. Skipping repo tag setting for '%s'.", name)

    def _edit_slackbuild(self, name: str, folder: Path) -> None:
        """Edit the SlackBuild file before build, allowing the user to make changes."""
        logger.debug("Attempting to edit SlackBuild for package '%s' in folder '%s'.", name, folder)
        filename_path: str = ''
        # 'option_sbo_edit' can be a string (filename or '*') or False (if not provided)
        option_sbo_name: Union[str, bool] = self.options.get('option_sbo_edit', False)
        logger.debug("option_sbo_edit value: '%s'", option_sbo_name)

        # Set the specified sbo name from user enter.
        if isinstance(option_sbo_name, str) and option_sbo_name == name:
            filename_path = str(Path(folder, f'{option_sbo_name}.SlackBuild'))
            logger.debug("User specified exact SBo name '%s'. File path: '%s'", option_sbo_name, filename_path)

        # Edit all sbo files.
        elif isinstance(option_sbo_name, str) and option_sbo_name == '*':
            filename_path = str(Path(folder, f'{name}.SlackBuild'))
            logger.debug("User specified wildcard '*'. Editing current SBo file: '%s'", filename_path)

        if filename_path:
            file_path_obj = Path(filename_path)

            if not file_path_obj.is_file():
                logger.warning("Attempted to edit non-existent SlackBuild file: '%s'. Skipping.", filename_path)
                return  # Exit if file doesn't exist

            size_before_edit = file_path_obj.stat().st_size
            logger.info("File size before editing: %d bytes for '%s'", size_before_edit, filename_path)

            command: str = f'{self.editor} {filename_path}'
            logger.info("Opening SlackBuild file '%s' for editing with command: '%s'", filename_path, command)
            try:
                self.multi_proc.process(command)
                logger.info("Editor process completed for '%s'.", filename_path)

                size_after_edit = file_path_obj.stat().st_size
                logger.info("File size after editing: %d bytes for '%s'", size_after_edit, filename_path)

                if size_after_edit != size_before_edit:
                    logger.info("File size changed from %d to %d bytes.", size_before_edit, size_after_edit)
                    self.view.question(f"File '{self.yellow}{file_path_obj.name}{self.endc}' changed, do you want to continue ?")
                else:
                    logger.info("File size remained unchanged (%d bytes).", size_before_edit)
                    print(f"No changes detected in '{self.green}{file_path_obj.name}{self.endc}'. Continuing...\n")

            except Exception as e:  # pylint: disable=[W0718]
                logger.error("Failed to open editor for '%s' with command '%s': %s", filename_path, command, e, exc_info=True)
        else:
            logger.debug("No SlackBuild file selected for editing based on 'option_sbo_edit' value.")


class PackageInstaller:  # pylint: disable=[R0902]
    """
    Handles the installation or reinstallation of built packages.
    """

    def __init__(self, installpkg: str, reinstall: str, multi_proc_instance: MultiProcess,  # pylint: disable=[R0913,R0917]
                 options: dict[str, bool], mode: str, data: dict[str, dict[str, str]],
                 deps_log_file: Path, utils_instance: Utilities) -> None:
        self.installpkg = installpkg
        self.reinstall = reinstall
        self.multi_proc = multi_proc_instance
        self.options = options
        self.mode = mode
        self.data = data
        self.deps_log_file = deps_log_file
        self.utils = utils_instance
        self.progress_message: str = 'Installing'  # Default, will be set by set_progress_message.
        self.dependency_logger = DependencyLogger()

    def set_progress_message(self) -> None:
        """Set the progress message based on the current mode or reinstall option."""
        if self.mode == 'upgrade' or self.options.get('option_reinstall', False):
            self.progress_message = 'Upgrading'
            logger.debug("Progress message set to 'Upgrading' due to mode or reinstall option.")
        else:
            logger.debug("Progress message remains default: '%s'.", self.progress_message)

    def install(self, name: str, output_env: Path) -> None:
        """
        Install the built SlackBuild package using installpkg or upgradepkg.
        """
        package_files = [f.name for f in output_env.iterdir() if f.is_file()]
        if not package_files:
            logger.error("No package file found in output directory '%s' for SlackBuild '%s'. Skipping installation.", output_env, name)
            return
        package: str = package_files[0]

        command: str = f'{self.installpkg} {output_env}/{package}'
        if self.options.get('option_reinstall', False):
            command = f'{self.reinstall} {output_env}/{package}'
            logger.debug("Using reinstall command for package '%s': '%s'", package, command)
        else:
            logger.debug("Using install command for package '%s': '%s'", package, command)

        self.multi_proc.process_and_log(command, package, self.progress_message)
        logger.info("Package '%s' installation command executed.", package)
        resolved_requires: tuple[str, ...] = Requires(self.data, name, self.options).resolve()
        self.dependency_logger.write_deps_log(name, resolved_requires)


class PackageMoverAndCleaner:  # pylint: disable=[R0903]
    """
    Handles moving the built package and cleaning up temporary directories.
    """

    def __init__(self, tmp_path: Path, progress_bar: bool, utils_instance: Utilities) -> None:
        self.tmp_path = tmp_path
        self.progress_bar = progress_bar
        self.utils = utils_instance

    def move_and_clean(self, output_env: Path) -> None:
        """
        Move the built binary package to /tmp and delete the temporary build folder.
        """
        package_files = [f.name for f in output_env.iterdir() if f.is_file()]
        if not package_files:
            logger.warning("No package file found in output directory '%s'. Skipping move and folder deletion.", output_env)
            return
        package_name: str = package_files[0]
        binary_path_file: Path = Path(output_env, package_name)
        logger.debug("Attempting to move package '%s' from '%s' to '%s'.", package_name, binary_path_file, self.tmp_path)

        self.utils.remove_file_if_exists(self.tmp_path, package_name)
        logger.debug("Ensured no old package '%s' exists in '%s'.", package_name, self.tmp_path)

        if binary_path_file.is_file():
            try:
                shutil.move(binary_path_file, self.tmp_path)
                logger.info("Moved package '%s' to '%s'.", package_name, self.tmp_path)
                if not self.progress_bar:
                    message: str = f'| Moved: {package_name} to the {self.tmp_path} folder.'
                    length_message: int = len(message) - 1
                    print(f"\n+{'=' * length_message}")
                    print(message)
                    print(f"+{'=' * length_message}\n")
            except shutil.Error as e:
                logger.error("Failed to move package '%s' to '%s': %s", package_name, self.tmp_path, e)
            except Exception as e:  # pylint: disable=[W0718]
                logger.critical("An unexpected error occurred while moving package '%s': %s", package_name, e)
        else:
            logger.warning("Binary package file '%s' not found at '%s'. Cannot move.", package_name, binary_path_file)

        self.utils.remove_folder_if_exists(output_env)
        logger.debug("Removed temporary output directory: %s", output_env)


class Slackbuilds:   # pylint: disable=[R0902,R0903] # The main orchestrator class, retaining original __init__ signature
    """
    Orchestrates the entire SlackBuild download, build, and install process.
    """

    def __init__(self, repository: str, data: dict[str, dict[str, str]], slackbuilds: list[str], options: dict[str, bool], mode: str) -> None:  # pylint: disable=[R0913,R0915,R0917]
        logger.debug("Initializing Slackbuilds module for repository: '%s', mode: '%s', with %d slackbuilds and options: %s",
                     repository, mode, len(slackbuilds), options)
        self.repository = repository
        self.data = data
        self.options = options
        self.mode = mode

        # Configuration values from config_load
        self.build_path = config_load.build_path
        self.is_64bit = config_load.is_64bit()
        self.gpg_verification = config_load.gpg_verification
        self.process_log_file = config_load.process_log_file
        self.delete_sources = config_load.delete_sources
        self.progress_bar = config_load.progress_bar
        self.installpkg = config_load.installpkg
        self.reinstall = config_load.reinstall
        self.deps_log_file = config_load.deps_log_file
        self.tmp_slpkg = config_load.tmp_slpkg
        self.tmp_path = config_load.tmp_path
        self.prog_name = config_load.prog_name
        self.makeflags = config_load.makeflags
        self.dialog = config_load.dialog
        self.editor = config_load.editor
        # Console colors.
        self.green = config_load.green
        self.yellow = config_load.yellow
        self.red = config_load.red
        self.endc = config_load.endc

        # Original helper instances (these are still created directly)
        self.repos = Repositories()
        self.utils = Utilities()
        self.multi_proc = MultiProcess(options)
        self.view = View(options, repository, data)
        self.view_process = ViewProcess()
        self.check_md5 = Md5sum(options)
        self.download = Downloader(options)
        self.gpg = GPGVerify()
        self.choose_package_dependencies = ChooseDependencies(repository, data, options, mode)

        # Initialize new SRP-focused classes, passing necessary dependencies
        self.dependency_manager = DependencyManager(self.data, self.options, self.choose_package_dependencies, self.view_process, self.utils)
        self.source_preparer = SourcePreparer(self.build_path, self.tmp_slpkg, self.prog_name,
                                              self.is_64bit, self.gpg_verification, self.repos,
                                              self.utils, self.view_process)
        self.package_builder = PackageBuilder(self.options, self.build_path, self.tmp_slpkg, self.prog_name,
                                              self.makeflags, self.editor, self.multi_proc, self.utils, self.view)
        self.package_installer = PackageInstaller(self.installpkg, self.reinstall, self.multi_proc,
                                                  self.options, self.mode, self.data, self.deps_log_file, self.utils)
        self.package_mover_and_cleaner = PackageMoverAndCleaner(self.tmp_path, self.progress_bar, self.utils)

        self.build_order: list[str] = []
        self.skipped_packages: list[str] = []
        self.slackbuilds_initial: list[str] = self.utils.apply_package_pattern(data, slackbuilds)
        logger.debug("Initial SlackBuilds after pattern matching: %s", self.slackbuilds_initial)

        self.repo_tag: str = self.repos.repositories[repository]['repo_tag']
        self.tar_suffix: str = self.repos.repositories[repository]['tar_suffix']
        logger.debug("Slackbuilds module initialized. Repo tag: '%s', Tar suffix: '%s'", self.repo_tag, self.tar_suffix)

    def execute(self) -> None:
        """
        Executes the full SlackBuild process: resolves dependencies, prepares sources,
        downloads, builds, and installs packages.
        """
        logger.info("Executing SlackBuilds process for mode: '%s'.", self.mode)

        # 1. Resolve and select dependencies
        selected_dependencies = self.dependency_manager.resolve_and_select(self.slackbuilds_initial)

        # 2. Manage build order and skipped packages
        self.build_order, self.skipped_packages = self.dependency_manager.manage_build_order(
            self.slackbuilds_initial, selected_dependencies, self.options.get('option_skip_installed', False)
        )

        # 3. View packages before build/install
        # The view methods need the original slackbuilds and dependencies, not the filtered build_order directly
        main_slackbuilds_for_view = [sbo for sbo in self.slackbuilds_initial if sbo not in selected_dependencies]
        self.view.install_upgrade_packages(main_slackbuilds_for_view, selected_dependencies, self.mode)
        self.view.missing_dependencies(self.build_order)
        self.view.question()  # Ask user for final confirmation.

        start: float = time.time()
        self.view.skipping_packages(self.skipped_packages)

        # 4. Prepare sources
        sources_to_download, asc_files, total_sources_count, repo_data_for_downloader = \
            self.source_preparer.prepare(self.build_order, self.data, self.repository, self.tar_suffix)

        # 5. Download sources
        if sources_to_download:
            print(f'Started to download total ({total_sources_count}) sources:\n')
            logger.info("Starting download of %d total sources.", total_sources_count)
            self.download.download(sources_to_download, repo_data_for_downloader)
            print()
            self._checksum_downloaded_sources(sources_to_download)  # Checksum after download.
            logger.info("Source downloading and checksum verification completed.")
        else:
            logger.info("No sources to download. Skipping download phase.")

        # 6. Build and install packages
        self._build_and_install_packages(asc_files)

        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)
        logger.info("SlackBuilds execution completed in %.2f seconds.", elapsed_time)

    def _checksum_downloaded_sources(self, sources_to_download: dict[str, tuple[list[str], Path]]) -> None:
        """Perform MD5 checksum verification for all downloaded source files."""
        logger.info("Starting MD5 checksum verification for downloaded sources.")
        for sbo in self.build_order:
            # Get the path where sources for this sbo were downloaded.
            path: Path = sources_to_download[sbo][1]  # The second element of the tuple is the path.
            logger.debug("Checking checksums for sources in '%s' (SlackBuild: %s).", path, sbo)

            checksums_list: Union[list[str], str]
            sources_list: Union[list[str], str]
            if self.is_64bit and self.data[sbo].get('download64'):
                checksums_list = self.data[sbo]['md5sum64']
                sources_list = self.data[sbo]['download64']
                logger.debug("Using 64-bit checksums and sources for '%s'.", sbo)
            else:
                checksums_list = self.data[sbo]['md5sum']
                sources_list = self.data[sbo]['download']
                logger.debug("Using default checksums and sources for '%s'.", sbo)

            for source, checksum in zip(sources_list, checksums_list):
                self.check_md5.md5sum(path, source, checksum)
                logger.debug("Checksum verified for source '%s' (SlackBuild: %s).", source, sbo)
        logger.info("MD5 checksum verification completed for all downloaded sources.")

    def _build_and_install_packages(self, asc_files: list[Path]) -> None:
        """
        Orchestrates the building and optional installation of packages.
        """
        logger.info("Starting build and install phase for SlackBuilds.")
        if self.process_log_file.is_file():
            try:
                self.process_log_file.unlink()
                logger.debug("Removed old process log file: %s", self.process_log_file)
            except OSError as e:
                logger.error("Failed to remove old process log file '%s': %s", self.process_log_file, e)

        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            if asc_files:
                logger.info("Performing GPG verification for %d .asc files.", len(asc_files))
                self.gpg.verify(asc_files)
                logger.info("GPG verification completed.")
            else:
                logger.debug("GPG verification enabled but no .asc files found to verify.")
        else:
            logger.debug("GPG verification is disabled or not applicable for repository '%s'.", self.repository)

        if not self.build_order:
            logger.info("No SlackBuilds in build order. Skipping build and install phase.")
            return

        print(f'Started the processing of ({len(self.build_order)}) packages:\n')
        logger.info("Starting processing of %d packages in build order.", len(self.build_order))

        self.package_installer.set_progress_message()  # Set message once for all installations.

        for sbo in self.build_order:
            logger.info("Processing SlackBuild: '%s'", sbo)

            # Build the package
            output_env_path = self.package_builder.build(sbo)

            # Install the package if mode allows
            if self.mode in ('install', 'upgrade'):
                self.package_installer.install(sbo, output_env_path)
            else:
                logger.debug("Skipping package installation for '%s' as mode is '%s'.", sbo, self.mode)

            # Move package and clean up
            self.package_mover_and_cleaner.move_and_clean(output_env_path)
            logger.info("Finished processing SlackBuild: '%s'.", sbo)
