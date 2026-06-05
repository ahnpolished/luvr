# 💝 Luvr — iMessage Dating Advice Chatbot

> **Like Poke, but for dating advice.**  
> An AI-powered chatbot that lives in iMessage and gives you real, empathetic dating advice — via text, photos, and voice memos.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status: MVP](https://img.shields.io/badge/status-v0.1.0--alpha-orange.svg)](https://github.com/ahnpolished/luvr)

## 🎯 What is Luvr?

Luvr is an iMessage-based chatbot that gives **dating and relationship advice**. You talk to it just like you'd text a friend:

- **Text**: "Should I text him back tonight?"
- **Photo**: Screenshot a confusing conversation → get analysis
- **Voice memo**: Vent about your date → get thoughtful advice

It uses an iMessage bridge (BlueBubbles) to connect to your Mac's Messages app, and GPT-4o-mini or Claude to generate responses.

## 🏗️ Architecture

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
5. Configure webhook: set it to POST to `http://localhost:8000/webhook`

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

## 📋 Features (v0.1.0)

| Feature | Status | Description |
|---------|--------|-------------|
| 💬 Text messages | ✅ | Plain text dating advice via LLM |
| 📸 Photo analysis | ✅ | Screenshot/photo analysis via vision model |
| 🎤 Voice memos | ✅ | Audio transcription via Whisper → advice |
| 🔄 Multi-turn chat | ✅ | Natural back-and-forth conversation |
| 🔒 Safety filters | ✅ | Crisis recognition + resource provision |
| 🧪 Smoke tests | ✅ | Test without real iMessage |

## 🛠️ Tech Stack

- **Bridge**: [BlueBubbles](https://bluebubbles.app) — iMessage ↔ REST API
- **Server**: FastAPI + uvicorn (async Python)
- **LLM**: OpenAI GPT-4o-mini (primary) or Anthropic Claude 3 Haiku
- **Vision**: Native vision capabilities in both models
- **Transcription**: OpenAI Whisper
- **Config**: pydantic-settings + python-dotenv

## 📁 Project Structure

```
luvr/
├── src/
│   ├── server.py              # FastAPI app entrypoint
│   ├── config.py              # Centralized settings
│   ├── logging_config.py      # Structured logging
│   ├── bridge/                # BlueBubbles API client
│   │   ├── client.py          # Async HTTP client
│   │   └── models.py          # Pydantic models
│   ├── handler/               # Message processing
│   │   ├── pipeline.py        # Orchestrator
│   │   ├── router.py          # Message type router
│   │   ├── text_handler.py    # Text messages
│   │   ├── photo_handler.py   # Photo/images
│   │   └── voice_handler.py   # Voice memos
│   ├── llm/                   # AI integration
│   │   ├── client.py          # Abstract interface + factory
│   │   ├── openai_client.py   # OpenAI implementation
│   │   ├── anthropic_client.py # Claude implementation
│   │   └── prompts.py         # System prompts
│   └── media/                 # Media processing
│       ├── vision.py          # Image analysis
│       └── transcription.py   # Whisper transcription
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
│   ├── setup.sh               # One-command setup
│   └── smoke_test.py          # End-to-end smoke tests
├── Makefile                   # Common commands
├── pyproject.toml             # Python project config
└── .env.example               # Configuration template
```

## 🔧 Development

```bash
make install     # Install dependencies
make run         # Start development server
make test        # Run tests
make lint        # Run linter
make format      # Format code
make smoke-test  # Run smoke tests (needs API keys)
```

## 🗺️ Roadmap

- **v0.1.0** (current): Local dev environment, text + photo + voice support
- **v0.2.0**: Multi-user support, conversation history, personality customization
- **v0.3.0**: Cloud deployment, authentication, monitoring
- **v1.0.0**: Public release, App Store companion app

## 📄 License

MIT © Humphrey Ahn
