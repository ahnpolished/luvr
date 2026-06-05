"""Message processing pipeline - orchestrates the full message handling flow."""

from __future__ import annotations

import structlog

from src.bridge.client import BlueBubblesClient
from src.bridge.models import WebhookPayload
from src.handler.photo_handler import PhotoHandler
from src.handler.router import MessageRouter
from src.handler.text_handler import TextHandler
from src.handler.voice_handler import VoiceHandler
from src.llm.client import create_llm_client

logger = structlog.get_logger(__name__)


class MessagePipeline:
    """Orchestrates the full message processing pipeline.

    Flow:
    1. Receive webhook payload from BlueBubbles
    2. Route to appropriate handler (text/photo/voice)
    3. Handler generates response via LLM
    4. Send response back via BlueBubbles
    """

    def __init__(self, bridge_client: BlueBubblesClient) -> None:
        self.bridge_client = bridge_client
        self.router = MessageRouter()

        # Lazy-initialized handlers
        self._llm_client = None
        self._text_handler: TextHandler | None = None
        self._photo_handler: PhotoHandler | None = None
        self._voice_handler: VoiceHandler | None = None

    @property
    def text_handler(self) -> TextHandler:
        if self._text_handler is None:
            self._text_handler = TextHandler(llm_client=self.llm_client)
        return self._text_handler

    @property
    def photo_handler(self) -> PhotoHandler:
        if self._photo_handler is None:
            self._photo_handler = PhotoHandler(
                bridge_client=self.bridge_client,
                llm_client=self.llm_client,
            )
        return self._photo_handler

    @property
    def voice_handler(self) -> VoiceHandler:
        if self._voice_handler is None:
            self._voice_handler = VoiceHandler(
                bridge_client=self.bridge_client,
                llm_client=self.llm_client,
            )
        return self._voice_handler

    @property
    def llm_client(self):
        if self._llm_client is None:
            self._llm_client = create_llm_client()
        return self._llm_client

    async def process(self, raw_payload: dict) -> None:
        """Process an incoming webhook payload from BlueBubbles.

        Args:
            raw_payload: Raw JSON payload from BlueBubbles webhook
        """
        try:
            payload = WebhookPayload.model_validate(raw_payload)

            # Skip messages from ourselves (don't loop)
            if payload.is_from_me:
                logger.debug("skipping_own_message")
                return

            # Skip messages without a valid chat GUID
            if not payload.chat_guid:
                logger.warning("missing_chat_guid")
                return

            msg_type = self.router.route(payload)

            if msg_type == "text":
                response = await self.text_handler.handle(payload)
            elif msg_type == "photo":
                response = await self.photo_handler.handle(payload)
            elif msg_type == "voice":
                response = await self.voice_handler.handle(payload)
            else:
                logger.warning("unknown_message_type", msg_type=msg_type)
                return

            if response:
                await self.bridge_client.send_message(
                    chat_guid=payload.chat_guid,
                    message=response,
                )
                logger.info("response_sent", msg_type=msg_type, chat_guid=payload.chat_guid)

        except Exception:
            logger.exception("pipeline_error")
            # Try to send error message back to user
            try:
                if "payload" in locals() and payload.chat_guid:
                    await self.bridge_client.send_message(
                        chat_guid=payload.chat_guid,
                        message="😅 Oops, something went wrong on my end. Could you try again?",
                    )
            except Exception:
                logger.exception("error_response_failed")
