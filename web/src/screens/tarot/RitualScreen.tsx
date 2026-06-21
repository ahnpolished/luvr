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
