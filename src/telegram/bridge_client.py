"""Telegram bridge client — adapts Telegram's API to look like a bridge client.

The existing handler classes (TextHandler, PhotoHandler, VoiceHandler) expect
a ``bridge_client`` that provides ``download_attachment`` and ``send_message``.
This module provides a lightweight adapter so those handlers can be reused
without modification in the Telegram bot.
"""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class TelegramBridgeClient:
    """Adapts the Telegram bot to the bridge-client interface expected by handlers.

    This is intentionally lightweight — it delegates file downloads to the
    real Telegram ``Bot`` instance and keeps a reference to ``update.message``
    for sending replies.
    """

    def __init__(self) -> None:
        self._attachment_cache: dict[str, bytes] = {}
        self._chat_id: int = 0
        self._message_reply: Any = None  # telegram.Message.reply_text

    def configure(self, chat_id: int, reply_method: Any) -> None:
        """Configure the bridge client for the current update context.

        Called once per incoming message before dispatching to a handler.

        Args:
            chat_id: Telegram chat identifier.
            reply_method: Callable for sending a reply (``message.reply_text``).
        """
        self._chat_id = chat_id
        self._message_reply = reply_method

    def cache_attachment(self, file_id: str, data: bytes) -> None:
        """Pre-load attachment bytes into the in-memory cache.

        The Telegram handler functions download media *before* calling the
        handler pipeline, so we cache the bytes here for the handler to
        retrieve via ``download_attachment``.
        """
        self._attachment_cache[file_id] = data

    async def download_attachment(self, attachment_guid: str) -> bytes:
        """Return pre-cached attachment bytes.

        Args:
            attachment_guid: The Telegram file_id acting as the attachment guid.

        Returns:
            Raw bytes of the media file.

        Raises:
            KeyError: If the file_id was not cached beforehand.
        """
        if attachment_guid not in self._attachment_cache:
            logger.warning("attachment_not_cached", file_id=attachment_guid)
            raise KeyError(f"Attachment {attachment_guid} not found in cache")
        return self._attachment_cache[attachment_guid]

    async def send_message(self, chat_guid: str, message: str) -> Any:
        """Send a reply message back to the user via Telegram.

        Args:
            chat_guid: Ignored (Telegram uses chat_id set via ``configure``).
            message: The text to reply with.

        Returns:
            The sent ``telegram.Message`` object.
        """
        if self._message_reply is None:
            logger.warning("bridge_not_configured")
            raise RuntimeError("TelegramBridgeClient not configured for this message")

        # Respect Telegram's 4096 char limit for messages
        if len(message) > 4096:
            message = message[:4090] + "..."

        try:
            sent = await self._message_reply(text=message)
            logger.debug("telegram_reply_sent", chat_id=self._chat_id)
            return sent
        except Exception:
            logger.exception("telegram_send_failed", chat_id=self._chat_id)
            raise

    async def aclose(self) -> None:
        """No-op close — Telegram connection is managed by the Application."""
        self._attachment_cache.clear()

    async def health_check(self) -> bool:
        """Always returns True — real health check is done at the Application level."""
        return True
