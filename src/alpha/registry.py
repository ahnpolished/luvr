"""Minimal v0.1.0 alpha user profile registry.

This registry stores operational alpha profile/linking metadata only. It is not
product memory: conversation content and long-term memory retrieval are out of
scope for v0.1.0.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field


class UsageLimitResult(BaseModel):
    """Result of checking an alpha feature usage limit."""

    allowed: bool
    remaining: int


class AlphaUserProfile(BaseModel):
    """Operational alpha profile used for linking, labels, and quota checks."""

    user_id: str
    telegram_user_id: int | None = None
    telegram_chat_id: int | None = None
    telegram_username: str | None = None
    display_name: str | None = None
    nickname: str | None = None
    email: str | None = None
    auth_completed: bool = False
    onboarding_completed: bool = False
    allowlisted: bool = False
    usage_counters: dict[str, int] = Field(default_factory=dict)
    instagram_context_summary: str | None = None


class _RegistryState(BaseModel):
    """Serialized registry state."""

    profiles: dict[str, AlphaUserProfile] = Field(default_factory=dict)


class AlphaUserRegistry:
    """Lookup and update alpha profiles by internal or Telegram identifiers."""

    def __init__(
        self,
        storage_path: Path | None = None,
        allowlisted_telegram_user_ids: set[int] | None = None,
    ) -> None:
        self.storage_path = storage_path
        self._allowlisted_telegram_user_ids = allowlisted_telegram_user_ids or set()
        self._state = self._load_state()

    def get_or_create_for_telegram(
        self,
        *,
        telegram_user_id: int,
        telegram_chat_id: int,
        telegram_username: str | None = None,
        display_name: str | None = None,
    ) -> AlphaUserProfile:
        """Return the alpha profile linked to Telegram IDs, creating it if needed."""
        profile = self.find_by_telegram(telegram_user_id=telegram_user_id, telegram_chat_id=telegram_chat_id)
        if profile is None:
            profile = AlphaUserProfile(
                user_id=f"alpha_{uuid4().hex[:12]}",
                telegram_user_id=telegram_user_id,
                telegram_chat_id=telegram_chat_id,
            )

        return self.link_telegram(
            profile.user_id,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            telegram_username=telegram_username,
            display_name=display_name,
        )

    def link_telegram(
        self,
        user_id: str,
        *,
        telegram_user_id: int,
        telegram_chat_id: int,
        telegram_username: str | None = None,
        display_name: str | None = None,
    ) -> AlphaUserProfile:
        """Link or relink a profile to Telegram identifiers."""
        profile = self._state.profiles.get(user_id) or AlphaUserProfile(user_id=user_id)
        profile.telegram_user_id = telegram_user_id
        profile.telegram_chat_id = telegram_chat_id
        profile.allowlisted = self.is_allowlisted(telegram_user_id=telegram_user_id)
        if telegram_username is not None:
            profile.telegram_username = telegram_username
        if display_name is not None:
            profile.display_name = display_name
        self._state.profiles[user_id] = profile
        self._save_state()
        return profile

    def find_by_telegram(
        self,
        *,
        telegram_user_id: int | None = None,
        telegram_chat_id: int | None = None,
    ) -> AlphaUserProfile | None:
        """Find a profile by Telegram user ID and/or chat ID."""
        for profile in self._state.profiles.values():
            if telegram_user_id is not None and profile.telegram_user_id == telegram_user_id:
                return profile
            if telegram_chat_id is not None and profile.telegram_chat_id == telegram_chat_id:
                return profile
        return None

    def get_profile(self, user_id: str) -> AlphaUserProfile:
        """Return a profile by internal alpha user ID."""
        return self._state.profiles[user_id]

    def update_profile(
        self,
        user_id: str,
        *,
        auth_completed: bool | None = None,
        onboarding_completed: bool | None = None,
        telegram_username: str | None = None,
        display_name: str | None = None,
        nickname: str | None = None,
        email: str | None = None,
        instagram_context_summary: str | None = None,
    ) -> AlphaUserProfile:
        """Update intentionally provided alpha profile fields."""
        profile = self.get_profile(user_id)
        if auth_completed is not None:
            profile.auth_completed = auth_completed
        if onboarding_completed is not None:
            profile.onboarding_completed = onboarding_completed
        if telegram_username is not None:
            profile.telegram_username = telegram_username
        if display_name is not None:
            profile.display_name = display_name
        if nickname is not None:
            profile.nickname = nickname
        if email is not None:
            profile.email = email
        if instagram_context_summary is not None:
            profile.instagram_context_summary = instagram_context_summary
        self._state.profiles[user_id] = profile
        self._save_state()
        return profile

    def has_completed_auth(self, *, telegram_user_id: int) -> bool:
        """Return whether a Telegram user has completed web auth."""
        profile = self.find_by_telegram(telegram_user_id=telegram_user_id)
        return bool(profile and profile.auth_completed)

    def has_completed_onboarding(self, *, telegram_user_id: int) -> bool:
        """Return whether a Telegram user has completed onboarding."""
        profile = self.find_by_telegram(telegram_user_id=telegram_user_id)
        return bool(profile and profile.onboarding_completed)

    def is_allowlisted(self, *, telegram_user_id: int) -> bool:
        """Return whether a Telegram user is allowlisted for alpha access."""
        if telegram_user_id in self._allowlisted_telegram_user_ids:
            return True
        profile = self.find_by_telegram(telegram_user_id=telegram_user_id)
        return bool(profile and profile.allowlisted)

    def set_allowlisted(self, user_id: str, *, allowlisted: bool) -> AlphaUserProfile:
        """Persist an explicit allowlist decision on a profile."""
        profile = self.get_profile(user_id)
        profile.allowlisted = allowlisted
        self._state.profiles[user_id] = profile
        self._save_state()
        return profile

    def weave_labels_for_telegram(self, *, telegram_user_id: int) -> dict[str, str]:
        """Return Weave trace labels for a linked Telegram user."""
        profile = self.find_by_telegram(telegram_user_id=telegram_user_id)
        if profile is None:
            return {}

        labels = {
            "user_id": profile.user_id,
            "telegram_user_id": str(profile.telegram_user_id),
            "telegram_chat_id": str(profile.telegram_chat_id),
            "auth_completed": str(profile.auth_completed).lower(),
            "onboarding_completed": str(profile.onboarding_completed).lower(),
            "allowlisted": str(self.is_allowlisted(telegram_user_id=telegram_user_id)).lower(),
        }
        optional_labels = {
            "telegram_username": profile.telegram_username,
            "display_name": profile.display_name,
            "nickname": profile.nickname,
            "email": profile.email,
        }
        labels.update({key: value for key, value in optional_labels.items() if value is not None})
        return labels

    def check_limit(self, user_id: str, feature: str, *, limit: int) -> UsageLimitResult:
        """Check whether a profile can use a limited alpha feature."""
        profile = self.get_profile(user_id)
        used = profile.usage_counters.get(feature, 0)
        remaining = max(limit - used, 0)
        return UsageLimitResult(allowed=used < limit, remaining=remaining)

    def increment_usage(self, user_id: str, feature: str, *, amount: int = 1) -> AlphaUserProfile:
        """Increment a feature usage counter after successful processing."""
        profile = self.get_profile(user_id)
        profile.usage_counters[feature] = profile.usage_counters.get(feature, 0) + amount
        self._state.profiles[user_id] = profile
        self._save_state()
        return profile

    def _load_state(self) -> _RegistryState:
        if self.storage_path is None or not self.storage_path.exists():
            return _RegistryState()
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        return _RegistryState.model_validate(raw)

    def _save_state(self) -> None:
        if self.storage_path is None:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.storage_path.with_suffix(f"{self.storage_path.suffix}.tmp")
        tmp_path.write_text(
            json.dumps(self._state.model_dump(mode="json"), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        tmp_path.replace(self.storage_path)
