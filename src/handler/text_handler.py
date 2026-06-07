"""Plain text message handler - processes text-only iMessages and Telegram messages."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from src.bridge.models import WebhookPayload
from src.llm.client import LLMClient

if TYPE_CHECKING:
    from src.telegram.models import InternalMessage

logger = structlog.get_logger(__name__)


class TextHandler:
    """Handles plain text messages by feeding them to the LLM for dating advice."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    async def handle(self, payload: WebhookPayload) -> str:
        """Process a text message and generate dating advice.

        Args:
            payload: Parsed webhook payload containing the text message

        Returns:
            Generated response text
        """
        user_text = payload.text.strip()
        return await self._generate(user_text)

    async def _handle_internal(self, msg: InternalMessage) -> str:
        """Process an InternalMessage (Telegram path) and generate dating advice.

        Args:
            msg: Normalised internal message with text content.

        Returns:
            Generated response text.
        """
        return await self._generate(msg.text.strip())

    async def _generate(self, user_text: str) -> str:
        """Core generation logic shared by iMessage and Telegram paths."""
        if not user_text:
            logger.info("empty_text_message")
            return "Hey! What's on your mind? I'm here to help with any dating or relationship questions you have. 💝"

        logger.info("handling_text_message", text_len=len(user_text))

        response = await self.llm_client.generate_response(user_message=user_text)

        logger.info("text_response_generated", response_len=len(response))
        return response
