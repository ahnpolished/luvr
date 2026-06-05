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
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # --- BlueBubbles iMessage Bridge ---
    bluebubbles_server_url: str = "http://localhost:1234"
    bluebubbles_password: str = ""

    # --- LLM ---
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"

    # --- Media ---
    max_attachment_size_mb: int = 25
    whisper_model: str = "whisper-1"

    # --- Rate Limiting ---
    max_messages_per_minute: int = 10
    max_messages_per_hour: int = 50

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
