"""Mail `list` command module."""

from libcli import BaseCmd
from loguru import logger

from gmail.api import GoogleMailAPI
from gmail.cli import GoogleMailCLI


class MailListCmd(BaseCmd):
    """Mail `list` command class."""

    def init_command(self) -> None:
        """Initialize mail `list` command."""

        parser = self.add_subcommand_parser(
            "list",
            help="list mail messages",
            description=self.cli.dedent(
                """
    The `%(prog)s` program lists mail messages.
                """
            ),
        )

        parser.add_argument(
            "--print-message",
            "--print-msg",
            action="store_true",
            help="print message",
        )

        parser.add_argument(
            "--print-listing",
            action="store_true",
            help="print listing",
        )

        parser.add_argument(
            "--download",
            action="store_true",
            help="download attachments",
        )

        parser.add_argument(
            "--msg-id",
            "--msgid",
            help="operate on `MSG_ID` only",
        )

        parser.add_argument(
            "--label-ids",
            nargs="*",
            default=GoogleMailAPI.default_label_ids(),
            help="match labels",
        )

        parser.add_argument(
            "--has-attachments",
            action="store_true",
            help="search messages with any files attached",
        )

        parser.add_argument(
            "--has-images",
            action="store_true",
            help="search messages with image files attached",
        )

        parser.add_argument(
            "--has-videos",
            action="store_true",
            help="search messages with video files attached",
        )

        parser.add_argument(
            "--search-query",
            help="gmail search box query pattern",
        )

    def run(self) -> None:
        """Run mail `list` command."""

        assert isinstance(self.cli, GoogleMailCLI)

        if self.options.msg_id:
            if self.options.print_message:
                self.cli.api.print_message(self.options.msg_id)
            if self.options.download:
                self.cli.api.download(self.options.msg_id)
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
            if self.cli.check_limit():
                break

            logger.info("Message {} id {!r}", idx + 1, msg_id)

            if self.options.print_listing:
                self.cli.api.print_listing(msg_id)

            if self.options.print_message:
                self.cli.api.print_message(msg_id)

            if self.options.download:
                self.cli.api.download(msg_id)
