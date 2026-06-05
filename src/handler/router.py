"""Message router - determines message type and dispatches to appropriate handler."""

from __future__ import annotations

import structlog

from src.bridge.models import WebhookPayload

logger = structlog.get_logger(__name__)


class MessageRouter:
    """Routes incoming messages to the correct handler based on content type."""

    def route(self, payload: WebhookPayload) -> str:
        """Determine the handler route for an incoming message.

        Args:
            payload: Parsed BlueBubbles webhook payload

        Returns:
            Handler name: "text", "photo", or "voice"
        """
        msg_type = payload.message_type

        logger.info(
            "message_routed",
            msg_type=msg_type,
            has_text=bool(payload.text.strip()),
            num_attachments=len(payload.attachments),
        )

        return msg_type
