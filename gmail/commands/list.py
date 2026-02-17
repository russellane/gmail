"""Mail `list` command module."""

from time import localtime, strftime
from typing import Any

from loguru import logger

from gmail.api import GoogleMailAPI
from gmail.commands import GoogleMailCmd


class MailListCmd(GoogleMailCmd):
    """Mail `list` command class."""

    def init_command(self) -> None:
        """Initialize mail `list` command."""

        parser = self.add_subcommand_parser(
            "list",
            help="list mail messages",
            description=self.cli.dedent("""
    The `%(prog)s` program lists mail messages.
                """),
        )

        group = parser.add_argument_group(
            "Printing options",
            "These options are mutually exclusive.",
        )

        exc = group.add_mutually_exclusive_group()
        exc.add_argument(
            "--print-message",
            "--print-msg",
            action="store_true",
            help="print message",
        )
        exc.add_argument(
            "--print-listing",
            action="store_true",
            help="print listing",
        )
        self.add_pretty_print_option(exc)

        group = parser.add_argument_group("Filtering options")

        group.add_argument(
            "--msg-id",
            "--msgid",
            help="operate on `MSG_ID` only",
        )

        arg = group.add_argument(
            "--label-ids",
            nargs="*",
            default=GoogleMailAPI.default_label_ids(),
            help="match labels",
        )
        self.cli.add_default_to_help(arg, group)

        group.add_argument(
            "--has-attachments",
            action="store_true",
            help="search messages with any files attached",
        )

        group.add_argument(
            "--has-images",
            action="store_true",
            help="search messages with image files attached",
        )

        group.add_argument(
            "--has-videos",
            action="store_true",
            help="search messages with video files attached",
        )

        group.add_argument(
            "--search-query",
            help="gmail search box query pattern",
        )

        self.add_limit_option(parser)

    def run(self) -> None:
        """Run mail `list` command."""

        if self.options.msg_id:
            msg = self.cli.api.get_message(self.options.msg_id)
            self.display_message(msg)
            return

        # See https://support.google.com/mail/answer/7190?hl=en

        if self.options.has_attachments:
            self.options.search_query = "has:attachment"

        elif self.options.has_images:
            self.options.search_query = "filename:(jpg OR jpeg OR png OR tiff OR bmp OR pdf)"

        elif self.options.has_videos:
            self.options.search_query = "filename:(mp4 OR wmv OR mov OR mpg)"

        print(
            str.format(
                "Searching for {!r} in {!r}", self.options.search_query, self.options.label_ids
            )
        )

        for idx, msg_id in enumerate(
            self.cli.api.get_next_msg_id(
                label_ids=self.options.label_ids,
                search_query=self.options.search_query,
            )
        ):
            if self.check_limit():
                break

            if not self.options.print_listing:
                logger.info("Message {} id {!r}", idx + 1, msg_id)

            if (
                self.options.pretty_print
                or self.options.print_listing
                or self.options.print_message
            ):
                msg = self.cli.api.get_message(msg_id)
                self.display_message(msg)

    def display_message(self, msg: dict[str, Any]) -> None:
        """Display `msg`."""

        if self.options.pretty_print:
            self.pprint(msg, max_string=200)
        elif self.options.print_listing:
            self.print_listing(msg)
        elif self.options.print_message:
            self.print_message(msg)

    def print_message(self, msg: dict[str, Any]) -> None:
        """docstring."""

        # logger.debug("msg {!r}", msg)

        for key, value in msg.items():
            self._print_item("MSG", key, value)

        self._print_item(
            "MSG",
            "LOCALTIME",
            strftime("%Y-%m-%d %H:%M:%S %Z", localtime(int(msg["internalDate"]) / 1000)),
        )

        #
        payload = msg["payload"]

        for key, value in payload.items():
            self._print_item("PAYLOAD", key, value)

        #
        headers = payload["headers"]
        for hdr_dict in headers:
            key = hdr_dict["name"]
            value = hdr_dict["value"]
            self._print_item("HEADER", key, value)

        try:
            msg_subject = [h["value"] for h in headers if h["name"] == "Subject"][0]
        except IndexError:  # pragma: no cover
            msg_subject = ""  # pragma: no cover
        self._print_item("HEADER", "SUBJECT", msg_subject)

        try:
            msg_from = [h["value"] for h in headers if h["name"] == "From"][0]
        except IndexError:  # pragma: no cover
            msg_from = ""  # pragma: no cover
        self._print_item("HEADER", "FROM", msg_from)

    def print_listing(self, msg: dict[str, Any]) -> None:
        """docstring."""

        # logger.info('msg {!r}', msg.keys())

        # self._print_item('MSG', 'id', msg['id'])
        # self._print_item('MSG', 'snippet', msg['snippet'])
        # self._print_item('MSG', 'sizeEstimate', msg['sizeEstimate'])
        # self._print_item('MSG', 'labelIds', msg['labelIds'])

        timestamp = strftime("%Y-%m-%d %H:%M:%S %Z", localtime(int(msg["internalDate"]) / 1000))

        payload = msg["payload"]
        headers = payload["headers"]

        try:
            msg_subject = [h["value"] for h in headers if h["name"] == "Subject"][0]
        except IndexError:  # pragma: no cover
            msg_subject = ""  # pragma: no cover
        # self._print_item('HEADER', 'SUBJECT', msg_subject)

        try:
            msg_from = [h["value"] for h in headers if h["name"] == "From"][0]
        except IndexError:  # pragma: no cover
            msg_from = ""  # pragma: no cover
        # self._print_item('HEADER', 'FROM', msg_from)

        print(str.format("{} {:<40} {}", timestamp, msg_from, msg_subject))

    @staticmethod
    def _print_item(tag: str, key: str, value: str) -> None:
        """docstring."""
        truncated = str(value)[:90] + (str(value)[90:] and "...")
        print(str.format("{!r:<7} {!r:<20} {!r}", tag, key, truncated))
