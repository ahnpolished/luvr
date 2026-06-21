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
