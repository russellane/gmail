from pprint import pformat

from gmail.api import GoogleMailAPI
from tests.testlib import ptrunc, slow, tprint

# import sys
# from loguru import logger
# logger.add(sys.stdout, level="TRACE")


class TestGoogleMail:

    mail = GoogleMailAPI()

    def test_labels_1(self) -> None:
        tprint()
        for label in self.mail.get_labels():
            tprint("label", pformat(label["name"]))

    def test_get_next_msg_id_1(self) -> None:
        tprint()
        n = 5
        for msg_id in self.mail.get_next_msg_id():
            tprint("msg_id", pformat(msg_id))
            n -= 1
            if not n:
                break

    @slow
    def test_get_next_msg_id_label_ids_1(self) -> None:
        tprint()
        label_ids = ["INBOX"]
        count = sum(1 for _ in self.mail.get_next_msg_id(label_ids=label_ids))
        tprint(
            str.format("labels_ids {} count(messages) {}", pformat(label_ids), pformat(count))
        )

    @slow
    def test_get_next_msg_id_label_ids_2(self) -> None:
        tprint()
        label_ids = ["INBOX", "UNREAD"]
        count = sum(1 for _ in self.mail.get_next_msg_id(label_ids=label_ids))
        tprint(
            str.format("labels_ids {} count(messages) {}", pformat(label_ids), pformat(count))
        )

    def test_get_next_msg_id_search_query_1(self) -> None:
        tprint()
        search_query = "filename:pdf"
        count = sum(1 for _ in self.mail.get_next_msg_id(search_query=search_query))
        tprint(
            str.format(
                "search_query {} count(messages) {}", pformat(search_query), pformat(count)
            )
        )

    @slow
    def test_get_next_msg_id_search_query_2(self) -> None:
        tprint()
        search_query = "has:attachment"
        count = sum(1 for _ in self.mail.get_next_msg_id(search_query=search_query))
        tprint(
            str.format(
                "search_query {} count(messages) {}", pformat(search_query), pformat(count)
            )
        )

    def test_get_message_1(self) -> None:
        tprint()
        n = 5
        for _ in self.mail.get_next_msg_id():
            msg = self.mail.get_message(_)
            ptrunc(str(msg))
            n -= 1
            if not n:
                break

    def test_get_next_attachment_id_1(self) -> None:
        tprint()
        search_query = "has:attachment"
        n = 5
        for msg_id in self.mail.get_next_msg_id(search_query=search_query):
            for attachment_id in self.mail.get_next_attachment_id(msg_id):
                tprint(
                    str.format(
                        "msg_id {} attachment_id {}", pformat(msg_id), pformat(attachment_id)
                    )
                )
            n -= 1
            if not n:
                break

    @slow
    def test_get_next_attachment_id_2(self) -> None:
        # test against messages that do not have an attachment
        tprint()
        n = 50
        for msg_id in self.mail.get_next_msg_id():
            tprint(str.format("msg_id {}", pformat(msg_id)))
            for attachment_id in self.mail.get_next_attachment_id(msg_id):
                tprint(
                    str.format(
                        "msg_id {} attachment_id {}", pformat(msg_id), pformat(attachment_id)
                    )
                )
            n -= 1
            if not n:
                break

    def test_get_next_attachment_data_1(self) -> None:
        tprint()
        search_query = "has:attachment"
        n = 5
        for msg_id in self.mail.get_next_msg_id(search_query=search_query):
            tprint(str.format("msg_id {}", pformat(msg_id)))
            for attachment_id in self.mail.get_next_attachment_id(msg_id):
                tprint(
                    str.format(
                        "msg_id {} attachment_id {}", pformat(msg_id), pformat(attachment_id)
                    )
                )
            n -= 1
            if not n:
                break


#        self.args.limit = 3
#
#        for msg_id in self.cli.api.get_next_msg_id(label_ids=self.cli.api.default_label_ids()):
#
#            if self.cli.check_limit():
#                break
#
#            self._print_listing(msg_id)
