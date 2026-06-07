"""OpenAI LLM client implementation (gpt-4o-mini)."""

from __future__ import annotations

import base64

import structlog
from openai import APIError, AsyncOpenAI

from src.llm.client import LLMClient, LLMAPIError, LLMContentFilterError
from src.llm.prompts import DATING_ADVISOR_SYSTEM_PROMPT, PHOTO_ANALYSIS_PROMPT

logger = structlog.get_logger(__name__)


class OpenAIClient(LLMClient):
    """LLM client using OpenAI's API (gpt-4o-mini with vision)."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", base_url: str | None = None) -> None:
        self.model = model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        image_data: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        """Generate a text response from OpenAI."""
        messages: list[dict[str, object]] = [
            {"role": "system", "content": system_prompt or DATING_ADVISOR_SYSTEM_PROMPT},
        ]

        if image_data and image_mime_type:
            # Build multimodal message with image
            base64_image = base64.b64encode(image_data).decode("utf-8")
            data_uri = f"data:{image_mime_type};base64,{base64_image}"

            messages.append({
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri, "detail": "auto"}},
                    {"type": "text", "text": user_message or PHOTO_ANALYSIS_PROMPT},
                ],
            })
        else:
            messages.append({"role": "user", "content": user_message})

        logger.debug("openai_request", model=self.model, msg_len=len(user_message))

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=600,
                temperature=0.85,
            )

            content = response.choices[0].message.content or ""
            logger.info(
                "openai_response",
                model=self.model,
                tokens=response.usage.total_tokens if response.usage else 0,
            )
            return content.strip()

        except APIError as e:
            if "content_filter" in str(e).lower() or "content_policy" in str(e).lower():
                logger.warning("openai_content_filtered")
                raise LLMContentFilterError(
                    "Your message was flagged by safety filters. "
                    "Try rephrasing or focusing on the dating advice aspect."
                ) from e
            logger.exception("openai_api_error")
            raise LLMAPIError(f"OpenAI API error: {e}") from e

    async def analyze_image(self, image_data: bytes, mime_type: str, context: str = "") -> str:
        """Analyze an image using GPT-4V and return dating advice."""
        base64_image = base64.b64encode(image_data).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{base64_image}"

        user_text = context if context else PHOTO_ANALYSIS_PROMPT

        messages: list[dict[str, object]] = [
            {"role": "system", "content": DATING_ADVISOR_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri, "detail": "auto"}},
                    {"type": "text", "text": user_text},
                ],
            },
        ]

        logger.debug("openai_vision_request", model=self.model, mime_type=mime_type)

        try:
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=600,
                temperature=0.85,
            )
            content = response.choices[0].message.content or ""
            return content.strip()

        except APIError as e:
            logger.exception("openai_vision_error")
            raise LLMAPIError(f"OpenAI Vision error: {e}") from e
