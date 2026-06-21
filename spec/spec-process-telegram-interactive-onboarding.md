---
title: Telegram Interactive Conversational Onboarding
version: 1.0
date_created: 2026-06-21
last_updated: 2026-06-21
owner: Luvr Team
tags: process, design, telegram, onboarding
---

# Introduction

This specification defines the interactive, conversational onboarding flow for the Luvr Telegram bot. It replaces the passive `/link` command-only approach with a proactive, stateful onboarding experience that detects unauthenticated users, guides them through profile setup conversationally, and supports an anonymous fallback path. The goal is to reduce friction between first contact and first meaningful conversation.

## 1. Purpose & Scope

**Purpose:** Define the end-to-end onboarding interaction between the Telegram bot, the web onboarding SPA, and the alpha user registry so that the bot can:

1. Detect when a Telegram user has not completed authentication (`auth_completed=false`).
2. Initiate a conversational onboarding prompt instead of a static `/link` command.
3. Provide a deep-link to the web onboarding flow that carries chatroom context via query parameters.
4. Detect successful completion of web onboarding and transition the user to full-feature access.
5. Offer an anonymous fallback path for users who decline web onboarding.

**Scope:** This specification covers the Telegram bot handler changes, the onboarding state machine, the anonymous-mode guardrails, the web→bot completion handoff mechanism, and the acceptance criteria for each path. It does NOT redesign the web onboarding SPA screens themselves (they remain as-is), nor does it change the alpha auth token scheme.

**Audience:** Backend engineers implementing the Telegram bot handlers, and the frontend engineer maintaining the web onboarding SPA.

**Assumptions:**
- The alpha user registry (`AlphaUserRegistry`) with `auth_completed` and `onboarding_completed` flags already exists.
- The web onboarding SPA (React + TypeScript + Vite) already exists at `web/`.
- The FastAPI server with `/auth/alpha/exchange` and `/auth/alpha/onboarding` endpoints already exists.
- The `build_linking_url()` function already embeds `telegram_user_id` and `telegram_chat_id` in the deep-link query string.

## 2. Definitions

| Term | Definition |
|------|------------|
| **Onboarding** | The end-to-end process of a new Telegram user authenticating via the web flow and providing Instagram context. |
| **Auth state** | A boolean flag (`auth_completed`) on the `AlphaUserProfile` indicating the user completed web authentication. |
| **Onboarding completion** | A boolean flag (`onboarding_completed`) on the `AlphaUserProfile` indicating the user finished the full web onboarding flow including Instagram context collection. |
| **Anonymous mode** | A fallback state where a user who declines web onboarding can still send messages and receive basic dating advice, but without personalized context or persona selection. |
| **Deep-link** | A URL carrying a signed HMAC-SHA256 `linking_token` with `telegram_user_id`, `telegram_chat_id`, and a 10-minute expiry. Opens the web onboarding SPA. |
| **Chatroom context** | The `telegram_chat_id` embedded in the deep-link, enabling the bot to associate the authenticated session with the originating Telegram chatroom. |
| **PTB** | python-telegram-bot, the library used for the Telegram bot. |
| **Onboarding gate** | The check at the start of each message handler that determines whether to proceed normally, prompt onboarding, or serve anonymous mode. |

## 3. Requirements, Constraints & Guidelines

