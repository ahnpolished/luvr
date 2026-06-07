"""Anthropic (Claude) LLM client implementation (claude-3-haiku)."""

from __future__ import annotations

import base64

import structlog
from anthropic import APIError, AsyncAnthropic

from src.llm.client import LLMAPIError, LLMClient, LLMContentFilterError
from src.llm.prompts import DATING_ADVISOR_SYSTEM_PROMPT, PHOTO_ANALYSIS_PROMPT

logger = structlog.get_logger(__name__)


class AnthropicClient(LLMClient):
    """LLM client using Anthropic's Claude API (claude-3-haiku with vision)."""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307") -> None:
        self.model = model
        self._client = AsyncAnthropic(api_key=api_key)

    async def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        image_data: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        """Generate a text response from Claude."""
        system = system_prompt or DATING_ADVISOR_SYSTEM_PROMPT

        content: list[dict[str, object]] = []
        if image_data and image_mime_type:
            base64_image = base64.b64encode(image_data).decode("utf-8")
            media_type = image_mime_type

            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_image,
                },
            })

        content.append({"type": "text", "text": user_message or PHOTO_ANALYSIS_PROMPT})

        logger.debug("anthropic_request", model=self.model, msg_len=len(user_message))

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=600,
                system=system,
                messages=[{"role": "user", "content": content}],  # type: ignore[typeddict-item]
                temperature=0.85,
            )

            # Extract text from response
            text_blocks = [b.text for b in response.content if b.type == "text"]
            result = " ".join(text_blocks).strip()

            logger.info(
                "anthropic_response",
                model=self.model,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
            )
            return result

        except APIError as e:
            if "safety" in str(e).lower() or "content" in str(e).lower():
                logger.warning("anthropic_content_filtered")
                raise LLMContentFilterError(
                    "Your message was flagged by safety filters. "
                    "Try rephrasing or focusing on the dating advice aspect."
                ) from e
            logger.exception("anthropic_api_error")
            raise LLMAPIError(f"Anthropic API error: {e}") from e

    async def analyze_image(self, image_data: bytes, mime_type: str, context: str = "") -> str:
        """Analyze an image using Claude Vision and return dating advice."""
        base64_image = base64.b64encode(image_data).decode("utf-8")

        content: list[dict[str, object]] = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64_image,
                },
            },
            {"type": "text", "text": context or PHOTO_ANALYSIS_PROMPT},
        ]

        logger.debug("anthropic_vision_request", model=self.model, mime_type=mime_type)

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=600,
                system=DATING_ADVISOR_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": content}],  # type: ignore[typeddict-item]
                temperature=0.85,
            )

            text_blocks = [b.text for b in response.content if b.type == "text"]
            return " ".join(text_blocks).strip()

        except APIError as e:
            logger.exception("anthropic_vision_error")
            raise LLMAPIError(f"Anthropic Vision error: {e}") from e
