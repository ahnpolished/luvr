import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { ReflectScreen } from './ReflectScreen';

vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn(),
  advanceSession: vi.fn(),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <ReflectScreen />
    </TarotProvider>
  );
}

describe('ReflectScreen', () => {
  it('renders the synthesis heading', () => {
    renderScreen();
    const heading = screen.getByText('The cards have spoken', { selector: '.reflect__header-text' });
    expect(heading).toBeInTheDocument();
  });

  it('renders action buttons', () => {
    renderScreen();
    expect(screen.getByText('New reading')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('renders ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
