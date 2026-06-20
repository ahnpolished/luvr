"""Tests for Telegram-web deep-link account linking."""

from __future__ import annotations

import pytest

from src.alpha.registry import AlphaUserRegistry
from src.alpha_auth import create_linking_token, decode_linking_token


class TestLinkingToken:
    def test_create_and_decode_linking_token(self):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "linking-secret-32-bytes!!!")
        token = create_linking_token(telegram_user_id=123, telegram_chat_id=456)
        payload = decode_linking_token(token)

        assert payload["telegram_user_id"] == "123"
        assert payload["telegram_chat_id"] == "456"
        assert "purpose" in payload
        assert payload["purpose"] == "telegram_web_linking"

    def test_expired_linking_token_is_rejected(self):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "linking-secret-32-bytes!!!")
        token = create_linking_token(telegram_user_id=123, max_age_seconds=-1)
        with pytest.raises(ValueError, match="token expired"):
            decode_linking_token(token)

    def test_tampered_linking_token_is_rejected(self):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "linking-secret-32-bytes!!!")
        token = create_linking_token(telegram_user_id=123)
        parts = token.split(".")
        parts[0] = parts[0][:-1] + "X"
        with pytest.raises(ValueError, match="invalid token"):
            decode_linking_token(".".join(parts))


class TestWebhookLinking:
    def test_start_command_returns_linking_url(self, tmp_path):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "linking-secret-32-bytes!!!")
        monkeypatch.setenv("ALPHA_WEB_BASE_URL", "http://localhost:8000")

        from src.alpha_auth import build_linking_url as _cf

        url = _cf(telegram_user_id=123, telegram_chat_id=456)
        assert url.startswith("http://localhost:8000")
        assert "/auth/alpha/exchange" in url
        assert "linking_token=" in url

    def test_linking_endpoint_associates_web_auth_with_telegram(self, client, registry, tmp_path):
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "linking-secret-32-bytes!!!")
        monkeypatch.setenv("ALPHA_INVITE_CODE", "invite-1383")
        monkeypatch.setenv("ALPHA_WEB_BASE_URL", "http://localhost:8000")

        # Step 1: Create a linking token
        token = create_linking_token(telegram_user_id=123, telegram_chat_id=456)

        # Step 2: Submit exchange with the linking token
        resp = client.post(
            "/auth/alpha/exchange",
            json={
                "alpha_code": "invite-1383",
                "linking_token": token,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["linking_completed"] is True
        assert body["telegram_user_id"] == 123


@pytest.fixture
def registry(tmp_path):
    return AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")


@pytest.fixture
def client():
    from starlette.testclient import TestClient

    from src.server import app

    return TestClient(app)
