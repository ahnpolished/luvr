import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { EmberField } from './EmberField';

describe('EmberField', () => {
  it('renders the correct number of ember particles', () => {
    const { container } = render(<EmberField count={12} />);
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBe(12);
  });

  it('renders 16 embers by default', () => {
    const { container } = render(<EmberField />);
    const embers = container.querySelectorAll('.ember-field__particle');
    expect(embers.length).toBe(16);
  });

  it('has a container that fills its parent', () => {
    const { container } = render(<EmberField />);
    const field = container.querySelector('.ember-field');
    expect(field).toBeInTheDocument();
  });

  it('renders glow element by default', () => {
    const { container } = render(<EmberField />);
    const glow = container.querySelector('.ember-field__glow');
    expect(glow).toBeInTheDocument();
  });

  it('hides glow when showGlow is false', () => {
    const { container } = render(<EmberField showGlow={false} />);
    const glow = container.querySelector('.ember-field__glow');
    expect(glow).toBeNull();
  });
});
