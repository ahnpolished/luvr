import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import {
  createSession,
  advanceSession,
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
      if (result.messages) {
        setMessages(result.messages);
      }
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
      setFlips([true, false, false]);
      setActiveCardIndex(0);
      setPositionsShown([true, false, false]);
      setOrbState('speaking');
      if (result.messages) {
        setMessages(result.messages);
      }
    } catch (err) {
      console.error('Failed to draw cards', err);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  const respond = useCallback(async (
    cardIndex: number,
    response: 'resonates' | 'not_quite' | 'tell_me_more',
    correctionText?: string,
  ) => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const result = await advanceSession(sessionId, {
        kind: 'respond',
        card_index: cardIndex,
        response,
        correction_text: correctionText,
      });
      if (result.messages) {
        setMessages(result.messages);
      }
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
      try {
        const result = await advanceSession(sessionId, { kind: 'continue' });
        setPhase('reflect');
        if (result.messages) {
          setMessages(result.messages);
        }
      } catch (err) {
        console.error('Failed to advance to reflect', err);
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
      if (result.messages) {
        setMessages(result.messages);
      }
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
