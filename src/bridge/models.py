"""Pydantic models for BlueBubbles iMessage bridge data types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class Attachment(BaseModel):
    """An attachment in an iMessage."""

    guid: str = ""
    uri: str | None = None
    path: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")
    size: int = 0
    transfer_state: int = Field(default=0, alias="transferState")


class WebhookPayload(BaseModel):
    """Incoming message webhook payload from BlueBubbles.

    BlueBubbles may send ``null`` for any absent string field, so we coerce
    None → "" in a before-validator to keep the rest of the code simple.

    BlueBubbles v1.9.9 nests the chat GUID inside a ``chats`` array rather
    than a top-level ``chatGuid`` field, and uses ``handle`` instead of
    ``sender``.  The before-validator normalises both shapes.
    """

    chat_guid: str = Field(default="", alias="chatGuid")
    text: str = ""
    subject: str = ""
    sender: str = ""
    is_from_me: bool = Field(default=False, alias="isFromMe")
    attachments: list[Attachment] = []
    group_chat_name: str | None = Field(default=None, alias="groupChatName")

    @model_validator(mode="before")
    @classmethod
    def _normalise_bluebubbles_payload(cls, data: Any) -> Any:
        """Normalise BlueBubbles webhook payloads into the shape we expect.

        - v1.9.9 nests chat GUIDs inside ``chats[0].guid`` → promote to ``chatGuid``.
        - v1.9.9 uses ``handle`` for the sender phone number → map to ``sender``.
        - Coerce ``None`` string fields to ``""``.
        """
        if not isinstance(data, dict):
            return data

        # --- chatGuid from chats array (BlueBubbles v1.9.9+) ---
        if not data.get("chatGuid") and data.get("chats"):
            chats = data["chats"]
            if isinstance(chats, list) and len(chats) > 0:
                first_chat = chats[0]
                if isinstance(first_chat, dict) and first_chat.get("guid"):
                    data["chatGuid"] = first_chat["guid"]

        # --- sender from handle (BlueBubbles v1.9.9+) ---
        # BlueBubbles v1.9.9 sends ``handle`` as a dict like
        # {"address": "+15551234567", "country": "US", ...}.
        if not data.get("sender") and data.get("handle"):
            handle = data["handle"]
            if isinstance(handle, dict):
                data["sender"] = handle.get("address", "")
            elif isinstance(handle, str):
                data["sender"] = handle

        # --- None → "" for string fields ---
        for field_name in ("text", "subject", "sender", "groupChatName"):
            if data.get(field_name) is None:
                data[field_name] = ""

        return data

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
