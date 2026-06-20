import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('onboarding flow', () => {
  it('walks through Landing -> Auth -> Context -> Telegram in sequence', async () => {
    render(<App />)

    // Landing
    expect(
      screen.getByText("Dating is confusing. Your advice shouldn't be."),
    ).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Start texting Luvr' }))

    // Auth: phone -> OTP
    expect(screen.getByLabelText('Phone number')).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Phone number'), '5551234567')
    await userEvent.click(screen.getByRole('button', { name: 'Send code' }))
    const digitBoxes = screen.getAllByRole('textbox', { name: /Digit/ })
    for (let i = 0; i < 6; i += 1) {
      await userEvent.type(digitBoxes[i], String(i + 1))
    }

    // Instagram context
    expect(await screen.findByLabelText('Instagram handle')).toBeInTheDocument()
    await userEvent.type(screen.getByLabelText('Instagram handle'), 'jane.doe')
    await userEvent.click(screen.getByRole('button', { name: 'Continue' }))

    // Telegram hand-off
    expect(
      await screen.findByText("You're all set. Now say hi on Telegram."),
    ).toBeInTheDocument()
  })

  it('redirects unknown routes back to Landing', () => {
    window.history.pushState({}, '', '/some/unknown/route')
    render(<App />)
    expect(
      screen.getByText("Dating is confusing. Your advice shouldn't be."),
    ).toBeInTheDocument()
  })
})
