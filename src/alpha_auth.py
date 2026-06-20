"""Lightweight v0.1.0 alpha web authentication.

Uses a pre-shared alpha invite code (``ALPHA_INVITE_CODE`` env var) and an
HMAC-signed session token. This is not production auth — it is the minimum
needed to link a Telegram identity to an alpha profile during onboarding.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

_TOKEN_MAX_AGE_SECONDS = 86400  # 24 hours


def _get_secret() -> str:
    return os.environ.get("ALPHA_AUTH_SECRET", "")


def _get_alpha_code() -> str:
    return os.environ.get("ALPHA_INVITE_CODE", "")


def create_alpha_token(
    *,
    user_id: str,
    telegram_user_id: int | None = None,
    secret: str | None = None,
    max_age_seconds: int = _TOKEN_MAX_AGE_SECONDS,
) -> str:
    """Create a signed alpha session token.

    The token is an HMAC-SHA256 over a JSON payload containing ``user_id``,
    ``telegram_user_id``, and ``iat`` (issued-at timestamp).
    """
    key = (secret or _get_secret()).encode("utf-8")
    payload_bytes = json.dumps(
        {
            "user_id": user_id,
            "telegram_user_id": str(telegram_user_id) if telegram_user_id is not None else "",
            "iat": int(time.time()) + max_age_seconds,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = urlsafe_b64encode(payload_bytes).rstrip(b"=").decode("ascii")
    signature = hmac.new(key, encoded.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"


def decode_alpha_token(
    token: str,
    *,
    secret: str | None = None,
    max_age_seconds: int = _TOKEN_MAX_AGE_SECONDS,
) -> dict[str, str]:
    """Verify and decode an alpha session token.

    Returns the payload dict on success; raises ``ValueError`` on any
    validation failure (tampered, expired, malformed).
    """
    try:
        encoded, signature = token.rsplit(".", 1)
    except ValueError as err:
        raise ValueError("invalid token format") from err

    key = (secret or _get_secret()).encode("utf-8")
    expected_sig = hmac.new(key, encoded.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_sig, signature):
        raise ValueError("invalid token")

    # Add padding back for base64
    padding = 4 - len(encoded) % 4
    if padding != 4:
        encoded += "=" * padding
    try:
        payload_bytes = urlsafe_b64decode(encoded)
    except Exception as exc:
        raise ValueError("invalid token payload") from exc

    try:
        payload: dict[str, str] = json.loads(payload_bytes)
    except json.JSONDecodeError as err:
        raise ValueError("invalid token payload") from err

    now = int(time.time())
    iat: int = int(payload.get("iat", 0))
    if iat < now:
        raise ValueError("token expired")

    # Fix up iat back to a reasonable timestamp display
    payload["iat"] = str(iat - _TOKEN_MAX_AGE_SECONDS)
    return payload
