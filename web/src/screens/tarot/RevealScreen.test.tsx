import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { RevealScreen } from './RevealScreen';

vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn(),
  advanceSession: vi.fn().mockResolvedValue({
    session_id: 'test-1',
    phase: 'reveal',
    cards: [{ slug: 'star', name: 'The Star', numeral: 'XVII', glyph: '\u2652', is_reversed: false, position_meaning: 'Where you are', arcana: 'major', suit: null }],
    messages: [{ speaker: 'reader', text: 'The first card.' }],
  }),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <RevealScreen />
    </TarotProvider>
  );
}

describe('RevealScreen', () => {
  it('renders response chips', () => {
    renderScreen();
    expect(screen.getByText('That resonates')).toBeInTheDocument();
    expect(screen.getByText('Not quite')).toBeInTheDocument();
    expect(screen.getByText('Tell me more')).toBeInTheDocument();
  });

  it('renders the orb', () => {
    renderScreen();
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('renders ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
