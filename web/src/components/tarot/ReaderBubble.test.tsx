import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ReaderBubble } from './ReaderBubble';

describe('ReaderBubble', () => {
  it('renders reader message text', () => {
    render(<ReaderBubble text="The Star is a card of hope." />);
    expect(screen.getByText('The Star is a card of hope.')).toBeInTheDocument();
  });

  it('renders past message with reduced opacity', () => {
    const { container } = render(
      <ReaderBubble text="A past message." isPast />
    );
    const bubble = container.querySelector('.reader-bubble--past');
    expect(bubble).toBeInTheDocument();
  });

  it('renders user-style message', () => {
    const { container } = render(
      <ReaderBubble text="User said this." isUser />
    );
    const bubble = container.querySelector('.reader-bubble--user');
    expect(bubble).toBeInTheDocument();
  });
});
