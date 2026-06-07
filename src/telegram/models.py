"""Pydantic models for Telegram message representation.

These models provide an internal message representation that decouples
the Telegram-specific ``Update``/``Message`` types from the existing handler
pipeline, allowing the same LLM handlers to process Telegram messages.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TelegramMessageType(str, Enum):
    """Type of a Telegram message as relevant to Luvr's processing pipeline."""

    TEXT = "text"
    PHOTO = "photo"
    VOICE = "voice"
    UNKNOWN = "unknown"


class TelegramAttachment(BaseModel):
    """Represents a media attachment from a Telegram message."""

    file_id: str = ""
    mime_type: str = ""
    file_size: int = 0
    # Raw bytes populated after download
    data: bytes = Field(default=b"", exclude=True)


class InternalMessage(BaseModel):
    """Normalised internal message format.

    All Telegram message types (text / photo / voice) are converted into
    this representation before being dispatched to the existing handler
    pipeline.
    """

    chat_id: int
    message_type: TelegramMessageType = TelegramMessageType.TEXT
    text: str = ""
    attachment: TelegramAttachment | None = None
