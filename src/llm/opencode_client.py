"""OpenCode LLM client using the opencode-ai SDK."""

from __future__ import annotations

import structlog
from opencode_ai import AsyncOpencode

from src.llm.client import LLMAPIError, LLMClient
from src.llm.prompts import DATING_ADVISOR_SYSTEM_PROMPT

logger = structlog.get_logger(__name__)


class OpenCodeClient(LLMClient):
    """LLM client backed by a locally running OpenCode server."""

    def __init__(
        self,
        model_id: str,
        provider_id: str,
        base_url: str = "http://localhost:54321",
        api_key: str | None = None,
    ) -> None:
        self.model_id = model_id
        self.provider_id = provider_id
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
        self._client = AsyncOpencode(base_url=base_url, default_headers=headers)

    async def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        image_data: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        session = await self._client.session.create(extra_body={})
        try:
            await self._client.session.chat(
                session.id,
                model_id=self.model_id,
                provider_id=self.provider_id,
                parts=[{"type": "text", "text": user_message}],
                system=system_prompt or DATING_ADVISOR_SYSTEM_PROMPT,
            )
            messages = await self._client.session.messages(session.id)
            for item in reversed(messages):
                if item.info.role == "assistant":
                    text = " ".join(
                        part.text for part in item.parts if hasattr(part, "text")
                    )
                    if text:
                        return text.strip()
            return ""
        except LLMAPIError:
            raise
        except Exception as e:
            logger.exception("opencode_api_error")
            raise LLMAPIError(f"OpenCode API error: {e}") from e
        finally:
            try:
                await self._client.session.delete(session.id)
            except Exception:
                pass

    async def analyze_image(self, image_data: bytes, mime_type: str, context: str = "") -> str:
        raise LLMAPIError("Image analysis is not supported for the OpenCode provider.")
