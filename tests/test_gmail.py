import os
import sys
from argparse import Namespace

import pytest

from gmail.api import GoogleMailAPI
from gmail.cli import GoogleMailCLI

# import sys
# from loguru import logger
# logger.add(sys.stdout, level="TRACE")

slow = pytest.mark.skipif(not os.environ.get("SLOW"), reason="slow")


@pytest.fixture(name="mail")
def mail_() -> GoogleMailAPI:
    options = Namespace()
    return GoogleMailAPI(options)


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


def test_gmail_labels() -> None:
    run_cli(["labels"])


def test_gmail_labels_pretty_print() -> None:
    run_cli(["labels", "--pretty"])


def test_gmail_labels_limit_3() -> None:
    run_cli(["labels", "--limit", "3"])


@slow
def test_gmail_labels_show_counts() -> None:
    run_cli(["labels", "--show-counts"])


def test_gmail_list_limit_20() -> None:
    run_cli(["list", "--limit", "20"])


def test_list_pretty_print_limit_1() -> None:
    run_cli(["list", "--pretty-print", "--limit", "1"])


def test_list_print_message_limit_1() -> None:
    run_cli(["list", "--print-message", "--limit", "1"])


def test_list_print_message_msg_id(mail: GoogleMailAPI) -> None:

    for i, msg_id in enumerate(mail.get_next_msg_id()):
        run_cli(["list", "--print-message", "--msg-id", msg_id])
        if i >= 2:
            break


def test_list_print_listing_limit_3() -> None:
    run_cli(["list", "--print-listing", "--limit", "3"])


def test_list_has_attachments_limit_3() -> None:
    run_cli(["list", "--has-attachments", "--print-listing", "--limit", "3"])


def test_list_has_images_limit_3() -> None:
    run_cli(["list", "--has-images", "--print-listing", "--limit", "3"])


def test_list_has_videos_limit_3() -> None:
    run_cli(["list", "--has-videos", "--print-listing", "--limit", "3"])


@slow
def _test_get_next_msg_id_label_ids_1(mail: GoogleMailAPI) -> None:
    label_ids = ["INBOX"]
    count = sum(1 for _ in mail.get_next_msg_id(label_ids=label_ids))
    print(f"labels_ids {label_ids!r} count(messages) {count}")


def test_get_next_msg_id_label_ids_2(mail: GoogleMailAPI) -> None:
    label_ids = ["INBOX", "UNREAD"]
    count = sum(1 for _ in mail.get_next_msg_id(label_ids=label_ids))
    print(f"labels_ids {label_ids!r} count(messages) {count}")


def test_get_next_msg_id_search_query_1(mail: GoogleMailAPI) -> None:
    search_query = "filename:pdf"
    count = sum(1 for _ in mail.get_next_msg_id(search_query=search_query))
    print(f"search_query {search_query!r} count(messages) {count}")


def test_get_next_msg_id_search_query_2(mail: GoogleMailAPI) -> None:
    search_query = "has:attachment"
    count = sum(1 for _ in mail.get_next_msg_id(search_query=search_query))
    print(f"search_query {search_query!r} count(messages) {count}")


def test_get_next_attachment_id_1(mail: GoogleMailAPI) -> None:
    search_query = "has:attachment"
    for i, msg_id in enumerate(mail.get_next_msg_id(search_query=search_query)):
        for attachment_id in mail.get_next_attachment_id(msg_id):
            print(f"msg_id {msg_id!r} attachment_id {attachment_id!r}")
        if i >= 2:
            break


def test_download_msg_id(mail: GoogleMailAPI) -> None:
    search_query = "has:attachment"
    for i, msg_id in enumerate(mail.get_next_msg_id(search_query=search_query)):
        run_cli(["download", msg_id])
        if i >= 2:
            break
