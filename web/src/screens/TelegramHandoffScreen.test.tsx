import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { TelegramHandoffScreen } from './TelegramHandoffScreen'

describe('TelegramHandoffScreen', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders without crashing and shows the deep link', () => {
    render(<TelegramHandoffScreen deepLink="https://t.me/LuvrBot?start=abc" />)
    expect(screen.getByText('https://t.me/LuvrBot?start=abc')).toBeInTheDocument()
  })

  it('opens the deep link when the CTA is clicked', async () => {
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null)
    render(<TelegramHandoffScreen deepLink="https://t.me/LuvrBot?start=abc" />)
    await userEvent.click(screen.getByRole('button', { name: 'Open in Telegram' }))
    expect(openSpy).toHaveBeenCalledWith(
      'https://t.me/LuvrBot?start=abc',
      '_blank',
      'noopener,noreferrer',
    )
  })

  it('falls back to a default mocked deep link', () => {
    render(<TelegramHandoffScreen />)
    expect(screen.getByText(/t\.me\//)).toBeInTheDocument()
  })
})
