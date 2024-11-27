"""Mail `labels` command module."""

from loguru import logger

from gmail.commands import GoogleMailCmd


class MailLabelsCmd(GoogleMailCmd):
    """Mail `labels` command class."""

    def init_command(self) -> None:
        """Initialize mail `labels` command."""

        parser = self.add_subcommand_parser(
            "labels",
            help="list labels",
            description=self.cli.dedent(
                """
    The `%(prog)s` program lists labels.
                """
            ),
        )

        parser.add_argument(
            "--show-counts",
            action="store_true",
            help="show message counts",
        )

        self.add_limit_option(parser)
        self.add_pretty_print_option(parser)

    def run(self) -> None:
        """Run mail `labels` command."""

        labels = self.cli.api.get_labels()
        nlabels = len(labels)

        print("There are", nlabels, "labels")

        for idx, label in enumerate(labels):

            if self.check_limit():
                break

            if self.cli.options.pretty_print:
                self.pprint(label)
                continue

            logger.debug("idx {} label {!r}", idx, label)

            label_id = label["id"]
            label_name = label["name"]

            if self.options.show_counts:
                n_msg_ids = sum(1 for _ in self.cli.api.get_next_msg_id(label_ids=[label_id]))

                print(
                    str.format(
                        "Label {:3} of {:3}: {:7} msgs id {:20} name {}",
                        idx + 1,
                        nlabels,
                        n_msg_ids,
                        label_id,
                        label_name,
                    )
                )
            else:
                print(
                    str.format(
                        "Label {:3} of {:3}: id {:20} name {}",
                        idx + 1,
                        nlabels,
                        label_id,
                        label_name,
                    )
                )
