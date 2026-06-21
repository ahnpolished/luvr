# Luvr Architecture

> Detailed technical architecture for the Luvr dating advice chatbot (Telegram primary, iMessage secondary).

## System Overview

Luvr is a multi-platform pipeline connecting messaging apps to an LLM-powered dating advice engine. The primary platform is **Telegram** via python-telegram-bot. An **iMessage** bridge via BlueBubbles + FastAPI is also available for Mac users.

Luvr also includes a **web onboarding frontend** (React + TypeScript + Vite) for alpha user authentication, Telegram linking, and Instagram context collection, served through the same FastAPI backend.

## Component Architecture

### 1. Telegram Bot (Primary)

The Telegram bot runs as a standalone Python process using `python-telegram-bot`.

**Key capabilities:**
- Long-polling mode (default) or webhook mode
- Message handlers for text, photo, voice, and tarot commands
- Command handlers for `/start`, `/link`
- Optional user allowlist via `TELEGRAM_ALLOWED_USER_IDS`
- Graceful SIGTERM/SIGINT shutdown
- Alpha user profile registry integration
- Usage limit enforcement per feature

**Architecture:**

```
LuvrBot
  ├── Application (python-telegram-bot)
  │   ├── CommandHandler("start", handle_start)
  │   ├── CommandHandler("link", handle_link)
  │   ├── MessageHandler(TEXT, handle_text)
  │   ├── MessageHandler(PHOTO, handle_photo)
  │   └── MessageHandler(VOICE, handle_voice)
  ├── LLM Client (injected via bot_data)
  ├── Bridge Client (Telegram API reply sender)
  └── Alpha Registry (profile lookup per request)
```

**Handlers** (`src/telegram/handlers.py`):

- `handle_start` — Welcome message with usage instructions
- `handle_link` — Deep-link URL for web onboarding + Telegram linking
- `handle_text` — Forwards message to LLM, applies user allowlist check
- `handle_photo` — Downloads photo, sends to vision-capable LLM
- `handle_voice` — Downloads voice note, transcribes via Whisper, sends transcription to LLM, optionally replies with TTS voice memo

**Entrypoints:**

```bash
# Direct module run
python -m src.telegram_server

# CLI with mode override
luvr-telegram --mode webhook --webhook-url https://example.com/webhook

# Via Makefile
make run-telegram
```

### 2. Web Onboarding Frontend

A React + TypeScript + Vite single-page app for alpha user onboarding.

**Screens** (`web/src/screens/`):
- `LandingScreen` — Entry point with alpha code input
- `AuthScreen` — Phone number verification / OTP
- `InstagramContextScreen` — Instagram handle + bio or self-summary
- `TelegramHandoffScreen` — Redirect back to Telegram

**State management**: `OnboardingProvider` context with step-based flow.

**Components**: PageShell, StepHeader, Button, Card, OTPInput, TextInput.

### 3. FastAPI Server (iMessage + Web Auth)

The FastAPI server serves two roles: iMessage webhook handling and alpha web auth endpoints.

**Endpoints:**
- `GET /health` — Health check
- `POST /webhook` — Receive incoming iMessages from BlueBubbles
- `POST /auth/alpha/exchange` — Exchange alpha invite code for session token + profile
- `GET /auth/alpha/profile` — Return linked alpha profile (requires Bearer token)
- `POST /auth/alpha/onboarding` — Complete onboarding with Instagram context / self-summary

### 3b. iMessage Bridge (BlueBubbles)

**BlueBubbles** is a self-hosted macOS server bridging iMessage to a REST API.

**Configuration:**
- Server runs on `http://localhost:1234` (configurable)
- Password-protected API access
- Webhook configured to POST new messages to Luvr's `/webhook` endpoint

### 4. Message Processing Pipeline

```
Incoming Message (Telegram or iMessage webhook)
    │
    ▼
MessageRouter / Handler dispatch
    │
    ├── "text"   → TextHandler  → LLM.generate_response()
    ├── "photo"  → PhotoHandler → download → LLM.analyze_image()
    ├── "voice"  → VoiceHandler → download → transcribe() → LLM.generate_response()
    │                                                   └─→ TTS (optional voice reply)
    └── "/tarot" → Tarot flow   → select cards → build prompt → LLM with card images
                                     │
                                     ▼
                              BridgeClient.send_message()
```

#### Text Handler
- Takes raw text from user
- Detects language (Korean/English)
- Sends to LLM with dating advisor system prompt
- Returns response text