- **REQ-001**: The bot SHALL detect when a Telegram user has not completed authentication (`auth_completed == false`) on any incoming message (text, photo, voice, command).
- **REQ-002**: When an unauthenticated user is detected for the first time in a session, the bot SHALL initiate a conversational onboarding prompt rather than silently processing the message.
- **REQ-003**: The conversational onboarding prompt SHALL offer two paths: (a) proceed to web onboarding via deep-link, or (b) continue as anonymous.
- **REQ-004**: If the user chooses web onboarding, the bot SHALL send a deep-link URL containing `telegram_user_id` and `telegram_chat_id` as query parameters, enabling the web flow to associate the session with the originating chatroom.
- **REQ-005**: The deep-link SHALL use the existing `build_linking_url()` function with a 10-minute expiry.
- **REQ-006**: When the web onboarding flow completes, the bot SHALL detect this and send a confirmation message in the originating chatroom ("you're all set", resuming full features).
- **REQ-007**: If the user chooses anonymous mode, the bot SHALL send an abbreviated welcome message, record the anonymous choice, and allow basic message processing without personalized context or persona selection.
- **REQ-008**: The bot SHALL NOT re-prompt for onboarding on every single message from an anonymous user — it SHALL track that onboarding was declined in the current conversation session.
- **REQ-009**: The bot SHALL re-check auth state on each incoming message so that a user who completes web onboarding while the chat is open immediately transitions to fully-authenticated mode.
- **REQ-010**: The existing `/start` handler SHALL be modified to check auth state and route to the onboarding flow when appropriate, rather than always sending the static `WELCOME_MESSAGE`.
- **REQ-011**: The existing `/link` command SHALL continue to work as a manual fallback for users who need to regenerate their deep-link.
- **REQ-012**: Anonymous users SHALL have access to text, photo, and voice message processing, but SHALL NOT have access to persona selection (`/persona`), tarot readings (`/tarot`), or personalized Instagram context in prompts.
- **REQ-013**: The onboarding completion detection mechanism SHALL use the existing `AlphaUserRegistry.has_completed_auth()` and `has_completed_onboarding()` methods. No new polling infrastructure is required.

- **CON-001**: The conversational onboarding prompt SHALL fit within Telegram's 4096-character message limit.
- **CON-002**: The onboarding state machine SHALL NOT persist conversation state beyond the AlphaUserProfile flags — in-memory session state (e.g., "declined onboarding this session") is acceptable and resets on bot restart.
- **CON-003**: All deep-links SHALL use HMAC-SHA256 signing with the existing `ALPHA_AUTH_SECRET`.

- **GUD-001**: The onboarding prompt tone SHALL match Luvr's brand voice: warm, honest, non-pushy. No guilt-tripping the user into signing up.
- **GUD-002**: The anonymous welcome message SHALL be shorter than the full onboarding prompt and set appropriate expectations about limited features.
- **GUD-003**: The onboarding gate logic SHALL be implemented as a reusable decorator or middleware function rather than duplicated in each handler.

- **PAT-001**: Use a `check_onboarding(update, context) -> OnboardingDecision` pattern where `OnboardingDecision` is an enum: `PROCEED` (already authed), `PROMPT` (first detection), `ANONYMOUS` (declined, process anonymously), `PENDING` (link sent, waiting for completion).

## 4. Interfaces & Data Contracts

### 4.1 OnboardingGate — Bot-side middleware

A single function called at the top of each message handler:

```python
from enum import Enum, auto

class OnboardingDecision(Enum):
    PROCEED = auto()       # Already authenticated — process message normally
    PROMPT = auto()        # Unauthenticated, first detection — send onboarding prompt
    PENDING = auto()       # Link sent, awaiting web completion — send waiting message
    ANONYMOUS = auto()     # User declined — process in anonymous mode
    JUST_COMPLETED = auto() # Auth was previously false, now true — send welcome-back


async def onboarding_gate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> OnboardingDecision:
    """Determine the onboarding action for an incoming message."""
    ...
```

### 4.2 Deep-link URL format (unchanged from existing `build_linking_url`)

```
https://<ALPHA_WEB_BASE_URL>/auth/alpha/exchange?linking_token=<signed_token>
```

The `linking_token` payload decodes to:

```json
{
  "user_id": "link_123456789",
  "telegram_user_id": "987654321",
  "telegram_chat_id": "-1001234567890",
  "iat": 1719000000,
  "purpose": "telegram_web_linking"
}
```

### 4.3 Web onboarding completion → Bot handoff

After the web onboarding SPA successfully calls `POST /auth/alpha/onboarding`, the server sets `auth_completed=true` and `onboarding_completed=true` on the profile.

The **next message** the user sends in the Telegram chat triggers `onboarding_gate()` which detects:
- `has_completed_auth() == true` (was `false` previously in this session)
- Returns `OnboardingDecision.JUST_COMPLETED`
- Bot sends a welcome-back message and begins normal processing

