"""Command Line Interface to Google Mail."""

from pathlib import Path

from libcli import BaseCLI

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

    api: GoogleMailAPI  # connection to google service

    def init_parser(self) -> None:
        """Initialize argument parser."""

        self.ArgumentParser(
            prog=__package__,
            description="Google `mail` command line interface.",
            epilog="See `%(prog)s COMMAND --help` for help on a specific command.",
        )

    def add_arguments(self) -> None:
        """Add arguments to parser."""

        self.add_subcommand_modules("gmail.commands", prefix="Mail", suffix="Cmd")

    def main(self) -> None:
        """Command line interface entry point (method)."""

        if not self.options.cmd:
            self.parser.print_help()
            self.parser.exit(2, "error: Missing COMMAND\n")

        self.api = GoogleMailAPI(self.options)
        self.options.cmd()


def main(args: list[str] | None = None) -> None:
    """Command line interface entry point (function)."""
    GoogleMailCLI(args).main()
