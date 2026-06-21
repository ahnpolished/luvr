import './CardSpread.css';

export interface SpreadCard {
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