There is **no push notification or callback** from the web app to the bot. Detection is pull-based on next user message.

### 4.4 Session state (in-memory, non-persistent)

```python
# Keyed by (telegram_user_id, telegram_chat_id) tuple
# Tracks onboarding decisions within the current bot process lifetime
_onboarding_sessions: dict[tuple[int, int], str] = {}
# Values: "prompted" | "link_sent" | "anonymous" | "completed"
```

This session state is used to avoid re-prompting on every message. It resets on bot restart (acceptable for v0.1 — the profile flags are the source of truth).

## 5. Acceptance Criteria

- **AC-001**: Given a Telegram user with `auth_completed == false` sends their first message, When the bot receives it, Then the bot replies with the conversational onboarding prompt offering "Set up profile" and "Continue anonymously" options.

- **AC-002**: Given the onboarding prompt is displayed, When the user taps the "Set up profile" button, Then the bot replies with a deep-link URL that includes `telegram_user_id` and `telegram_chat_id` in the `linking_token`.

- **AC-003**: Given a user has received the deep-link but not yet completed web onboarding, When the user sends another message, Then the bot replies with a gentle reminder ("Your setup link is still open!") rather than re-sending the onboarding prompt.

- **AC-004**: Given a user completed web onboarding (auth_completed=true, onboarding_completed=true), When the user sends their next message in the chatroom, Then the bot sends a welcome-back confirmation ("You're all set! 💝") and proceeds to process the message normally.

- **AC-005**: Given a user chooses "Continue anonymously", When they send any message, Then the bot processes it with basic dating advice but without Instagram context, persona customization, or tarot access.

- **AC-006**: Given an anonymous user sends `/persona`, When the persona command is triggered, Then the bot replies with a message indicating persona selection requires setting up a profile first, and offers the onboarding link again.

- **AC-007**: Given an anonymous user sends `/tarot`, When the tarot command is triggered, Then the bot replies with a message indicating tarot readings require setting up a profile first, and offers the onboarding link again.

- **AC-008**: Given a fully authenticated user (`auth_completed == true`) who has already completed onboarding, When they send any message or command, Then the onboarding gate returns `PROCEED` and the message is processed as before this specification (no regression).

- **AC-009**: Given an anonymous user sends subsequent messages in the same bot process session, When the onboarding gate is checked, Then it returns `ANONYMOUS` directly (no re-prompt).

- **AC-010**: Given an anonymous user restarts the bot process (session cleared) and sends a message, When the onboarding gate is checked, Then it returns `PROMPT` again (since `auth_completed` is still `false` and session state was lost).

- **AC-011**: The `/link` command SHALL continue to work for any user (authenticated or not) and return a fresh deep-link URL.

## 6. Test Automation Strategy

- **Test Levels**: Unit (onboarding_gate logic), Integration (bot handler + registry interaction), End-to-End (full Telegram → web → back flow)

- **Frameworks**: pytest for Python (bot logic), Vitest + React Testing Library for web (unchanged), python-telegram-bot's `CallbackContext` mocking for handler tests.

- **Test Data Management**: Use an in-memory `AlphaUserRegistry` with a temporary `_RegistryState`. Pre-seed profiles with known `auth_completed` and `onboarding_completed` states for each test case.

- **CI/CD Integration**: Run onboarding gate unit tests and handler integration tests in existing GitHub Actions CI pipeline alongside existing tests.

- **Coverage Requirements**: 100% branch coverage on `onboarding_gate()` function. Happy-path integration tests for PROCEED, PROMPT, PENDING, ANONYMOUS, and JUST_COMPLETED decisions.

- **Performance Testing**: N/A — the onboarding gate is a local registry lookup with no network I/O. Expected latency <5ms.

### Test Cases (pytest-style)

