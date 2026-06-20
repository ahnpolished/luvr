import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { LandingScreen } from './LandingScreen'

describe('LandingScreen', () => {
  it('renders without crashing and shows the headline', () => {
    render(<LandingScreen onGetStarted={vi.fn()} />)
    expect(
      screen.getByText("Dating is confusing. Your advice shouldn't be."),
    ).toBeInTheDocument()
  })

  it('renders a primary CTA that is enabled', () => {
    render(<LandingScreen onGetStarted={vi.fn()} />)
    const cta = screen.getByRole('button', { name: 'Start texting Luvr' })
    expect(cta).toBeEnabled()
  })

  it('calls onGetStarted when the hero CTA is clicked', async () => {
    const onGetStarted = vi.fn()
    render(<LandingScreen onGetStarted={onGetStarted} />)
    await userEvent.click(screen.getByRole('button', { name: 'Start texting Luvr' }))
    expect(onGetStarted).toHaveBeenCalledTimes(1)
  })

  it('disables the not-yet-available iMessage channel', () => {
    render(<LandingScreen onGetStarted={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Notify me' })).toBeDisabled()
  })
})
