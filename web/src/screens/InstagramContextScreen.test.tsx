import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { InstagramContextScreen } from './InstagramContextScreen'

describe('InstagramContextScreen', () => {
  it('renders the Instagram handle field by default', () => {
    render(<InstagramContextScreen onContinue={vi.fn()} />)
    expect(screen.getByLabelText('Instagram handle')).toBeInTheDocument()
  })

  it('calls onContinue with the typed handle', async () => {
    const onContinue = vi.fn()
    render(<InstagramContextScreen onContinue={onContinue} />)
    await userEvent.type(screen.getByLabelText('Instagram handle'), 'jane.doe')
    await userEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(onContinue).toHaveBeenCalledWith({ handle: 'jane.doe' })
  })

  it('reveals the self-summary fallback without blocking the user', async () => {
    render(<InstagramContextScreen onContinue={vi.fn()} />)
    await userEvent.click(
      screen.getByRole('button', { name: "I'd rather describe myself" }),
    )
    expect(screen.getByLabelText('About you')).toBeInTheDocument()
    expect(screen.queryByLabelText('Instagram handle')).not.toBeInTheDocument()
  })

  it('calls onContinue with the self-summary fallback', async () => {
    const onContinue = vi.fn()
    render(<InstagramContextScreen onContinue={onContinue} />)
    await userEvent.click(
      screen.getByRole('button', { name: "I'd rather describe myself" }),
    )
    await userEvent.type(screen.getByLabelText('About you'), 'into hiking')
    await userEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(onContinue).toHaveBeenCalledWith({ selfSummary: 'into hiking' })
  })
})
