"""Abstract LLM client interface with factory for provider selection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal

import structlog

from src.config import settings

logger = structlog.get_logger(__name__)

LLMProvider = Literal["openai", "anthropic", "deepseek", "opencode"]


class LLMClient(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_response(
        self,
        user_message: str,
        system_prompt: str | None = None,
        image_data: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            user_message: The user's message text
            system_prompt: Optional system prompt override
            image_data: Optional raw image bytes for vision analysis
            image_mime_type: MIME type of the image (required if image_data provided)

        Returns:
            Generated text response

        Raises:
            LLMError: If the API call fails
        """
        ...

    @abstractmethod
    async def analyze_image(self, image_data: bytes, mime_type: str, context: str = "") -> str:
        """Analyze an image and return a description/advice.

        Args:
            image_data: Raw image bytes
            mime_type: Image MIME type (e.g., image/jpeg)
            context: Optional user-provided context about what they want to know

        Returns:
            Analysis and advice based on the image
        """
        ...


class LLMError(Exception):
    """Base exception for LLM-related errors."""

    pass


class LLMAPIError(LLMError):
    """Error from the LLM provider's API."""

    pass


class LLMContentFilterError(LLMError):
    """Content was filtered by the provider's safety systems."""

    pass


def create_llm_client(provider: LLMProvider | None = None) -> LLMClient:
    """Factory function to create the appropriate LLM client based on settings.

    Args:
        provider: Override the configured provider. If None, uses settings.llm_provider.

    Returns:
        An LLMClient implementation

    Raises:
        ValueError: If the provider is not supported or API key is missing
    """
    provider = provider or settings.llm_provider

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when using OpenAI. "
                "Set it in your .env file or environment."
            )
        from src.llm.openai_client import OpenAIClient

        logger.info("llm_client_created", provider="openai", model=settings.llm_model)
        return OpenAIClient(api_key=settings.openai_api_key, model=settings.llm_model)

    elif provider == "deepseek":
        if not settings.deepseek_api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is required when using DeepSeek. "
                "Set it in your .env file or environment."
            )
        from src.llm.openai_client import OpenAIClient

        logger.info("llm_client_created", provider="deepseek", model=settings.llm_model)
        return OpenAIClient(
            api_key=settings.deepseek_api_key,
            model=settings.llm_model,
            base_url="https://api.deepseek.com",
        )

    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when using Anthropic. "
                "Set it in your .env file or environment."
            )
        from src.llm.anthropic_client import AnthropicClient

        logger.info("llm_client_created", provider="anthropic", model=settings.llm_model)
        return AnthropicClient(api_key=settings.anthropic_api_key, model=settings.llm_model)

    elif provider == "opencode":
        from src.llm.opencode_client import OpenCodeClient

        logger.info(
            "llm_client_created",
            provider="opencode",
            model=settings.llm_model,
            opencode_provider=settings.opencode_provider_id,
        )
        return OpenCodeClient(
            model_id=settings.llm_model,
            provider_id=settings.opencode_provider_id,
            base_url=settings.opencode_base_url,
            api_key=settings.opencode_api_key,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
