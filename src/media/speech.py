"""Text-to-speech synthesis using OpenAI TTS API.

Converts LLM text responses to spoken audio so the bot can reply with
voice memos, enabling full voice memo conversations.
"""

from __future__ import annotations

import structlog
from openai import OpenAI

from src.config import settings

logger = structlog.get_logger(__name__)


def text_to_speech(text: str) -> bytes:
    """Convert text to speech audio using OpenAI TTS.

    Uses the configured TTS model and voice. Returns raw audio bytes
    in the format specified by the model (typically opus/ogg for
    ``tts-1`` / ``tts-1-hd``).

    Args:
        text: The text to convert to speech (max 4096 chars by OpenAI).

    Returns:
        Raw audio bytes suitable for sending as a voice message.

    Raises:
        ValueError: If ``OPENAI_API_KEY`` is not configured.
        RuntimeError: If the TTS API call fails.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for TTS synthesis")

    # OpenAI TTS has a 4096 char input limit
    if len(text) > 4096:
        text = text[:4090] + "..."

    logger.info(
        "synthesizing_speech",
        text_len=len(text),
        model=settings.tts_model,
        voice=settings.tts_voice,
    )

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.audio.speech.create(
            model=settings.tts_model,
            voice=settings.tts_voice,
            input=text,
            response_format="opus",  # Telegram prefers opus/ogg
        )

        audio_bytes: bytes = response.content
        logger.info("speech_synthesized", audio_size=len(audio_bytes))
        return audio_bytes

    except Exception as e:
        logger.exception("speech_synthesis_failed", text_len=len(text))
        raise RuntimeError(f"TTS synthesis failed: {e}") from e
