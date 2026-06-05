"""Voice memo / audio message handler - transcribes audio then generates dating advice."""

from __future__ import annotations

import structlog

from src.bridge.client import BlueBubblesClient
from src.bridge.models import WebhookPayload
from src.config import settings
from src.llm.client import LLMClient
from src.llm.prompts import UNSUPPORTED_MEDIA_RESPONSE, VOICE_MEMO_SYSTEM_EXTRA
from src.media.transcription import transcribe_audio

logger = structlog.get_logger(__name__)

SUPPORTED_AUDIO_TYPES = {
    "audio/x-caf",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
    "audio/aac",
    "audio/x-m4a",
    "audio/m4a",
}


class VoiceHandler:
    """Handles voice memo/audio iMessages by transcribing them and generating advice."""

    def __init__(self, bridge_client: BlueBubblesClient, llm_client: LLMClient) -> None:
        self.bridge_client = bridge_client
        self.llm_client = llm_client

    async def handle(self, payload: WebhookPayload) -> str:
        """Process a voice memo and generate dating advice.

        Flow:
        1. Download audio from BlueBubbles
        2. Transcribe using Whisper
        3. Feed transcription to LLM with modified system prompt

        Args:
            payload: Parsed webhook payload with audio attachments

        Returns:
            Generated response text based on transcribed audio
        """
        # Find the first audio attachment
        audio_attachment = None
        for att in payload.attachments:
            if att.mime_type in SUPPORTED_AUDIO_TYPES:
                audio_attachment = att
                break

        if not audio_attachment:
            logger.warning("no_valid_audio_attachment")
            return UNSUPPORTED_MEDIA_RESPONSE

        # Check file size
        if audio_attachment.size > settings.max_attachment_size_bytes:
            logger.warning(
                "audio_too_large",
                size=audio_attachment.size,
                max=settings.max_attachment_size_bytes,
            )
            return (
                f"That voice memo is a bit long for me to process (over {settings.max_attachment_size_mb}MB). "
                "Could you send a shorter one? 🎤"
            )

        logger.info(
            "handling_voice",
            mime_type=audio_attachment.mime_type,
            size=audio_attachment.size,
        )

        try:
            # Download the audio from BlueBubbles
            audio_data = await self.bridge_client.download_attachment(audio_attachment.guid)

            # Save to temp file for Whisper (Whisper API needs file path or bytes)
            import tempfile

            suffix = ".caf"  # Default for iMessage voice memos
            if audio_attachment.mime_type:
                suffix_map = {
                    "audio/mp4": ".m4a",
                    "audio/mpeg": ".mp3",
                    "audio/wav": ".wav",
                    "audio/aac": ".aac",
                    "audio/x-m4a": ".m4a",
                    "audio/m4a": ".m4a",
                }
                suffix = suffix_map.get(audio_attachment.mime_type, ".caf")

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            # Transcribe using Whisper
            transcription = transcribe_audio(tmp_path)

            # Clean up temp file
            import os

            os.unlink(tmp_path)

            if not transcription.strip():
                return (
                    "I couldn't make out what you said in that voice memo. "
                    "Could you try again, or type it out? 🎤"
                )

            logger.info("voice_transcribed", transcription_len=len(transcription))

            # Feed transcription to LLM for advice
            response = await self.llm_client.generate_response(
                user_message=transcription,
                system_prompt=f"{VOICE_MEMO_SYSTEM_EXTRA}\n\nTranscribed voice memo: {transcription}",
            )

            logger.info("voice_response_generated", response_len=len(response))
            return response

        except Exception:
            logger.exception("voice_processing_error")
            return "I had trouble processing that voice memo. Could you try again or type it out instead? 🎤"
