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
