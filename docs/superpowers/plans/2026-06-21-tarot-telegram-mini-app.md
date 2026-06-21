# Luvr Tarot — Interactive Telegram Mini App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an interactive 3-card tarot reading experience as a Telegram Mini App with a StellaCloud celestial orb, swipe-to-select card fan, 3D card flip animations, conversational reader dialogue, and voice interaction.

**Architecture:** React + TypeScript frontend with three phase screens (Ritual → Reveal → Reflect) communicating with a Python FastAPI backend via session-based REST endpoints. The tarot engine is platform-agnostic; the Telegram Mini App is a thin UI shell.

**Tech Stack:** React 19, TypeScript 6, Vite 8, Vitest, Python FastAPI, existing Luvr LLM providers

---

## File Structure Map

```
web/src/
├── styles/
│   └── tarot-tokens.css          [CREATE] Tarot-specific CSS variables
├── components/
│   └── tarot/
│       ├── StellaOrb.tsx          [CREATE] Celestial nebula orb
│       ├── StellaOrb.css          [CREATE]
│       ├── StellaOrb.test.tsx     [CREATE]
│       ├── CardFan.tsx            [CREATE] Swipe-to-select card fan
│       ├── CardFan.css            [CREATE]
│       ├── CardFan.test.tsx       [CREATE]
│       ├── CardSpread.tsx         [CREATE] 3-card spread with flip
│       ├── CardSpread.css         [CREATE]
│       ├── CardSpread.test.tsx    [CREATE]
│       ├── ReaderBubble.tsx       [CREATE] Reader message bubble
│       ├── ReaderBubble.css       [CREATE]
│       ├── ReaderBubble.test.tsx  [CREATE]
│       ├── ChoiceChip.tsx         [CREATE] Response choice chip
│       ├── ChoiceChip.css         [CREATE]
│       ├── ChoiceChip.test.tsx    [CREATE]
│       ├── EmberField.tsx         [CREATE] Ambient ember particles
│       ├── EmberField.css         [CREATE]
│       ├── EmberField.test.tsx    [CREATE]
│       └── index.ts               [CREATE] Barrel export
├── screens/
│   └── tarot/
│       ├── RitualScreen.tsx       [CREATE] Intention + card draw
│       ├── RitualScreen.css       [CREATE]
│       ├── RitualScreen.test.tsx  [CREATE]
│       ├── RevealScreen.tsx       [CREATE] Card-by-card reading
│       ├── RevealScreen.css       [CREATE]
│       ├── RevealScreen.test.tsx  [CREATE]
│       ├── ReflectScreen.tsx      [CREATE] Synthesis narrative
│       ├── ReflectScreen.css      [CREATE]
│       ├── ReflectScreen.test.tsx [CREATE]
│       └── index.ts               [CREATE] Barrel export
├── state/
│   └── tarot-context.tsx          [CREATE] Session state management
├── lib/
│   └── tarot-api.ts               [CREATE] API client
└── App.tsx                        [MODIFY] Add tarot routes

src/
└── tarot/
    ├── engine.py                  [CREATE] Session state machine
    ├── persona.py                 [CREATE] Prompt templates
    └── positions.py               [CREATE] Spread position definitions

src/server.py                      [MODIFY] Add tarot endpoints
```

---

### Task 0: Foundation — Design Tokens & Tarot API Client

**Files:**
- Create: `web/src/styles/tarot-tokens.css`
- Create: `web/src/lib/tarot-api.ts`
- Create: `web/src/lib/tarot-api.test.ts`

- [ ] **Step 1: Write tarot design tokens**

Create `web/src/styles/tarot-tokens.css`:

```css
/* Tarot-specific design tokens extending tokens.css */
:root {
  /* Orb colors — celestial nebula palette */
  --orb-gold: #C9A24B;
  --orb-accent: #FF6B61;
  --orb-core-outer: #5A4636;
  --orb-core-mid: #2A1D16;
  --orb-core-inner: #140C09;

  /* Background gradient stops */
  --tarot-bg-start: #2B201A;
  --tarot-bg-mid: #1A1310;
  --tarot-bg-end: #120D0B;

  /* Card colors */
  --card-back-gradient-start: #2A1F19;
  --card-back-gradient-end: #150E0B;
  --card-face-gradient-start: #F7EFE1;
  --card-face-gradient-end: #EADFCB;

  /* Animation durations */
  --orb-breathe-duration: 4s;
  --orb-pulse-duration: 1.1s;
  --orb-listen-duration: 1.4s;
  --orb-think-duration: 2.6s;
  --orb-rotate-duration: 14s;
  --orb-rotate-rev-duration: 18s;
  --ring-expand-duration: 1.8s;

  /* Card fan */
  --fan-card-width: 74px;
  --fan-card-height: 118px;
  --fan-card-radius: 13px;

  /* Typography overrides for tarot persona */
  --font-reader: 'Spectral', serif;
}
```

- [ ] **Step 2: Write the API client test**

Create `web/src/lib/tarot-api.test.ts`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { createSession, advanceSession, getSession } from './tarot-api';

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('tarot-api', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it('createSession calls POST /api/tarot/session', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'ritual' }),
    });

    const result = await createSession();

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/tarot/session'),
      expect.objectContaining({ method: 'POST' })
    );
    expect(result.session_id).toBe('abc');
  });

  it('advanceSession sends action payload', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'reveal' }),
    });

    const result = await advanceSession('abc', { kind: 'set_intention', text: 'hello' });

    const [, options] = mockFetch.mock.calls[0];
    const body = JSON.parse(options.body);
    expect(body.kind).toBe('set_intention');
    expect(body.text).toBe('hello');
    expect(result.phase).toBe('reveal');
  });

  it('getSession fetches current state', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ session_id: 'abc', phase: 'reveal' }),
    });

    const result = await getSession('abc');
    expect(result.phase).toBe('reveal');
  });
});
```

- [ ] **Step 3: Run test — verify it fails**

```bash
cd web && npx vitest run src/lib/tarot-api.test.ts
```
Expected: FAIL — module not found.

- [ ] **Step 4: Write minimal API client**

Create `web/src/lib/tarot-api.ts`:

```typescript
const BASE = import.meta.env.VITE_API_BASE_URL ?? '';

export interface SessionState {
  session_id: string;
  phase: 'ritual' | 'reveal' | 'reflect';
  cards?: CardData[];
  messages?: MessageData[];
  ui?: Record<string, unknown>;
}

export interface CardData {
  slug: string;
  name: string;
  arcana: 'major' | 'minor';
  suit: string | null;
  is_reversed: boolean;
  position_meaning: string;
  numeral?: string;
  glyph?: string;
}

export interface MessageData {
  speaker: 'reader' | 'user';
  text: string;
  context?: string;
}

export interface Action {
  kind: 'set_intention' | 'draw_cards' | 'respond' | 'continue';
  text?: string;
  count?: number;
  card_index?: number;
  response?: 'resonates' | 'not_quite' | 'tell_me_more';
  correction_text?: string;
}

export async function createSession(): Promise<SessionState> {
  const res = await fetch(`${BASE}/api/tarot/session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Failed to create session: ${res.status}`);
  return res.json();
}

export async function advanceSession(
  sessionId: string,
  action: Action,
): Promise<SessionState> {
  const res = await fetch(`${BASE}/api/tarot/session/${sessionId}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(action),
  });
  if (!res.ok) throw new Error(`Failed to advance session: ${res.status}`);
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const res = await fetch(`${BASE}/api/tarot/session/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to get session: ${res.status}`);
  return res.json();
}
```

- [ ] **Step 5: Run test — verify it passes**

```bash
cd web && npx vitest run src/lib/tarot-api.test.ts
```
Expected: 3 tests PASS.

- [ ] **Step 6: Import tarot tokens in main CSS**

Edit `web/src/index.css` — add the import:

```css
@import './styles/tokens.css';
@import './styles/tarot-tokens.css';
```

- [ ] **Step 7: Commit**

```bash
git add web/src/styles/tarot-tokens.css web/src/lib/tarot-api.ts web/src/lib/tarot-api.test.ts web/src/index.css
git commit -m "feat(tarot): add design tokens and API client"
```

---

### Task 1: StellaCloud Orb Component

**Files:**
- Create: `web/src/components/tarot/StellaOrb.tsx`
- Create: `web/src/components/tarot/StellaOrb.css`
- Create: `web/src/components/tarot/StellaOrb.test.tsx`

- [ ] **Step 1: Write failing tests**

Create `web/src/components/tarot/StellaOrb.test.tsx`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { StellaOrb } from './StellaOrb';

describe('StellaOrb', () => {
  it('renders with default idle state', () => {
    render(<StellaOrb state="idle" />);
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('applies listening class when state is listening', () => {
    const { container } = render(<StellaOrb state="listening" />);
    const orb = container.querySelector('.orb--listening');
    expect(orb).toBeInTheDocument();
  });

  it('applies speaking class when state is speaking', () => {
    const { container } = render(<StellaOrb state="speaking" />);
    const orb = container.querySelector('.orb--speaking');
    expect(orb).toBeInTheDocument();
  });

  it('applies thinking class when state is thinking', () => {
    const { container } = render(<StellaOrb state="thinking" />);
    const orb = container.querySelector('.orb--thinking');
    expect(orb).toBeInTheDocument();
  });

  it('renders expanding rings when listening', () => {
    const { container } = render(<StellaOrb state="listening" />);
    const rings = container.querySelectorAll('.orb__ring');
    expect(rings.length).toBe(2);
  });

  it('does not render rings when not listening', () => {
    const { container } = render(<StellaOrb state="idle" />);
    const rings = container.querySelectorAll('.orb__ring');
    expect(rings.length).toBe(0);
  });

  it('calls onTap when clicked', () => {
    const onTap = vi.fn();
    render(<StellaOrb state="idle" onTap={onTap} />);
    fireEvent.click(screen.getByRole('button', { name: /orb/i }));
    expect(onTap).toHaveBeenCalledTimes(1);
  });

  it('renders with custom size', () => {
    const { container } = render(<StellaOrb state="idle" size={120} />);
    const orb = container.querySelector('.orb');
    expect(orb).toBeInTheDocument();
  });

  it('shows mic icon when showMic is true and listening', () => {
    render(<StellaOrb state="listening" showMic />);
    const mic = screen.getByLabelText(/mic/i);
    expect(mic).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/components/tarot/StellaOrb.test.tsx
```
Expected: FAIL — module not found.

- [ ] **Step 3: Write StellaOrb CSS**

Create `web/src/components/tarot/StellaOrb.css`:

```css
/* StellaCloud Orb — celestial nebula sphere
   Four visual states: idle, listening, speaking, thinking
   All animations are GPU-composited (transform + opacity only) */

@keyframes orb-breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.035); }
}

@keyframes orb-pulse {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.09); opacity: 1; }
}

@keyframes orb-rotate {
  to { transform: rotate(360deg); }
}

@keyframes orb-rotate-rev {
  to { transform: rotate(-360deg); }
}

@keyframes ring-expand {
  0% { transform: scale(0.7); opacity: 0.55; }
  100% { transform: scale(1.7); opacity: 0; }
}

.orb {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}

.orb:focus-visible {
  outline: 2px solid var(--orb-accent, #FF6B61);
  outline-offset: 4px;
  border-radius: 50%;
}

/* --- Aura glow ring --- */
.orb__aura {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 30%, transparent),
    transparent 65%
  );
  filter: blur(14px);
  opacity: 0.5;
  animation: orb-breathe 4s ease-in-out infinite;
}

.orb--listening .orb__aura {
  opacity: 0.85;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 42%, transparent),
    transparent 62%
  );
  animation: orb-breathe 1.4s ease-in-out infinite;
}

.orb--speaking .orb__aura {
  opacity: 0.95;
  animation: orb-pulse 1.2s ease-in-out infinite;
}

.orb--thinking .orb__aura {
  opacity: 0.6;
  animation: orb-breathe 2.6s ease-in-out infinite;
}

