"""
Defines the supply-chain firewall's command-line interface and performs argument parsing.
"""

from argparse import ArgumentError, Namespace, SUPPRESS
from enum import Enum
import logging
import sys
from typing import Callable, Optional

import scfw
from scfw.cli.parser import ArgumentParser
from scfw.logger import FirewallAction
from scfw.package_managers import SUPPORTED_PACKAGE_MANAGERS

_LOG_LEVELS = list(
    map(
        logging.getLevelName,
        [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
    )
)
_DEFAULT_LOG_LEVEL = logging.getLevelName(logging.WARNING)


def _add_audit_cli(parser: ArgumentParser):
    """
    Defines the command-line interface for the firewall's `audit` subcommand.

    Args:
        parser: The `ArgumentParser` to which the `audit` command line will be added.
    """
    parser.add_argument(
        "package_manager",
        type=str,
        choices=SUPPORTED_PACKAGE_MANAGERS,
        help="The package manager whose installed packages should be verified"
    )

    parser.add_argument(
        "--executable",
        type=str,
        default=None,
        metavar="PATH",
        help="Package manager executable to use for running commands (default: environmentally determined)"
    )


def _add_configure_cli(parser: ArgumentParser):
    """
    Defines the command-line interface for the firewall's `configure` subcommand.

    Args:
        parser: The `ArgumentParser` to which the `configure` command line will be added.
    """
    parser.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="Remove all Supply-Chain Firewall-managed configuration"
    )

    parser.add_argument(
        "--alias-npm",
        action="store_true",
        help="Add shell aliases to always run npm commands through Supply-Chain Firewall"
    )

    parser.add_argument(
        "--alias-pip",
        action="store_true",
        help="Add shell aliases to always run pip commands through Supply-Chain Firewall"
    )

    parser.add_argument(
        "--alias-poetry",
        action="store_true",
        help="Add shell aliases to always run Poetry commands through Supply-Chain Firewall"
    )

    parser.add_argument(
        "--dd-agent-port",
        type=str,
        default=None,
        metavar="PORT",
        help="Configure log forwarding to the local Datadog Agent on the given port"
    )

    parser.add_argument(
        "--dd-api-key",
        type=str,
        default=None,
        metavar="KEY",
        help="API key to use when forwarding logs via the Datadog API"
    )

    parser.add_argument(
        "--dd-log-level",
        type=str,
        default=None,
        choices=[str(action) for action in FirewallAction],
        metavar="LEVEL",
        help="Desired logging level for Datadog log forwarding (options: %(choices)s)"
    )

    parser.add_argument(
        "--scfw-home",
        type=str,
        default=None,
        metavar="PATH",
        help="Directory that Supply-Chain Firewall can use as a local cache"
    )


def _add_run_cli(parser: ArgumentParser):
    """
    Defines the command-line interface for the firewall's `run` subcommand.

    Args:
        parser: The `ArgumentParser` to which the `run` command line will be added.
    """
    parser.add_argument(
        "package_manager",
        type=str,
        choices=SUPPORTED_PACKAGE_MANAGERS,
        help=SUPPRESS,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify any installation targets but do not run the package manager command"
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--allow-on-warning",
        action="store_true",
        help="Non-interactively allow commands with only warning-level findings"
    )

    parser.add_argument(
        "--allow-unsupported",
        action="store_true",
        help="Disable verification and allow commands for unsupported package manager versions"
    )

    group.add_argument(
        "--block-on-warning",
        action="store_true",
        help="Non-interactively block commands with only warning-level findings"
    )

    parser.add_argument(
        "--error-on-block",
        action="store_true",
        help="Treat blocked commands as errors (useful for scripting)"
    )

    parser.add_argument(
        "--executable",
        type=str,
        default=None,
        metavar="PATH",
        help="Package manager executable to use for running commands (default: environmentally determined)"
    )


