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
