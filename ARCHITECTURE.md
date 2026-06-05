# Luvr Architecture

> Detailed technical architecture for the Luvr iMessage dating advice chatbot.

## System Overview

Luvr is a pipeline that connects iMessage to an LLM-powered dating advice engine. It uses BlueBubbles as an iMessage bridge and FastAPI as the bot server.

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

### 4. LLM Integration

**Abstract interface** (`LLMClient`) with two implementations:

| Feature | OpenAI (gpt-4o-mini) | Anthropic (claude-3-haiku) |
|---------|---------------------|---------------------------|
| Text generation | ✅ | ✅ |
| Vision/image | ✅ (GPT-4V) | ✅ (Claude Vision) |
| Speed | Fast | Very fast |
| Cost (input/1M) | $0.15 | $0.25 |
| Cost (output/1M) | $0.60 | $1.25 |
| Context window | 128K | 200K |

**Provider selection**: Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` in `.env`.

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

## Future Architecture (v0.2+)

- **Database**: PostgreSQL for conversation history
- **Multi-user**: User identification and session management
- **Caching**: Redis for common responses and rate limiting
- **Deployment**: Docker + cloud hosting (Fly.io / Railway)
- **Monitoring**: Sentry for errors, Prometheus for metrics
