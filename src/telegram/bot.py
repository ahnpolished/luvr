"""Luvr Telegram bot — wraps python-telegram-bot Application with Luvr's logic."""

from __future__ import annotations

import asyncio
import signal
from pathlib import Path
from typing import Any

import structlog
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.alpha.registry import AlphaUserRegistry
from src.alpha.tarot_usage import TarotUsageGate
from src.alpha_auth import build_linking_url
from src.config import settings
from src.llm.client import LLMClient, create_llm_client
from src.telegram.bridge_client import TelegramBridgeClient
from src.telegram.handlers import (
    PERSONA_CALLBACK_PREFIX,
    handle_link,
    handle_persona,
    handle_persona_callback,
    handle_photo,
    handle_start,
    handle_tarot,
    handle_text,
    handle_voice,
)
from src.telegram.onboarding import (
    ONBOARDING_CALLBACK_PREFIX,
    handle_onboarding_callback,
)

logger = structlog.get_logger(__name__)


class LuvrBot:
    """Main Telegram bot class for the Luvr dating advice chatbot.

    Wraps a ``telegram.ext.Application``, registers message handlers, and
    manages the bot lifecycle (start / stop / shutdown).

    Typical usage::

        bot = LuvrBot(token="...", mode="polling")
        await bot.start()
        # ... bot is running ...
        await bot.stop()
    """

    def __init__(
        self,
        token: str,
        mode: str = "polling",
        webhook_url: str | None = None,
        allowed_user_ids: list[int] | None = None,
    ) -> None:
        self.token = token
        self.mode = mode
        self.webhook_url = webhook_url
        self.allowed_user_ids: set[int] = set(allowed_user_ids or [])

        # Core components (lazy-initialized in start)
        self._llm_client: LLMClient | None = None
        self._bridge_client: TelegramBridgeClient | None = None
        self._app: Application[Any, Any, Any, Any, Any, Any] | None = None
        self._alpha_registry: AlphaUserRegistry | None = None
        self._tarot_gate: TarotUsageGate | None = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def llm_client(self) -> LLMClient:
        """Lazy-initialize the LLM client."""
        if self._llm_client is None:
            self._llm_client = create_llm_client()
        return self._llm_client

    @property
    def bridge_client(self) -> TelegramBridgeClient:
        """Lazy-initialize the Telegram bridge client."""
        if self._bridge_client is None:
            self._bridge_client = TelegramBridgeClient()
        return self._bridge_client

    @property
    def app(self) -> Application[Any, Any, Any, Any, Any, Any]:
        """Return the telegram Application (must be started first)."""
        if self._app is None:
            raise RuntimeError("Bot not started. Call start() first.")
        return self._app

    @property
    def alpha_registry(self) -> AlphaUserRegistry:
        """Lazy-initialize the alpha user registry (persona + tarot usage)."""
        if self._alpha_registry is None:
            self._alpha_registry = AlphaUserRegistry(
                storage_path=Path(settings.alpha_registry_path),
            )
        return self._alpha_registry

    @property
    def tarot_gate(self) -> TarotUsageGate:
        """Lazy-initialize the tarot usage gate."""
        if self._tarot_gate is None:
            self._tarot_gate = TarotUsageGate(self.alpha_registry)
        return self._tarot_gate

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Build the Application, register handlers, and start polling/webhook."""
        logger.info("luvr_telegram_starting", mode=self.mode)

        builder = ApplicationBuilder().token(self.token)

        self._app = builder.build()

        # Store shared dependencies in bot_data so handlers can access them
        self._app.bot_data["bridge_client"] = self.bridge_client
        self._app.bot_data["llm_client"] = self.llm_client
        self._app.bot_data["alpha_registry"] = self.alpha_registry
        self._app.bot_data["tarot_gate"] = self.tarot_gate

        _register_handlers(self._app)

        if self.mode == "webhook" and self.webhook_url:
            await self._app.bot.set_webhook(url=self.webhook_url)
            logger.info("luvr_telegram_webhook_set", url=self.webhook_url)
        else:
            # Polling mode
            await self._app.initialize()
            await self._app.start()
            assert self._app.updater is not None
            await self._app.updater.start_polling()

        logger.info("luvr_telegram_ready", mode=self.mode)

    async def stop(self) -> None:
        """Gracefully shut down the bot."""
        logger.info("luvr_telegram_shutting_down")

        if self._app is not None:
            try:
                if self._app.updater:
                    await self._app.updater.stop()
                await self._app.stop()
                await self._app.shutdown()
            except Exception:
                logger.exception("telegram_shutdown_error")

        if self._bridge_client is not None:
            await self._bridge_client.aclose()

        self._app = None
        logger.info("luvr_telegram_stopped")

    async def run_until_sigterm(self) -> None:
        """Start the bot and block until SIGTERM/SIGINT."""
        await self.start()

        # Wait for shutdown signal
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        def _signal_handler() -> None:
            logger.info("shutdown_signal_received")
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _signal_handler)
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                pass

        await stop_event.wait()
        await self.stop()


# ------------------------------------------------------------------
# Handler registration
# ------------------------------------------------------------------


def _register_handlers(app: Application[Any, Any, Any, Any, Any, Any]) -> None:
    """Register all Telegram message handlers on the Application."""
    # /start command
    app.add_handler(CommandHandler("start", handle_start))

    # /link command — send onboarding deep-link
    app.add_handler(CommandHandler("link", _build_handler(handle_link)))

    # /persona command — pick a persona; callback handles the button tap
    app.add_handler(CommandHandler("persona", handle_persona))
    app.add_handler(CallbackQueryHandler(handle_persona_callback, pattern=f"^{PERSONA_CALLBACK_PREFIX}"))

    # Onboarding inline keyboard callbacks (Set up profile / Continue anonymously)
    app.add_handler(CallbackQueryHandler(handle_onboarding_callback, pattern=f"^{ONBOARDING_CALLBACK_PREFIX}"))

    # /tarot command — 3-card relationship reading
    app.add_handler(CommandHandler("tarot", _build_handler(handle_tarot)))

    # Text messages (excluding commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _build_handler(handle_text)))

    # Photo messages
    app.add_handler(MessageHandler(filters.PHOTO, _build_handler(handle_photo)))

    # Voice messages
    app.add_handler(MessageHandler(filters.VOICE, _build_handler(handle_voice)))


def _build_handler(handler_fn: Any) -> Any:
    """Wrap a handler function to inject bot_data dependencies at runtime.

    This avoids globals and keeps the handler functions testable — they
    accept optional ``bridge_client`` and ``llm_client`` keyword arguments.
    """

    async def wrapper(update: Any, context: Any) -> None:
        bc = context.bot_data.get("bridge_client")
        lc = context.bot_data.get("llm_client")
        await handler_fn(update, context, bridge_client=bc, llm_client=lc)

    return wrapper


def _build_linking_url(*, telegram_user_id: int, telegram_chat_id: int | None = None) -> str:
    """Build a deep-link URL for Telegram-web auth linking (delegates to alpha_auth)."""
    return build_linking_url(telegram_user_id=telegram_user_id, telegram_chat_id=telegram_chat_id)
