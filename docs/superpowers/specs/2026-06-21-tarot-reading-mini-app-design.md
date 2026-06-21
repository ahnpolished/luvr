# Tarot Reading Mini App — Phased Canvas Design

**Status:** Design (pre-implementation)
**Date:** 2026-06-21
**Context:** Extending Luvr's existing deterministic 3-card tarot into a rich, human-like interactive reading experience. Platform: Telegram Mini App (first), with a platform-agnostic engine so the standalone web app is a second shell.

---

## 1. Design Goals

| Goal | Constraint |
|------|------------|
| Feels like a human reader, not a form | 3-5 minute session cap |
| Ceremony + conversation + narrative woven together | No fake complexity — every interaction earns its place |
| Platform-agnostic engine; Mini App as first shell | Clean port to standalone web later |
| Extends existing `src/tarot/` — not a rewrite | Reuses Luvr's LLM providers, card images, tarot persona |

## 2. Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Telegram Mini App                   │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  RITUAL  │  │    REVEAL    │  │   REFLECT    │  │
│  │  Screen  │─▶│   Screen     │─▶│   Screen     │  │
│  └──────────┘  └──────────────┘  └──────────────┘  │
│                                                      │
│            ┌──────────────────────┐                  │
│            │   Tarot Engine       │                  │
│            │   (platform-agnostic)│                  │
│            │   • Deck logic       │                  │
│            │   • Reader persona   │                  │
│            │   • Session state    │                  │
│            │   • LLM orchestration│                  │
│            └──────────┬───────────┘                  │
│                       │                              │
│            ┌──────────▼───────────┐                  │
│            │    LLM Providers     │                  │
│            │   (reuse Luvr's)     │                  │
│            └──────────────────────┘                  │
└─────────────────────────────────────────────────────┘
```

- **Tarot Engine** — single Python module (`src/tarot/engine.py`) holding session state, deck logic, reader persona, and LLM orchestration. Stateless interface: takes a session ID + user action, returns new session state + UI instructions.
- **Mini App shell** — thin React UI (reuses `web/`'s Vite + TypeScript stack) with three screens. Talks to FastAPI endpoints in `src/server.py`. Renders `CardFan` component (horizontal swipe), `ReaderBubble` (persona messages), and `ChoiceChip` (deepen / move on).
- **LLM layer** — reuses existing `src/llm/` providers. Three prompt roles: "ritualist" (intention mirroring), "reader" (card interpretation + dialogue), "weaver" (synthesis narrative). All use the distinct tarot persona (see §6).

No Telegram coupling in the engine. The shell is the only platform-specific layer.

## 3. Core Data Model

```python
class Session:
    id: str
    phase: Literal["ritual", "reveal", "reflect"]
    intention: str | None
    drawn_cards: list[Card]             # in draw order
    current_card_index: int | None      # which card we're on in reveal
    dialogue: list[Message]             # full conversation transcript
    deepened_on: set[int]               # indices of cards user chose to explore deeper
    reflection: str | None              # synthesis text, written in reflect phase

class Card:
    slug: str                           # e.g. "star", "fool"
    name: str                           # e.g. "The Star"
    arcana: Literal["major", "minor"]
    suit: str | None                    # cups, pentacles, swords, wands
    is_reversed: bool
    position_meaning: str               # what this position means in the spread

class Message:
    speaker: Literal["reader", "user"]
    text: str
    context: str | None                 # "intention", "card_1_initial", "card_1_deepen", etc.
```

The engine exposes a single entry point:

```python
def advance(session: Session, action: Action) -> tuple[Session, UIInstruction]:
    ...
```

Where `Action` is a discriminated union — "set_intention", "draw_card", "choose_deepen", "choose_continue", "confirm_done". The engine enforces valid phase transitions; invalid actions (e.g., drawing before intention is set) return an error state.

`UIInstruction` tells the shell what to render: which screen, what cards to show face-up/down, what reader text to display, what choices to offer.

## 4. Screen-by-Screen Flow

### 4.1 RITUAL — The Ceremony (one screen, ~60 seconds)

**Goal:** Set the mood and capture intention before any cards are touched.

**Visual:**
- Dark, warm background with subtle ambient animation (slow particle drift, candle-like glow).
- Card back image centered or subtly present as a visual anchor.
- No buttons visible until intention is set.

**Interaction:**
1. Reader appears as a short text: "What brings you in today?" — optional prompt chips below ("A situationship", "I'm unsure about someone", "Something else").
2. User types or taps their intention in a single text input. Character limit ~150.
3. Reader mirrors it back in the tarot persona voice: "So we're asking about [reframed intention] — let's see what the cards have to say."
4. Transition cue: reader says "When you're ready, find three cards that call to you."
5. The **Swipe Fan** slides up: a horizontal scroll of card backs. User swipes through the deck visibly — cards slide with parallax, haptic feedback on supported devices. User taps 3 cards.
6. Each selected card pulses and rises slightly, stays in a "held" row above the fan.
7. Once 3 are selected, fan fades down. The held cards animate into a row, face-down. Transition to REVEAL.

**State transition:** `ritual → reveal`, `intention` stored, `drawn_cards` populated with 3 random cards (drawn server-side at the moment of 3rd selection).

**Engine work:** on setting intention, engine runs a lightweight LLM call ("ritualist" prompt) to reframe the intention in the tarot persona voice. On draw, engine uses `random.sample` from the existing card slugs, assigns a random reversal state per card, and tags each with its position meaning. No LLM yet — it's just prep.

### 4.2 REVEAL — The Reading (one screen, ~2-3 minutes)

**Goal:** Card-by-card reveal with conversational dialogue. User controls depth.

**Visual:**
- Top 40% — the spread: 3 cards in a row. The current card is face-up, centered and highlighted. The other two are face-down with a soft glow.
- Bottom 60% — chat-like thread. Reader messages appear with a stylized bubble (serif font, soft glow to signal "this is the distinct tarot persona"). User responses are shorter, right-aligned chips or short text.
- Below the chat: choice chips for current decision point.

**Interaction loop** (repeats for cards 1, 2, then 3):

1. **Card flip:** Reader text announces: "The first card — [Position Name]." The card flips with a 3D animation (rotate Y). Face-up card shows image, name, and position meaning badge.
2. **Initial interpretation:** Reader delivers a 3-4 sentence interpretation in the persona voice. Connects to the intention if possible.
3. **Resonance check:** Reader asks a question like "Does that land?" or "What comes up for you?" User picks from quick-reply chips: "That tracks", "Sort of...", "Not really".
4. **Branch — user responds:**
   - If "That tracks" → Reader acknowledges, offers: "Want to sit with this card a bit more, or move to the next?" — choice chips: "Tell me more" / "Next card"
   - If "Sort of..." / "Not really" → Reader asks a gentle follow-up: "What feels off?" User types a short response. Reader adapts the interpretation based on user's correction (LLM call), then offers deepen/continue.
5. **If user chooses "Tell me more":** Reader goes one layer deeper — a different angle on the same card, perhaps connecting to the reversal meaning, the suit's element, or asking the user to reflect on a specific life area. This is an LLM call with the card + full dialogue context.
6. **Continue:** Move to next card. The just-read card slides slightly to the side, still visible but de-emphasized. Next card flips.

**After card 3:** Reader delivers a bridging line like "Three cards — let me step back and weave this into something you can hold onto." This is not the full synthesis yet — it's a transition tease. Auto-advance to REFLECT after a brief pause, or on a "Ready" tap.

**Dialogue cap:** User can deepen on at most one card to keep within the 3-5 minute budget. If they haven't used it by the end, the reader offers it once after card 3 before transitioning.

**Engine work:** each card flip triggers an LLM call (3-4 total: initial interpretation for each card, optionally one deepen call). The "reader" prompt includes the full session context — intention, drawn cards so far, dialogue history, which card and position is current. The persona is consistent across all calls (§6).

The resonance-check branching is NOT an LLM call — it's a simple routing in the engine based on the user's chip selection. Only "Tell me more" (deepen) and the initial interpretation use LLM.

### 4.3 REFLECT — The Story (one screen, ~60 seconds)

**Goal:** Weave all three cards into a single personal narrative. Leave the user with one grounded takeaway.

**Visual:**
- All three cards face-up in a tighter row at the top, smaller.
- The synthesis narrative appears as a single long reader message, revealed progressively (typewriter effect or paragraph-by-paragraph).
- Below it: the one-line takeaway, emphasized (larger text, different treatment).
- Bottom: share button, save button, "New reading" button.

**Interaction:**
1. The synthesis appears — a 4-6 sentence narrative connecting all three cards to the original intention. Written as one flowing paragraph, not three separate interpretations glued together.
2. The takeaway line is extracted and highlighted. Something concrete: "The invitation here is to [one grounded action / shift in perspective]."
3. User can:
   - **Share** — generates a stylized share card (image) with the three cards + takeaway, ready for Telegram/Instagram.
   - **Save** — stores the reading to user's history (future feature; v1 can be a screenshot prompt).
   - **Do another reading** — navigates back to RITUAL (but abandons current session).

**Engine work:** one LLM call ("weaver" prompt). Takes the full session — intention, all three cards with their interpretations, user's dialogue, which card was deepened — and produces the synthesis + a single takeaway sentence. Engine parses the takeaway from the response (e.g., a `## Takeaway` marker).

## 5. Interaction Map (Full Flow)

```
RITUAL
  │
  ├─ User sets intention ──▶ Reader mirrors it back
  │
  ├─ User swipes fan, picks 3 cards ──▶ [auto] → REVEAL
  │
  ▼
REVEAL
  │
  ├─ Card 1 flips ──▶ Reader interprets ──▶ "Resonates?"
  │     ├─ Yes → offer deepen/next
  │     │     ├─ Deepen → Reader goes deeper → next
  │     │     └─ Next → Card 2
  │     └─ No → "What feels off?" → user types → Reader adapts → offer deepen/next
  │
  ├─ Card 2 flips ──▶ (same loop)
  │
  ├─ Card 3 flips ──▶ (same loop)
  │     └─ If deepen unused, offer once after card 3
  │
  ├─ [auto] → REFLECT
  │
  ▼
REFLECT
  │
  ├─ Synthesis + takeaway display
  ├─ Share | Save | New Reading
  └─ [session complete]
```

## 6. Reader Persona

The tarot reader is a distinct persona from Luvr's default "empathetic friend" voice. Luvr is direct and grounded; the tarot reader is slightly more mysterious and archetypal — but never cold, never pretends to be psychic.

**Voice traits:**
- **Archetypal but warm** — uses card names and symbols naturally ("The Star asks you to trust the long arc"), not like a textbook.
- **Asks, doesn't declare** — interpretations are offerings, not pronouncements. "This could mean..." or "What I'm seeing is..." — always invite the user's experience.
- **Poetic but not purple** — one well-chosen metaphor per reading is enough. No "the universe is conspiring" fluff.
- **Grounded** — every card reading ends in something actionable or reframe-able. No fate-telling.
- **Modern** — references real relationship dynamics (situationships, ghosting, texting anxiety) comfortably.

**Prompt strategy:** Each LLM call includes a persona preamble in the system prompt. The preamble is the same across all calls — consistent voice. The user prompt is the specific task (interpret this card in this position for this intention, etc.).

**Example persona preamble:**
> You are a tarot reader for Luvr, a dating-advice service. Your readings blend archetypal wisdom with grounded, modern relationship insight. You speak like someone who's read a lot of cards and had a lot of conversations — warm, perceptive, never performatively mystical. You ask questions. You offer interpretations as possibilities, not pronouncements. You never predict the future. You connect cards into a story the querent can actually use.

## 7. Key LLM Calls (per Session)

| Call | When | Prompt Role | Tokens (est.) |
|------|------|-------------|---------------|
| Intention mirror | After user sets intention | "ritualist" | ~200 |
| Card 1 interpretation | Card 1 flip | "reader" | ~400 |
| Card 2 interpretation | Card 2 flip | "reader" | ~400 |
| Card 3 interpretation | Card 3 flip | "reader" | ~400 |
| Deepen (optional) | User chooses deepen | "reader" | ~400 |
| Synthesis + takeaway | Reflect phase | "weaver" | ~500 |

**Total:** ~1,900–2,300 tokens per session. Acceptable for a 3-5 minute experience.

## 8. Card Selection UX (Swipe Fan Detail)

The swipe fan is the most novel interaction. Requirements:

- Horizontal scroll of card-back images, ~20 cards visible in the viewport (fetch all 22 Major Arcana from existing `CARD_SLUGS`; engine draws 3 server-side but the fan shows the full deck for the tactile experience).
- Scroll is freeform — user can swipe left/right to browse. Parallax: cards in the center are larger, cards at the edges are smaller and slightly rotated.
- Tap a card to select it. Selected card animates upward into a "held" row (top 20% of screen), shrinks slightly, gets a subtle glow border. Card disappears from the fan.
- Can tap a held card to deselect it — it animates back into the fan at its original position.
- Once 3 cards are held, a "Ready" button appears (or auto-confirm after 1.5 seconds — designer's choice). Fan fades down, held cards animate into the spread row.
- Haptic feedback on selection (if device supports it — Telegram Mini App does on iOS/Android).

**Why 22 Majors only?** The existing image assets are Major Arcana only. Minor Arcana can be added later as assets. For v1, Major Arcana cards carry enough symbolic weight to drive a 3-5 minute reading. The reader persona can reference suits/elements conceptually without Minor Arcana-specific card images.

## 9. Technical Integration with Luvr

**Existing reuse:**
- Card images: `src/tarot/images.py` — `card_image_path()`, `card_back_path()`, `random_cards()`
- LLM layer: `src/llm/` — abstract provider interface reused as-is
- Web stack: `web/` — React + TypeScript + Vite. The Mini App is a new route/screen set within this existing app.
- Server: `src/server.py` — FastAPI. New endpoints:
  - `POST /api/tarot/session` — create new session, returns session ID + initial state
  - `POST /api/tarot/session/{id}/action` — advance session with user action, returns new state + UI instruction
  - `GET /api/tarot/session/{id}` — fetch current state (for resume)

**Existing update:**
- `src/tarot/flow.py` — the existing `THREE_CARD_TAROT_FLOW` remains as the text-chat version for Telegram bot users who don't open the Mini App. The new engine lives alongside it, not replacing it.
- `src/tarot/` gains: `engine.py` (session logic), `persona.py` (prompt templates), `positions.py` (spread position definitions).

**No new dependencies.** Everything runs within the existing Python + React stack.

## 10. Error & Edge Cases

| Scenario | Behavior |
|----------|----------|
| Mini App fails to load | Graceful fallback to existing text-based tarot flow in Telegram chat |
| LLM call times out | Reader persona delivers a fallback card meaning (stored in a lookup table for each card). User can retry or skip. |
| User closes Mini App mid-session | Session saved for 24 hours. On reopen, resume at current phase. |
| User selects < 3 cards, taps "Ready" | Button disabled until exactly 3 selected. Prompt: "Pick two more." |
| User's intention is empty or all spaces | Gentle nudge: "Even a word or two helps the cards speak to your situation." |
| Network lost during reveal | Current phase + dialogue stored server-side. Resume on reconnect. |
| User spams taps during card flip animation | Animations are tappable — each flip queues at most one card revelation at a time. Input ignored during active animation. |

## 11. What's Out of Scope for v1

- Minor Arcana card images (assets don't exist yet)
- Multi-spread support (only the 3-card relationship spread)
- Reading history / saved readings (encourage screenshot instead)
- Reversal-specific visual treatment (just a badge or label)
- Audio/voice mode for the reader persona
- Multi-language support beyond existing Luvr i18n
- Social features (public feed, friends reading each other's cards)
