---
title: Luvr Tarot — Interactive Telegram Mini App Specification
version: 1.0
date_created: 2026-06-21
last_updated: 2026-06-21
owner: Luvr Team
tags: design, app, telegram-mini-app, tarot
---

# Introduction

This specification defines the Luvr Tarot interactive reading experience — a Telegram Mini App that extends the existing deterministic 3-card tarot into a rich, human-like tarot reading with ceremony, conversation, and narrative. The experience is centered around a **StellaCloud Orb** — a celestial, nebula-like sphere that serves as the reader's voice and the emotional anchor of the interaction.

The design is imported from `Luvr Tarot.dc.html` (Claude Design) and adapted to React + TypeScript with a Python FastAPI backend.

## 1. Purpose & Scope

**Purpose:** Deliver a 3–5 minute interactive tarot reading experience inside Telegram Mini App. The user sets an intention, draws three cards from a tactile swipe fan, receives a card-by-card interpretation with conversational dialogue, and gets a synthesized narrative at the end.

**Scope:**
- React + TypeScript frontend with three screens: Ritual, Reveal, Reflect
- Platform-agnostic tarot engine in Python (reuses existing `src/llm/` providers)
- FastAPI endpoints for session management and card interpretations
- StellaCloud Orb — a celestial nebula sphere with infinite animated transitions, voice interaction, and state-driven visual modes
- Card fan with swipe/parallax for card selection
- 3D card flip animations and conversational transcript
- Voice input (SpeechRecognition) and text-to-speech output (SpeechSynthesis)

**Out of Scope (v1):**
- Minor Arcana card images (assets exist but use Major Arcana only for v1)
- Multi-spread support beyond 3-card relationship spread
- Reading history / saved readings
- Audio/voice mode beyond browser Speech APIs
- Multi-language support
- Social sharing features

**Audience:** Luvr users on Telegram, dating-advice seekers.

## 2. Definitions

| Term | Definition |
|------|-----------|
| **StellaCloud Orb** | A celestial nebula-like sphere at the center of the experience. Composed of conic gradient layers, particle systems, and state-driven glow/breathing/pulsing animations. Serves as the visual representation of the reader's voice. |
| **Fan** | The horizontal scrollable card deck UI where users swipe and tap to select three cards |
| **Gate** | A pause point during the reading phase where the reader asks the user a question ("Does that land?") and waits for a response before continuing |
| **Ritual** | Phase 1 — setting intention and drawing cards |
| **Reveal** | Phase 2 — card-by-card interpretation with conversational dialogue |
| **Reflect** | Phase 3 — synthesis narrative and takeaway |
| **Reader Persona** | The distinct voice of the tarot reader — archetypal but warm, interpretive not declarative, grounded not mystical |
| **Session** | A complete tarot reading state, persisted server-side for 24 hours |
| **Telegram Mini App** | A web application launched from within Telegram, with access to Telegram WebApp API |
| **DC** | Claude Design Component — the source design format (`support.js` runtime + `DCLogic` components) |

## 3. Requirements, Constraints & Guidelines

### Architectural Requirements

- **ARC-001**: The tarot engine (`src/tarot/engine.py`) shall be platform-agnostic with no Telegram-specific coupling
- **ARC-002**: The frontend shall be a React + TypeScript + Vite application reusing the existing `web/` stack
- **ARC-003**: Session state shall be persisted server-side with 24-hour TTL
- **ARC-004**: LLM calls shall reuse existing `src/llm/` providers with three prompt roles: "ritualist", "reader", "weaver"
- **ARC-005**: The existing `src/tarot/flow.py` (text-chat tarot) shall remain unchanged alongside the new engine

### Visual & UX Requirements

