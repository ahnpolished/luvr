import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TarotProvider } from '../../state/tarot-context';
import { RitualScreen } from './RitualScreen';

vi.mock('../../lib/tarot-api', () => ({
  createSession: vi.fn().mockResolvedValue({ session_id: 'test-1', phase: 'ritual' }),
  advanceSession: vi.fn().mockResolvedValue({ session_id: 'test-1', phase: 'ritual' }),
  getSession: vi.fn(),
}));

function renderScreen() {
  return render(
    <TarotProvider>
      <RitualScreen />
    </TarotProvider>
  );
}

describe('RitualScreen', () => {
  it('renders the orb', () => {
    renderScreen();
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('shows intention prompt text', () => {
    renderScreen();
    expect(screen.getByText(/weighing on your heart/i)).toBeInTheDocument();
  });

  it('renders intention quick-reply chips', () => {
    renderScreen();
    expect(screen.getByText('A situationship')).toBeInTheDocument();
    expect(screen.getByText('Unsure about someone')).toBeInTheDocument();
    expect(screen.getByText('Should I reach out?')).toBeInTheDocument();
  });

  it('shows text input for intention', () => {
    renderScreen();
    const input = screen.getByPlaceholderText(/Speak, or type/i);
    expect(input).toBeInTheDocument();
  });

  it('disables send button when input is empty', () => {
    renderScreen();
    const sendBtn = screen.getByText('Send');
    expect(sendBtn).toBeDisabled();
  });

  it('shows ember particles', () => {
    const { container } = renderScreen();
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBeGreaterThan(0);
  });
});
