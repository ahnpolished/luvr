"""FastAPI application entrypoint for the Luvr iMessage dating advice chatbot."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.alpha.registry import AlphaUserRegistry
from src.alpha_auth import (
    _get_alpha_code,
    create_alpha_token,
    decode_alpha_token,
    decode_linking_token,
)
from src.bridge.client import BlueBubblesClient
from src.config import settings
from src.handler.pipeline import MessagePipeline
from src.logging_config import setup_logging

logger = structlog.get_logger(__name__)

# Global instances
bridge_client: BlueBubblesClient
message_pipeline: MessagePipeline


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle: startup and shutdown events."""
    global bridge_client, message_pipeline

    setup_logging()
    logger.info("luvr_starting", version="0.1.0", llm_provider=settings.llm_provider)

    bridge_client = BlueBubblesClient(
        server_url=settings.bluebubbles_server_url,
        password=settings.bluebubbles_password,
    )
    message_pipeline = MessagePipeline(bridge_client=bridge_client)

    logger.info("luvr_ready", port=settings.port)
    yield

    logger.info("luvr_shutting_down")
    await bridge_client.aclose()


app = FastAPI(
    title="Luvr",
    description="💝 iMessage-based dating advice chatbot",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")  # type: ignore[misc]
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "luvr", "version": "0.1.0"}


alpha_registry = AlphaUserRegistry()


@app.post("/webhook")  # type: ignore[misc]
async def webhook(request: Request) -> JSONResponse:
    """Receive incoming iMessage webhook from BlueBubbles.

    BlueBubbles forwards new messages to this endpoint as JSON payloads.
    """
    try:
        payload = await request.json()
        logger.info("webhook_received", payload_keys=list(payload.keys()))

        # Process asynchronously and respond immediately
        # (BlueBubbles expects quick 200 response)
        await message_pipeline.process(payload)

        return JSONResponse({"status": "processed"})

    except Exception:
        logger.exception("webhook_error")
        return JSONResponse({"status": "error", "message": "Internal processing error"}, status_code=500)


# ------------------------------------------------------------------
# Alpha web auth endpoints
# ------------------------------------------------------------------


@app.post("/auth/alpha/exchange")  # type: ignore[misc]
async def auth_alpha_exchange(request: Request) -> JSONResponse:
    """Exchange an alpha invite code for a signed session token and profile."""
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "invalid json"}, status_code=400)

    code = body.get("alpha_code", "")
    alpha_code = _get_alpha_code()
    if not alpha_code or code != alpha_code:
        return JSONResponse({"detail": "invalid alpha code"}, status_code=401)

    linking_token = body.get("linking_token")
    telegram_user_id = body.get("telegram_user_id")
    linking_completed = False

    if linking_token:
        try:
            link_payload = decode_linking_token(linking_token)
            telegram_user_id = int(link_payload["telegram_user_id"])
            linking_completed = True
        except ValueError as exc:
            return JSONResponse({"detail": str(exc)}, status_code=401)
    profile = alpha_registry.get_or_create_for_telegram(
        telegram_user_id=int(telegram_user_id) if telegram_user_id else 0,
        telegram_chat_id=body.get("telegram_chat_id", 0),
        telegram_username=body.get("telegram_username"),
        display_name=body.get("display_name"),
    )
    alpha_registry.update_profile(profile.user_id, auth_completed=True)

    session_token = create_alpha_token(user_id=profile.user_id, telegram_user_id=profile.telegram_user_id)

    return JSONResponse(
        {
            "user_id": profile.user_id,
            "telegram_user_id": profile.telegram_user_id,
            "telegram_username": profile.telegram_username,
            "display_name": profile.display_name,
            "auth_completed": profile.auth_completed,
            "session_token": session_token,
            "linking_completed": linking_completed,
        }
    )


@app.get("/auth/alpha/profile")  # type: ignore[misc]
async def auth_alpha_profile(request: Request) -> JSONResponse:
    """Return the linked alpha profile for a valid session token."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return JSONResponse({"detail": "missing authorization token"}, status_code=403)

    try:
        payload = decode_alpha_token(token)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=403)

    user_id = payload.get("user_id", "")
    try:
        profile = alpha_registry.get_profile(user_id)
    except KeyError:
        return JSONResponse({"detail": "unknown user"}, status_code=404)

    return JSONResponse(profile.model_dump(mode="json"))


@app.post("/auth/alpha/onboarding")  # type: ignore[misc]
async def auth_alpha_onboarding(request: Request) -> JSONResponse:
    """Complete onboarding with optional Instagram info or self-summary."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        return JSONResponse({"detail": "missing authorization token"}, status_code=403)

    try:
        payload = decode_alpha_token(token)
    except ValueError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=403)

    user_id = payload.get("user_id", "")
    try:
        alpha_registry.get_profile(user_id)  # validate user exists
    except KeyError:
        return JSONResponse({"detail": "unknown user"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "invalid json"}, status_code=400)

    instagram_handle = body.get("instagram_handle", "").strip()
    instagram_bio = body.get("instagram_bio", "").strip()
    self_summary = body.get("self_summary", "").strip()

    if instagram_handle:
        context_summary = f"Instagram: {instagram_handle}"
        if instagram_bio:
            context_summary += f" | Bio: {instagram_bio}"
    elif self_summary:
        context_summary = f"Self-summary: {self_summary}"
    else:
        context_summary = "No context provided (skipped)"

    updated = alpha_registry.update_profile(
        user_id,
        onboarding_completed=True,
        instagram_context_summary=context_summary,
    )

    return JSONResponse(updated.model_dump(mode="json"))
