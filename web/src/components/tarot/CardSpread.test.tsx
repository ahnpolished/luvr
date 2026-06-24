import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { CardSpread } from './CardSpread';

const DRAWN = [
  { slug: 'star', name: 'The Star', numeral: 'XVII', glyph: '\u2652', isReversed: false, position: 'Where you are' },
  { slug: 'moon', name: 'The Moon', numeral: 'XVIII', glyph: '\u2653', isReversed: true, position: 'Beneath the surface' },
  { slug: 'lovers', name: 'The Lovers', numeral: 'VI', glyph: '\u264a', isReversed: false, position: "Where it's heading" },
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
    const inner = container.querySelectorAll('.card-spread__inner--flipped');
    expect(inner.length).toBe(1);
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

  it('dims cards before activeIndex (already read)', () => {
    const { container } = render(
      <CardSpread cards={DRAWN} flips={[true, true, false]} activeIndex={1} positionsShown={[true, true, false]} />
    );
    const dimmed = container.querySelectorAll('.card-spread__card--dimmed');
    // Card 0 (already read) should be dimmed, cards 1-2 not
    expect(dimmed.length).toBe(1);
  });
});
