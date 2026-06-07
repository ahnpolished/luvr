"""Centralized configuration using pydantic-settings.

All environment variables are loaded from .env file and validated on startup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Luvr application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Server ---
    host: str = "::"
    port: int = 8000
    debug: bool = False

    # --- BlueBubbles iMessage Bridge ---
    bluebubbles_server_url: str = "http://localhost:1234"
    bluebubbles_password: str = ""
    skip_own_messages: bool = True

    # --- Telegram Bot ---
    telegram_bot_token: str = ""
    telegram_mode: Literal["polling", "webhook"] = "polling"
    telegram_webhook_url: str | None = None
    telegram_allowed_user_ids: str = ""  # comma-separated list of allowed user IDs

    @property
    def telegram_allowed_user_id_list(self) -> list[int]:
        """Parse the comma-separated user IDs string into a list of ints."""
        raw = self.telegram_allowed_user_ids
        if not raw or not raw.strip():
            return []
        try:
            return [int(uid.strip()) for uid in raw.split(",") if uid.strip()]
        except ValueError:
            return []

    # --- LLM ---
    llm_provider: Literal["openai", "anthropic", "deepseek", "opencode"] = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    deepseek_api_key: str | None = None
    opencode_api_key: str | None = None
    opencode_base_url: str = "http://localhost:54321"
    opencode_provider_id: str = "deepseek"
    llm_model: str = "gpt-4o-mini"

    # --- Media ---
    max_attachment_size_mb: int = 25
    whisper_model: str = "whisper-1"

    # --- Rate Limiting ---
    max_messages_per_minute: int = 10
    max_messages_per_hour: int = 50

    # --- Platform ---
    platform: Literal["imessage", "telegram"] = "imessage"

    # --- Logging ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["console", "json"] = "console"

    # --- Paths ---
    @property
    def temp_dir(self) -> Path:
        """Directory for temporary media files."""
        path = Path("tmp")
        path.mkdir(exist_ok=True)
        return path

    @property
    def max_attachment_size_bytes(self) -> int:
        """Max attachment size in bytes."""
        return self.max_attachment_size_mb * 1024 * 1024


# Singleton settings instance
settings = Settings()