#### Photo Handler
- Detects image attachments (JPEG, PNG, HEIC, WebP)
- Downloads image from Telegram or BlueBubbles
- Sends to vision-capable LLM for analysis
- Returns analysis + advice

#### Voice Handler
- Detects audio attachments (CAF, M4A, MP3, WAV, OGG/OPUS)
- Downloads audio
- Transcribes via OpenAI Whisper
- Feeds transcription to LLM with modified system prompt
- Optionally generates TTS voice reply via OpenAI TTS (`tts-1` or `tts-1-hd`)

### 5. LLM Integration

**Abstract interface** (`LLMClient`) with four implementations:

| Feature | OpenAI (gpt-4o-mini) | Anthropic (Claude) | DeepSeek | OpenCode (local) |
|---------|---------------------|-------------------|----------|------------------|
| Text generation | ✅ | ✅ | ✅ | ✅ |
| Vision/image | ✅ (GPT-4V) | ✅ (Claude Vision) | ✅ | ❌ (not yet) |
| Speed | Fast | Very fast | Fast | Fast (local) |
| API required | OpenAI key | Anthropic key | DeepSeek key | Local OpenCode server |
| Cost (input/1M) | $0.15 | $0.25 | $0.14 | Free (local) |
| Cost (output/1M) | $0.60 | $1.25 | $0.28 | Free (local) |
| Context window | 128K | 200K | 128K | Model-dependent |

**Provider selection**: Set `LLM_PROVIDER=openai`, `anthropic`, `deepseek`, or `opencode` in `.env`.

#### OpenCode Provider