```python
# tests/test_onboarding_gate.py

async def test_proceed_when_auth_completed():
    """AC-008: Authenticated user proceeds normally."""
    ...

async def test_prompt_when_first_contact_unauthenticated():
    """AC-001: Unauthenticated user gets onboarding prompt."""
    ...

async def test_pending_when_link_sent_but_not_completed():
    """AC-003: Awaiting completion shows reminder."""
    ...

async def test_just_completed_when_auth_flips_to_true():
    """AC-004: Freshly authenticated user gets welcome-back."""
    ...

async def test_anonymous_mode_processes_messages():
    """AC-005: Anonymous user gets basic processing."""
    ...

async def test_anonymous_re_prompt_on_restart():
    """AC-010: Lost session state triggers re-prompt."""
    ...

async def test_anonymous_blocked_from_persona():
    """AC-006: /persona blocked for anonymous."""
    ...

async def test_anonymous_blocked_from_tarot():
    """AC-007: /tarot blocked for anonymous."""
    ...
```

## 7. Rationale & Context

**Why conversational instead of command-driven?** The current `/link` flow requires the user to know a command exists. Many users type `/start` or just start chatting. By making onboarding proactive, we catch users in their natural flow. A conversational prompt also feels more like Luvr's brand (warm, helpful friend) than a CLI command.

**Why pull-based completion detection instead of push/callback?** The alternative would require the FastAPI server to communicate back to the Telegram bot process (e.g., via an internal API, Redis pub/sub, or a webhook). For v0.1, pull-based detection (checking `has_completed_auth()` on next message) is simpler, requires no new infrastructure, and the UX difference is minimal: the user sends one more message after completing onboarding and immediately gets the welcome-back response. The user was going to send a message anyway — that's the point of onboarding.

**Why anonymous mode?** Not every user will trust a bot with personal information on first contact. Anonymous mode lets them try the product before committing. It's a conversion mechanism: once they see value, they'll be more willing to set up a profile.

**Why in-memory session state?** To avoid re-prompting on every message without adding database complexity. The source of truth remains `AlphaUserProfile.auth_completed`. Session state is a UX optimization, not a data store. Losing it on restart is acceptable — the user will be re-prompted once, which is still better than being prompted on every single message.

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: Telegram Bot API — PTB receives `Update` objects and sends messages. No Telegram API changes needed.

### Third-Party Services
- N/A — this specification introduces no new third-party services.

### Infrastructure Dependencies
- **INF-001**: Existing FastAPI server must remain available to serve the web onboarding SPA and process `/auth/alpha/exchange` and `/auth/alpha/onboarding` requests. This specification does not change the server.

### Data Dependencies
- **DAT-001**: `AlphaUserRegistry` — the profile store must correctly report `auth_completed` and `onboarding_completed` flags. The web onboarding sets these via `update_profile()`. This specification depends on those flags being reliable.

### Technology Platform Dependencies
- **PLT-001**: python-telegram-bot (existing dependency) — used for `Update`, `ContextTypes`, `InlineKeyboardMarkup`, `InlineKeyboardButton`, and `CallbackQueryHandler`.
- **PLT-002**: pydantic (existing dependency) — `AlphaUserProfile` model.

### Compliance Dependencies
- N/A — this specification introduces no new compliance requirements beyond existing alpha auth practices.

## 9. Examples & Edge Cases

### 9.1 Happy path: New user, full onboarding

```
User: "hey"
Bot:  "💝 Hey! I'm Luvr, your personal dating advice assistant.
      Before we dive in — want to set up your profile? It takes
      about 2 minutes and I'll be able to give you much better advice.

      [✨ Set up profile]  [👋 Continue anonymously]"

User: [taps ✨ Set up profile]
Bot:  "Awesome! Here's your personal setup link:
      https://luvr.app/auth/alpha/exchange?linking_token=...
      (expires in 10 min) — I'll be here when you're done! 💝"

--- User completes web onboarding (Landing → Auth → Instagram → Handoff) ---

User: "ok done"
Bot:  "You're all set, [Name]! 💝 Send me anything — texts, photos,
      voice memos. I'm here for you.

      (User's original message "ok done" is now processed normally)"
```

### 9.2 Anonymous path

```
User: "hey"
Bot:  [onboarding prompt as above]

User: [taps 👋 Continue anonymously]
Bot:  "No problem! I'll give you my best advice either way. Just
      know some features like personalized context and tarot
      readings need a profile. If you change your mind, just
      type /link anytime.

      What's on your mind? 💝"

User: "I need dating advice"
Bot:  [Processes normally with basic system prompt, no Instagram context]
```

