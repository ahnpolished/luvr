"""Tests for lightweight alpha web authentication."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.alpha.registry import AlphaUserRegistry
from src.alpha_auth import create_alpha_token, decode_alpha_token


@pytest.fixture
def registry(tmp_path):
    return AlphaUserRegistry(storage_path=tmp_path / "alpha-users.json")


@pytest.fixture
def client():
    from src.server import app

    return TestClient(app)


@pytest.fixture
def auth_secret():
    return "alpha-test-secret-32-bytes!!!"


class TestTokenRoundTrip:
    def test_create_and_decode_token_round_trip(self, auth_secret):
        """Signed token encodes and decodes alpha user payload safely."""
        token = create_alpha_token(
            user_id="alpha_abc123",
            telegram_user_id=456,
            secret=auth_secret,
        )
        payload = decode_alpha_token(token, secret=auth_secret)

        assert payload["user_id"] == "alpha_abc123"
        assert payload["telegram_user_id"] == "456"
        assert "iat" in payload

    def test_tampered_token_is_rejected(self, auth_secret):
        """A token with modified payload is rejected."""
        token = create_alpha_token(user_id="alpha_x", telegram_user_id=1, secret=auth_secret)
        parts = token.split(".")
        parts[0] = parts[0][:-1] + ("Z" if parts[0][-1] != "Z" else "A")
        tampered = ".".join(parts)

        with pytest.raises(ValueError, match="invalid token"):
            decode_alpha_token(tampered, secret=auth_secret)

    def test_token_expiry_is_enforced(self, auth_secret):
        """Token older than expiry is rejected."""
        token = create_alpha_token(
            user_id="alpha_x",
            telegram_user_id=1,
            secret=auth_secret,
            max_age_seconds=-1,  # already expired
        )
        with pytest.raises(ValueError, match="token expired"):
            decode_alpha_token(token, secret=auth_secret, max_age_seconds=3)


class TestAuthEndpoint:
    def test_exchange_succeeds_with_correct_alpha_code(self, client, registry, monkeypatch):
        monkeypatch.setenv("ALPHA_INVITE_CODE", "test-invite-code-1337")
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "alpha-test-secret-32-bytes!!!")
        resp = client.post(
            "/auth/alpha/exchange",
            json={"alpha_code": "test-invite-code-1337", "telegram_user_id": 123},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["user_id"].startswith("alpha_")
        assert body["auth_completed"] is True
        assert "session_token" in body

    def test_exchange_fails_with_wrong_alpha_code(self, client, monkeypatch):
        monkeypatch.setenv("ALPHA_INVITE_CODE", "test-invite-code-1337")
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "alpha-test-secret-32-bytes!!!")
        resp = client.post("/auth/alpha/exchange", json={"alpha_code": "wrong", "telegram_user_id": 123})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "invalid alpha code"

    def test_profile_endpoint_requires_authorization(self, client, monkeypatch):
        monkeypatch.setenv("ALPHA_INVITE_CODE", "test-invite-code-1337")
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "alpha-test-secret-32-bytes!!!")
        resp = client.get("/auth/alpha/profile")
        assert resp.status_code == 403

    def test_profile_returns_linked_alpha_data(self, client, registry, monkeypatch):
        monkeypatch.setenv("ALPHA_INVITE_CODE", "test-invite-code-1337")
        monkeypatch.setenv("ALPHA_AUTH_SECRET", "alpha-test-secret-32-bytes!!!")
        exchange = client.post(
            "/auth/alpha/exchange",
            json={"alpha_code": "test-invite-code-1337", "telegram_user_id": 123, "telegram_username": "humphrey"},
        )
        token = exchange.json()["session_token"]

        resp = client.get("/auth/alpha/profile", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        profile = resp.json()
        assert profile["telegram_user_id"] == 123
        assert profile["telegram_username"] == "humphrey"
        assert profile["auth_completed"] is True


def _override_settings():
    """Not used — settings now injected via monkeypatch.setenv."""
    raise NotImplementedError
