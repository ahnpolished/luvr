"""Tests for media processing (vision, transcription, and speech synthesis)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.media.transcription import transcribe_audio_bytes


def test_transcribe_audio_bytes_no_api_key():
    """Test that transcription requires API key."""
    with patch("src.media.transcription.settings") as mock_settings:
        mock_settings.openai_api_key = None
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            transcribe_audio_bytes(b"fake audio data")


# ---------------------------------------------------------------------------
# Speech synthesis (TTS)
# ---------------------------------------------------------------------------


def test_text_to_speech_no_api_key():
    """Test that TTS requires an API key."""
    from src.media.speech import text_to_speech

    with patch("src.media.speech.settings") as mock_settings:
        mock_settings.openai_api_key = None
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            text_to_speech("Hello world")


def test_text_to_speech_returns_bytes():
    """Test that TTS returns audio bytes when API call succeeds."""
    from src.media.speech import text_to_speech

    with (
        patch("src.media.speech.settings") as mock_settings,
        patch("src.media.speech.OpenAI") as mock_openai_cls,
    ):
        mock_settings.openai_api_key = "sk-test"
        mock_settings.tts_model = "tts-1"
        mock_settings.tts_voice = "nova"

        mock_client = mock_openai_cls.return_value
        mock_response = mock_client.audio.speech.create.return_value
        mock_response.content = b"fake-opus-audio"

        result = text_to_speech("Hello, this is a test.")

        assert result == b"fake-opus-audio"
        mock_client.audio.speech.create.assert_called_once_with(
            model="tts-1",
            voice="nova",
            input="Hello, this is a test.",
            response_format="opus",
        )


def test_text_to_speech_truncates_long_text():
    """Test that text over 4096 chars is truncated before TTS."""
    from src.media.speech import text_to_speech

    with (
        patch("src.media.speech.settings") as mock_settings,
        patch("src.media.speech.OpenAI") as mock_openai_cls,
    ):
        mock_settings.openai_api_key = "sk-test"
        mock_settings.tts_model = "tts-1"
        mock_settings.tts_voice = "nova"

        mock_client = mock_openai_cls.return_value
        mock_response = mock_client.audio.speech.create.return_value
        mock_response.content = b"audio"

        long_text = "x" * 5000
        text_to_speech(long_text)

        sent_input = mock_client.audio.speech.create.call_args[1]["input"]
        assert len(sent_input) <= 4096
        assert sent_input.endswith("...")


def test_text_to_speech_api_error():
    """Test that TTS API errors are wrapped in RuntimeError."""
    from src.media.speech import text_to_speech

    with (
        patch("src.media.speech.settings") as mock_settings,
        patch("src.media.speech.OpenAI") as mock_openai_cls,
    ):
        mock_settings.openai_api_key = "sk-test"
        mock_settings.tts_model = "tts-1"
        mock_settings.tts_voice = "nova"

        mock_client = mock_openai_cls.return_value
        mock_client.audio.speech.create.side_effect = Exception("API error")

        with pytest.raises(RuntimeError, match="TTS synthesis failed"):
            text_to_speech("Hello")


def test_transcribe_audio_bytes_file_not_found():
    """Test error handling for missing file."""
    from src.media.transcription import transcribe_audio

    with patch("src.media.transcription.settings") as mock_settings:
        mock_settings.openai_api_key = "sk-test-key"
        with pytest.raises(FileNotFoundError):
            transcribe_audio("/nonexistent/path/audio.caf")
