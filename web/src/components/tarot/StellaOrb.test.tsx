import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { StellaOrb } from './StellaOrb';

describe('StellaOrb', () => {
  it('renders with default idle state', () => {
    render(<StellaOrb state="idle" />);
    const orb = screen.getByRole('button', { name: /orb/i });
    expect(orb).toBeInTheDocument();
  });

  it('applies listening class when state is listening', () => {
    const { container } = render(<StellaOrb state="listening" />);
    const orb = container.querySelector('.orb--listening');
    expect(orb).toBeInTheDocument();
  });

  it('applies speaking class when state is speaking', () => {
    const { container } = render(<StellaOrb state="speaking" />);
    const orb = container.querySelector('.orb--speaking');
    expect(orb).toBeInTheDocument();
  });

  it('applies thinking class when state is thinking', () => {
    const { container } = render(<StellaOrb state="thinking" />);
    const orb = container.querySelector('.orb--thinking');
    expect(orb).toBeInTheDocument();
  });

  it('renders expanding rings when listening', () => {
    const { container } = render(<StellaOrb state="listening" />);
    const rings = container.querySelectorAll('.orb__ring');
    expect(rings.length).toBe(2);
  });

  it('does not render rings when not listening', () => {
    const { container } = render(<StellaOrb state="idle" />);
    const rings = container.querySelectorAll('.orb__ring');
    expect(rings.length).toBe(0);
  });

  it('calls onTap when clicked', () => {
    const onTap = vi.fn();
    render(<StellaOrb state="idle" onTap={onTap} />);
    fireEvent.click(screen.getByRole('button', { name: /orb/i }));
    expect(onTap).toHaveBeenCalledTimes(1);
  });

  it('renders with custom size', () => {
    const { container } = render(<StellaOrb state="idle" size={120} />);
    const orb = container.querySelector('.orb');
    expect(orb).toBeInTheDocument();
  });

  it('shows mic icon when showMic is true and listening', () => {
    render(<StellaOrb state="listening" showMic />);
    const mic = screen.getByLabelText(/mic active/i);
    expect(mic).toBeInTheDocument();
  });
});
