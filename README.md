# 💝 Luvr — Dating Advice Chatbot

> **Like Poke, but for dating advice.**
> An AI-powered chatbot that lives in iMessage or Telegram and gives you real, empathetic dating advice — via text, photos, and voice memos.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status: v0.1.0-alpha](https://img.shields.io/badge/status-v0.1.0--alpha-orange.svg)](https://github.com/ahnpolished/luvr)
[![CI](https://github.com/ahnpolished/luvr/actions/workflows/ci.yml/badge.svg)](https://github.com/ahnpolished/luvr/actions/workflows/ci.yml)

## 🎯 What is Luvr?

Luvr is a chatbot that gives **dating and relationship advice**. You talk to it just like you'd text a friend:

- **Text**: "Should I text him back tonight?"
- **Photo**: Screenshot a confusing conversation → get analysis
- **Voice memo**: Vent about your date → get thoughtful advice

Luvr works on two platforms:

| Platform | Bridge | Setup Complexity | Requires Mac? |
|----------|--------|-----------------|---------------|
| **iMessage** 💬 | BlueBubbles | Medium | ✅ Yes |
| **Telegram** 🤖 | Telegram Bot API | Easy | ❌ No |

### Telegram Version (NEW! 🎉)

The Telegram version is the easiest way to get started. Just create a bot with @BotFather, set your API keys, and you're ready to go — no Mac required!

### iMessage Version

The iMessage version uses BlueBubbles to bridge iMessage to a REST API, allowing Luvr to read and respond to your iMessages on any device.

LLM-powered by OpenAI, Anthropic Claude, DeepSeek, or OpenCode (local LLM gateway).

## 🏗️ Architecture

### Telegram Version

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
                 └──────────────────────────────────────┘
```

### iMessage Version

```
┌──────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────┐
│  iPhone  │────▶│  BlueBubbles     │────▶│  Luvr Bot       │────▶│   LLM    │
│ iMessage │     │  (Mac Bridge)    │     │  (FastAPI)      │     │ (GPT-4o) │
└──────────┘     └──────────────────┘     └─────────────────┘     └──────────┘
                        │                           │
                        │  Webhook                  │  API Calls
                        │  (new msg)                │  (send msg)
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
                 └──────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Mac** with iMessage signed in
- **Python 3.12+**
- **BlueBubbles** server installed ([bluebubbles.app](https://bluebubbles.app))
- **OpenAI API key** (for GPT-4o-mini + Whisper) **or** **Anthropic API key** (for Claude)

### 1. Clone & Install

```bash
git clone https://github.com/ahnpolished/luvr.git
cd luvr
make install
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys and BlueBubbles server URL
```

### 3. Set Up BlueBubbles

1. Download and install [BlueBubbles](https://bluebubbles.app) on your Mac
2. Configure it with your iMessage account
3. Set a server password in BlueBubbles settings
4. Note your server URL (usually `http://localhost:1234`)
5. Configure webhook: set it to POST to `http://127.0.0.1:8000/webhook` (use 127.0.0.1, not localhost — BlueBubbles prefers IPv6 and won't reach the server)

### 4. Run

```bash
make run
```

### 5. Test

Send an iMessage to the account running BlueBubbles and ask for dating advice!

Or run smoke tests (no iMessage needed):
```bash
make smoke-test
```

## 🤖 Telegram Quick Start

### Prerequisites

- **Python 3.12+**
- **Telegram Bot Token** from [@BotFather](https://t.me/BotFather)
- **OpenAI API key** (for GPT-4o-mini + Whisper) **or** **Anthropic API key** (for Claude)

### 1. Clone & Install

```bash
git clone https://github.com/ahnpolished/luvr.git
cd luvr
make install
```

### 2. Create a Telegram Bot

1. Open Telegram and chat with [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive (looks like `123456:ABCdef...`)

### 3. Configure

```bash
cp .env.example .env
# Edit .env:
#   TELEGRAM_BOT_TOKEN=your_token_from_botfather
#   OPENAI_API_KEY=sk-your-key
#   LLM_PROVIDER=openai
#   PLATFORM=telegram
```

### 4. Run

```bash
make run-telegram
```

### 5. Chat!

Open Telegram, find your bot, and send `/start`!

---

## 💬 iMessage Quick Start

(Requires a Mac with iMessage signed in and BlueBubbles installed.)

## 📋 Features (v0.1.0)

| Feature | iMessage | Telegram | Description |
|---------|----------|----------|-------------|
| 💬 Text messages | ✅ | ✅ | Plain text dating advice via LLM |
| 📸 Photo analysis | ✅ | ✅ | Screenshot/photo analysis via vision model |
| 🎤 Voice memos | ✅ | ✅ | Audio transcription via Whisper → advice |
| 🔄 Multi-turn chat | ✅ | ✅ | Natural back-and-forth conversation |
| 🔒 Safety filters | ✅ | ✅ | Crisis recognition + resource provision |
| 🧪 Smoke tests | ✅ | ✅ | Test without real messaging |
| 🤖 Telegram Bot API | — | ✅ | Easy setup, no Mac required |

## 🛠️ Tech Stack

- **Bridges**: [BlueBubbles](https://bluebubbles.app) (iMessage) | [python-telegram-bot](https://python-telegram-bot.org) (Telegram)
- **Server**: FastAPI + uvicorn (iMessage) | python-telegram-bot polling/webhook (Telegram)
- **LLM**: OpenAI GPT-4o-mini, Anthropic Claude, DeepSeek, or OpenCode (local gateway)
- **Vision**: Native vision capabilities in OpenAI and Anthropic models
- **Transcription**: OpenAI Whisper
- **Eval**: DeepEval for AI quality & safety testing
- **Config**: pydantic-settings + python-dotenv

## 📁 Project Structure

```
luvr/
├── src/
│   ├── server.py              # FastAPI app entrypoint (iMessage)
│   ├── telegram_server.py     # Telegram bot entrypoint
│   ├── config.py              # Centralized settings
│   ├── logging_config.py      # Structured logging
│   ├── bridge/                # BlueBubbles API client (iMessage)
│   │   ├── client.py          # Async HTTP client
│   │   └── models.py          # Pydantic models
│   ├── telegram/              # Telegram bot module
│   │   ├── bot.py             # Bot lifecycle + handler registration
│   │   ├── handlers.py        # Message handlers (text/photo/voice)
│   │   ├── bridge_client.py   # Telegram reply API client
│   │   ├── models.py          # Internal message models
│   │   ├── cli.py             # CLI wrapper
│   │   └── __main__.py        # Entry point
│   ├── handler/               # Message processing (iMessage)
│   │   ├── pipeline.py        # Orchestrator
│   │   ├── router.py          # Message type router
│   │   ├── text_handler.py    # Text messages
│   │   ├── photo_handler.py   # Photo/images
│   │   └── voice_handler.py   # Voice memos
│   ├── llm/                   # AI integration
│   │   ├── client.py          # Abstract interface + factory
│   │   ├── openai_client.py   # OpenAI implementation
│   │   ├── anthropic_client.py # Claude implementation
│   │   ├── opencode_client.py # OpenCode (local gateway) impl
│   │   └── prompts.py         # System prompts
│   └── media/                 # Media processing
│       ├── vision.py          # Image analysis
│       └── transcription.py   # Whisper transcription
├── tests/                     # Test suite
│   └── eval/                  # DeepEval AI quality tests
├── scripts/                   # Utility scripts
│   ├── setup.sh               # One-command setup
│   ├── smoke_test.py          # iMessage smoke tests
│   └── telegram_smoke_test.py # Telegram smoke tests
├── examples/                  # Example usage
│   └── telegram_bot.py        # Standalone Telegram example
├── Makefile                   # Common commands
├── pyproject.toml             # Python project config
└── .env.example               # Configuration template
```

## 🔧 Development

```bash
make install       # Install dependencies
make run           # Start iMessage server
make run-telegram  # Start Telegram bot
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Run linter
make format        # Format code
make smoke-test    # Run iMessage smoke tests (needs API keys)
make tg-smoke-test # Run Telegram smoke tests (no API keys needed)
make eval          # Run eval suite (fast deterministic tests)
make eval-slow     # Run full eval suite (includes slow tests)
make eval-all      # Run ALL eval tests
```

## 🗺️ Roadmap

- **v0.1.0** (current): Local dev environment, text + photo + voice support
- **v0.2.0**: Multi-user support, conversation history, personality customization
- **v0.3.0**: Cloud deployment, authentication, monitoring
- **v1.0.0**: Public release, App Store companion app

## 📄 License

MIT © Humphrey Ahn
