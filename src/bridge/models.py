"""Pydantic models for BlueBubbles iMessage bridge data types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Attachment(BaseModel):
    """An attachment in an iMessage."""

    guid: str = ""
    uri: str | None = None
    path: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")
    size: int = 0
    transfer_state: int = Field(default=0, alias="transferState")


class WebhookPayload(BaseModel):
    """Incoming message webhook payload from BlueBubbles."""

    chat_guid: str = Field(default="", alias="chatGuid")
    text: str = ""
    subject: str = ""
    sender: str = ""
    is_from_me: bool = Field(default=False, alias="isFromMe")
    attachments: list[Attachment] = []
    group_chat_name: str | None = Field(default=None, alias="groupChatName")

    @property
    def has_images(self) -> bool:
        """Check if message contains image attachments."""
        image_types = {"image/jpeg", "image/png", "image/heic", "image/webp", "image/gif"}
        return any(a.mime_type in image_types for a in self.attachments)

    @property
    def has_audio(self) -> bool:
        """Check if message contains audio attachments."""
        audio_types = {
            "audio/x-caf",
            "audio/mp4",
            "audio/mpeg",
            "audio/wav",
            "audio/aac",
            "audio/x-m4a",
        }
        return any(a.mime_type in audio_types for a in self.attachments)

    @property
    def message_type(self) -> str:
        """Determine the primary message type."""
        if self.has_images:
            return "photo"
        if self.has_audio:
            return "voice"
        return "text"


class SendMessageRequest(BaseModel):
    """Request to send a message via BlueBubbles."""

    chat_guid: str
    message: str
    method: str = "apple-script"
    subject: str = ""


class SendMessageResponse(BaseModel):
    """Response from BlueBubbles send message API."""

    status: int = 0
    message: str = ""
    data: dict[str, Any] = {}