### 9.3 Edge case: User sends message while link is pending

```
User: [received deep-link but hasn't opened it yet]
User: "actually wait"
Bot:  "Your setup link is still open! No rush — I'll be here when
      you're ready. Want me to resend the link? Just type /link. 💝"
```

### 9.4 Edge case: Anonymous user tries restricted features

```
User (anonymous): "/persona"
Bot:  "Personas are available once you set up your profile!
      Want to do that now?

      [✨ Set up profile]  [Not now]"

User (anonymous): "/tarot"
Bot:  "🔮 Tarot readings need a profile — once you're set up,
      you'll get 3 free readings per month! Want to set up
      your profile?

      [✨ Set up profile]  [Not now]"
```

### 9.5 Edge case: Web onboarding completes mid-conversation

```
User: "hey"
Bot:  [onboarding prompt]

User: [taps ✨ Set up profile → opens web → completes onboarding]

User: "I'm back"
Bot:  "You're all set, [Name]! 💝

      [processes "I'm back" normally as dating advice request]"
```

### 9.6 Edge case: Deep-link expires

```
User: [received link 15 minutes ago, didn't open]
Bot:  [not proactively notified of expiry — link is validated server-side]

User: [opens expired link in browser]
Web:  "This link has expired. Please request a new one from the bot."

User: "/link"
Bot:  [sends fresh deep-link]
```

### 9.7 Edge case: User who completed onboarding in another chatroom

```
User in Chatroom A: [completes onboarding]
User in Chatroom B: "hey"

Bot checks: has_completed_auth(telegram_user_id=123) → true
Bot returns: PROCEED — user is authenticated globally, not per-chatroom
```

Note: `auth_completed` is per Telegram user, NOT per chatroom. This means a user who completes onboarding in one chatroom is authenticated in all chatrooms. This is the intended behavior for v0.1.

## 10. Validation Criteria

- **VAL-001**: All handlers (`handle_text`, `handle_photo`, `handle_voice`, `handle_start`, `handle_persona`, `handle_tarot`) pass through the onboarding gate before their existing logic.
- **VAL-002**: `onboarding_gate()` returns `PROCEED` when `has_completed_auth()` is `true`.
- **VAL-003**: `onboarding_gate()` returns `PROMPT` on first detection of `has_completed_auth() == false`.
- **VAL-004**: `onboarding_gate()` returns `PENDING` when session state is `"link_sent"` and auth is still incomplete.
- **VAL-005**: `onboarding_gate()` returns `ANONYMOUS` when session state is `"anonymous"`.
- **VAL-006**: `onboarding_gate()` returns `JUST_COMPLETED` when auth was previously `false` this session but is now `true`.
- **VAL-007**: Anonymous users receive a functional response to text, photo, and voice messages.
- **VAL-008**: Anonymous users are blocked from `/persona` and `/tarot` with a helpful message offering profile setup.
- **VAL-009**: The existing `/link` command still works and is unaffected by the onboarding gate.
- **VAL-010**: No regression in behavior for users with `auth_completed == true` (existing tests pass).
- **VAL-011**: The inline keyboard buttons in the onboarding prompt use `CallbackQueryHandler` patterns consistent with the existing persona callback implementation.

## 11. Related Specifications / Further Reading

- [ARCHITECTURE.md](/docs/ARCHITECTURE.md) — Overall system architecture
- [DESIGN_BRIEF.md](/docs/DESIGN_BRIEF.md) — Brand voice and tone guidelines
- [AUTH_MEMORY.md](/docs/AUTH_MEMORY.md) — Authentication and memory architecture planning
- [alpha_auth.py](/src/alpha_auth.py) — Existing deep-link and token infrastructure
- [alpha/registry.py](/src/alpha/registry.py) — AlphaUserRegistry with auth_completed/onboarding_completed flags
- [telegram/handlers.py](/src/telegram/handlers.py) — Current handler implementations to modify
- [telegram/bot.py](/src/telegram/bot.py) — Handler registration and dependency injection
