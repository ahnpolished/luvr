"""Photo/image message handler - processes images via vision LLM for dating advice."""

from __future__ import annotations

import structlog

from src.bridge.client import BlueBubblesClient
from src.bridge.models import WebhookPayload
from src.config import settings
from src.llm.client import LLMClient
from src.llm.prompts import UNSUPPORTED_MEDIA_RESPONSE

logger = structlog.get_logger(__name__)

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/heic", "image/webp", "image/gif"}


class PhotoHandler:
    """Handles photo/image iMessages by analyzing them with vision LLM."""

    def __init__(self, bridge_client: BlueBubblesClient, llm_client: LLMClient) -> None:
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
            return "I had trouble analyzing that image. Could you try sending it again, or describe what you wanted me to look at? 🧐"
