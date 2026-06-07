"""Photo/image message handler - processes images via vision LLM for dating advice."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from src.bridge.client import BlueBubblesClient
from src.bridge.models import WebhookPayload
from src.config import settings
from src.llm.client import LLMClient
from src.llm.prompts import UNSUPPORTED_MEDIA_RESPONSE

if TYPE_CHECKING:
    from src.telegram.bridge_client import TelegramBridgeClient
    from src.telegram.models import InternalMessage

logger = structlog.get_logger(__name__)

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/heic", "image/webp", "image/gif"}


class PhotoHandler:
    """Handles photo/image messages by analyzing them with vision LLM."""

    def __init__(self, bridge_client: BlueBubblesClient | TelegramBridgeClient, llm_client: LLMClient) -> None:
        self.bridge_client = bridge_client
        self.llm_client = llm_client

    async def handle(self, payload: WebhookPayload) -> str:
        """Process a photo message and generate dating advice based on the image.

        Args:
            payload: Parsed webhook payload with image attachments

        Returns:
            Generated response text analyzing the image
        """
        # Find the first image attachment
        image_attachment = None
        for att in payload.attachments:
            if att.mime_type in SUPPORTED_IMAGE_TYPES:
                image_attachment = att
                break

        if not image_attachment:
            logger.warning("no_valid_image_attachment")
            return UNSUPPORTED_MEDIA_RESPONSE

        # Check file size
        if image_attachment.size > settings.max_attachment_size_bytes:
            logger.warning(
                "image_too_large",
                size=image_attachment.size,
                max=settings.max_attachment_size_bytes,
            )
            return (
                f"That image is a bit large for me to process (over {settings.max_attachment_size_mb}MB). "
                "Could you send a smaller version? 📸"
            )

        logger.info(
            "handling_photo",
            mime_type=image_attachment.mime_type,
            size=image_attachment.size,
        )

        try:
            # Download the image from BlueBubbles
            image_data = await self.bridge_client.download_attachment(image_attachment.guid)

            # Analyze with vision LLM
            context = payload.text.strip() if payload.text else ""
            analysis = await self.llm_client.analyze_image(
                image_data=image_data,
                mime_type=image_attachment.mime_type or "image/jpeg",
                context=context,
            )

            logger.info("photo_response_generated", response_len=len(analysis))
            return analysis

        except Exception:
            logger.exception("photo_processing_error")
            return (
                "I had trouble analyzing that image. "
                "Could you try sending it again, or describe what you wanted me to look at? 🧐"
            )

    async def _handle_internal(self, msg: InternalMessage) -> str:
        """Process an InternalMessage (Telegram path) containing a photo.

        The attachment bytes must already be cached in the bridge client
        before this method is called.

        Args:
            msg: Normalised internal message with photo attachment.

        Returns:
            Generated analysis / advice text.
        """
        if msg.attachment is None:
            return UNSUPPORTED_MEDIA_RESPONSE

        att = msg.attachment

        # File size check
        if att.file_size > settings.max_attachment_size_bytes:
            logger.warning(
                "image_too_large",
                size=att.file_size,
                max=settings.max_attachment_size_bytes,
            )
            return (
                f"That image is a bit large for me to process (over {settings.max_attachment_size_mb}MB). "
                "Could you send a smaller version? 📸"
            )

        logger.info("handling_photo_internal", size=att.file_size)

        try:
            image_data = await self.bridge_client.download_attachment(att.file_id)
            context = msg.text.strip() if msg.text else ""
            analysis = await self.llm_client.analyze_image(
                image_data=image_data,
                mime_type=att.mime_type or "image/jpeg",
                context=context,
            )
            logger.info("photo_response_generated", response_len=len(analysis))
            return analysis
        except KeyError:
            logger.warning("photo_attachment_not_cached", file_id=att.file_id)
            return "I couldn't find that photo. Could you send it again? 📸"
        except Exception:
            logger.exception("photo_processing_error")
            return (
                "I had trouble analyzing that image. "
                "Could you try sending it again, or describe what you wanted me to look at? 🧐"
            )
