import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CardFan } from './CardFan';

const DECK = ['fool', 'magician', 'high_priestess'];

describe('CardFan', () => {
  it('renders all cards from the deck', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[]} onToggle={() => {}} />
    );
    const cards = container.querySelectorAll('.card-fan__card');
    expect(cards.length).toBe(DECK.length);
  });

  it('applies selected class to selected cards', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0]} onToggle={() => {}} />
    );
    const selectedCard = container.querySelector('.card-fan__card--selected');
    expect(selectedCard).toBeInTheDocument();
  });

  it('calls onToggle with card index on click', () => {
    const onToggle = vi.fn();
    const { container } = render(
      <CardFan cards={DECK} selected={[]} onToggle={onToggle} />
    );
    const firstCard = container.querySelector('.card-fan__card')!;
    fireEvent.click(firstCard);
    expect(onToggle).toHaveBeenCalledWith(0);
  });

  it('renders held slots', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0, 1]} onToggle={() => {}} maxSelect={3} />
    );
    const slots = container.querySelectorAll('.card-fan__held-slot');
    expect(slots.length).toBe(3);
  });

  it('shows filled state for selected slot indices', () => {
    const { container } = render(
      <CardFan cards={DECK} selected={[0]} onToggle={() => {}} maxSelect={3} />
    );
    const filled = container.querySelectorAll('.card-fan__held-slot--filled');
    expect(filled.length).toBe(1);
  });
});
