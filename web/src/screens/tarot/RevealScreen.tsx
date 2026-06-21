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
    return cards.map((c) => ({
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
                <p className="reveal__dock-label">Does this land?</p>
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
            <button className="reveal__action-btn reveal__action-btn--primary" onClick={endReading}>
              View takeaway
            </button>
            <button className="reveal__action-btn reveal__action-btn--secondary" onClick={endReading}>
              New reading
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
