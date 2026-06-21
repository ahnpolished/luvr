# 💝 Luvr — Dating Advice Chatbot

> **Like texting a friend who actually knows what they're talking about.**
> An AI-powered chatbot that lives in Telegram and gives you real, empathetic dating advice — via text, photos, and voice memos.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status: v0.1.0-alpha](https://img.shields.io/badge/status-v0.1.0--alpha-orange.svg)](https://github.com/ahnpolished/luvr)
[![CI](https://github.com/ahnpolished/luvr/actions/workflows/ci.yml/badge.svg)](https://github.com/ahnpolished/luvr/actions/workflows/ci.yml)

## 🎯 What is Luvr?

Luvr is a Telegram chatbot that gives **dating and relationship advice**. You talk to it just like you'd text a friend:

- **Text**: "Should I text him back tonight?"
- **Photo**: Screenshot a confusing conversation → get analysis
- **Voice memo**: Vent about your date → get thoughtful advice + optional voice reply

LLM-powered by OpenAI, Anthropic Claude, DeepSeek, or OpenCode (local LLM gateway).

## 🏗️ Architecture

```
┌──────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────┐
│ Telegram │────▶│  python-telegram │────▶│  Luvr Bot       │────▶│   LLM    │
│   App    │     │  -bot (polling)  │     │  (Handlers)     │     │ (GPT-4o) │
└──────────┘     └──────────────────┘     └─────────────────┘     └──────────┘
                        │                           │
                        │  Update                   │  API Calls
                        │  (new msg)                │
                        ▼                           ▼
                 ┌──────────────────────────────────────┐
                 │        Message Pipeline              │
                 │  ┌──────┐ ┌───────┐ ┌────────┐      │
                 │  │ Text │ │ Photo │ │ Voice  │      │
                 │  │Handler│ │Handler│ │Handler │      │
                 │  └──┬───┘ └──┬────┘ └───┬────┘      │
                 │     │        │          │            │
                 │     ▼        ▼          ▼            │
                 │   LLM     Vision     Whisper→LLM     │
                 │                          │           │
                 │                          ▼           │
                 │                     TTS voice reply  │
                 └──────────────────────────────────────┘
                        │
                        │  /link command
                        ▼
                 ┌──────────────────────┐
                 │    Web Onboarding    │
                 │  (React + FastAPI)   │
                 │                      │
                 │  • Alpha auth        │
                 │  • Instagram context │
                 │  • Profile setup     │
                 └──────────────────────┘
```

| Module | Description |
|--------|-------------|
| `telegram/` | Bot lifecycle, message handlers (text/photo/voice/tarot), command handlers (/start, /link) |
| `llm/` | Abstract LLM interface + OpenAI, Anthropic, DeepSeek, OpenCode clients; prompts; tarot deck; language detection |
| `handler/` | Message processing pipeline for iMessage bridge |
| `bridge/` | BlueBubbles API client (iMessage) |
| `media/` | Vision analysis, Whisper transcription, TTS speech synthesis |
| `alpha/` | Alpha user registry, usage limits, voice quotas |
| `tarot/` | Deterministic 3-card tarot reading UX flow |
| `memory/` | mem0-backed per-user memory store (research prototype) |
| `proactive/` | Manual check-in copy builder |
| `web/` | React + TypeScript + Vite onboarding frontend |

Architecture details: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

## 🚀 Quick Start (Telegram)

### Prerequisites

- **Python 3.12+**
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- An **LLM API key** — at least one of:
  - **OpenAI API key** ([platform.openai.com](https://platform.openai.com/api-keys))
  - **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com))
  - **DeepSeek API key** ([platform.deepseek.com](https://platform.deepseek.com))
  - **OpenCode server** (local gateway, no external key needed)

### 1. Clone & Install

```bash
git clone https://github.com/ahnpolished/luvr.git
cd luvr
make install
```

### 2. Create a Telegram Bot

1. Open Telegram and chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token (looks like `123456:ABCdef...`)

### 3. Configure

```bash
cp .env.example .env
# Edit .env with your settings:
#   TELEGRAM_BOT_TOKEN=your_token_from_botfather
#   LLM_PROVIDER=openai          # or anthropic, deepseek, opencode
#   OPENAI_API_KEY=sk-your-key
```

### 4. Run

```bash
make run-telegram
```

### 5. Chat!

Open Telegram, find your bot, and send `/start`!

---

## 📋 Features (v0.1.0)

| Feature | Status | Description |
|---------|--------|-------------|
| 💬 Text messages | ✅ | Plain text dating advice via LLM |
| 📸 Photo analysis | ✅ | Screenshot/photo analysis via vision model |
| 🎤 Voice memos | ✅ | Audio transcription via Whisper → advice + optional TTS voice reply |
| 🔄 Multi-turn chat | ✅ | Natural back-and-forth conversation |
| 🔒 Safety filters | ✅ | Crisis recognition + resource provision |
| 🃏 Tarot readings | ✅ | 3-card relationship spread with Major Arcana card images |
| 🌐 Web onboarding | ✅ | Alpha auth, Telegram linking, Instagram context collection |
| 🔗 /link command | ✅ | Deep-link from Telegram to web onboarding flow |
| 🔑 Alpha auth | ✅ | HMAC-signed session tokens + invite-code gating |
| 📊 Usage limits | ✅ | Per-feature quotas (voice messages, tarot readings) |
| 🌍 Language detection | ✅ | Auto-detect Korean vs. English, bilingual prompts |
| 📈 Weave tracing | ✅ | Optional W&B Weave spans with alpha user labels |
| 🧪 Eval suite | ✅ | DeepEval safety, tone, friend-likeness; Korean eval cases |
| 💾 Memory prototype | ✅ | mem0 per-user memory store (research, not wired into chat) |
| 🤖 iMessage bridge | ✅ | BlueBubbles + FastAPI (requires Mac) |

Full release status: [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md)

## 🛠️ Tech Stack

- **Bot**: [python-telegram-bot](https://python-telegram-bot.org) (polling/webhook)
- **Server**: FastAPI + uvicorn (iMessage bridge + web auth)
- **Frontend**: React + TypeScript + Vite (web onboarding)
- **LLM**: OpenAI GPT-4o-mini, Anthropic Claude, DeepSeek, OpenCode (local gateway)
- **Vision**: Native vision in OpenAI and Anthropic models
- **Transcription**: OpenAI Whisper
- **TTS**: OpenAI TTS (tts-1 / tts-1-hd)
- **Eval**: DeepEval for AI quality & safety testing
- **Tracing**: W&B Weave (optional)
- **Config**: pydantic-settings + python-dotenv
- **Infra**: Cloudflare DNS + Vercel (Terraform-managed)

## 📁 Project Structure

```
luvr/
├── src/
│   ├── server.py              # FastAPI + iMessage webhook + alpha auth endpoints
│   ├── telegram_server.py     # Telegram bot entrypoint
│   ├── config.py              # Centralized pydantic-settings
│   ├── logging_config.py      # Structured JSON logging
│   ├── alpha_auth.py          # HMAC token creation/verification + linking URLs
│   ├── weave_spans.py         # W&B Weave conversation span helpers
│   ├── eval_trace_policy.py   # Trace retention policy (7–30 days)
│   ├── eval_trace_schema.py   # Structured eval trace models
│   ├── eval_workflow.py       # Conversation eval workflow runner
│   ├── telegram/              # Telegram bot module
│   │   ├── bot.py             # LuvrBot lifecycle + handler registration
│   │   ├── handlers.py        # /start, /link, text, photo, voice, tarot
│   │   ├── bridge_client.py   # Telegram reply API client
│   │   ├── models.py          # Internal message models
│   │   ├── cli.py             # CLI wrapper
│   │   └── __main__.py        # `python -m src.telegram` entry point
│   ├── handler/               # Message processing (iMessage)
│   │   ├── pipeline.py        # Orchestrator
│   │   ├── router.py          # Message type router
│   │   ├── text_handler.py    # Text messages
│   │   ├── photo_handler.py   # Photo/images
│   │   └── voice_handler.py   # Voice memos
│   ├── bridge/                # BlueBubbles API client (iMessage)
│   │   ├── client.py          # Async HTTP client
│   │   └── models.py          # Pydantic models
│   ├── llm/                   # AI integration
│   │   ├── client.py          # Abstract interface + provider factory
│   │   ├── openai_client.py   # OpenAI implementation
│   │   ├── anthropic_client.py # Claude implementation
│   │   ├── opencode_client.py # OpenCode (local gateway) impl
│   │   ├── prompts.py         # System prompts
│   │   ├── tarot.py           # Major Arcana deck + prompt builder
│   │   └── language_detection.py # Korean/English detection
│   ├── media/                 # Media processing
│   │   ├── vision.py          # Image analysis
│   │   ├── transcription.py   # Whisper transcription
│   │   └── speech.py          # TTS voice reply synthesis
│   ├── alpha/                 # Alpha user management
│   │   ├── registry.py        # Profile storage + Telegram linking
│   │   ├── usage_limits.py    # Feature quota enforcement
│   │   ├── tarot_usage.py     # Tarot-specific usage checks
│   │   └── voice_usage.py     # Voice message quota checks
│   ├── tarot/                 # Tarot reading
│   │   ├── flow.py            # Deterministic 3-card UX flow
│   │   └── images.py          # Card image loading
│   ├── memory/                # Memory prototype
│   │   └── mem0_store.py      # mem0 per-user memory wrapper
│   └── proactive/             # Proactive messaging
│       └── checkin.py         # Manual check-in copy builder
├── web/                       # React + TypeScript onboarding frontend
│   └── src/
│       ├── screens/           # Landing, Auth, InstagramContext, TelegramHandoff
│       ├── components/        # PageShell, StepHeader, Button, Card, OTPInput, TextInput
│       ├── state/             # OnboardingProvider + context
│       ├── styles/            # Design tokens
│       └── lib/               # Validation utilities
├── tests/                     # pytest test suite
│   └── eval/                  # DeepEval AI quality tests
├── infra/                     # Terraform (Cloudflare DNS, Vercel)
├── scripts/                   # Utility scripts
│   ├── setup.sh               # One-command setup
│   ├── smoke_test.py          # iMessage smoke tests
│   ├── telegram_smoke_test.py # Telegram smoke tests
│   ├── manual_proactive_checkin.py   # Manual proactive check-in
│   ├── run_weave_conversation_eval.py # Weave eval runner
│   └── generate_tarot_images.py      # Tarot card image generator
├── examples/                  # Example usage
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md        # Technical architecture
│   ├── SETUP.md               # Step-by-step setup guide
│   ├── SECURITY.md            # Security policy & baseline
│   ├── DESIGN_BRIEF.md        # Product design brief
│   ├── AUTH_MEMORY.md         # Auth + memory research
│   ├── RELEASE_CHECKLIST.md   # v0.1.0 readiness checklist
│   └── TODO.md                # Future roadmap & ideas
├── Makefile                   # Common commands
├── pyproject.toml             # Python project config
└── .env.example               # Configuration template
```

## 🔧 Development

```bash
make install             # Install dependencies
make run-telegram        # Start Telegram bot (polling mode)
make run                 # Start iMessage server (FastAPI)
make test                # Run tests
make test-cov            # Run tests with coverage report
make lint                # Run linter (ruff)
make format              # Format code (ruff)
make typecheck           # Type check (ty)
make smoke-test          # Run iMessage smoke tests
make tg-smoke-test       # Run Telegram smoke tests
make eval                # Run eval suite (fast deterministic)
make eval-slow           # Run full eval suite (includes slow tests)
make eval-all            # Run ALL eval tests
make generate-tarot-images  # Generate Major Arcana card images
```

## 🗺️ Roadmap

- **v0.1.0** (current): Telegram bot, text/photo/voice, tarot, web onboarding, alpha auth, usage limits, Weave evals
- **v0.2.0**: Persistent product memory, conversation history, personality customization
- **v0.3.0**: Multi-channel (iMessage revival, Kakaotalk), monitoring, production deployment
- **v1.0.0**: Public release, App Store companion app

## 📄 License

MIT © Humphrey Ahn
