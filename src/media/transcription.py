"""Audio transcription using OpenAI Whisper.

Transcribes voice memos and audio messages to text for LLM processing.
Uses OpenAI's Whisper API for high-quality transcription.
"""

from __future__ import annotations

from pathlib import Path

import structlog
from openai import OpenAI

from src.config import settings

logger = structlog.get_logger(__name__)


def transcribe_audio(audio_path: str | Path) -> str:
    """Transcribe an audio file to text using OpenAI Whisper.

    Args:
        audio_path: Path to the audio file (supports caf, m4a, mp3, wav, etc.)

    Returns:
        Transcribed text

    Raises:
        ValueError: If OpenAI API key is not configured
        FileNotFoundError: If the audio file doesn't exist
        RuntimeError: If transcription fails
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for Whisper transcription")

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info("transcribing_audio", path=str(audio_path), size=audio_path.stat().st_size)

    client = OpenAI(api_key=settings.openai_api_key)

    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=audio_file,
                response_format="text",
                language="en",  # Can make configurable later for multilingual support
            )

        # The API returns the transcription text directly when response_format="text"
        result = str(transcript).strip()

        logger.info("transcription_complete", text_len=len(result))
        return result

    except Exception as e:
        logger.exception("transcription_failed", path=str(audio_path))
        raise RuntimeError(f"Audio transcription failed: {e}") from e


def transcribe_audio_bytes(audio_data: bytes, suffix: str = ".caf") -> str:
    """Transcribe audio from raw bytes (writes to temp file first).

    Args:
        audio_data: Raw audio bytes
        suffix: File extension for temp file (default .caf for iMessage voice memos)

    Returns:
        Transcribed text
    """
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name

    try:
        return transcribe_audio(tmp_path)
    finally:
        import os

        os.unlink(tmp_path)
