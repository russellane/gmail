import os
import sys

import pytest

from gmail.api import GoogleMailAPI
from gmail.cli import GoogleMailCLI

# import sys
# from loguru import logger
# logger.add(sys.stdout, level="TRACE")

slow = pytest.mark.skipif(not os.environ.get("SLOW"), reason="slow")


@pytest.fixture(name="mail")
def mail_() -> GoogleMailAPI:
    return GoogleMailAPI()


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


def test_gmail_labels_limit_3() -> None:
    run_cli(["--limit", "3", "labels"])


@slow
def test_gmail_labels_show_counts() -> None:
    run_cli(["labels", "--show-counts"])


def test_gmail_list_limit_20() -> None:
    run_cli(["--limit", "20", "list"])


def test_list_print_message_limit_3() -> None:
    run_cli(["--limit", "3", "list", "--print-message"])


def test_list_print_message_msg_id(mail: GoogleMailAPI) -> None:

    for i, msg_id in enumerate(mail.get_next_msg_id()):
        run_cli(["list", "--print-message", "--msg-id", msg_id])
        if i >= 2:
            break


def test_list_download_msg_id(mail: GoogleMailAPI) -> None:

    for i, msg_id in enumerate(mail.get_next_msg_id()):
        run_cli(["list", "--download", "--msg-id", msg_id])
        if i >= 2:
            break


def test_list_print_listing_limit_3() -> None:
    run_cli(["--limit", "3", "list", "--print-listing"])


def test_list_has_attachments() -> None:
    run_cli(["--limit", "3", "list", "--has-attachments", "--print-message", "--print-listing"])


def test_list_has_images() -> None:
    run_cli(["--limit", "3", "list", "--has-images", "--print-message", "--print-listing"])


def test_list_has_videos() -> None:
    run_cli(["--limit", "3", "list", "--has-videos", "--print-message", "--print-listing"])


def test_list_images_download_limit_3() -> None:
    run_cli(["--limit", "3", "list", "--has-images", "--download"])


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
