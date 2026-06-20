import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Button } from './Button'

describe('Button', () => {
  it('renders children and defaults to primary/md', () => {
    render(<Button>Start texting</Button>)
    const button = screen.getByRole('button', { name: 'Start texting' })
    expect(button).toHaveClass('lv-button--primary')
    expect(button).toHaveClass('lv-button--md')
  })

  it('applies variant and size classes', () => {
    render(
      <Button variant="secondary" size="lg">
        See how it works
      </Button>,
    )
    const button = screen.getByRole('button', { name: 'See how it works' })
    expect(button).toHaveClass('lv-button--secondary')
    expect(button).toHaveClass('lv-button--lg')
  })

  it('renders ghost variant for link-style actions', () => {
    render(<Button variant="ghost">I&apos;d rather describe myself</Button>)
    expect(screen.getByRole('button')).toHaveClass('lv-button--ghost')
  })

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Continue</Button>)
    await userEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', async () => {
    const onClick = vi.fn()
    render(
      <Button onClick={onClick} disabled>
        Continue
      </Button>,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('applies full width modifier', () => {
    render(<Button fullWidth>Send code</Button>)
    expect(screen.getByRole('button')).toHaveClass('lv-button--full')
  })
})
