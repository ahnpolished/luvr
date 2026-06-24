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
          // CSS custom properties for animation
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
