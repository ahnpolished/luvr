"""Tests for web onboarding flow."""

from __future__ import annotations

import pytest


@pytest.fixture
def client():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("ALPHA_AUTH_SECRET", "onboarding-secret-32-bytes!!!")
    monkeypatch.setenv("ALPHA_INVITE_CODE", "invite-1391")
    monkeypatch.setenv("ALPHA_WEB_BASE_URL", "http://localhost:8000")

    from starlette.testclient import TestClient

    from src.server import app

    return TestClient(app)


def test_onboarding_completes_with_instagram_handle(client):
    """Full onboarding: auth → provide Instagram → mark complete."""
    from src.alpha_auth import create_linking_token

    token = create_linking_token(telegram_user_id=123, telegram_chat_id=456)

    # Step 1: auth with linking token
    resp = client.post(
        "/auth/alpha/exchange",
        json={"alpha_code": "invite-1391", "linking_token": token},
    )
    assert resp.status_code == 200
    session_token = resp.json()["session_token"]

    # Step 2: submit onboarding
    resp2 = client.post(
        "/auth/alpha/onboarding",
        json={
            "instagram_handle": "@humphreyahn",
            "instagram_bio": "Builder of things. Lover of people.",
        },
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["onboarding_completed"] is True
    assert body["instagram_context_summary"] is not None
    assert "humphreyahn" in body["instagram_context_summary"]


def test_onboarding_allows_skip_of_instagram(client):
    """User can skip Instagram and provide a self-summary fallback."""
    from src.alpha_auth import create_linking_token

    token = create_linking_token(telegram_user_id=789)
    resp = client.post(
        "/auth/alpha/exchange",
        json={"alpha_code": "invite-1391", "linking_token": token},
    )
    session_token = resp.json()["session_token"]

    resp2 = client.post(
        "/auth/alpha/onboarding",
        json={"self_summary": "I'm a developer who loves hiking and photography."},
        headers={"Authorization": f"Bearer {session_token}"},
    )
    assert resp2.status_code == 200
    assert resp2.json()["onboarding_completed"] is True
    assert "hiking" in resp2.json()["instagram_context_summary"]


def test_onboarding_rejects_unauthenticated_requests(client):
    resp = client.post("/auth/alpha/onboarding", json={"self_summary": "hello"})
    assert resp.status_code == 403


def test_onboarding_rejects_invalid_token(client):
    resp = client.post(
        "/auth/alpha/onboarding",
        json={"self_summary": "hello"},
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 403
