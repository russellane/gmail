import sys

import pytest

from gmail.cli import GoogleMailCLI


def run_cli(options: list[str]) -> None:
    """Test calling the cli directly."""

    sys.argv = ["gmail"]
    if options:
        sys.argv += options
    print(f"\nRunning {sys.argv!r}", flush=True)
    GoogleMailCLI().main()


def test_gmail_no_args() -> None:
    with pytest.raises(SystemExit) as err:
        run_cli([])
    assert err.value.code == 2


# def test_gmail_download() -> None:
#     run_cli(["download"])


def test_gmail_labels() -> None:
    run_cli(["labels"])


def test_gmail_list() -> None:
    run_cli(["list"])
