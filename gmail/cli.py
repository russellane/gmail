"""Command Line Interface to Google Mail."""

from pathlib import Path
from typing import Any

from libcli import BaseCLI
from loguru import logger

from gmail.api import GoogleMailAPI

__all__ = ["GoogleMailCLI"]


class GoogleMailCLI(BaseCLI):
    """Command Line Interface to Google Mail."""

    config = {
        # name of config file.
        "config-file": Path("~/.pygoogle.toml"),
        # toml [section-name].
        "config-name": "gmail",
        # distribution name, not importable package name
        "dist-name": "rlane-gmail",
    }

    api: Any = None  # connection to google service

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.ArgumentParser(
            prog="gmail",
            description="Google `mail` command line interface.",
            epilog="See `%(prog)s COMMAND --help` for help on a specific command.",
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        arg = self.parser.add_argument(
            "--limit",
            type=int,
            help="limit execution to `LIMIT` number of items",
        )
        self.add_default_to_help(arg)

        self.add_subcommand_modules("gmail.commands", prefix="Mail", suffix="Cmd")

    def main(self) -> None:
        """Command line interface entry point (method)."""

        if not self.options.cmd:
            self.parser.print_help()
            self.parser.exit(2, "error: Missing COMMAND\n")

        self.api = GoogleMailAPI()
        self.options.cmd()

    def check_limit(self) -> bool:
        """Call at top of loop before performing work."""

        if self.options.limit is None:
            logger.trace("No limit")
            return False

        self.options.limit -= 1
        logger.trace("limit {!r}", self.options.limit)
        assert isinstance(self.options.limit, int)
        return self.options.limit < 0


def main(args: list[str] | None = None) -> None:
    """Command line interface entry point (function)."""
    GoogleMailCLI(args).main()
