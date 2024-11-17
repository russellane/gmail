"""Interface to Google Mail."""

import base64
import os
from time import localtime, strftime
from typing import Any, Iterator

import xdg
from loguru import logger

from gmail.google import connect_to_google

# from typing import Any, Iterator


__all__ = ["GoogleMailAPI"]


class GoogleMailAPI:
    """Interface to Google Mail.

    See https://developers.google.com/gmail/api/v1/reference
    """

    mimetype_PDF = "application/pdf"

    def __init__(self) -> None:
        """Connect to Google Mail."""

        self.service = connect_to_google("gmail.readonly", "v1")

        self.download_dir = xdg.xdg_data_home() / "pygoogle-gmail"
        self.user_id = "me"

    @staticmethod
    def default_label_ids() -> list[str]:
        """docstring."""
        return ["INBOX"]

    def get_labels(self) -> list[dict[str, str]]:
        """Return all labels in the user's mailbox."""

        # https://developers.google.com/gmail/api/v1/reference/users/labels/list

        parms = {"userId": self.user_id}

        logger.debug("service.users().labels().list({!r})", parms)
        response: dict[str, list[Any]] = (
            self.service.users().labels().list(**parms).execute()  # noqa: PLE101
        )  # noqa: PLE101
        logger.trace("response {!r}", response)

        assert isinstance(response, dict)

        if not (labels := response.get("labels")):
            return []

        assert isinstance(labels, list)
        return labels

    def get_next_msg_id(
        self,
        label_ids: list[str] | None = None,
        search_query: str | None = None,
    ) -> Iterator[str]:
        """Return the messages in the user's mailbox."""

        # https://developers.google.com/gmail/api/v1/reference/users/messages/list

        parms = {
            "userId": self.user_id,
            "labelIds": label_ids,
            "q": search_query,
        }

        while True:
            logger.debug("service.users().messages().list({!r})", parms)
            response = self.service.users().messages().list(**parms).execute()  # noqa: PLE101
            logger.trace("response {!r}", response)

            for _ in response.get("messages", []):
                yield _["id"]

            parms["pageToken"] = response.get("nextPageToken")
            if parms["pageToken"] is None:
                return

    def get_message(self, msg_id: str) -> dict[str, Any]:
        """Return specified message."""

        # https://developers.google.com/gmail/api/v1/reference/users/messages/get

        parms = {
            "userId": self.user_id,
            "id": msg_id,
        }

        logger.debug("service.users().messages().get({!r})", parms)
        response = self.service.users().messages().get(**parms).execute()  # noqa: PLE101
        logger.trace("response {!r}", response)

        assert isinstance(response, dict)
        return response

    def get_next_attachment_id(self, msg_id: str) -> Iterator[tuple[str, str, str]]:
        """docstring."""

        msg = self.get_message(msg_id)

        payload = msg.get("payload")
        if not payload:
            logger.debug("No payload")
            return

        parts = payload.get("parts", [])
        if not parts:
            logger.debug("No parts")
            return

        for part in self._flatten_nested_email_parts(parts):

            mimetype = part.get("mimeType")

            (basename, ext) = os.path.splitext(part["filename"])
            filename = os.path.join(self.download_dir, basename + "-" + msg_id + ext)

            body: dict[str, str] | None = part.get("body")
            attachment_id = body.get("attachmentId") if body else None

            logger.debug(
                "Part mimeType {!r} filename {!r} attachment_id {!r}",
                mimetype,
                filename,
                attachment_id,
            )

            if not mimetype:
                logger.debug("Missing mimeType")
                continue
            if not filename:
                logger.debug("Missing filename")
                continue
            if not body:
                logger.debug("Missing body")
                continue
            if not attachment_id:
                logger.debug("Missing attachmentId")
                continue

            yield mimetype, filename, attachment_id

    def get_attachment_data(self, msg_id: str, attachment_id: str) -> bytes:
        """docstring."""

        att = (
            self.service.users()  # noqa: PLE101
            .messages()
            .attachments()
            .get(userId=self.user_id, id=attachment_id, messageId=msg_id)
            .execute()
        )

        # LANG=en_US.UTF-8
        data = att["data"]
        data = data.replace("-", "+")
        data = data.replace("_", "/")
        data = base64.b64decode(bytes(data, "UTF-8"))

        return bytes(data)

    @staticmethod
    def _flatten_nested_email_parts(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        all_parts: list[dict[str, Any]] = []
        for part in parts:
            if p := part.get("parts"):
                all_parts.extend(p)
            else:
                all_parts.append(part)
        return all_parts

    def print_message(self, msg_id: str) -> None:
        """docstring."""

        msg = self.get_message(msg_id)

        logger.debug("msg {!r}", msg)

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
        except IndexError:
            msg_subject = ""
        self._print_item("HEADER", "SUBJECT", msg_subject)

        try:
            msg_from = [h["value"] for h in headers if h["name"] == "From"][0]
        except IndexError:
            msg_from = ""
        self._print_item("HEADER", "FROM", msg_from)

    def print_listing(self, msg_id: str) -> None:
        """docstring."""

        msg = self.get_message(msg_id)

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
        except IndexError:
            msg_subject = ""
        # self._print_item('HEADER', 'SUBJECT', msg_subject)

        try:
            msg_from = [h["value"] for h in headers if h["name"] == "From"][0]
        except IndexError:
            msg_from = ""
        # self._print_item('HEADER', 'FROM', msg_from)

        print(str.format("{} {:<40} {}", timestamp, msg_from, msg_subject))

    @staticmethod
    def _print_item(tag: str, key: str, value: str) -> None:
        """docstring."""
        truncated = str(value)[:90] + (str(value)[90:] and "...")
        print(str.format("{!r:<7} {!r:<20} {!r}", tag, key, truncated))