The OpenCode provider connects to a locally running [OpenCode](https://github.com/sst/opencode) server (default: `http://localhost:54321`). It acts as a gateway to any model configured in your OpenCode instance.

#### DeepSeek Provider

Uses the DeepSeek API via an OpenAI-compatible client. Competitive pricing and strong performance.

### 6. Media Processing

#### Vision (Image Analysis)
- Uses the LLM provider's native vision capabilities
- Both OpenAI and Anthropic support base64-encoded images
- Images analyzed with dating-specific context prompts

#### Transcription (Whisper)
- Uses OpenAI Whisper API (`whisper-1` model)
- Supports all common audio formats
- Telegram voice notes are typically OGG/OPUS
- iMessage voice memos are typically CAF (Core Audio Format)

#### TTS (Text-to-Speech)
- Uses OpenAI TTS API (`tts-1` or `tts-1-hd`)
- Configurable voice: alloy, echo, fable, onyx, nova, shimmer (default: nova)
- Enabled by default when user sends a voice message (`TTS_ENABLED=true`)
- Falls back to text-only reply on TTS failure

### 7. Tarot Reading System

A deterministic UX flow for 3-card relationship tarot readings.

**Flow** (`src/tarot/flow.py`):
1. User triggers `/tarot` or natural language request
2. Three cards selected from the 22 Major Arcana
3. Cards mapped to positions: Situation → Tension → Next Move
4. Card images loaded from pre-generated assets (`src/tarot/images.py`)
5. Language-aware prompt built via `src/llm/tarot.py`
6. LLM generates a cohesive narrative reading
7. Response includes card images + reading text

**Usage limits**: 3 readings per user per month (enforced via `src/alpha/tarot_usage.py`).

### 8. Alpha User Management

#### Alpha Registry (`src/alpha/registry.py`)

A file-backed profile store for alpha users:
- Telegram user ↔ alpha profile linking
- Auth completion tracking
- Onboarding completion tracking
- Instagram context summary storage
- Weave trace label generation
- Usage counter management

#### Alpha Auth (`src/alpha_auth.py`)

- Pre-shared invite code gating (`ALPHA_INVITE_CODE` env var)
- HMAC-SHA256 session tokens (24-hour expiry)
- Short-lived linking tokens for Telegram→web deep-linking (10-minute expiry)

#### Usage Limits (`src/alpha/usage_limits.py`)

Per-feature quota enforcement:
- Voice messages: 10/month
- Tarot readings: 3/month
- Monthly reset policy

### 9. Memory Prototype (`src/memory/`)

A thin mem0 wrapper for per-user memory storage (research prototype, not wired into conversation flow):
- `PerUserMemoryStore` scopes every operation by `user_id`
- `Mem0Backend` protocol allows swapping real mem0 or fake backend
- `remember()` / `recall()` / `forget_all()` operations

### 10. Proactive Messaging (`src/proactive/`)

Deterministic copy builder for manual proactive check-ins:
- `ManualCheckinInput` with display name + optional context
- Generates friendly "quick check-in" message copy

### 11. Language Detection

Auto-detects Korean vs. English in user messages (`src/llm/language_detection.py`):
- Korean: uses Hangul character range
- Mixed: both scripts present
- English: default

Used to select appropriate system prompts and tarot reading language.

### 12. Evaluation Framework

#### DeepEval (`tests/eval/`)
- Relevance — how well responses match dating advice domain
- Safety — crisis recognition and appropriate resource provision
- Tone — empathetic, non-judgmental voice
- Korean eval cases for multilingual testing

#### Weave Conversation Eval (`src/eval_workflow.py`)
- Synthetic conversation eval cases (friend-likeness, safety, boundaries)
- Optional Weave integration for labeled trace runs
- `scripts/run_weave_conversation_eval.py` CLI entry point

#### Weave Spans (`src/weave_spans.py`)
- Conversation span attributes (message type, model, latency, user labels)
- Optional Weave SDK integration (gracefully falls back if not installed)

#### Eval Trace Policy (`src/eval_trace_policy.py`)
- Consent gate for alpha user traces
- Retention window: 7–30 days (configurable)
- Separates eval traces from product memory

## Data Flow

### Telegram Message Flow

```
1. User sends message in Telegram
2. python-telegram-bot receives Update via polling/webhook
3. Handler extracts message type and content
4. Alpha profile looked up via registry
5. Usage limits checked if applicable
6. Media downloaded (for photo/voice)
7. LLM call (optionally with vision/transcription)
8. Response sent back via Telegram API
9. Optional: TTS voice reply generated and sent
```

### Web Onboarding Flow

```
1. User sends /link in Telegram
2. Bot generates short-lived linking token
3. Deep-link URL returned to user
4. User opens URL in browser → web onboarding SPA
5. User enters alpha invite code
6. Server validates code, returns session token
7. User provides Instagram context (or skips)
8. Profile updated with auth_completed + onboarding_completed
9. User redirected back to Telegram
10. Bot confirms successful setup
```

## Security Considerations

### API Keys
- Stored in `.env` (never committed)
- Loaded via `pydantic-settings` with validation
- Passed to API clients at runtime

### Alpha Auth
- Pre-shared invite code (`ALPHA_INVITE_CODE`)
- HMAC-SHA256 session tokens with 24-hour expiry
- Short-lived linking tokens (10 minutes) for Telegram→web deep-linking
- Token verification on every authenticated endpoint

### Message Privacy
- Messages processed in-memory, not stored persistently
- Logs exclude message content
- Temporary media files cleaned up after processing
- Eval traces only stored for consenting alpha users

### Safety
- System prompt includes safety guidelines
- Crisis resources provided when needed
- Content filters at LLM level catch harmful content
- Rate limiting prevents abuse

See [`docs/SECURITY.md`](SECURITY.md) for the full security policy.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| LLM API error | Retry once, then send error message |
| Content filtered | Send user-friendly "try rephrasing" message |
| Unsupported media | Send explanation of supported types |
| Large attachment | Send size limit message |
| Empty message | Send friendly greeting |
| Missing API key | Clear error on startup with fix instructions |
| Auth token expired | 401 with "token expired" detail |
| Usage limit exceeded | Friendly message with remaining quota |
| TTS generation failure | Fall back to text-only reply |

## Performance Characteristics

| Operation | Expected Latency |
|-----------|-----------------|
| Text message → response | 1–3 seconds |
| Photo analysis | 3–8 seconds |
| Voice memo (transcribe + LLM) | 5–12 seconds |
| Voice memo + TTS reply | 8–20 seconds |
| Tarot reading (3 cards) | 5–10 seconds |
| Message send | <500ms |

## Infrastructure

- **DNS**: Cloudflare (Terraform-managed)
- **Hosting**: Vercel (web frontend) + Railway/Fly.io (Python backend)
- **CI/CD**: GitHub Actions
- **Config**: `infra/` directory with Terraform modules

## Future Architecture (v0.2+)

- **Database**: PostgreSQL for conversation history and alpha profiles
- **Persistent Memory**: Product-grade memory store (see [`docs/AUTH_MEMORY.md`](AUTH_MEMORY.md))
- **Multi-channel**: Unified user identity across Telegram, iMessage, Kakaotalk
- **Caching**: Redis for rate limiting and session management
- **Monitoring**: Sentry for errors, structured logging for metrics
- **Admin**: Dashboard for alpha user management and eval review
