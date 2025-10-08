"""
Provides a `PackageManager` representation of `pip`.
"""

import json
import logging
import os
import shutil
import subprocess
from typing import Optional

from packaging.version import InvalidVersion, Version, parse as version_parse

from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.package_manager import PackageManager, UnsupportedVersionError

_log = logging.getLogger(__name__)

MIN_PIP_VERSION = version_parse("22.2")


class Pip(PackageManager):
    """
    A `PackageManager` representation of `pip`.
    """
    def __init__(self, executable: Optional[str] = None):
        """
        Initialize a new `Pip` instance.

        Args:
            executable:
                An optional path in the local filesystem to the Python executable
                to use for running `pip` as a module. If not provided, this value
                is determined by the current environment.

        Raises:
            RuntimeError: A valid executable could not be resolved.
        """
        def get_python_executable() -> Optional[str]:
            # Explicitly checking whether we are in a venv circumvents issues
            # caused by pyenv shims stomping the PATH with its own directories
            venv_path = None
            if (venv := os.environ.get("VIRTUAL_ENV")):
                venv_path = os.path.join(venv, "bin")
            for bin in ["python3", "python"]:
                if (executable := shutil.which(bin, path=venv_path)):
                    return executable
            return None

        executable = executable if executable else get_python_executable()
        if not executable:
            raise RuntimeError("Failed to resolve local Python executable: is Python installed?")
        if not os.path.isfile(executable):
            raise RuntimeError(f"Path '{executable}' does not correspond to a regular file")

        self._executable = executable

    @classmethod
    def name(cls) -> str:
        """
        Return the token for invoking `pip` on the command line.
        """
        return "pip"

    @classmethod
    def ecosystem(cls) -> ECOSYSTEM:
        """
        Return the ecosystem of packages managed by `pip`.
        """
        return ECOSYSTEM.PyPI

    def executable(self) -> str:
        """
        Return the local filesystem path to the underlying `pip` executable.
        """
        return self._executable

    def run_command(self, command: list[str]) -> int:
        """
        Run a `pip` command.

        Args:
            command: A `list[str]` containing a `pip` command to execute.

        Returns:
            An `int` return code describing the exit status of the executed `pip` command.

        Raises:
            ValueError: The given `command` is empty or not a valid `pip` command.
        """
        return subprocess.run(self._normalize_command(command)).returncode

    def resolve_install_targets(self, command: list[str]) -> list[Package]:
        """
        Resolve the installation targets of the given `pip` command.

        Args:
            command:
                A `list[str]` representing a `pip` command whose installation targets
                are to be resolved.

        Returns:
            A `list[Package]` representing the package targets that would be installed
            if `command` were run.

        Raises:
            ValueError:
                1) The given `command` is empty or not a valid `pip` command, or 2) dry-run output
                did not have the required format.
            UnsupportedVersionError: The underlying `pip` executable is of an unsupported version.
        """
        def report_to_install_target(install_report: dict) -> Package:
            if not (metadata := install_report.get("metadata")):
                raise ValueError("Missing metadata for pip installation target")
            if not (name := metadata.get("name")):
                raise ValueError("Missing name for pip installation target")
            if not (version := metadata.get("version")):
                raise ValueError("Missing version for pip installation target")
            return Package(ECOSYSTEM.PyPI, name, version)

        command = self._normalize_command(command)

        # pip only installs or upgrades packages via the `pip install` subcommand
        # If `install` is not present, the command is automatically safe to run
        if "install" not in command:
            return []

        self._check_version()

        # On supported versions, the presence of these options prevents the command from running
        if any(opt in command for opt in {"-h", "--help", "--dry-run"}):
            return []

        # Otherwise, this is probably a live `pip install` command
        # To be certain, we would need to write a full parser for pip
        try:
            dry_run_command = command + ["--dry-run", "-qqqqq", "--report", "-"]
            dry_run = subprocess.run(dry_run_command, check=True, text=True, capture_output=True)
            install_reports = json.loads(dry_run.stdout).get("install", [])
            return list(map(report_to_install_target, install_reports))
        except subprocess.CalledProcessError:
            # An error must have resulted from the given pip command
            # As nothing will be installed in this case, allow the command
            _log.info("Encountered an error while resolving pip installation targets")
            return []

    def list_installed_packages(self) -> list[Package]:
        """
        List all `PyPI` packages installed in the active `pip` environment.

        Returns:
            A `list[Package]` representing all `PyPI` packages installed in the active
            `pip` environment.

        Raises:
            RuntimeError: Failed to list installed packages or decode report JSON.
            ValueError: Encountered a malformed report for an installed package.
            UnsupportedVersionError: The underlying `pip` executable is of an unsupported version.
        """
        self._check_version()

        try:
            pip_list_command = self._normalize_command(["pip", "list", "--format", "json"])
            pip_list = subprocess.run(pip_list_command, check=True, text=True, capture_output=True)
            return [
                Package(ECOSYSTEM.PyPI, package["name"], package["version"])
                for package in json.loads(pip_list.stdout.strip())
            ]

        except subprocess.CalledProcessError:
            raise RuntimeError("Failed to list pip installed packages")

        except json.JSONDecodeError:
            raise RuntimeError("Failed to decode installed package report JSON")

        except KeyError:
            raise ValueError("Malformed installed package report")

    def _check_version(self):
        """
        Check whether the underlying `pip` executable is of a supported version.

        Raises:
            UnsupportedVersionError: The underlying `pip` executable is of an unsupported version.
        """
        def get_pip_version(executable: str) -> Optional[Version]:
            try:
                pip_version = subprocess.run(
                    [executable, "-m", "pip", "--version"],
                    check=True,
                    text=True,
                    capture_output=True
                )
                # All supported versions adhere to this format
                version_str = pip_version.stdout.split()[1]
                return version_parse(version_str)
            except IndexError:
                return None
            except InvalidVersion:
                return None

        pip_version = get_pip_version(self._executable)
        if not pip_version or pip_version < MIN_PIP_VERSION:
            raise UnsupportedVersionError(f"pip before v{MIN_PIP_VERSION} is not supported")

    def _normalize_command(self, command: list[str]) -> list[str]:
        """
        Normalize a `pip` command.

        Args:
            command:
                A `list[str]` containing a "pure" `pip` command line (i.e., one
                that starts with `"pip"`)

        Returns:
            The equivalent but normalized form of `command` permitting Python
            module invocation of `pip`.

        Raises:
            ValueError: The given `command` is empty or not a valid `pip` command.
        """
        if not command:
            raise ValueError("Received empty pip command line")
        if command[0] != self.name():
            raise ValueError("Received invalid pip command line")

        return [self._executable, "-m"] + command
