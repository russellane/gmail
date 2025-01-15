"""Interface to Google Mail."""

import base64
import os
from argparse import Namespace
from typing import Any, Iterator

import libgoogle
import xdg
from loguru import logger

__all__ = ["GoogleMailAPI"]


class GoogleMailAPI:
    """Interface to Google Mail.

    See https://developers.google.com/gmail/api/v1/reference
    """

    mimetype_PDF = "application/pdf"

    def __init__(self, options: Namespace) -> None:
        """Connect to Google Mail."""

        self.options = options
        self.service = libgoogle.connect("gmail.readonly", "v1")

        self.download_dir = xdg.xdg_data_home() / "gmail"
        self.user_id = "me"

    @staticmethod
    def default_label_ids() -> list[str]:
        """Return list of default label ids."""
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
            return []  # pragma: no cover

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
            logger.debug("No payload")  # pragma: no cover
            return  # pragma: no cover

        parts = payload.get("parts", [])
        if not parts:
            logger.debug("No parts")  # pragma: no cover
            return  # pragma: no cover

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
                logger.debug("Missing mimeType")  # pragma: no cover
                continue  # pragma: no cover
            if not filename:
                logger.debug("Missing filename")  # pragma: no cover
                continue  # pragma: no cover
            if not body:
                logger.debug("Missing body")  # pragma: no cover
                continue  # pragma: no cover
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
