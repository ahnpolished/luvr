# Luvr Architecture

> Detailed technical architecture for the Luvr dating advice chatbot (iMessage + Telegram).

## System Overview

Luvr is a multi-platform pipeline that connects iMessage or Telegram to an LLM-powered dating advice engine. It supports two bridges:

- **iMessage** via BlueBubbles (self-hosted macOS bridge) + FastAPI server
- **Telegram** via python-telegram-bot (polling or webhook mode)

Both platforms share the same LLM integration layer, media processing pipeline, and configuration system.

## Component Architecture

### 1. iMessage Bridge (BlueBubbles)

**BlueBubbles** is a self-hosted macOS server that bridges iMessage to a REST API. It runs on the same Mac where iMessage is signed in.

**Key capabilities:**
- REST API for sending/receiving iMessages
- Webhook support for push-style message delivery
- Attachment download/upload
- Chat management

**Configuration:**
- Server runs on `http://localhost:1234` (configurable)
- Password-protected API access
- Webhook configured to POST new messages to Luvr's `/webhook` endpoint

### 2. Bot Server (FastAPI)

The bot server is a FastAPI application that:

1. **Receives** webhook payloads from BlueBubbles
2. **Routes** messages by type (text, photo, voice)
3. **Processes** through appropriate handlers
4. **Sends** responses back via BlueBubbles API

**Endpoints:**
- `GET /health` — Health check
- `POST /webhook` — Receive incoming iMessages

### 3. Message Processing Pipeline

```
Webhook Payload
    │
    ▼
MessageRouter.route()
    │
    ├── "text"  → TextHandler  → LLM.generate_response()
    ├── "photo" → PhotoHandler → download_attachment() → LLM.analyze_image()
    └── "voice" → VoiceHandler → download_attachment() → transcribe() → LLM.generate_response()
                                     │
                                     ▼
                              BlueBubblesClient.send_message()
```

#### Text Handler
- Takes raw text from iMessage
- Sends to LLM with dating advisor system prompt
- Returns response text

#### Photo Handler
- Detects image attachments (JPEG, PNG, HEIC, WebP)
- Downloads image from BlueBubbles
- Sends to vision-capable LLM for analysis
- Returns analysis + advice

#### Voice Handler
- Detects audio attachments (CAF, M4A, MP3, WAV)
- Downloads audio from BlueBubbles
- Transcribes via OpenAI Whisper
- Feeds transcription to LLM with modified system prompt
- Returns advice based on transcribed content

### 3b. Telegram Bot (python-telegram-bot)

The Telegram bot runs as a standalone Python process using `python-telegram-bot`.

**Key capabilities:**
- Long-polling mode (default) or webhook mode
- Message handlers for text, photo, and voice
- Command handler for `/start`
- Optional user allowlist via `TELEGRAM_ALLOWED_USER_IDS`
- Graceful SIGTERM/SIGINT shutdown

**Architecture:**

```
LuvrBot
  ├── Application (python-telegram-bot)
  │   ├── CommandHandler("start", handle_start)
  │   ├── MessageHandler(TEXT, handle_text)
  │   ├── MessageHandler(PHOTO, handle_photo)
  │   └── MessageHandler(VOICE, handle_voice)
  ├── LLM Client (injected via bot_data)
  └── Bridge Client (Telegram API reply sender)
```

**Handlers** (`src/telegram/handlers.py`):

- `handle_start` — Welcome message with usage instructions
- `handle_text` — Forwards message to LLM, applies user allowlist check
- `handle_photo` — Downloads photo, sends to vision-capable LLM
- `handle_voice` — Downloads voice note, transcribes via Whisper, sends transcription to LLM

**Entrypoints:**

```bash
# Direct module run
python -m src.telegram_server

# CLI with mode override
luvr-telegram --mode webhook --webhook-url https://example.com/webhook

# Via Makefile
make run-telegram
```

### 4. LLM Integration

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

