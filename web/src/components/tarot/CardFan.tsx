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