class Subcommand(Enum):
    """
    The set of subcommands that comprise the supply-chain firewall's command line.
    """
    Audit = "audit"
    Configure = "configure"
    Run = "run"

    def __str__(self) -> str:
        """
        Format a `Subcommand` for printing.

        Returns:
            A `str` representing the given `Subcommand` suitable for printing.
        """
        return self.value

    def _parser_spec(self) -> dict:
        """
        Return the `ArgumentParser` configuration for the given subcommand's parser.

        Returns:
            A `dict` of `kwargs` to pass to the `argparse.SubParsersAction.add_parser()`
            method for configuring the subparser corresponding to the subcommand.
        """
        match self:
            case Subcommand.Audit:
                return {
                    "exit_on_error": False,
                    "description": "Audit installed packages using Supply-Chain Firewall's verifiers."
                }
            case Subcommand.Configure:
                return {
                    "exit_on_error": False,
                    "description": "Configure the environment for using Supply-Chain Firewall."
                }
            case Subcommand.Run:
                return {
                    "usage": "%(prog)s [options] COMMAND",
                    "exit_on_error": False,
                    "description": "Run a package manager command through Supply-Chain Firewall."
                }

    def _cli_spec(self) -> Callable[[ArgumentParser], None]:
        """
        Return a function for adding the given subcommand's command-line options
        to a given `ArgumentParser`.

        Returns:
            A `Callable[[ArgumentParser], None]` that adds the command-line options
            for the subcommand to the `ArgumentParser` it is given, in the intended
            case via a sequence of calls to `ArgumentParser.add_argument()`.
        """
        match self:
            case Subcommand.Audit:
                return _add_audit_cli
            case Subcommand.Configure:
                return _add_configure_cli
            case Subcommand.Run:
                return _add_run_cli


def _cli() -> ArgumentParser:
    """
    Defines the command-line interface for the supply-chain firewall.

    Returns:
        A parser for the supply-chain firewall's command line.

        This parser only handles the firewall's own optional arguments and subcommands.
        It does not parse the package manager commands being run through the firewall.
    """
    parser = ArgumentParser(
        prog="scfw",
        exit_on_error=False,
        description="A tool for preventing the installation of malicious PyPI and npm packages."
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=scfw.__version__
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=_LOG_LEVELS,
        default=_DEFAULT_LOG_LEVEL,
        metavar="LEVEL",
        help="Desired logging level (default: %(default)s, options: %(choices)s)"
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    for subcommand in Subcommand:
        subparser = subparsers.add_parser(str(subcommand), **subcommand._parser_spec())
        subcommand._cli_spec()(subparser)

    return parser


def _parse_command_line(argv: list[str]) -> tuple[Optional[Namespace], str]:
    """
    Parse the supply-chain firewall's command line from a given argument vector.

    Args:
        argv: The argument vector to be parsed.

    Returns:
        A `tuple` of a `Namespace` object containing the results of parsing the given
        argument vector and a `str` help message for the caller's use in early exits.
        In the case of a parsing failure, `None` is returned instead of a `Namespace`.

        On success, and only for the `run` subcommand, the returned `Namespace` contains
        the package manager command present in the given argument vector as a `list[str]`
        under the `command` attribute.
    """
    hinge = len(argv)
    for name in SUPPORTED_PACKAGE_MANAGERS:
        try:
            hinge = min(hinge, argv.index(name))
        except ValueError:
            pass

    parser = _cli()
    help_msg = parser.format_help()

    try:
        args = parser.parse_args(argv[1:hinge+1])
        args.subcommand = Subcommand(args.subcommand)

        if args.subcommand == Subcommand.Run:
            args.command = argv[hinge:]

        if args.subcommand == Subcommand.Audit and argv[hinge+1:]:
            raise ArgumentError(None, "Received unexpected package manager command")

        if (
            args.subcommand == Subcommand.Configure
            and args.remove
            and any({
                args.alias_npm,
                args.alias_pip,
                args.alias_poetry,
                args.dd_agent_port,
                args.dd_api_key,
                args.dd_log_level,
                args.scfw_home,
            })
        ):
            raise ArgumentError(None, "Cannot combine configuration and removal options")

        return args, help_msg

    except ArgumentError:
        return None, help_msg


def parse_command_line() -> tuple[Optional[Namespace], str]:
    """
    Parse the supply-chain firewall's command line.

    Returns:
        A `tuple` of a `Namespace` object containing the results of parsing the
        firewall's command line and a `str` help message for the caller's use in
        early exits. In the case of a parsing failure, `None` is returned instead
        of a `Namespace`.

        On successful parsing of a command line for the `run` subcommand, the
        returned `Namespace` contains the package manager command provided to the
        firewall as a `list[str]` under the `command` attribute. Meanwhile, the name
        of the selected package manager is contained under the `package_manager`
        attribute.
    """
    return _parse_command_line(sys.argv)