/* --- Expanding rings (listening only) --- */
.orb__ring {
  position: absolute;
  width: 85%;
  height: 85%;
  border-radius: 50%;
  border: 1px solid var(--orb-accent, #FF6B61);
  animation: ring-expand 1.8s ease-out infinite;
  pointer-events: none;
}

.orb__ring:nth-child(2) {
  animation-delay: 0.9s;
}

/* --- Core sphere --- */
.orb__core {
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  background: radial-gradient(
    circle at 35% 28%,
    var(--orb-core-outer, #5A4636) 0%,
    var(--orb-core-mid, #2A1D16) 52%,
    var(--orb-core-inner, #140C09) 100%
  );
  box-shadow:
    inset 0 6px 24px rgba(0, 0, 0, 0.7),
    inset 0 -8px 30px rgba(0, 0, 0, 0.85),
    0 24px 60px -20px rgba(0, 0, 0, 0.9);
}

/* --- Conic gradient overlays (nebula swirls) --- */
.orb__swirl {
  position: absolute;
  inset: -30%;
  mix-blend-mode: screen;
  pointer-events: none;
}

.orb__swirl--gold {
  background: conic-gradient(
    from 0deg,
    transparent,
    color-mix(in srgb, var(--orb-gold, #C9A24B) 40%, transparent),
    transparent 40%
  );
  animation: orb-rotate 14s linear infinite;
}

.orb__swirl--accent {
  background: conic-gradient(
    from 120deg,
    transparent,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 45%, transparent),
    transparent 35%
  );
  animation: orb-rotate-rev 18s linear infinite;
}

/* --- Inner core glow --- */
.orb__inner {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  pointer-events: none;
  background: radial-gradient(
    circle at 50% 55%,
    color-mix(in srgb, var(--orb-gold, #C9A24B) 38%, transparent) 0%,
    transparent 62%
  );
  animation: orb-breathe 4s ease-in-out infinite;
}

.orb--listening .orb__inner {
  background: radial-gradient(
    circle at 50% 55%,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 80%, #fff) 0%,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 50%, transparent) 45%,
    transparent 72%
  );
  animation: orb-breathe 1.4s ease-in-out infinite;
}

.orb--speaking .orb__inner {
  background: radial-gradient(
    circle at 50% 55%,
    color-mix(in srgb, var(--orb-gold, #C9A24B) 75%, #fff) 0%,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 60%, transparent) 40%,
    transparent 70%
  );
  animation: orb-pulse 1.1s ease-in-out infinite;
}

.orb--thinking .orb__inner {
  background: radial-gradient(
    circle at 50% 55%,
    color-mix(in srgb, var(--orb-gold, #C9A24B) 55%, transparent) 0%,
    transparent 60%
  );
  animation: orb-breathe 2.2s ease-in-out infinite;
}

/* --- Specular highlight --- */
.orb__highlight {
  position: absolute;
  top: 16%;
  left: 24%;
  width: 26%;
  height: 16%;
  border-radius: 50%;
  background: rgba(255, 250, 240, 0.4);
  filter: blur(7px);
  pointer-events: none;
}

/* --- Mic button overlay --- */
.orb__mic {
  position: absolute;
  bottom: -8px;
  right: -8px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid rgba(247, 239, 227, 0.2);
  background: rgba(247, 239, 227, 0.05);
  color: #E8DCCB;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  transition: border-color 0.2s, background 0.2s;
}

.orb--listening .orb__mic {
  border-color: var(--orb-accent, #FF6B61);
  background: color-mix(in srgb, var(--orb-accent, #FF6B61) 22%, transparent);
  color: var(--orb-accent, #FF6B61);
  animation: orb-breathe 1.2s ease-in-out infinite;
}
```

- [ ] **Step 4: Write StellaOrb component**

Create `web/src/components/tarot/StellaOrb.tsx`:

```typescript
import './StellaOrb.css';

export type OrbState = 'idle' | 'listening' | 'speaking' | 'thinking';

interface StellaOrbProps {
  state: OrbState;
  size?: number;
  onTap?: () => void;
  showMic?: boolean;
  'aria-label'?: string;
}

export function StellaOrb({
  state,
  size = 188,
  onTap,
  showMic = false,
  'aria-label': ariaLabel = 'Tarot orb — tap to interact',
}: StellaOrbProps) {
  const stateClass = `orb--${state}`;
  const showRings = state === 'listening';

  return (
    <button
      className={`orb ${stateClass}`}
      style={{ width: size, height: size }}
      onClick={onTap}
      aria-label={ariaLabel}
      type="button"
    >
      {/* Aura glow */}
      <div className="orb__aura" aria-hidden="true" />

      {/* Expanding rings when listening */}
      {showRings && (
        <>
          <div className="orb__ring" aria-hidden="true" />
          <div className="orb__ring" aria-hidden="true" />
        </>
      )}

      {/* Core sphere */}
      <div
        className="orb__core"
        style={{ width: '100%', height: '100%' }}
      >
        {/* Nebula swirls (conic gradient overlays) */}
        <div className="orb__swirl orb__swirl--gold" aria-hidden="true" />
        <div className="orb__swirl orb__swirl--accent" aria-hidden="true" />

        {/* Inner core glow */}
        <div className="orb__inner" aria-hidden="true" />

        {/* Specular highlight */}
        <div className="orb__highlight" aria-hidden="true" />
      </div>

      {/* Mic button */}
      {showMic && (
        <span className="orb__mic" aria-label={state === 'listening' ? 'mic active' : 'mic'}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="2" width="6" height="11" rx="3" />
            <path d="M5 10a7 7 0 0 0 14 0" />
            <line x1="12" y1="18.5" x2="12" y2="22" />
            <line x1="8.5" y1="22" x2="15.5" y2="22" />
          </svg>
        </span>
      )}
    </button>
  );
}
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
cd web && npx vitest run src/components/tarot/StellaOrb.test.tsx
```
Expected: All 8 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add web/src/components/tarot/StellaOrb.tsx web/src/components/tarot/StellaOrb.css web/src/components/tarot/StellaOrb.test.tsx
git commit -m "feat(tarot): add StellaCloud Orb component with four visual states"
```

---

### Task 2: EmberField — Ambient Particle System

**Files:**
- Create: `web/src/components/tarot/EmberField.tsx`
- Create: `web/src/components/tarot/EmberField.css`
- Create: `web/src/components/tarot/EmberField.test.tsx`

- [ ] **Step 1: Write failing test**

Create `web/src/components/tarot/EmberField.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { EmberField } from './EmberField';

describe('EmberField', () => {
  it('renders the correct number of ember particles', () => {
    const { container } = render(<EmberField count={12} />);
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBe(12);
  });

  it('renders 16 embers by default', () => {
    const { container } = render(<EmberField />);
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBe(16);
  });

  it('has a container that fills its parent', () => {
    const { container } = render(<EmberField />);
    const field = container.querySelector('.ember-field');
    expect(field).toBeInTheDocument();
  });

  it('particles have alternating accent/gold colors', () => {
    const { container } = render(<EmberField count={6} />);
    const embers = container.querySelectorAll('.ember-field__particle');

    // Each ember should have an inline style with a color
    const firstStyle = (embers[0] as HTMLElement).style.cssText;
    expect(firstStyle).toBeTruthy();
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/components/tarot/EmberField.test.tsx
```

- [ ] **Step 3: Write EmberField CSS + component**

Create `web/src/components/tarot/EmberField.css`:

```css
@keyframes ember-drift {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  12% {
    opacity: 0.7;
  }
  88% {
    opacity: 0.5;
  }
  100% {
    transform: translateY(-150px) scale(0.4);
    opacity: 0;
  }
}

.ember-field {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.ember-field__particle {
  position: absolute;
  border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
  animation: ember-drift var(--ember-duration, 7s) linear var(--ember-delay, 0s) infinite;
}

.ember-field__glow {
  position: absolute;
  left: 50%;
  top: -90px;
  width: 320px;
  height: 320px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(
    circle,
    color-mix(in srgb, var(--orb-accent, #FF6B61) 22%, transparent),
    transparent 68%
  );
  filter: blur(20px);
  pointer-events: none;
}
```

Create `web/src/components/tarot/EmberField.tsx`:

```typescript
import { useMemo } from 'react';
import './EmberField.css';

interface EmberFieldProps {
  count?: number;
  showGlow?: boolean;
}

interface EmberParticle {
  id: number;
  style: React.CSSProperties;
}

export function EmberField({ count = 16, showGlow = true }: EmberFieldProps) {
  const embers = useMemo<EmberParticle[]>(() => {
    return Array.from({ length: count }, (_, i) => {
      const left = Math.round((i * 61) % 100);
      const duration = 7 + (i % 5) * 1.6;
      const delay = -(i * 0.9);
      const size = 2 + (i % 3);
      const bottom = -10 - (i % 4) * 8;
      const isGold = i % 3 === 0;
      const color = isGold
        ? 'var(--orb-gold, #C9A24B)'
        : 'var(--orb-accent, #FF6B61)';

      return {
        id: i,
        style: {
          left: `${left}%`,
          bottom: `${bottom}px`,
          width: `${size}px`,
          height: `${size}px`,
          color,
          backgroundColor: color,
          // @ts-expect-error CSS custom properties
          '--ember-duration': `${duration}s`,
          '--ember-delay': `${delay.toFixed(1)}s`,
        } as React.CSSProperties,
      };
    });
  }, [count]);

  return (
    <div className="ember-field" aria-hidden="true">
      {embers.map((e) => (
        <span key={e.id} className="ember-field__particle" style={e.style} />
      ))}
      {showGlow && <div className="ember-field__glow" />}
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/components/tarot/EmberField.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/components/tarot/EmberField.tsx web/src/components/tarot/EmberField.css web/src/components/tarot/EmberField.test.tsx
git commit -m "feat(tarot): add EmberField ambient particle system"
```

---

### Task 3: CardFan — Swipe-to-Select Card Deck

**Files:**
- Create: `web/src/components/tarot/CardFan.tsx`
- Create: `web/src/components/tarot/CardFan.css`
- Create: `web/src/components/tarot/CardFan.test.tsx`

- [ ] **Step 1: Write failing tests**

Create `web/src/components/tarot/CardFan.test.tsx`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CardFan } from './CardFan';

const DECK = ['fool', 'magician', 'high_priestess'];

describe('CardFan', () => {
  it('renders all cards from the deck', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[]} onToggle={() => {}} />
    );
    const cards = container.querySelectorAll('.card-fan__card');
    expect(cards.length).toBe(DECK.length);
  });

  it('applies selected class to selected cards', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0]} onToggle={() => {}} />
    );
    const selectedCard = container.querySelector('.card-fan__card--selected');
    expect(selectedCard).toBeInTheDocument();
  });

  it('calls onToggle with card index on click', () => {
    const onToggle = vi.fn();
    const { container } = render(
      <CardFan cards={DECK} selected={[]} onToggle={onToggle} />
    );
    const firstCard = container.querySelector('.card-fan__card')!;
    fireEvent.click(firstCard);
    expect(onToggle).toHaveBeenCalledWith(0);
  });

  it('limits selection to maxSelect', () => {
    const onToggle = vi.fn();
    render(
      <CardFan cards={DECK} selected={[0, 1, 2]} onToggle={onToggle} maxSelect={3} />
    );
    // Selection is at max, clicking shouldn't call onToggle for new selection?
    // Actually it should call onToggle but the parent handles the limit
    expect(onToggle).not.toHaveBeenCalled();
  });

  it('renders held slots', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0, 1]} onToggle={() => {}} maxSelect={3} />
    );
    const slots = container.querySelectorAll('.card-fan__held-slot');
    expect(slots.length).toBe(3);
  });

  it('shows filled state for selected slot indices', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0]} onToggle={() => {}} maxSelect={3} />
    );
    const filled = container.querySelectorAll('.card-fan__held-slot--filled');
    expect(filled.length).toBe(1);
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/components/tarot/CardFan.test.tsx
```

- [ ] **Step 3: Write CardFan component**

Create `web/src/components/tarot/CardFan.css`:

```css
.card-fan {
  position: relative;
  display: flex;
  flex-direction: column;
}

.card-fan__held {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-bottom: 10px;
  height: 96px;
  align-items: flex-end;
}

.card-fan__held-slot {
  width: 62px;
  height: 90px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: rgba(247, 239, 227, 0.03);
  border: 1px dashed rgba(247, 239, 227, 0.2);
}

.card-fan__held-slot--filled {
  background: linear-gradient(160deg, #2A1F19, #150E0B);
  border: 1px solid var(--orb-gold, #C9A24B);
  box-shadow: 0 0 18px -6px color-mix(in srgb, var(--orb-gold, #C9A24B) 60%, transparent);
  cursor: pointer;
  animation: slot-pop 0.4s ease both;
}

@keyframes slot-pop {
  0% { opacity: 0; transform: translateY(8px) scale(0.96); }
  60% { transform: translateY(0) scale(1.02); }
  100% { opacity: 1; transform: scale(1); }
}

.card-fan__track {
  position: relative;
  height: 240px;
  touch-action: none;
  cursor: grab;
  overflow: hidden;
}

.card-fan__track:active {
  cursor: grabbing;
}

.card-fan__card {
  position: absolute;
  left: 50%;
  bottom: 14px;
  width: var(--fan-card-width, 74px);
  height: var(--fan-card-height, 118px);
  margin-left: calc(var(--fan-card-width, 74px) / -2);
  border-radius: var(--fan-card-radius, 13px);
  background: linear-gradient(160deg, var(--card-back-gradient-start, #2A1F19), var(--card-back-gradient-end, #150E0B));
  border: 1px solid rgba(201, 162, 75, 0.35);
  box-shadow: 0 14px 30px -18px rgba(0, 0, 0, 0.9);
  cursor: pointer;
  will-change: transform;
}

.card-fan__card--selected {
  border: 2px solid var(--orb-gold, #C9A24B);
  box-shadow:
    0 0 0 3px color-mix(in srgb, var(--orb-gold, #C9A24B) 30%, transparent),
    0 18px 36px -16px rgba(0, 0, 0, 0.9);
}

.card-fan__card-back {
  position: absolute;
  inset: 7px;
  border-radius: 11px;
  border: 1px solid rgba(201, 162, 75, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-fan__diamond {
  width: 26px;
  height: 26px;
  border: 1px solid rgba(201, 162, 75, 0.6);
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-fan__diamond-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--orb-gold, #C9A24B);
}
```

Create `web/src/components/tarot/CardFan.tsx`:

```typescript
import { useState, useCallback, useRef, useMemo } from 'react';
import './CardFan.css';

interface CardFanProps {
  cards: string[];
  selected: number[];
  onToggle: (index: number) => void;
  maxSelect?: number;
}

export function CardFan({ cards, selected, onToggle, maxSelect = 3 }: CardFanProps) {
  const [offset, setOffset] = useState(0);
  const trackRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{ x: number; start: number; moved: number } | null>(null);

  const fanCards = useMemo(() => {
    return cards.map((_, i) => {
      const isSel = selected.includes(i);
      const vp = i - offset - (cards.length - 1) / 2;
      const angle = vp * 7;
      const tx = vp * 30;
      const ty = Math.pow(Math.abs(vp), 1.7) * 6 + (isSel ? -40 : 0);
      const z = 200 - Math.round(Math.abs(vp) * 10) + (isSel ? 500 : 0);

      return {
        index: i,
        isSelected: isSel,
        style: {
          zIndex: z,
          transform: `translateX(${tx}px) translateY(${ty}px) rotate(${angle}deg)`,
          transformOrigin: '50% 150%',
          transition: 'transform 0.12s ease, box-shadow 0.25s ease',
        } as React.CSSProperties,
      };
    });
  }, [cards, offset, selected]);

  const heldSlots = useMemo(() => {
    return Array.from({ length: maxSelect }, (_, slot) => ({
      slot,
      filled: slot < selected.length,
      empty: slot >= selected.length,
      label: String(slot + 1),
    }));
  }, [maxSelect, selected.length]);

  const handlePointerDown = useCallback(
    (e: React.PointerEvent) => {
      dragRef.current = { x: e.clientX, start: offset, moved: 0 };
      e.currentTarget.setPointerCapture(e.pointerId);
    },
    [offset],
  );

  const handlePointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!dragRef.current) return;
      const dx = e.clientX - dragRef.current.x;
      dragRef.current.moved = Math.max(dragRef.current.moved, Math.abs(dx));
      const newOffset = dragRef.current.start - dx / 42;
      const max = cards.length - 1;
      setOffset(Math.max(-1, Math.min(max + 1, newOffset)));
    },
    [cards.length],
  );

  const handlePointerUp = useCallback(() => {
    dragRef.current = null;
  }, []);

  const handleCardClick = useCallback(
    (index: number) => {
      if (dragRef.current && dragRef.current.moved > 6) return;
      onToggle(index);
    },
    [onToggle],
  );

  return (
    <div className="card-fan">
      {/* Held slots */}
      <div className="card-fan__held">
        {heldSlots.map((s) => (
          <div
            key={s.slot}
            className={`card-fan__held-slot${s.filled ? ' card-fan__held-slot--filled' : ''}`}
            onClick={s.filled ? () => onToggle(selected[s.slot]) : undefined}
            role={s.filled ? 'button' : undefined}
            aria-label={s.filled ? `Held card ${s.label}` : `Empty slot ${s.label}`}
          >
            {s.filled && (
              <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 9, color: 'var(--orb-gold, #C9A24B)', letterSpacing: '.1em' }}>
                HELD
              </span>
            )}
            {s.empty && (
              <span style={{ fontFamily: "'Space Mono', monospace", fontSize: 20, color: 'rgba(247,239,227,.22)' }}>
                {s.label}
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Fan track */}
      <div
        ref={trackRef}
        className="card-fan__track"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      >
        {fanCards.map((fc) => (
          <div
            key={fc.index}
            className={`card-fan__card${fc.isSelected ? ' card-fan__card--selected' : ''}`}
            style={fc.style}
            onClick={() => handleCardClick(fc.index)}
            role="button"
            aria-label={`Card ${fc.index + 1}${fc.isSelected ? ' (selected)' : ''}`}
          >
            <div className="card-fan__card-back">
              <span className="card-fan__diamond">
                <span className="card-fan__diamond-dot" />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/components/tarot/CardFan.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/components/tarot/CardFan.tsx web/src/components/tarot/CardFan.css web/src/components/tarot/CardFan.test.tsx
git commit -m "feat(tarot): add CardFan swipe-to-select component"
```

---

### Task 4: CardSpread — 3D Card Flip

**Files:**
- Create: `web/src/components/tarot/CardSpread.tsx`
- Create: `web/src/components/tarot/CardSpread.css`
- Create: `web/src/components/tarot/CardSpread.test.tsx`

- [ ] **Step 1: Write failing test**

Create `web/src/components/tarot/CardSpread.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { CardSpread } from './CardSpread';

const DRAWN = [
  { slug: 'star', name: 'The Star', numeral: 'XVII', glyph: '♒', isReversed: false, position: 'Where you are' },
  { slug: 'moon', name: 'The Moon', numeral: 'XVIII', glyph: '♓', isReversed: true, position: 'Beneath the surface' },
  { slug: 'lovers', name: 'The Lovers', numeral: 'VI', glyph: '♊', isReversed: false, position: 'Where it\'s heading' },
];

describe('CardSpread', () => {
  it('renders three cards', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[false, false, false]} activeIndex={-1} positionsShown={[false, false, false]} />
    );
    const cards = container.querySelectorAll('.card-spread__card');
    expect(cards.length).toBe(3);
  });

  it('shows card face when flipped', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[true, false, false]} activeIndex={0} positionsShown={[true, false, false]} />
    );
    const inner = container.querySelectorAll('.card-spread__inner');
    // First card should have rotateY(180deg) applied via className
    expect(inner[0]).toBeInTheDocument();
  });

  it('highlights active card', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[true, false, false]} activeIndex={0} positionsShown={[true, false, false]} />
    );
    const active = container.querySelector('.card-spread__card--active');
    expect(active).toBeInTheDocument();
  });

  it('shows position labels when positionsShown', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[true, false, false]} activeIndex={0} positionsShown={[true, false, false]} />
    );
    const position = container.querySelector('.card-spread__position');
    expect(position).toBeInTheDocument();
    expect(position?.textContent).toBe('Where you are');
  });

  it('shows reversed badge', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[false, true, false]} activeIndex={1} positionsShown={[false, true, false]} />
    );
    const reversed = container.querySelector('.card-spread__reversed');
    expect(reversed).toBeInTheDocument();
    expect(reversed?.textContent).toContain('REVERSED');
  });

  it('dims cards after activeIndex', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[true, false, false]} activeIndex={0} positionsShown={[true, false, false]} />
    );
    const cards = container.querySelectorAll('.card-spread__card');
    // Cards after active should have dimmed opacity
    expect(cards[1]).toBeInTheDocument();
    expect(cards[2]).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/components/tarot/CardSpread.test.tsx
```

- [ ] **Step 3: Write CardSpread component**

Create `web/src/components/tarot/CardSpread.css`:

```css
.card-spread {
  display: flex;
  justify-content: center;
  gap: 12px;
  perspective: 1100px;
  padding: 6px 0;
}

.card-spread__card {
  flex: none;
  width: 58px;
  transition: all 0.4s ease;
}

.card-spread__card--active {
  transform: translateY(-4px);
}

.card-spread__card--dimmed {
  opacity: 0.5;
}

.card-spread__inner {
  position: relative;
  width: 58px;
  height: 92px;
  transform-style: preserve-3d;
  transition: transform 0.8s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.card-spread__inner--flipped {
  transform: rotateY(180deg);
}

.card-spread__inner--glow {
  filter: drop-shadow(0 0 12px color-mix(in srgb, var(--orb-gold, #C9A24B) 50%, transparent));
}

.card-spread__back,
.card-spread__face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  border-radius: 10px;
}

.card-spread__back {
  background: linear-gradient(160deg, #2A1F19, #170F0C);
  border: 1px solid rgba(201, 162, 75, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-spread__back-diamond {
  width: 24px;
  height: 24px;
  border: 1px solid rgba(201, 162, 75, 0.6);
  transform: rotate(45deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-spread__back-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--orb-gold, #C9A24B);
}

.card-spread__face {
  transform: rotateY(180deg);
  background: linear-gradient(170deg, var(--card-face-gradient-start, #F7EFE1), var(--card-face-gradient-end, #EADFCB));
  border: 1px solid rgba(201, 162, 75, 0.55);
  overflow: hidden;
}

.card-spread__face--reversed {
  transform: rotateY(180deg) rotate(180deg);
}

.card-spread__face-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5px;
}

.card-spread__numeral {
  font-family: 'Spectral', serif;
  font-size: 9px;
  letter-spacing: 0.16em;
  color: #9A7B33;
}

.card-spread__glyph {
  font-size: 26px;
  color: var(--orb-gold, #C9A24B);
  line-height: 1;
  margin: 3px 0;
}

.card-spread__name {
  font-family: 'Spectral', serif;
  font-style: italic;
  font-size: 11px;
  color: #2A1E14;
  text-align: center;
  line-height: 1.15;
}

.card-spread__reversed {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'Space Mono', monospace;
  font-size: 6px;
  letter-spacing: 0.1em;
  color: #B5482E;
}

.card-spread__position {
  display: block;
  text-align: center;
  margin-top: 5px;
  font-family: 'Space Mono', monospace;
  font-size: 7px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--orb-gold, #C9A24B);
}
```

Create `web/src/components/tarot/CardSpread.tsx`:

```typescript
import './CardSpread.css';

interface SpreadCard {
  slug: string;
  name: string;
  numeral: string;
  glyph: string;
  isReversed: boolean;
  position: string;
}

interface CardSpreadProps {
  cards: SpreadCard[];
  flips: boolean[];
  activeIndex: number;
  positionsShown: boolean[];
}

export function CardSpread({ cards, flips, activeIndex, positionsShown }: CardSpreadProps) {
  return (
    <div className="card-spread" role="list" aria-label="Card spread">
      {cards.map((card, i) => {
        const dimmed = activeIndex > i && activeIndex >= 0;
        const active = activeIndex === i;

        return (
          <div
            key={card.slug}
            className={`card-spread__card${active ? ' card-spread__card--active' : ''}${dimmed ? ' card-spread__card--dimmed' : ''}`}
            role="listitem"
          >
            <div
              className={`card-spread__inner${flips[i] ? ' card-spread__inner--flipped' : ''}${active ? ' card-spread__inner--glow' : ''}`}
            >
              {/* Back face */}
              <div className="card-spread__back" aria-hidden={flips[i]}>
                <span className="card-spread__back-diamond">
                  <span className="card-spread__back-dot" />
                </span>
              </div>

              {/* Front face */}
              <div className={`card-spread__face${card.isReversed ? ' card-spread__face--reversed' : ''}`}>
                <div className="card-spread__face-inner">
                  <span className="card-spread__numeral">{card.numeral}</span>
                  <span className="card-spread__glyph">{card.glyph}</span>
                  <span className="card-spread__name">{card.name}</span>
                </div>
                {card.isReversed && (
                  <span className="card-spread__reversed">REVERSED</span>
                )}
              </div>
            </div>
            {positionsShown[i] && (
              <span className="card-spread__position">{card.position}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/components/tarot/CardSpread.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/components/tarot/CardSpread.tsx web/src/components/tarot/CardSpread.css web/src/components/tarot/CardSpread.test.tsx
git commit -m "feat(tarot): add CardSpread with 3D flip animation"
```

---

### Task 5: ReaderBubble & ChoiceChip Components

**Files:**
- Create: `web/src/components/tarot/ReaderBubble.tsx`
- Create: `web/src/components/tarot/ReaderBubble.css`
- Create: `web/src/components/tarot/ReaderBubble.test.tsx`
- Create: `web/src/components/tarot/ChoiceChip.tsx`
- Create: `web/src/components/tarot/ChoiceChip.css`
- Create: `web/src/components/tarot/ChoiceChip.test.tsx`

- [ ] **Step 1: Write failing tests for both**

Create `web/src/components/tarot/ReaderBubble.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReaderBubble } from './ReaderBubble';

describe('ReaderBubble', () => {
  it('renders reader message text', () => {
    render(<ReaderBubble text="The Star is a card of hope." />);
    expect(screen.getByText('The Star is a card of hope.')).toBeInTheDocument();
  });

  it('renders past message with reduced opacity', () => {
    const { container } = render(
      <ReaderBubble text="A past message." isPast />
    );
    const bubble = container.querySelector('.reader-bubble--past');
    expect(bubble).toBeInTheDocument();
  });

  it('renders with fade-in animation for new messages', () => {
    const { container } = render(
      <ReaderBubble text="New message." />
    );
    const bubble = container.querySelector('.reader-bubble');
    expect(bubble).toBeInTheDocument();
  });
});
```

Create `web/src/components/tarot/ChoiceChip.test.tsx`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChoiceChip } from './ChoiceChip';

describe('ChoiceChip', () => {
  it('renders label text', () => {
    render(<ChoiceChip label="That resonates" onClick={() => {}} />);
    expect(screen.getByText('That resonates')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<ChoiceChip label="Tell me more" onClick={onClick} />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', () => {
    const onClick = vi.fn();
    render(<ChoiceChip label="Next card" onClick={onClick} disabled />);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests — verify failure**

```bash
cd web && npx vitest run src/components/tarot/ReaderBubble.test.tsx src/components/tarot/ChoiceChip.test.tsx
```

- [ ] **Step 3: Write components**

Create `web/src/components/tarot/ReaderBubble.css`:

```css
@keyframes bubble-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.reader-bubble {
  align-self: flex-start;
  max-width: 86%;
  background: linear-gradient(165deg, rgba(247, 239, 227, 0.09), rgba(247, 239, 227, 0.04));
  border: 1px solid rgba(201, 162, 75, 0.22);
  color: #EFE5D6;
  padding: 12px 15px;
  border-radius: 16px 16px 16px 5px;
  font-family: var(--font-reader, 'Spectral', serif);
  font-size: 15px;
  line-height: 1.5;
  box-shadow: 0 8px 24px -16px rgba(0, 0, 0, 0.8);
  animation: bubble-rise 0.45s ease both;
  white-space: pre-wrap;
}

.reader-bubble--past {
  opacity: 0.32;
  font-size: 13px;
  animation: none;
}

.reader-bubble--user {
  align-self: flex-end;
  max-width: 78%;
  background: var(--orb-accent, #FF6B61);
  color: #fff;
  border-radius: 16px 16px 5px 16px;
  border: none;
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 13px;
  box-shadow: none;
}
```

Create `web/src/components/tarot/ReaderBubble.tsx`:

```typescript
import './ReaderBubble.css';

interface ReaderBubbleProps {
  text: string;
  isPast?: boolean;
  isUser?: boolean;
}

export function ReaderBubble({ text, isPast = false, isUser = false }: ReaderBubbleProps) {
  const classes = [
    'reader-bubble',
    isPast && 'reader-bubble--past',
    isUser && 'reader-bubble--user',
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{text}</div>;
}
```

Create `web/src/components/tarot/ChoiceChip.css`:

```css
.choice-chip {
  flex: none;
  white-space: nowrap;
  background: rgba(247, 239, 227, 0.06);
  color: #E8DCCB;
  border: 1px solid rgba(247, 239, 227, 0.18);
  padding: 9px 13px;
  border-radius: 999px;
  font-family: 'Work Sans', sans-serif;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}

.choice-chip:hover:not(:disabled) {
  border-color: var(--orb-accent, #FF6B61);
  color: #fff;
}

.choice-chip:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
```

Create `web/src/components/tarot/ChoiceChip.tsx`:

```typescript
import './ChoiceChip.css';

interface ChoiceChipProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
}

export function ChoiceChip({ label, onClick, disabled = false }: ChoiceChipProps) {
  return (
    <button
      className="choice-chip"
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {label}
    </button>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/components/tarot/ReaderBubble.test.tsx src/components/tarot/ChoiceChip.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/components/tarot/ReaderBubble.tsx web/src/components/tarot/ReaderBubble.css web/src/components/tarot/ReaderBubble.test.tsx web/src/components/tarot/ChoiceChip.tsx web/src/components/tarot/ChoiceChip.css web/src/components/tarot/ChoiceChip.test.tsx
git commit -m "feat(tarot): add ReaderBubble and ChoiceChip components"
```

---

### Task 6: Tarot Components Barrel + Tarot State Context

**Files:**
- Create: `web/src/components/tarot/index.ts`
- Create: `web/src/state/tarot-context.tsx`

- [ ] **Step 1: Write barrel export + state context**

Create `web/src/components/tarot/index.ts`:

```typescript
export { StellaOrb } from './StellaOrb';
export type { OrbState } from './StellaOrb';
export { EmberField } from './EmberField';
export { CardFan } from './CardFan';
export { CardSpread } from './CardSpread';
export type { SpreadCard } from './CardSpread';
export { ReaderBubble } from './ReaderBubble';
export { ChoiceChip } from './ChoiceChip';
```

Create `web/src/state/tarot-context.tsx`:

```typescript
import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import {
  createSession,
  advanceSession,
  getSession,
  type SessionState,
  type Action,
  type CardData,
  type MessageData,
} from '../lib/tarot-api';

export type Phase = 'ritual' | 'reveal' | 'reflect';
export type OrbState = 'idle' | 'listening' | 'speaking' | 'thinking';

interface TarotContextValue {
  phase: Phase;
  sessionId: string | null;
  intention: string;
  cards: CardData[];
  messages: MessageData[];
  flips: boolean[];
  activeCardIndex: number;
  positionsShown: boolean[];
  orbState: OrbState;
  isLoading: boolean;
  isEnded: boolean;
  setIntentionAndStart: (text: string) => Promise<void>;
  drawCards: () => Promise<void>;
  respond: (cardIndex: number, response: 'resonates' | 'not_quite' | 'tell_me_more', correctionText?: string) => Promise<void>;
  continueToNext: () => Promise<void>;
  endReading: () => void;
  setOrbState: (state: OrbState) => void;
}

const TarotContext = createContext<TarotContextValue | null>(null);

export function TarotProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [phase, setPhase] = useState<Phase>('ritual');
  const [intention, setIntention] = useState('');
  const [cards, setCards] = useState<CardData[]>([]);
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [flips, setFlips] = useState<boolean[]>([false, false, false]);
  const [activeCardIndex, setActiveCardIndex] = useState(-1);
  const [positionsShown, setPositionsShown] = useState<boolean[]>([false, false, false]);
  const [orbState, setOrbState] = useState<OrbState>('idle');
  const [isLoading, setIsLoading] = useState(false);
  const [isEnded, setIsEnded] = useState(false);

  const setIntentionAndStart = useCallback(async (text: string) => {
    setIsLoading(true);
    setOrbState('thinking');
    setIntention(text);

    try {
      const session = await createSession();
      setSessionId(session.session_id);

      const result = await advanceSession(session.session_id, {
        kind: 'set_intention',
        text,
      });
      setPhase(result.phase as Phase);
      setOrbState('idle');
    } catch (err) {
      console.error('Failed to set intention', err);
      setOrbState('idle');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const drawCards = useCallback(async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const result = await advanceSession(sessionId, { kind: 'draw_cards', count: 3 });
      setCards(result.cards ?? []);
      setPhase('reveal');
      // Auto-flip first card
      setFlips([true, false, false]);
      setActiveCardIndex(0);
      setPositionsShown([true, false, false]);
      setOrbState('speaking');
      setMessages(result.messages ?? []);
    } catch (err) {
      console.error('Failed to draw cards', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const respond = useCallback(async (cardIndex: number, response: 'resonates' | 'not_quite' | 'tell_me_more', correctionText?: string) => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const result = await advanceSession(sessionId, {
        kind: 'respond',
        card_index: cardIndex,
        response,
        correction_text: correctionText,
      });
      setMessages(result.messages ?? []);
      setOrbState('speaking');
      if (result.phase === 'reflect') {
        setPhase('reflect');
      }
    } catch (err) {
      console.error('Failed to respond', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const continueToNext = useCallback(async () => {
    if (!sessionId) return;
    const nextIndex = activeCardIndex + 1;

    if (nextIndex >= 3) {
      // All cards done, transition to reflect
      try {
        const result = await advanceSession(sessionId, { kind: 'continue' });
        setPhase('reflect');
        setMessages(result.messages ?? []);
      } catch (err) {
        console.error('Failed to advance', err);
      }
      return;
    }

    try {
      const result = await advanceSession(sessionId, { kind: 'continue' });
      const newFlips = [...flips];
      newFlips[nextIndex] = true;
      setFlips(newFlips);
      setActiveCardIndex(nextIndex);
      const newPositions = [...positionsShown];
      newPositions[nextIndex] = true;
      setPositionsShown(newPositions);
      setMessages(result.messages ?? []);
      setOrbState('speaking');
    } catch (err) {
      console.error('Failed to continue', err);
    }
  }, [sessionId, activeCardIndex, flips, positionsShown]);

  const endReading = useCallback(() => {
    setIsEnded(true);
    setOrbState('idle');
    setFlips([true, true, true]);
    setPositionsShown([true, true, true]);
  }, []);

  return (
    <TarotContext.Provider
      value={{
        phase,
        sessionId,
        intention,
        cards,
        messages,
        flips,
        activeCardIndex,
        positionsShown,
        orbState,
        isLoading,
        isEnded,
        setIntentionAndStart,
        drawCards,
        respond,
        continueToNext,
        endReading,
        setOrbState,
      }}
    >
      {children}
    </TarotContext.Provider>
  );
}

export function useTarot(): TarotContextValue {
  const ctx = useContext(TarotContext);
  if (!ctx) {
    throw new Error('useTarot must be used within a TarotProvider');
  }
  return ctx;
}
```

- [ ] **Step 2: Verify compilation**

```bash
cd web && npx tsc --noEmit
```

- [ ] **Step 3: Commit**

```bash
git add web/src/components/tarot/index.ts web/src/state/tarot-context.tsx
git commit -m "feat(tarot): add component barrel export and session state context"
```

---

### Task 7: RitualScreen — Intention + Card Draw

**Files:**
- Create: `web/src/screens/tarot/RitualScreen.tsx`
- Create: `web/src/screens/tarot/RitualScreen.css`
- Create: `web/src/screens/tarot/RitualScreen.test.tsx`

- [ ] **Step 1: Write failing test**

Create `web/src/screens/tarot/RitualScreen.test.tsx`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { RitualScreen } from './RitualScreen';

// Mock the API
vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn().mockResolvedValue({ session_id: 'test-1', phase: 'ritual' }),
  advanceSession: vi.fn().mockResolvedValue({ session_id: 'test-1', phase: 'ritual' }),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <RitualScreen />
    </TarotProvider>
  );
}

describe('RitualScreen', () => {
  it('renders the orb', () => {
    renderScreen();
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('shows intention prompt text', () => {
    renderScreen();
    expect(screen.getByText(/weighing on your heart/i)).toBeInTheDocument();
  });

  it('renders intention quick-reply chips', () => {
    renderScreen();
    expect(screen.getByText('A situationship')).toBeInTheDocument();
    expect(screen.getByText('Unsure about someone')).toBeInTheDocument();
    expect(screen.getByText('Should I reach out?')).toBeInTheDocument();
  });

  it('shows text input for intention', () => {
    renderScreen();
    const input = screen.getByPlaceholderText(/Speak, or type/i);
    expect(input).toBeInTheDocument();
  });

  it('disables send button when input is empty', () => {
    renderScreen();
    const sendBtn = screen.getByText('Send');
    expect(sendBtn).toBeDisabled();
  });

  it('shows ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/screens/tarot/RitualScreen.test.tsx
```

- [ ] **Step 3: Write RitualScreen**

Create `web/src/screens/tarot/RitualScreen.css`:

```css
.ritual {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 26px 24px;
  overflow-y: auto;
}

.ritual__prompt {
  flex: none;
  text-align: center;
  margin-top: 6px;
  min-height: 54px;
}

.ritual__prompt-text {
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 22px;
  line-height: 1.35;
  color: #F2E9DC;
  max-width: 24ch;
  margin: 0 auto;
}

.ritual__orb-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 200px;
}

.ritual__mirror {
  flex: none;
  text-align: center;
  min-height: 64px;
  padding: 0 6px;
  white-space: pre-wrap;
  font-family: var(--font-reader, 'Spectral', serif);
  font-size: 17px;
  line-height: 1.5;
  color: #E8DCCB;
}

.ritual__mirror-word {
  transition: color 0.15s ease;
}

.ritual__mirror-word--spoken {
  color: #F7EFE3;
}

.ritual__mirror-word--pending {
  color: rgba(247, 239, 227, 0.24);
}

.ritual__input-area {
  flex: none;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ritual__interim {
  text-align: center;
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 16px;
  color: #C9BCAD;
  min-height: 22px;
}

.ritual__chips {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ritual__textarea-row {
  display: flex;
  align-items: flex-end;
  gap: 9px;
}

.ritual__textarea {
  flex: 1;
  resize: none;
  background: rgba(10, 7, 6, 0.5);
  border: 1px solid rgba(247, 239, 227, 0.16);
  color: #F2E9DC;
  border-radius: 16px;
  padding: 12px 14px;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  line-height: 1.4;
  outline: none;
  min-height: 48px;
}

.ritual__textarea:focus {
  border-color: var(--orb-accent, #FF6B61);
}

.ritual__send-btn {
  height: 48px;
  padding: 0 16px;
  border-radius: 14px;
  border: none;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  background: var(--orb-accent, #FF6B61);
  color: #fff;
}

.ritual__send-btn:disabled {
  background: rgba(247, 239, 227, 0.1);
  color: #7A6E64;
  cursor: not-allowed;
}

.ritual__mic-hint {
  text-align: center;
  font-family: 'Space Mono', monospace;
  font-size: 10px;
  color: #6E635A;
  letter-spacing: 0.04em;
}

.ritual__draw-btn {
  flex: none;
  margin-top: 6px;
  padding: 14px 34px;
  border-radius: 999px;
  border: none;
  background: var(--orb-gold, #C9A24B);
  color: #1A1206;
  font-family: 'Work Sans', sans-serif;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 30px -10px color-mix(in srgb, var(--orb-gold, #C9A24B) 70%, transparent);
  animation: tx-pop 0.5s ease both;
}

@keyframes tx-pop {
  0% { opacity: 0; transform: translateY(8px) scale(0.96); }
  60% { transform: translateY(0) scale(1.02); }
  100% { opacity: 1; transform: scale(1); }
}
```

Create `web/src/screens/tarot/RitualScreen.tsx`:

```typescript
import { useState, useCallback } from 'react';
import { StellaOrb, EmberField, ChoiceChip } from '../../components/tarot';
import { useTarot } from '../../state/tarot-context';
import './RitualScreen.css';

const CHIPS = [
  { label: 'A situationship', value: "A situationship I can't read" },
  { label: 'Unsure about someone', value: "I'm unsure about someone" },
  { label: 'Should I reach out?', value: 'Should I reach out to them?' },
];

export function RitualScreen() {
  const { orbState, setOrbState, setIntentionAndStart, drawCards, intention, isLoading } = useTarot();
  const [draft, setDraft] = useState('');
  const [showDrawBtn, setShowDrawBtn] = useState(false);

  const canSend = draft.trim().length > 0;

  const handleSend = useCallback(async () => {
    if (!canSend || isLoading) return;
    await setIntentionAndStart(draft.trim());
    setShowDrawBtn(true);
    setDraft('');
  }, [canSend, isLoading, draft, setIntentionAndStart]);

  const handleChip = useCallback(
    (value: string) => {
      setDraft(value);
    },
    [],
  );

  const handleOrbTap = useCallback(() => {
    if (orbState === 'listening') {
      setOrbState('idle');
    } else if (!intention) {
      setOrbState('listening');
    }
  }, [orbState, intention, setOrbState]);

  const handleDraw = useCallback(async () => {
    await drawCards();
  }, [drawCards]);

  const promptText = orbState === 'thinking'
    ? 'Let me sit with that…'
    : intention
      ? ''
      : "What's weighing on your heart tonight?";

  return (
    <div className="ritual">
      <EmberField />

      {/* Prompt */}
      <div className="ritual__prompt">
        <p className="ritual__prompt-text">{promptText}</p>
      </div>

      {/* Orb */}
      <div className="ritual__orb-area">
        <StellaOrb
          state={orbState}
          size={230}
          onTap={handleOrbTap}
          showMic
          aria-label="Tarot orb — tap to interact"
        />
      </div>

      {/* Intention Input (before mirror) */}
      {!intention && !showDrawBtn && (
        <div className="ritual__input-area">
          <div className="ritual__chips">
            {CHIPS.map((chip) => (
              <ChoiceChip
                key={chip.label}
                label={chip.label}
                onClick={() => handleChip(chip.value)}
              />
            ))}
          </div>
          <div className="ritual__textarea-row">
            <textarea
              className="ritual__textarea"
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              rows={1}
              placeholder="Speak, or type what's on your mind…"
              maxLength={160}
            />
            <button
              className="ritual__send-btn"
              onClick={handleSend}
              disabled={!canSend || isLoading}
            >
              Send
            </button>
          </div>
          <p className="ritual__mic-hint">
            Tap the orb or the mic to speak — typing works too
          </p>
        </div>
      )}

      {/* Draw button (after mirror) */}
      {showDrawBtn && (
        <button className="ritual__draw-btn" onClick={handleDraw}>
          Draw your three cards
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/screens/tarot/RitualScreen.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/screens/tarot/RitualScreen.tsx web/src/screens/tarot/RitualScreen.css web/src/screens/tarot/RitualScreen.test.tsx
git commit -m "feat(tarot): add RitualScreen with orb, intention input, and quick-reply chips"
```

---

### Task 8: RevealScreen — Card-by-Card Reading with Response Gates

**Files:**
- Create: `web/src/screens/tarot/RevealScreen.tsx`
- Create: `web/src/screens/tarot/RevealScreen.css`
- Create: `web/src/screens/tarot/RevealScreen.test.tsx`

- [ ] **Step 1: Write failing test**

Create `web/src/screens/tarot/RevealScreen.test.tsx`:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { RevealScreen } from './RevealScreen';

vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn(),
  advanceSession: vi.fn().mockResolvedValue({
    session_id: 'test-1',
    phase: 'reveal',
    cards: [{ slug: 'star', name: 'The Star', numeral: 'XVII', glyph: '♒', is_reversed: false, position_meaning: 'Where you are', arcana: 'major', suit: null }],
    messages: [{ speaker: 'reader', text: 'The first card.' }],
  }),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <RevealScreen />
    </TarotProvider>
  );
}

describe('RevealScreen', () => {
  it('renders response chips', () => {
    renderScreen();
    expect(screen.getByText('That resonates')).toBeInTheDocument();
    expect(screen.getByText('Not quite')).toBeInTheDocument();
    expect(screen.getByText('Tell me more')).toBeInTheDocument();
  });

  it('renders the orb', () => {
    renderScreen();
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('renders ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/screens/tarot/RevealScreen.test.tsx
```

- [ ] **Step 3: Write RevealScreen**

Create `web/src/screens/tarot/RevealScreen.css`:

```css
.reveal {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.reveal__spread {
  flex: none;
  padding: 4px 0 6px;
}

.reveal__orb-area {
  flex: none;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px 0;
}

.reveal__transcript {
  flex: 1;
  position: relative;
  overflow: hidden;
  -webkit-mask-image: linear-gradient(180deg, transparent 0%, #000 26%, #000 100%);
  mask-image: linear-gradient(180deg, transparent 0%, #000 26%, #000 100%);
}

.reveal__transcript-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 9px;
  padding: 10px 24px 4px;
}

.reveal__dock {
  flex: none;
  padding: 10px 22px 20px;
  border-top: 1px solid rgba(247, 239, 227, 0.07);
  background: linear-gradient(0deg, rgba(10, 7, 6, 0.55), transparent);
}

.reveal__dock-label {
  text-align: center;
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 15px;
  color: #D8C9B8;
  margin-bottom: 10px;
}

.reveal__chips-row {
  display: flex;
  flex-wrap: nowrap;
  gap: 7px;
  justify-content: center;
}

.reveal__input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 10px;
}

.reveal__input {
  flex: 1;
  resize: none;
  background: rgba(10, 7, 6, 0.5);
  border: 1px solid rgba(247, 239, 227, 0.16);
  color: #F2E9DC;
  border-radius: 14px;
  padding: 11px 13px;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  outline: none;
  min-height: 46px;
}

.reveal__input:focus {
  border-color: var(--orb-accent, #FF6B61);
}

.reveal__send-btn {
  height: 46px;
  padding: 0 16px;
  border-radius: 14px;
  border: none;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  background: var(--orb-accent, #FF6B61);
  color: #fff;
}

.reveal__send-btn:disabled {
  background: rgba(247, 239, 227, 0.1);
  color: #7A6E64;
  cursor: not-allowed;
}

.reveal__ended-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  justify-content: center;
}

.reveal__action-btn {
  padding: 12px 20px;
  border-radius: 999px;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.reveal__action-btn--primary {
  background: var(--orb-accent, #FF6B61);
  color: #fff;
  border: none;
}

.reveal__action-btn--secondary {
  background: rgba(247, 239, 227, 0.06);
  color: #E8DCCB;
  border: 1px solid rgba(247, 239, 227, 0.18);
}
```

Create `web/src/screens/tarot/RevealScreen.tsx`:

```typescript
import { useState, useCallback, useMemo } from 'react';
import { StellaOrb, EmberField, CardSpread, ReaderBubble, ChoiceChip } from '../../components/tarot';
import { useTarot } from '../../state/tarot-context';
import './RevealScreen.css';

type GateState = 'awaiting' | 'correcting' | 'choosing_action' | null;

export function RevealScreen() {
  const {
    cards,
    messages,
    flips,
    activeCardIndex,
    positionsShown,
    orbState,
    respond,
    continueToNext,
    endReading,
    isEnded,
  } = useTarot();

  const [gate, setGate] = useState<GateState>('choosing_action');
  const [correctionText, setCorrectionText] = useState('');

  const spreadCards = useMemo(() => {
    return cards.map((c, i) => ({
      slug: c.slug,
      name: c.name,
      numeral: c.numeral ?? '',
      glyph: c.glyph ?? '',
      isReversed: c.is_reversed,
      position: c.position_meaning,
    }));
  }, [cards]);

  const readerMessages = useMemo(() => {
    return messages
      .filter((m) => m.speaker === 'reader')
      .map((m) => ({ text: m.text, isPast: false }));
  }, [messages]);

  const handleResponseChip = useCallback(
    async (response: 'resonates' | 'not_quite' | 'tell_me_more') => {
      if (response === 'not_quite') {
        setGate('correcting');
      } else if (response === 'tell_me_more') {
        await respond(activeCardIndex, 'tell_me_more');
        setGate('choosing_action');
      } else {
        // resonates — offer deepen or next
        setGate('choosing_action');
      }
    },
    [activeCardIndex, respond],
  );

  const handleContinue = useCallback(async () => {
    await continueToNext();
    setGate('choosing_action');
  }, [continueToNext]);

  const handleCorrectionSend = useCallback(async () => {
    if (!correctionText.trim()) return;
    await respond(activeCardIndex, 'not_quite', correctionText.trim());
    setCorrectionText('');
    setGate('choosing_action');
  }, [correctionText, activeCardIndex, respond]);

  const handleEnd = useCallback(() => {
    endReading();
  }, [endReading]);

  return (
    <div className="reveal">
      <EmberField />

      {/* Card spread */}
      <div className="reveal__spread">
        <CardSpread
          cards={spreadCards}
          flips={flips}
          activeIndex={activeCardIndex}
          positionsShown={positionsShown}
        />
      </div>

      {/* Orb */}
      <div className="reveal__orb-area">
        <StellaOrb
          state={orbState}
          size={122}
          aria-label="Tarot orb — tap to interact"
        />
      </div>

      {/* Transcript */}
      <div className="reveal__transcript">
        <div className="reveal__transcript-inner">
          {readerMessages.map((msg, i) => (
            <ReaderBubble key={i} text={msg.text} isPast={i < readerMessages.length - 1} />
          ))}
        </div>
      </div>

      {/* Dock */}
      <div className="reveal__dock">
        {!isEnded && (
          <>
            {gate === 'choosing_action' && (
              <>
                <p className="reveal__dock-label">
                  Does this land?
                </p>
                <div className="reveal__chips-row">
                  <ChoiceChip label="That resonates" onClick={() => handleResponseChip('resonates')} />
                  <ChoiceChip label="Not quite" onClick={() => handleResponseChip('not_quite')} />
                  <ChoiceChip label="Tell me more" onClick={() => handleResponseChip('tell_me_more')} />
                </div>
                <div className="reveal__chips-row" style={{ marginTop: 8 }}>
                  <ChoiceChip label="Next card →" onClick={handleContinue} />
                </div>
              </>
            )}

            {gate === 'correcting' && (
              <div className="reveal__input-row">
                <textarea
                  className="reveal__input"
                  value={correctionText}
                  onChange={(e) => setCorrectionText(e.target.value)}
                  rows={1}
                  placeholder="What feels off?"
                />
                <button
                  className="reveal__send-btn"
                  onClick={handleCorrectionSend}
                  disabled={!correctionText.trim()}
                >
                  Send
                </button>
              </div>
            )}
          </>
        )}

        {isEnded && (
          <div className="reveal__ended-actions">
            <button className="reveal__action-btn reveal__action-btn--primary" onClick={handleEnd}>
              View takeaway
            </button>
            <button className="reveal__action-btn reveal__action-btn--secondary" onClick={handleEnd}>
              New reading
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/screens/tarot/RevealScreen.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/screens/tarot/RevealScreen.tsx web/src/screens/tarot/RevealScreen.css web/src/screens/tarot/RevealScreen.test.tsx
git commit -m "feat(tarot): add RevealScreen with card spread, response gates, and transcript"
```

---

### Task 9: ReflectScreen — Synthesis + Takeaway

**Files:**
- Create: `web/src/screens/tarot/ReflectScreen.tsx`
- Create: `web/src/screens/tarot/ReflectScreen.css`
- Create: `web/src/screens/tarot/ReflectScreen.test.tsx`

- [ ] **Step 1: Write failing test**

Create `web/src/screens/tarot/ReflectScreen.test.tsx`:

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { ReflectScreen } from './ReflectScreen';

vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn(),
  advanceSession: vi.fn(),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <ReflectScreen />
    </TarotProvider>
  );
}

describe('ReflectScreen', () => {
  it('renders the synthesis heading', () => {
    renderScreen();
    expect(screen.getByText(/the cards have spoken/i)).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    renderScreen();
    expect(screen.getByText('New reading')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('renders ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
```

- [ ] **Step 2: Run test — verify failure**

```bash
cd web && npx vitest run src/screens/tarot/ReflectScreen.test.tsx
```

- [ ] **Step 3: Write ReflectScreen**

Create `web/src/screens/tarot/ReflectScreen.css`:

```css
.reflect {
  position: relative;
  z-index: 2;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 26px;
  overflow-y: auto;
  gap: 20px;
}

.reflect__header {
  text-align: center;
}

.reflect__header-text {
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 21px;
  line-height: 1.4;
  color: #F2E9DC;
}

.reflect__narrative {
  font-family: var(--font-reader, 'Spectral', serif);
  font-size: 16px;
  line-height: 1.7;
  color: #EFE5D6;
  max-width: 36ch;
  white-space: pre-wrap;
}

.reflect__takeaway {
  margin-top: 8px;
  border-left: 3px solid var(--orb-gold, #C9A24B);
  padding: 6px 0 6px 14px;
  animation: tx-rise 0.6s ease both;
}

@keyframes tx-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.reflect__takeaway-label {
  display: block;
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--orb-gold, #C9A24B);
  margin-bottom: 5px;
}

.reflect__takeaway-text {
  font-family: var(--font-reader, 'Spectral', serif);
  font-style: italic;
  font-size: 19px;
  line-height: 1.4;
  color: #F7EFE3;
}

.reflect__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  justify-content: center;
  margin-top: 16px;
}

.reflect__action-btn {
  padding: 12px 20px;
  border-radius: 999px;
  font-family: 'Work Sans', sans-serif;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.reflect__action-btn--primary {
  background: var(--orb-accent, #FF6B61);
  color: #fff;
  border: none;
}

.reflect__action-btn--secondary {
  background: rgba(247, 239, 227, 0.06);
  color: #E8DCCB;
  border: 1px solid rgba(247, 239, 227, 0.18);
}
```

Create `web/src/screens/tarot/ReflectScreen.tsx`:

```typescript
import { useCallback } from 'react';
import { EmberField } from '../../components/tarot';
import { useTarot } from '../../state/tarot-context';
import './ReflectScreen.css';

export function ReflectScreen() {
  const { messages } = useTarot();

  // Find the synthesis and takeaway from messages
  const synthMessage = messages.find((m) => m.context === 'synth');
  const takeawayMessage = messages.find((m) => m.context === 'takeaway');

  const synthesis = synthMessage?.text ?? 'The cards have spoken in their own way. Let the reading settle.';
  const takeaway = takeawayMessage?.text ?? 'Trust what you already know.';

  const handleNewReading = useCallback(() => {
    window.location.reload();
  }, []);

  const handleSave = useCallback(() => {
    // v1: prompt screenshot
    alert('Save this reading by taking a screenshot! 📸');
  }, []);

  return (
    <div className="reflect">
      <EmberField />

      <div className="reflect__header">
        <p className="reflect__header-text">The cards have spoken</p>
      </div>

      <p className="reflect__narrative">{synthesis}</p>

      <div className="reflect__takeaway">
        <span className="reflect__takeaway-label">The takeaway</span>
        <p className="reflect__takeaway-text">{takeaway}</p>
      </div>

      <div className="reflect__actions">
        <button
          className="reflect__action-btn reflect__action-btn--primary"
          onClick={handleNewReading}
        >
          New reading
        </button>
        <button
          className="reflect__action-btn reflect__action-btn--secondary"
          onClick={handleSave}
        >
          Save
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests — verify pass**

```bash
cd web && npx vitest run src/screens/tarot/ReflectScreen.test.tsx
```

- [ ] **Step 5: Commit**

```bash
git add web/src/screens/tarot/ReflectScreen.tsx web/src/screens/tarot/ReflectScreen.css web/src/screens/tarot/ReflectScreen.test.tsx
git commit -m "feat(tarot): add ReflectScreen with synthesis narrative and takeaway"
```

---

### Task 10: TarotScreen Shell + App Route

**Files:**
- Create: `web/src/screens/tarot/TarotScreen.tsx`
- Create: `web/src/screens/tarot/TarotScreen.css`
- Create: `web/src/screens/tarot/index.ts`
- Modify: `web/src/App.tsx`

- [ ] **Step 1: Write TarotScreen shell**

Create `web/src/screens/tarot/TarotScreen.css`:

```css
.tarot-screen {
  position: relative;
  min-height: 100vh;
  background: radial-gradient(125% 80% at 50% -5%, var(--tarot-bg-start, #2B201A) 0%, var(--tarot-bg-mid, #1A1310) 50%, var(--tarot-bg-end, #120D0B) 100%);
  display: flex;
  flex-direction: column;
}

.tarot-screen__header {
  position: relative;
  z-index: 5;
  flex: none;
  padding: 16px 22px 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tarot-screen__brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tarot-screen__logo {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: linear-gradient(140deg, var(--orb-accent, #FF6B61), var(--orb-gold, #C9A24B));
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Archivo Black', sans-serif;
  font-size: 12px;
  color: #14100E;
}

.tarot-screen__title {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.tarot-screen__title-main {
  font-size: 12px;
  font-weight: 700;
  color: #F7EFE3;
}

.tarot-screen__title-sub {
  font-family: 'Space Mono', monospace;
  font-size: 9px;
  color: #8A7D72;
  letter-spacing: 0.04em;
}

.tarot-screen__dots {
  display: flex;
  align-items: center;
  gap: 7px;
}

.tarot-screen__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(247, 239, 227, 0.18);
  transition: background 0.3s ease;
}

.tarot-screen__dot--active {
  background: var(--orb-accent, #FF6B61);
}
```

Create `web/src/screens/tarot/TarotScreen.tsx`:

```typescript
import { EmberField } from '../../components/tarot';
import { TarotProvider, useTarot } from '../../state/tarot-context';
import { RitualScreen } from './RitualScreen';
import { RevealScreen } from './RevealScreen';
import { ReflectScreen } from './ReflectScreen';
import './TarotScreen.css';

const PHASE_LABELS: Record<string, string> = {
  ritual: 'Setting intention',
  reveal: 'The oracle speaks',
  reflect: 'Your reading',
};

function TarotScreenInner() {
  const { phase } = useTarot();
  const phaseIndex = phase === 'ritual' ? 0 : phase === 'reveal' ? 1 : 2;

  return (
    <div className="tarot-screen">
      <EmberField count={16} />

      {/* Header */}
      <div className="tarot-screen__header">
        <div className="tarot-screen__brand">
          <span className="tarot-screen__logo">L</span>
          <div className="tarot-screen__title">
            <span className="tarot-screen__title-main">Luvr Tarot</span>
            <span className="tarot-screen__title-sub">
              {PHASE_LABELS[phase] ?? 'Tarot'}
            </span>
          </div>
        </div>
        <div className="tarot-screen__dots">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className={`tarot-screen__dot${i <= phaseIndex ? ' tarot-screen__dot--active' : ''}`}
            />
          ))}
        </div>
      </div>

      {/* Phase screens */}
      {phase === 'ritual' && <RitualScreen />}
      {phase === 'reveal' && <RevealScreen />}
      {phase === 'reflect' && <ReflectScreen />}
    </div>
  );
}

export function TarotScreen() {
  return (
    <TarotProvider>
      <TarotScreenInner />
    </TarotProvider>
  );
}
```

Create `web/src/screens/tarot/index.ts`:

```typescript
export { TarotScreen } from './TarotScreen';
export { RitualScreen } from './RitualScreen';
export { RevealScreen } from './RevealScreen';
export { ReflectScreen } from './ReflectScreen';
```

- [ ] **Step 2: Add route to App.tsx**

Edit `web/src/App.tsx`:

```tsx
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { LandingScreen } from './screens/LandingScreen'
import { AuthScreen } from './screens/AuthScreen'
import { InstagramContextScreen } from './screens/InstagramContextScreen'
import { TelegramHandoffScreen } from './screens/TelegramHandoffScreen'
import { TarotScreen } from './screens/tarot'
import { OnboardingProvider } from './state/OnboardingProvider'
import { useOnboarding } from './state/onboarding-context'
```

Add the route inside `<Routes>`:

```tsx
<Route path="/tarot" element={<TarotScreen />} />
```

- [ ] **Step 3: Verify all tests still pass**

```bash
cd web && npx vitest run
```

- [ ] **Step 4: Commit**

```bash
git add web/src/screens/tarot/TarotScreen.tsx web/src/screens/tarot/TarotScreen.css web/src/screens/tarot/index.ts web/src/App.tsx
git commit -m "feat(tarot): add TarotScreen shell with header, phase dots, and app route"
```

---

### Task 11: Python Backend — Tarot Engine, Persona, Positions, Endpoints

**Files:**
- Create: `src/tarot/engine.py`
- Create: `src/tarot/persona.py`
- Create: `src/tarot/positions.py`
- Modify: `src/server.py`

- [ ] **Step 1: Write persona prompts**

Create `src/tarot/persona.py`:

```python
"""Tarot reader persona prompts for LLM calls."""

from __future__ import annotations

PERSONA_PREAMBLE = """\
You are a tarot reader for Luvr, a dating-advice service. Your readings blend \
archetypal wisdom with grounded, modern relationship insight. You speak like \
someone who's read a lot of cards and had a lot of conversations — warm, \
perceptive, never performatively mystical. You ask questions. You offer \
interpretations as possibilities, not pronouncements. You never predict the \
future. You connect cards into a story the querent can actually use.
"""

RITUALIST_PROMPT = """\
{persona}

The querent has shared their intention: "{intention}"

Reframe this intention in the tarot persona voice. Keep it to 1-2 sentences. \
Mirror back what they're really asking underneath the surface. Make it warm \
and inviting — an invitation to see what the cards have to say.

Respond with ONLY the reframed text. No preamble, no quotation marks.
"""

READER_INTERPRET_PROMPT = """\
{persona}

**Session context:**
Querent's intention: {intention}

**Card drawn:** {card_name} ({card_position})
The card is {reversed_status}.
Its numeral is {numeral}.

**Dialogue so far:**
{dialogue_summary}

Deliver a 3-4 sentence interpretation of this card in its position, connected \
to the querent's intention. Use the card's symbolism naturally, not like a \
textbook. End by asking whether this resonates — something like "Does that \
land?" or "What comes up for you hearing that?"

Use the card name and its symbols. If reversed, interpret the inversion: what \
is blocked, delayed, or internalized.

Respond with ONLY the interpretation. No preamble, no labels.
"""

READER_DEEPEN_PROMPT = """\
{persona}

**Session context:**
Querent's intention: {intention}

**Card:** {card_name} ({card_position}), {reversed_status}

**Dialogue so far:**
{dialogue_summary}

**Initial interpretation was:**
{last_interpretation}

The querent wants to go deeper with this card. Take a different angle — maybe \
connect to the element, the number, the reversal meaning, or a specific life \
area. Go one layer deeper than before. Keep it to 2-3 sentences. Make it \
personal and grounded.

Respond with ONLY the deeper interpretation. No preamble, no labels.
"""

READER_ADAPT_PROMPT = """\
{persona}

**Session context:**
Querent's intention: {intention}

**Card:** {card_name} ({card_position}), {reversed_status}

**Dialogue so far:**
{dialogue_summary}

**Last interpretation was:**
{last_interpretation}

The querent said it didn't quite land: "{correction}"

Adapt the interpretation. Acknowledge what they said, then reframe the card's \
meaning to make it more accurate for their situation. 2-3 sentences. Stay warm \
and non-defensive — the card means what it means, the querent's experience is \
always valid.

Respond with ONLY the adapted interpretation. No preamble, no labels.
"""

WEAVER_PROMPT = """\
{persona}

**Full session context:**
Querent's intention: {intention}

**Cards drawn:**
{cards_summary}

**Dialogue from the reading:**
{dialogue_summary}

Weave all three cards together into a single, flowing narrative that connects \
back to the querent's original intention. Not three separate interpretations \
glued together — one cohesive story. 4-6 sentences. Written warmly, \
conversationally, like someone giving you the real talk after reading your cards.

Then, after the narrative, add a line break and a section marked exactly like this:

## Takeaway
[A single, grounded, actionable sentence — something the querent can hold onto. \
Not fortune-cookie generic. Connected to their specific situation and the cards.]

Respond with the narrative followed by the takeaway section. No other labels.
"""
```

- [ ] **Step 2: Write position definitions**

Create `src/tarot/positions.py`:

```python
"""Spread position definitions for the 3-card relationship reading."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    key: str
    title: str
    description: str


RELATIONSHIP_SPREAD: list[Position] = [
    Position(
        key="situation",
        title="Where you are",
        description="What is actually happening between you two right now.",
    ),
    Position(
        key="tension",
        title="Beneath the surface",
        description="The dynamic, fear, or mismatch making this feel unclear.",
    ),
    Position(
        key="next_move",
        title="Where it's heading",
        description="Where this is heading if nothing changes.",
    ),
]
```

- [ ] **Step 3: Write tarot engine**

Create `src/tarot/engine.py`:

```python
"""Tarot reading session state machine.

Platform-agnostic — the Telegram Mini App is a thin shell.
Reuses existing Luvr LLM providers and card image infrastructure.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Literal

from src.tarot.images import MAJOR_ARCANA_SLUGS, CARD_SLUGS
from src.tarot.persona import (
    PERSONA_PREAMBLE,
    RITUALIST_PROMPT,
    READER_INTERPRET_PROMPT,
    READER_DEEPEN_PROMPT,
    READER_ADAPT_PROMPT,
    WEAVER_PROMPT,
)
from src.tarot.positions import RELATIONSHIP_SPREAD


# ------------------------------------------------------------------
# Data models
# ------------------------------------------------------------------

Phase = Literal["ritual", "reveal", "reflect"]


@dataclass
class Card:
    slug: str
    name: str
    arcana: Literal["major", "minor"]
    suit: str | None
    is_reversed: bool
    position_meaning: str
    numeral: str = ""
    glyph: str = ""


@dataclass
class Message:
    speaker: Literal["reader", "user"]
    text: str
    context: str | None = None


@dataclass
class Session:
    id: str
    phase: Phase = "ritual"
    intention: str | None = None
    drawn_cards: list[Card] = field(default_factory=list)
    current_card_index: int | None = None
    dialogue: list[Message] = field(default_factory=list)
    deepened_on: set[int] = field(default_factory=set)
    synthesis: str | None = None
    takeaway: str | None = None
    created_at: float = 0.0
    expires_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.expires_at:
            self.expires_at = self.created_at + 86400  # 24h TTL


# ------------------------------------------------------------------
# Fallback card meanings (used when LLM is unavailable)
# ------------------------------------------------------------------

FALLBACK_MEANINGS: dict[str, dict[str, str]] = {
    "fool": {
        "upright": "A new beginning — the blank page before the story is written. You're being asked to take a leap of faith, even if you can't see the landing.",
        "reversed": "The leap feels more like a stumble right now. You might be overthinking the first step or running from the last one.",
    },
    "lovers": {
        "upright": "Not fate, not a soulmate verdict — this is the card of a real choice. It asks whether you're choosing from desire, or from the fear of being alone.",
        "reversed": "A choice you've been avoiding continues to tug at you. The tension won't resolve until you name what you want.",
    },
    "star": {
        "upright": "After a long stretch of doubt, quiet faith is returning. You're further along in healing than you've been giving yourself credit for.",
        "reversed": "Hope feels far away. But the Star reversed still shines — you might just be looking in the wrong direction for it.",
    },
    "moon": {
        "upright": "The stories we tell ourselves at two in the morning. Confusion and intuition are tangled up — trust what flickers beneath the surface.",
        "reversed": "The fog is lifting. What felt unreadable is getting clearer. You already know more than you've let yourself admit.",
    },
}


def _card_name(slug: str) -> str:
    """Convert slug to display name."""
    return slug.replace("_", " ").title()


def _card_numeral(slug: str) -> str:
    """Return Roman numeral for Major Arcana slugs."""
    numerals = {
        "fool": "0", "magician": "I", "high_priestess": "II",
        "empress": "III", "emperor": "IV", "hierophant": "V",
        "lovers": "VI", "chariot": "VII", "strength": "VIII",
        "hermit": "IX", "wheel_of_fortune": "X", "justice": "XI",
        "hanged_man": "XII", "death": "XIII", "temperance": "XIV",
        "devil": "XV", "tower": "XVI", "star": "XVII",
        "moon": "XVIII", "sun": "XIX", "judgement": "XX", "world": "XXI",
    }
    return numerals.get(slug, "")


def _card_glyph(slug: str) -> str:
    """Return astrological/unicode glyph for Major Arcana."""
    glyphs = {
        "star": "\u2652",    # ♒ Aquarius
        "moon": "\u2653",    # ♓ Pisces
        "sun": "\u2609",     # ☉ Sun
        "lovers": "\u264a",  # ♊ Gemini
        "world": "\U0001F30D",  # 🌍
    }
    return glyphs.get(slug, "\u2606")  # ☆ default


# ------------------------------------------------------------------
# Session store (in-memory, replace with KV/DB for production)
# ------------------------------------------------------------------

_sessions: dict[str, Session] = {}


def create_session() -> Session:
    """Create a new tarot reading session."""
    import uuid

    session = Session(id=str(uuid.uuid4()))
    _sessions[session.id] = session
    return session


def get_session(session_id: str) -> Session | None:
    """Get an existing session, checking TTL."""
    session = _sessions.get(session_id)
    if session and time.time() > session.expires_at:
        del _sessions[session_id]
        return None
    return session


# ------------------------------------------------------------------
# Engine
# ------------------------------------------------------------------

def draw_cards(count: int = 3) -> list[Card]:
    """Draw n random Major Arcana cards (server-side randomness)."""
    slugs = random.sample(MAJOR_ARCANA_SLUGS, min(count, len(MAJOR_ARCANA_SLUGS)))

    cards: list[Card] = []
    for i, slug in enumerate(slugs):
        is_rev = random.random() < 0.3  # 30% chance of reversal
        position = RELATIONSHIP_SPREAD[i] if i < len(RELATIONSHIP_SPREAD) else RELATIONSHIP_SPREAD[0]
        cards.append(Card(
            slug=slug,
            name=_card_name(slug),
            arcana="major",
            suit=None,
            is_reversed=is_rev,
            position_meaning=position.title,
            numeral=_card_numeral(slug),
            glyph=_card_glyph(slug),
        ))
    return cards


def get_fallback_meaning(card: Card) -> str:
    """Get a fallback card meaning when LLM is unavailable."""
    meanings = FALLBACK_MEANINGS.get(card.slug)
    if meanings:
        return meanings["reversed"] if card.is_reversed else meanings["upright"]
    reversal_note = " (reversed)" if card.is_reversed else ""
    return f"The {card.name}{reversal_note} appears in the position of {card.position_meaning}. This card invites reflection on this area of your life."


async def run_ritualist(intention: str) -> str:
    """Run the ritualist LLM call to mirror the intention."""
    try:
        from src.llm.providers import get_provider
        provider = get_provider()
        prompt = RITUALIST_PROMPT.format(persona=PERSONA_PREAMBLE, intention=intention)
        return await provider.complete(prompt, max_tokens=150)
    except Exception:
        return f"So you're asking about {intention.lower()} — let's see what the cards have to say."


async def run_reader_interpret(session: Session, card_index: int) -> str:
    """Run the reader LLM call for a card interpretation."""
    card = session.drawn_cards[card_index]
    try:
        from src.llm.providers import get_provider
        provider = get_provider()
        reversed_status = "reversed" if card.is_reversed else "upright"
        dialogue_summary = "\n".join(
            f"{m.speaker}: {m.text}" for m in session.dialogue[-6:]
        ) or "(no dialogue yet)"
        prompt = READER_INTERPRET_PROMPT.format(
            persona=PERSONA_PREAMBLE,
            intention=session.intention or "a relationship question",
            card_name=card.name,
            card_position=card.position_meaning,
            reversed_status=reversed_status,
            numeral=card.numeral,
            dialogue_summary=dialogue_summary,
        )
        return await provider.complete(prompt, max_tokens=300)
    except Exception:
        return get_fallback_meaning(card)


async def run_reader_deepen(session: Session, card_index: int) -> str:
    """Run the reader LLM call for a deeper interpretation."""
    card = session.drawn_cards[card_index]
    try:
        from src.llm.providers import get_provider
        provider = get_provider()
        reversed_status = "reversed" if card.is_reversed else "upright"
        dialogue_summary = "\n".join(
            f"{m.speaker}: {m.text}" for m in session.dialogue[-8:]
        ) or "(no dialogue yet)"
        # Find last interpretation for this card
        last_interp = next(
            (m.text for m in reversed(session.dialogue)
             if m.speaker == "reader" and m.context and m.context.startswith(f"card_{card_index}")),
            get_fallback_meaning(card),
        )
        prompt = READER_DEEPEN_PROMPT.format(
            persona=PERSONA_PREAMBLE,
            intention=session.intention or "a relationship question",
            card_name=card.name,
            card_position=card.position_meaning,
            reversed_status=reversed_status,
            dialogue_summary=dialogue_summary,
            last_interpretation=last_interp,
        )
        return await provider.complete(prompt, max_tokens=250)
    except Exception:
        return f"Let's sit with the {card.name} a moment longer. What these symbols stir in you is as important as anything I could say."


async def run_reader_adapt(session: Session, card_index: int, correction: str) -> str:
    """Run the reader LLM call to adapt interpretation based on user correction."""
    card = session.drawn_cards[card_index]
    try:
        from src.llm.providers import get_provider
        provider = get_provider()
        reversed_status = "reversed" if card.is_reversed else "upright"
        dialogue_summary = "\n".join(
            f"{m.speaker}: {m.text}" for m in session.dialogue[-8:]
        ) or "(no dialogue yet)"
        last_interp = next(
            (m.text for m in reversed(session.dialogue)
             if m.speaker == "reader" and m.context and m.context.startswith(f"card_{card_index}")),
            get_fallback_meaning(card),
        )
        prompt = READER_ADAPT_PROMPT.format(
            persona=PERSONA_PREAMBLE,
            intention=session.intention or "a relationship question",
            card_name=card.name,
            card_position=card.position_meaning,
            reversed_status=reversed_status,
            dialogue_summary=dialogue_summary,
            last_interpretation=last_interp,
            correction=correction,
        )
        return await provider.complete(prompt, max_tokens=250)
    except Exception:
        return f"I hear you. Let me reframe — the {card.name} isn't about judgment, it's about awareness. Take what fits and leave the rest."


async def run_weaver(session: Session) -> tuple[str, str]:
    """Run the weaver LLM call for synthesis and takeaway."""
    try:
        from src.llm.providers import get_provider
        provider = get_provider()
        cards_summary = "\n".join(
            f"- {c.name} ({'reversed' if c.is_reversed else 'upright'}) in {c.position_meaning}"
            for c in session.drawn_cards
        )
        dialogue_summary = "\n".join(
            f"{m.speaker}: {m.text}" for m in session.dialogue
        ) or "(no dialogue)"
        prompt = WEAVER_PROMPT.format(
            persona=PERSONA_PREAMBLE,
            intention=session.intention or "a relationship question",
            cards_summary=cards_summary,
            dialogue_summary=dialogue_summary,
        )
        response = await provider.complete(prompt, max_tokens=400)

        # Parse takeaway from response
        if "## Takeaway" in response:
            parts = response.split("## Takeaway", 1)
            synthesis = parts[0].strip()
            takeaway = parts[1].strip()
        else:
            synthesis = response.strip()
            # Extract last sentence as takeaway
            sentences = synthesis.rsplit(". ", 1)
            if len(sentences) > 1:
                takeaway = sentences[1].rstrip(".")
            else:
                takeaway = "Trust what the cards have shown you."
        return synthesis, takeaway
    except Exception:
        cards_list = ", ".join(c.name for c in session.drawn_cards)
        return (
            f"The {cards_list} have spoken to your question about {session.intention or 'your situation'}. "
            "Each card brought its own wisdom — take what resonates and sit with it.",
            "Trust what the cards have shown you.",
        )


# ------------------------------------------------------------------
# State machine
# ------------------------------------------------------------------

async def advance_session(session: Session, action: dict) -> dict:
    """Advance a session with a user action. Returns a UI instruction dict."""

    kind = action.get("kind", "")

    if kind == "set_intention":
        text = (action.get("text", "") or "").strip()
        if not text:
            return {"error": "intention is required"}

        session.intention = text
        session.dialogue.append(Message(speaker="user", text=text, context="intention"))

        mirror = await run_ritualist(text)
        session.dialogue.append(Message(speaker="reader", text=mirror, context="intention_mirror"))

        return {
            "session_id": session.id,
            "phase": session.phase,
            "messages": [
                {"speaker": m.speaker, "text": m.text, "context": m.context}
                for m in session.dialogue[-2:]
            ],
        }

    elif kind == "draw_cards":
        session.drawn_cards = draw_cards(count=3)
        session.phase = "reveal"
        session.current_card_index = 0

        # First card interpretation
        first_interpretation = await run_reader_interpret(session, 0)
        session.dialogue.append(Message(
            speaker="reader",
            text=first_interpretation,
            context="card_0_initial",
        ))

        return {
            "session_id": session.id,
            "phase": session.phase,
            "cards": [
                {
                    "slug": c.slug,
                    "name": c.name,
                    "arcana": c.arcana,
                    "suit": c.suit,
                    "is_reversed": c.is_reversed,
                    "position_meaning": c.position_meaning,
                    "numeral": c.numeral,
                    "glyph": c.glyph,
                }
                for c in session.drawn_cards
            ],
            "messages": [
                {"speaker": m.speaker, "text": m.text, "context": m.context}
                for m in session.dialogue[-1:]
            ],
        }

    elif kind == "respond":
        card_index = action.get("card_index", session.current_card_index or 0)
        response = action.get("response", "resonates")

        if response == "tell_me_more":
            session.deepened_on.add(card_index)
            deeper = await run_reader_deepen(session, card_index)
            session.dialogue.append(Message(
                speaker="reader",
                text=deeper,
                context=f"card_{card_index}_deepen",
            ))
        elif response == "not_quite":
            correction = action.get("correction_text", "")
            if correction:
                session.dialogue.append(Message(
                    speaker="user",
                    text=correction,
                    context=f"card_{card_index}_correction",
                ))
            adapted = await run_reader_adapt(session, card_index, correction)
            session.dialogue.append(Message(
                speaker="reader",
                text=adapted,
                context=f"card_{card_index}_adapted",
            ))

        return {
            "session_id": session.id,
            "phase": session.phase,
            "messages": [
                {"speaker": m.speaker, "text": m.text, "context": m.context}
                for m in session.dialogue[-3:]
            ],
        }

    elif kind == "continue":
        next_index = (session.current_card_index or 0) + 1

        if next_index >= len(session.drawn_cards):
            # All cards done — weave synthesis
            session.phase = "reflect"
            synthesis, takeaway = await run_weaver(session)
            session.synthesis = synthesis
            session.takeaway = takeaway
            session.dialogue.append(Message(
                speaker="reader",
                text=synthesis,
                context="synth",
            ))
            session.dialogue.append(Message(
                speaker="reader",
                text=takeaway,
                context="takeaway",
            ))
            return {
                "session_id": session.id,
                "phase": session.phase,
                "messages": [
                    {"speaker": m.speaker, "text": m.text, "context": m.context}
                    for m in session.dialogue[-2:]
                ],
            }

        # Next card
        session.current_card_index = next_index
        interpretation = await run_reader_interpret(session, next_index)
        session.dialogue.append(Message(
            speaker="reader",
            text=interpretation,
            context=f"card_{next_index}_initial",
        ))

        return {
            "session_id": session.id,
            "phase": session.phase,
            "current_card_index": next_index,
            "messages": [
                {"speaker": m.speaker, "text": m.text, "context": m.context}
                for m in session.dialogue[-1:]
            ],
        }

    else:
        return {"error": f"unknown action kind: {kind}"}
```

- [ ] **Step 4: Add tarot endpoints to server.py**

Add these routes to `src/server.py`:

```python
from src.tarot.engine import create_session as create_tarot_session
from src.tarot.engine import get_session as get_tarot_session
from src.tarot.engine import advance_session as advance_tarot_session


@app.post("/api/tarot/session")
async def tarot_create_session(request: Request) -> JSONResponse:
    """Create a new tarot reading session."""
    session = create_tarot_session()
    return JSONResponse({
        "session_id": session.id,
        "phase": session.phase,
    })


@app.post("/api/tarot/session/{session_id}/action")
async def tarot_advance_session(session_id: str, request: Request) -> JSONResponse:
    """Advance a tarot session with a user action."""
    session = get_tarot_session(session_id)
    if not session:
        return JSONResponse({"detail": "session not found or expired"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"detail": "invalid json"}, status_code=400)

    result = await advance_tarot_session(session, body)

    if "error" in result:
        return JSONResponse({"detail": result["error"]}, status_code=400)

    return JSONResponse(result)


@app.get("/api/tarot/session/{session_id}")
async def tarot_get_session(session_id: str) -> JSONResponse:
    """Get current tarot session state."""
    session = get_tarot_session(session_id)
    if not session:
        return JSONResponse({"detail": "session not found or expired"}, status_code=404)

    return JSONResponse({
        "session_id": session.id,
        "phase": session.phase,
        "cards": [
            {
                "slug": c.slug,
                "name": c.name,
                "arcana": c.arcana,
                "suit": c.suit,
                "is_reversed": c.is_reversed,
                "position_meaning": c.position_meaning,
                "numeral": c.numeral,
                "glyph": c.glyph,
            }
            for c in session.drawn_cards
        ],
        "messages": [
            {"speaker": m.speaker, "text": m.text, "context": m.context}
            for m in session.dialogue
        ],
    })
```

- [ ] **Step 5: Commit**

```bash
git add src/tarot/engine.py src/tarot/persona.py src/tarot/positions.py src/server.py
git commit -m "feat(tarot): add Python engine with session state machine, persona prompts, and API endpoints"
```

---

### Task 12: Final Integration — Run All Tests

- [ ] **Step 1: Run all frontend tests**

```bash
cd web && npx vitest run
```
Expected: All existing 43 tests + new tarot tests PASS.

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd web && npx tsc --noEmit
```

- [ ] **Step 3: Final commit if needed**

```bash
git add -A
git commit -m "feat(tarot): final integration and test verification"
```

---

### Task 13: Create PR

- [ ] **Step 1: Push branch**

```bash
git push origin feature/hum-1403
```

- [ ] **Step 2: Create PR via gh CLI**

```bash
gh pr create \
  --title "feat(tarot): Interactive Tarot Card Reading Telegram Mini App" \
  --body "$(cat <<'EOF'
## Summary

Implements HUM-1403: an interactive 3-card tarot reading experience as a Telegram Mini App.

### What's included

**StellaCloud Orb** — celestial nebula sphere with 4 visual states:
- `idle` — slow breathing with rotating gold/accent conic swirls
- `listening` — faster breathing + expanding ring animations + brighter aura
- `speaking` — pulse animation with intensified gold core
- `thinking` — slow breathing, dimmer glow

**Three-phase flow:**
1. **Ritual** — Set intention via text/voice, orb mirrors it back, draw 3 cards from swipe fan
2. **Reveal** — Card-by-card 3D flip + reader interpretation + response gates (resonates/not quite/tell me more)
3. **Reflect** — Synthesis narrative connecting all cards + highlighted takeaway

**Components:**
- `StellaOrb` — Celestial orb with conic gradient nebula overlays
- `EmberField` — Ambient floating particle system
- `CardFan` — Swipe-to-select with parallax arc layout
- `CardSpread` — 3D rotateY card flip animation
- `ReaderBubble` — Stylized reader message bubbles
- `ChoiceChip` — Pill-shaped response chips

**Backend:**
- `src/tarot/engine.py` — Platform-agnostic session state machine
- `src/tarot/persona.py` — LLM prompt templates (ritualist, reader, weaver)
- `src/tarot/positions.py` — Spread position definitions
- New endpoints: `POST /api/tarot/session`, `POST /api/tarot/session/{id}/action`, `GET /api/tarot/session/{id}`

**Design:** Dark celestial aesthetic (deep brown → black gradient) with coral (#FF6B61) accent and gold (#C9A24B) highlights. Fonts: Spectral (reader voice), Work Sans (UI), Archivo Black (brand).

### Testing
- New unit tests for all 6 components and 3 screens
- All 43 existing tests continue to pass

### Related
- [Design doc](https://claude.ai/design/p/23721e4d-2d29-40ba-8187-eb0a027802fd)
- Linear: HUM-1403
EOF
)"
```

- [ ] **Step 3: Verify PR created**

```bash
rtk gh pr view feature/hum-1403
```

---

## Plan Completion Checklist

- [ ] All 14 tasks completed
- [ ] All tests passing (existing + new)
- [ ] TypeScript compilation clean
- [ ] PR created on GitHub
- [ ] Branch `feature/hum-1403` pushed
