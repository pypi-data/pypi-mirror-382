"""
Provides an interface for client loggers to receive information about a
completed run of the supply-chain firewall.
"""

from abc import (ABCMeta, abstractmethod)
from enum import Enum
from typing_extensions import Self

from scfw.ecosystem import ECOSYSTEM
from scfw.package import Package
from scfw.report import VerificationReport
from scfw.verifier import FindingSeverity


class FirewallAction(Enum):
    """
    The various actions the firewall may take in response to inspecting a
    package manager command.
    """
    ALLOW = 0
    BLOCK = 1

    def __lt__(self, other) -> bool:
        """
        Compare two `FirewallAction` instances on the basis of their underlying numeric values.

        Args:
            self: The `FirewallAction` to be compared on the left-hand side
            other: The `FirewallAction` to be compared on the right-hand side

        Returns:
            A `bool` indicating whether `<` holds between the two given `FirewallAction`.

        Raises:
            TypeError: The other argument given was not a `FirewallAction`.
        """
        if self.__class__ is not other.__class__:
            raise TypeError(
                f"'<' not supported between instances of '{self.__class__}' and '{other.__class__}'"
            )

        return self.value < other.value

    def __str__(self) -> str:
        """
        Format a `FirewallAction` for printing.

        Returns:
            A `str` representing the given `FirewallAction` suitable for printing.
        """
        return self.name

    @classmethod
    def from_string(cls, s: str) -> Self:
        """
        Convert a string into a `FirewallAction`.

        Args:
            s: The `str` to be converted.

        Returns:
            The `FirewallAction` referred to by the given string.

        Raises:
            ValueError: The given string does not refer to a valid `FirewallAction`.
        """
        mappings = {f"{action}".lower(): action for action in cls}
        if (action := mappings.get(s.lower())):
            return action
        raise ValueError(f"Invalid firewall action '{s}'")


class FirewallLogger(metaclass=ABCMeta):
    """
    An interface for passing information about runs of Supply-Chain Firewall to
    client loggers.
    """
    @abstractmethod
    def log_firewall_action(
        self,
        ecosystem: ECOSYSTEM,
        package_manager: str,
        executable: str,
        command: list[str],
        targets: list[Package],
        action: FirewallAction,
        verified: bool,
        warned: bool,
    ):
        """
        Log the data and action taken in a completed run of Supply-Chain Firewall.

        Args:
            ecosystem: The ecosystem of the inspected package manager command.
            package_manager: The command-line name of the package manager.
            executable: The executable used to execute the inspected package manager command.
            command: The package manager command line provided to the firewall.
            targets:
                The installation targets relevant to Supply-Chain Firewall's action:
                  * For `BLOCK` actions, contains the installation targets that caused the block
                  * For `ALLOW` actions, contains all installation targets
            action: The action taken by Supply-Chain Firewall.
            verified:
                Indicates whether Supply-Chain Firewall performed installation target
                verification in deciding to take the specified `action`. Verification is not
                performed **only** under the following conditions:
                  * The package manager is of an unsupported version and the user has passed the
                    command-line option `--allow-unsupported`
            warned:
                Indicates whether the user was warned about findings for any installation
                targets and prompted for approval to proceed with `command`.
        """
        pass

    @abstractmethod
    def log_audit(
        self,
        ecosystem: ECOSYSTEM,
        package_manager: str,
        executable: str,
        reports: dict[FindingSeverity, VerificationReport],
    ):
        """
        Log the results of an audit for the given ecosystem and package manager.

        Args:
            ecosystem: The ecosystem of the audited packages.
            package_manager: The package manager that manages the audited packages.
            executable: The package manager executable used to enumerate audited packages.
            reports:
                The severity-ranked reports resulting from auditing the installed packages.

                These reports contain only those packages for which at least one verifier had
                a finding (at the severity level associated with the entire report).  That is,
                packages with no findings are excluded from the audit results.
        """
        pass
