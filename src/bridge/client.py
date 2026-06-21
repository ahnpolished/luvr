"""Async HTTP client for BlueBubbles iMessage bridge REST API.

BlueBubbles is a self-hosted server that bridges iMessage to a REST API + WebSocket.
It must run on a Mac with iMessage signed in.

API Reference: https://bluebubbles.app/docs/api/
"""

from __future__ import annotations

import uuid
from pathlib import Path

import httpx
import structlog

from src.bridge.models import SendMessageResponse

logger = structlog.get_logger(__name__)


class BlueBubblesClient:
    """Async HTTP client for the BlueBubbles REST API."""

    def __init__(self, server_url: str, password: str) -> None:
        self.server_url = server_url.rstrip("/")
        self.password = password
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy-initialize the httpx async client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.server_url,
                timeout=httpx.Timeout(30.0),
                headers={"Content-Type": "application/json"},
                params={"password": self.password},
            )
        return self._client

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def send_message(
        self,
        chat_guid: str,
        message: str,
        subject: str = "",
    ) -> SendMessageResponse:
        """Send an iMessage text to a specific chat.

        Args:
            chat_guid: The chat GUID (e.g., "iMessage;-;+1234567890")
            message: The text message to send
            subject: Optional message subject (for SMS/MMS fallback)

        Returns:
            SendMessageResponse with status and details

        Raises:
            httpx.HTTPError: If the API request fails
        """
        payload = {
            "chatGuid": chat_guid,
            "message": message,
            "method": "apple-script",
            "subject": subject,
            "tempGuid": str(uuid.uuid4()),
        }

        logger.debug("sending_message", chat_guid=chat_guid, message_len=len(message))

        try:
            response = await self.client.post("/api/v1/message/text", json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info("message_sent", chat_guid=chat_guid, status=data.get("status"))
            return SendMessageResponse(**data)
        except httpx.HTTPError:
            logger.exception("send_message_failed", chat_guid=chat_guid)
            raise

    async def send_attachment(
        self,
        chat_guid: str,
        file_path: Path,
    ) -> SendMessageResponse:
        """Send a file attachment via iMessage.

        Args:
            chat_guid: The chat GUID
            file_path: Path to the file to send

        Returns:
            SendMessageResponse with status and details
        """
        logger.debug("sending_attachment", chat_guid=chat_guid, file=str(file_path))

        try:
            with open(file_path, "rb") as f:
                files = {"attachment": (file_path.name, f)}
                params = {"chatGuid": chat_guid, "password": self.password}
                response = await self.client.post(
                    "/api/v1/message/attachment",
                    files=files,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
                logger.info("attachment_sent", chat_guid=chat_guid)
                return SendMessageResponse(**data)
        except httpx.HTTPError:
            logger.exception("send_attachment_failed", chat_guid=chat_guid)
            raise
        except FileNotFoundError:
            logger.error("attachment_file_not_found", path=str(file_path))
            raise

    async def download_attachment(self, attachment_guid: str) -> bytes:
        """Download an attachment from the BlueBubbles server.

        Args:
            attachment_guid: The GUID of the attachment to download

        Returns:
            Raw bytes of the attachment

        Raises:
            httpx.HTTPError: If the download fails
        """
        logger.debug("downloading_attachment", guid=attachment_guid)

        try:
            response = await self.client.get(
                f"/api/v1/attachment/{attachment_guid}/download",
            )
            response.raise_for_status()
            logger.info("attachment_downloaded", guid=attachment_guid, size=len(response.content))
            return bytes(response.content)
        except httpx.HTTPError:
            logger.exception("download_attachment_failed", guid=attachment_guid)
            raise

    async def health_check(self) -> bool:
        """Check if the BlueBubbles server is reachable."""
        try:
            response = await self.client.get("/api/v1/server/info")
            return bool(response.is_success)
        except httpx.HTTPError:
            return False
