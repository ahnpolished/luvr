"""Plain text message handler - processes text-only iMessages."""

from __future__ import annotations

import structlog

from src.bridge.models import WebhookPayload
from src.llm.client import LLMClient

logger = structlog.get_logger(__name__)


class TextHandler:
    """Handles plain text iMessages by feeding them to the LLM for dating advice."""

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

        if not user_text:
            logger.info("empty_text_message")
            return "Hey! What's on your mind? I'm here to help with any dating or relationship questions you have. 💝"

        logger.info("handling_text_message", text_len=len(user_text))

        response = await self.llm_client.generate_response(user_message=user_text)

        logger.info("text_response_generated", response_len=len(response))
        return response
