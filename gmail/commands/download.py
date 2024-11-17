"""Mail `download` command module."""

import errno
import os
from collections import defaultdict

from libcli import BaseCmd
from loguru import logger

from gmail.cli import GoogleMailCLI


class MailDownloadCmd(BaseCmd):
    """Mail `download` command class."""

    def init_command(self) -> None:
        """Initialize mail `download` command."""

        self.add_subcommand_parser(
            "download",
            help="download mail messages",
            description=self.cli.dedent(
                """
    The `%(prog)s` program downloads mail messages.
                """
            ),
        )

    def run(self) -> None:
        """Run mail `download` command."""

        msg_id = "FIXME"

        unknown_mimetypes: dict[str, int] = defaultdict(int)

        assert isinstance(self.cli, GoogleMailCLI)

        for mimetype, filename, attachment_id in self.cli.api.get_next_attachment_id(msg_id):

            if mimetype[:5] not in ("image", "video") and mimetype != self.cli.api.mimetype_PDF:
                logger.debug("mimeType {!r} not image/video/pdf", mimetype)
                unknown_mimetypes[mimetype] += 1
                continue

            if self.options.no_action:
                print("Not downloading", filename)
                continue

            print("Downloading", filename)

            try:
                os.makedirs(self.cli.api.download_dir)
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise

            with open(filename, "wb") as _:
                _.write(self.cli.api.get_attachment_data(msg_id, attachment_id))

        #
        for mimetype, count in unknown_mimetypes.items():
            print(str.format("unknown mimeType {:5d} {:s}", count, mimetype))
