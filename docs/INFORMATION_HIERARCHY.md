# Luvr — Information Hierarchy

## What the user provides

### 1. Identity (onboarding, one-time)
- Auth credential — phone OTP or email magic link (method TBD, HUM-1373)
- Nickname or preferred name (optional)

### 2. Context (onboarding, ≤4 steps)
The minimum context Luvr needs to give relevant advice.

- **Instagram handle or URL** — primary context signal; public profile bio, themes, visible interests extracted where accessible
- **Self-summary fallback** — short typed description when Instagram is private or unavailable; prompted casually, not with a form

> What additional structured context to collect (e.g. relationship status, dating preference) is an open research question (HUM-1362). Not confirmed for v0.1.

### 3. Conversation input (real-time, recurring)
- **Text** — questions, vents, situation descriptions
- **Photo** — screenshots of conversations, dating profiles, anything they want analyzed
- **Voice memo** — spoken thoughts, too long or emotional to type

---

## System information layers

### Layer 1 — Auth & identity
What the system needs to know who is talking.

| Field | Source | Notes |
|---|---|---|
| `user_id` | Generated at signup | Internal identifier |
| `telegram_user_id` | Telegram link step | Maps Telegram session to profile |
| `telegram_username` | Telegram (optional) | Display handle |
| `display_name` | Onboarding (optional) | From auth or self-provided |
| `nickname` | Onboarding (optional) | Used in LLM greeting |
| `email` | Auth flow (optional) | Only when provided via magic link auth |
| `auth_status` | Auth flow | Whether user has completed web auth |
| `linking_status` | Deep-link flow | Whether Telegram identity is linked to web profile |
| `onboarding_status` | Onboarding flow | Whether user has completed Instagram/context step |

### Layer 2 — User profile (context layer)
Static context that shapes every conversation. Collected once, optionally updated.

| Field | Source | Notes |
|---|---|---|
| `instagram_context_summary` | Instagram extraction or self-summary | Short inspectable blob; not a raw scraped dump |
| `allowlist_member` | Admin-set | Controls alpha access; used for Weave trace labels |

This layer is injected into the LLM system prompt as background context.

### Layer 3 — Usage limits
Counters tracked per user for v0.1 alpha enforcement.

| Field | Source | Notes |
|---|---|---|
| `voice_message_count` | Incremented per voice handler call | Enforced limit TBD |
| `tarot_reading_count` | Incremented per tarot call | Enforced limit TBD |

### Layer 4 — Conversation state (session layer)
Active context within a conversation window.

| Field | Source | Notes |
|---|---|---|
| `conversation_history` | Message exchange | Multi-turn context; not persisted long-term in v0.1 |
| `current_message` | Incoming message | Text, photo, or voice |
| `media_type` | Detected from message | Routes to correct handler |
| `transcription` | Whisper (voice only) | Converted to text before LLM |
| `vision_analysis` | Vision model (photo only) | Converted to text before LLM |

### Layer 5 — LLM execution layer
What the model sees at inference time.

| Field | Source | Notes |
|---|---|---|
| `system_prompt` | `prompts.py` | Core persona, tone, behavior rules |
| `instagram_context_summary` | Layer 2 | Injected as background |
| `conversation_history` | Layer 4 | Multi-turn context |
| `current_input` | Layer 4 | Processed message (text or converted) |

### Layer 6 — Safety layer
Evaluated on every response, not stored.

- Crisis keyword detection in input
- LLM escalation behavior when flagged
- Crisis resource injection in response when triggered

### Layer 7 — Operational / eval metadata
Not user-facing. Used for debugging and eval via Weave.

- Handler name, message type, latency, model used, prompt version
- Error category (never raw content)
- Alpha trace records for consenting alpha users (raw: 7–30 day retention; redacted/synthetic: longer)
- Allowlist-resolved user labels for Weave spans

---

## What is NOT stored (v0.1)

- Raw photos or voice files after processing
- Full conversation transcripts as product memory (persistent memory is v0.2+ research, HUM-1366)
- Long-term behavioral signals or preference learning
- X/Twitter data (deferred, HUM-1380)
- Private Instagram content or raw social graph dumps
- Payment or billing identity
