"""FastAPI application entrypoint for the Luvr iMessage dating advice chatbot."""

from __future__ import annotations

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.bridge.client import BlueBubblesClient
from src.config import settings
from src.handler.pipeline import MessagePipeline
from src.logging_config import setup_logging

logger = structlog.get_logger(__name__)

# Global instances
bridge_client: BlueBubblesClient
message_pipeline: MessagePipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "luvr", "version": "0.1.0"}


@app.post("/webhook")
async def webhook(request: Request):
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
