"""Tests for media processing (vision and transcription)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from src.media.transcription import transcribe_audio_bytes


def test_transcribe_audio_bytes_no_api_key():
    """Test that transcription requires API key."""
    with patch("src.media.transcription.settings") as mock_settings:
        mock_settings.openai_api_key = None
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            transcribe_audio_bytes(b"fake audio data")


def test_transcribe_audio_bytes_file_not_found():
    """Test error handling for missing file."""
    from src.media.transcription import transcribe_audio

    with patch("src.media.transcription.settings") as mock_settings:
        mock_settings.openai_api_key = "sk-test-key"
        with pytest.raises(FileNotFoundError):
            transcribe_audio("/nonexistent/path/audio.caf")