- **VIS-001**: The StellaCloud Orb shall have four visual states: idle, listening, speaking, thinking — each with distinct animation patterns
- **VIS-002**: The orb shall use infinite conic gradient rotations (clockwise and counter-clockwise) at different speeds for a celestial nebula effect
- **VIS-003**: The orb shall have a particle/ember system floating upward from the bottom of the screen (ambient atmosphere)
- **VIS-004**: The card fan shall support horizontal swipe with parallax (center cards larger, edge cards smaller and rotated)
- **VIS-005**: Card flip shall be a 3D rotateY animation with cubic-bezier easing
- **VIS-006**: The reader's text shall appear with a progressive reveal (character-by-character or word-by-word fade-in)
- **VIS-007**: Design tokens shall extend the existing `web/src/styles/tokens.css` with additional tarot-specific variables
- **VIS-008**: Overall aesthetic: dark, moody, celestial — deep brown/black background with coral (#FF6B61) accent and gold (#C9A24B) highlights

### Functional Requirements

- **FUN-001**: User shall be able to set intention via text input OR voice (SpeechRecognition)
- **FUN-002**: User shall be able to use quick-reply chips for common intentions
- **FUN-003**: The reader shall mirror the intention back in the tarot persona voice before card draw
- **FUN-004**: User shall swipe through a fan of 22 Major Arcana cards and tap 3 to select
- **FUN-005**: Selected cards shall animate into a "held" row above the fan
- **FUN-006**: User shall be able to deselect a held card by tapping it
- **FUN-007**: Each card shall flip with a 3D animation to reveal its interpretation
- **FUN-008**: After each card's interpretation, the reader shall ask a resonance check ("Does that land?")
- **FUN-009**: User shall be able to respond: "That resonates", "Not quite", "Tell me more"
- **FUN-010**: "Not quite" shall allow free-text correction; reader adapts the interpretation
- **FUN-011**: "Tell me more" shall trigger a deeper interpretation (one deepen per session max)
- **FUN-012**: After all three cards, the reader shall deliver a synthesis narrative connecting all cards
- **FUN-013**: A one-line takeaway shall be extracted and emphasized
- **FUN-014**: Transport controls (play/pause, rewind, skip) shall be available during the reading
- **FUN-015**: Voice output (TTS via SpeechSynthesis) shall be toggleable (mute/unmute)
- **FUN-016**: At end, user shall be able to replay, start new reading, or save (screenshot prompt in v1)

### Technical Constraints

- **CON-001**: No new dependencies beyond existing Python + React stack
- **CON-002**: Total LLM tokens per session shall not exceed ~2,500 tokens
- **CON-003**: Card flip animations shall be GPU-accelerated (use `transform` and `will-change`)
- **CON-004**: The fan shall handle touch and pointer events for mobile Telegram Mini App
- **CON-005**: Voice recognition shall degrade gracefully (fallback to text-only when unavailable)
- **CON-006**: Session shall be resumable if Mini App is closed mid-reading
- **CON-007**: Single-card fan components must render at 60fps during swipe

### Security Requirements

- **SEC-001**: Session IDs shall be cryptographically random (uuid4)
- **SEC-002**: Card draws shall happen server-side (not client-side) to prevent manipulation
- **SEC-003**: API endpoints shall validate the session token from Telegram WebApp initData

### Guidelines

- **GUD-001**: The reader persona shall be consistent across all LLM calls (same system prompt preamble)
- **GUD-002**: Interpretations shall be offerings, not pronouncements — "This could mean..." not "This means..."
- **GUD-003**: Every reading shall end with something grounded and actionable
- **GUD-004**: Animations shall use CSS-only where possible; use React state for orchestration only

## 4. Interfaces & Data Contracts

### 4.1 Python Data Models

```python
from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4

class Phase(str):
    RITUAL = "ritual"
    REVEAL = "reveal"
    REFLECT = "reflect"

@dataclass
class Card:
    slug: str                    # e.g. "star", "fool"
    name: str                    # e.g. "The Star"
    arcana: Literal["major", "minor"]
    suit: str | None            # cups, pentacles, swords, wands
    is_reversed: bool
    position_meaning: str        # e.g. "Where you are"

@dataclass
class Message:
    speaker: Literal["reader", "user"]
    text: str
    context: str | None          # "intention", "card_1_initial", "card_1_deepen", etc.

@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    phase: str = Phase.RITUAL
    intention: str | None = None
    drawn_cards: list[Card] = field(default_factory=list)
    current_card_index: int | None = None
    dialogue: list[Message] = field(default_factory=list)
    deepened_on: set[int] = field(default_factory=set)
    reflection: str | None = None
    takeaway: str | None = None
    created_at: float = 0.0
    expires_at: float = 0.0
```

### 4.2 Engine API

```python
from typing import Literal, Union
from dataclasses import dataclass

@dataclass
class SetIntentionAction:
    kind: Literal["set_intention"]
    text: str

@dataclass
class DrawCardsAction:
    kind: Literal["draw_cards"]
    count: int = 3

@dataclass
class RespondAction:
    kind: Literal["respond"]
    card_index: int
    response: Literal["resonates", "not_quite", "tell_me_more"]
    correction_text: str | None = None

@dataclass
class ContinueAction:
    kind: Literal["continue"]

Action = SetIntentionAction | DrawCardsAction | RespondAction | ContinueAction

def advance(session: Session, action: Action) -> tuple[Session, UIInstruction]:
    """Advance the session state with a user action."""
    ...
```

### 4.3 REST API Endpoints

All endpoints are prefixed with `/api/tarot`.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tarot/session` | Create new session. Returns `{ session_id, phase, ui }` |
| `POST` | `/api/tarot/session/{id}/action` | Advance session with action. Body: `{ kind, ...params }`. Returns `{ session_id, phase, ui, cards?, messages? }` |
| `GET` | `/api/tarot/session/{id}` | Fetch current session state (for resume) |

### 4.4 Frontend API Client

```typescript
interface TarotAPI {
  createSession(): Promise<SessionState>;
  advance(sessionId: string, action: Action): Promise<SessionState>;
  getSession(sessionId: string): Promise<SessionState>;
}

interface SessionState {
  session_id: string;
  phase: 'ritual' | 'reveal' | 'reflect';
  ui: UIInstruction;
  cards?: CardData[];
  messages?: MessageData[];
}
```

### 4.5 Card Image Assets

Card image paths follow the existing convention in `src/tarot/images.py`:
- Card face: `/assets/tarot/{slug}.webp` (e.g., `/assets/tarot/star.webp`)
- Card back: `/assets/tarot/card_back.png`
- 22 Major Arcana: `fool` through `world`
- All images exist on disk at `assets/tarot/`

## 5. Acceptance Criteria

- **AC-001**: Given the Mini App opens, When the app loads, Then the Ritual screen displays with the StellaCloud Orb centered, ambient embers drifting upward, and the prompt "What's weighing on your heart tonight?"
- **AC-002**: Given the Ritual screen, When the user types an intention and taps Send OR speaks to the orb, Then the orb transitions to "thinking" state, then the reader mirrors the intention back in the tarot persona voice
- **AC-003**: Given the intention is mirrored, When the user taps "Draw your three cards", Then the card fan slides up with parallax-layered card backs, the user can swipe to browse, and tap three cards
- **AC-004**: Given a card is tapped in the fan, When selected, Then it animates upward into the held row with a pop animation and gold glow border
- **AC-005**: Given 3 cards are selected, When user taps "Begin the reading", Then cards animate into a spread row face-down, the first card flips with a 3D rotateY animation, and the reader's interpretation text appears progressively
- **AC-006**: Given a card's interpretation is complete, When the reader asks "Does that land?", Then three response chips appear: "That resonates", "Not quite", "Tell me more"
- **AC-007**: Given user taps "Not quite", When they type a correction and send, Then the reader adapts the interpretation with a follow-up message
- **AC-008**: Given all three cards are read, When the reader transitions to synthesis, Then a flowing narrative connects all cards to the original intention, followed by a highlighted one-line takeaway
- **AC-009**: Given the StellaCloud Orb, When its state changes (idle/listening/speaking/thinking), Then the animation, glow intensity, and aura color change smoothly (CSS transition)
- **AC-010**: Given the orb is in "listening" state, When Web Speech Recognition is active, Then expanding rings animate outward from the orb and the mic button pulses
- **AC-011**: Given the session is mid-reading, When the user closes and reopens the Mini App within 24 hours, Then the session resumes at the current phase with all dialogue preserved
- **AC-012**: Given any phase, When a network error occurs during an LLM call, Then a fallback card meaning is displayed and the user can retry or skip
- **AC-013**: Given the reading is complete (ended state), When user taps "New reading", Then a fresh session begins at the Ritual screen
- **AC-014**: Given the card fan, When the user drags/swipes, Then cards move with parallax (center cards larger, edge cards smaller/rotated) and the fan responds at 60fps

## 6. Test Automation Strategy

### Test Levels
- **Unit tests**: Individual components (Orb, CardFan, ReaderBubble, ChoiceChip) and pure functions
- **Integration tests**: Screen-level tests (RitualScreen, RevealScreen, ReflectScreen) with mocked API
- **End-to-End tests**: Full flow through the three phases (deferred to later phase)

### Frameworks
- **Frontend**: Vitest + @testing-library/react + jsdom (existing stack)
- **Backend**: pytest (existing stack)
- **Coverage**: 80%+ on new code

### Test Data Management
- Card interpretations loaded from fixture JSON for deterministic testing
- Session state fixtures for each phase
- Mock SpeechRecognition and SpeechSynthesis APIs

### CI/CD Integration
- Tests run on PR via existing GitHub Actions (or added if needed)
- Visual regression testing deferred to later phase

### Performance Testing
- Card fan render performance: 60fps benchmark with 22 cards
- Orb animation: no layout thrashing, GPU-composited only (transform + opacity)

## 7. Rationale & Context

### Why Major Arcana Only for v1
The existing `assets/tarot/` directory contains all 78 cards (22 Major + 56 Minor), but Major Arcana cards carry enough symbolic weight to drive a 3-5 minute reading. The reader persona can reference suits/elements conceptually without Minor Arcana-specific images. This reduces complexity in card selection UX and interpretation prompt engineering.

### Why the StellaCloud Orb is Central
The orb is not decorative — it is the "face" of the reader. In a text-based Mini App, users need an emotional anchor. The orb's state-driven animations (idle breathing, thinking pulse, listening rings, speaking glow) create a sense of presence and attention. The voice interaction (speak to the orb, the orb speaks back) makes the experience feel like a conversation, not a form.

### Why Server-Side Card Draws
Card draws happen server-side to prevent manipulation. The client fan is a UX affordance — the actual card selection is determined randomly on the server when the user taps "Begin the reading." The fan interaction is the ceremony; the randomness is guaranteed server-side.

### Why CSS Animations Over JS Animation Libraries
The orb and card animations use CSS animations with GPU-composited properties (transform, opacity, filter) to maintain 60fps on mobile devices. The `support.js` runtime design pattern (DCLogic class) maps cleanly to React state + CSS transitions.

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: Telegram Mini App platform — WebApp API for theme detection, viewport management
- **EXT-002**: Web Speech API — SpeechRecognition (voice input) and SpeechSynthesis (TTS output)

### Third-Party Services
- **SVC-001**: Luvr LLM providers (existing `src/llm/`) — OpenAI-compatible API for card interpretations

### Infrastructure Dependencies
- **INF-001**: FastAPI server (existing `src/server.py`) — new tarot endpoints
- **INF-002**: Vite dev server (existing `web/`) — new tarot routes

### Data Dependencies
- **DAT-001**: Card image assets in `assets/tarot/` (78 WebP + 1 PNG card back)
- **DAT-002**: Card slugs from `src/tarot/images.py` (existing)
- **DAT-003**: Fallback card meanings lookup table (new)

### Technology Platform Dependencies
- **PLT-001**: React 19.x + TypeScript 6.x (existing web stack)
- **PLT-002**: Python 3.12+ with FastAPI (existing server stack)
- **PLT-003**: No new npm or pip packages required

### Compliance Dependencies
- **COM-001**: Telegram Mini App policies — no external linking without Telegram confirmation, no data collection beyond what's needed for the reading

## 9. Examples & Edge Cases

### 9.1 StellaCloud Orb States

```css
/* Idle — slow breathing, subtle inner glow */
--orb-scale: 1;
--orb-opacity: 0.5;
animation: orb-breathe 4s ease-in-out infinite;

/* Listening — faster breathing, expanding rings, brighter aura */
--orb-scale: 1.09;
--orb-opacity: 1;
animation: orb-breathe 1.4s ease-in-out infinite;
/* + expanding ring animations */

/* Speaking — pulsing, gold core brightens */
--orb-scale: 1.035;
--orb-opacity: 0.95;
animation: orb-pulse 1.1s ease-in-out infinite;

/* Thinking — slow breathing, dimmer */
--orb-scale: 1;
--orb-opacity: 0.6;
animation: orb-breathe 2.6s ease-in-out infinite;
```

### 9.2 Card Fan Parallax

```typescript
// Each card's transform depends on its distance from center
const fanTransform = (index: number, offset: number, deckLength: number) => {
  const vp = index - offset - (deckLength - 1) / 2;
  const angle = vp * 7;           // degrees
  const tx = vp * 30;             // horizontal spread in px
  const ty = Math.pow(Math.abs(vp), 1.7) * 6;  // vertical arc
  return { angle, tx, ty, zIndex: 200 - Math.round(Math.abs(vp) * 10) };
};
```

### 9.3 Edge Cases

| Scenario | Behavior |
|----------|----------|
| Mini App fails to load | Graceful fallback to existing text-based tarot flow in Telegram chat |
| LLM call times out (>10s) | Fallback card meaning from lookup table; user can retry or skip |
| User closes Mini App mid-reading | Session saved for 24h; resume at current phase on reopen |
| User selects < 3 cards, taps "Begin" | Button disabled; prompt: "Pick two more" |
| User's intention is empty or all spaces | Gentle nudge: "Even a word or two helps the cards speak to your situation." |
| Network lost during reveal | Current phase + dialogue stored server-side; resume on reconnect |
| User spams taps during card flip | Animations are tappable; each flip queues at most one card revelation at a time; input ignored during active animation |
| SpeechRecognition not available | Fallback to text-only; mic button hidden; hint text updated |
| SpeechSynthesis not available | Mute button hidden; voice transport option removed |
| User deepens on >1 card | Only one deepen allowed per session; "Tell me more" chip hidden after first use |

## 10. Validation Criteria

- **VAL-001**: All 43 existing tests continue to pass after changes
- **VAL-002**: New tarot components have ≥80% test coverage
- **VAL-003**: Card fan renders 22 cards at 60fps on iPhone SE (simulated)
- **VAL-004**: Orb animations use only GPU-composited CSS properties (no layout triggers)
- **VAL-005**: All API endpoints return valid JSON with correct status codes
- **VAL-006**: Session persistence works across page reloads (within 24h TTL)
- **VAL-007**: Voice fallback works when SpeechRecognition is unavailable
- **VAL-008**: Card flip animation completes within 800ms
- **VAL-009**: Full reading flow completes in 3-5 minutes (user testing)
- **VAL-010**: No console errors during normal operation

## 11. Related Specifications / Further Reading

- [Tarot Reading Mini App Design Doc](/Users/taeahn/Downloads/2026-06-21-tarot-reading-mini-app-design.md)
- [Luvr Tarot.dc.html](/Users/taeahn/Downloads/Social%20integration%20landing/Luvr%20Tarot.dc.html) — Source Claude Design
- [Luvr Tarot (chat) v1.dc.html](/Users/taeahn/Downloads/Social%20integration%20landing/Luvr%20Tarot%20(KR).dc.html) — Chat variant
- [Linear Issue HUM-1403](https://linear.app/humphreyahn/issue/HUM-1403)
- [Existing Luvr source: src/tarot/](/Users/taeahn/devs/personal/2026/luvr/src/tarot/)
- [Existing Luvr web: web/src/](/Users/taeahn/devs/personal/2026/luvr/web/src/)
- [Frontend Design Skill](/Users/taeahn/.agents/skills/frontend-design/SKILL.md)