The OpenCode provider connects to a locally running [OpenCode](https://github.com/sst/opencode) server (default: `http://localhost:54321`). It acts as a gateway to any model configured in your OpenCode instance — you control the underlying model via the server, not Luvr.

```env
LLM_PROVIDER=opencode
OPENCODE_BASE_URL=http://localhost:54321
OPENCODE_PROVIDER_ID=deepseek
LLM_MODEL=deepseek-chat
```

#### DeepSeek Provider

Uses the DeepSeek API via an OpenAI-compatible client. DeepSeek offers competitive pricing and strong performance.

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-deepseek-key
LLM_MODEL=deepseek-chat
```

### 5. Media Processing

#### Vision (Image Analysis)
- Uses the LLM provider's native vision capabilities
- Both OpenAI and Anthropic support base64-encoded images
- Images are analyzed with dating-specific context prompts

#### Transcription (Whisper)
- Uses OpenAI Whisper API (`whisper-1` model)
- Supports all common audio formats
- iMessage voice memos are typically `.caf` (Core Audio Format)
- Transcription is synchronous (Whisper doesn't have an async SDK yet)

## Data Flow

### Incoming Message Flow

```
1. User sends iMessage → iPhone
2. BlueBubbles on Mac detects new message
3. BlueBubbles sends webhook POST to Luvr /webhook
4. Luvr parses payload and determines message type
5. Appropriate handler processes the message
6. Handler calls LLM (and optionally Whisper)
7. LLM generates response
8. Luvr calls BlueBubbles API to send response
9. BlueBubbles sends iMessage back to user
10. User receives response in iMessage
```

### Webhook Payload Format

```json
{
  "chatGuid": "iMessage;-;+1234567890",
  "text": "Should I text him back tonight?",
  "subject": "",
  "sender": "+1234567890",
  "isFromMe": false,
  "attachments": [
    {
      "guid": "attachment-uuid",
      "mimeType": "image/jpeg",
      "size": 102400,
      "transferState": 1
    }
  ]
}
```

## Security Considerations

### API Keys
- Stored in `.env` (never committed)
- Loaded via `pydantic-settings` with validation
- Passed to API clients at runtime

### Message Privacy
- Messages are processed in-memory, not stored persistently
- Logs exclude message content
- Temporary media files are cleaned up after processing

### Safety
- System prompt includes safety guidelines
- Crisis resources are provided when needed
- Content filters at LLM level catch harmful content
- Rate limiting prevents abuse

## Error Handling

| Scenario | Behavior |
|----------|----------|
| BlueBubbles unreachable | Send error message to user |
| LLM API error | Retry once, then send error message |
| Content filtered | Send user-friendly "try rephrasing" message |
| Unsupported media | Send explanation of supported types |
| Large attachment | Send size limit message |
| Empty message | Send friendly greeting |

## Performance Characteristics

| Operation | Expected Latency |
|-----------|-----------------|
| Text message → response | 1-3 seconds |
| Photo analysis | 3-8 seconds |
| Voice memo (transcribe + LLM) | 5-12 seconds |
| BlueBubbles send message | <500ms |

### 6. Evaluation Framework (DeepEval)

Luvr includes a DeepEval-based evaluation suite (`tests/eval/`) to assess AI output quality.

**Metrics:**
- Relevance — how well responses match the dating advice domain
- Safety — crisis recognition and appropriate resource provision
- Tone — empathetic, non-judgmental voice

**Commands:**
```bash
make eval         # Fast deterministic eval tests
make eval-slow    # Full eval suite (includes LLM-dependent tests)
make eval-all     # Every eval test
```

## Future Architecture (v0.2+)

- **Database**: PostgreSQL for conversation history
- **Multi-user**: User identification and session management
- **Caching**: Redis for common responses and rate limiting
- **Deployment**: Docker + cloud hosting (Fly.io / Railway)
- **Monitoring**: Sentry for errors, Prometheus for metrics
