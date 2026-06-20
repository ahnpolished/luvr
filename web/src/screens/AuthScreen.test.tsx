import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AuthScreen } from './AuthScreen'

describe('AuthScreen', () => {
  it('renders without crashing on the phone step', () => {
    render(<AuthScreen onVerified={vi.fn()} />)
    expect(screen.getByLabelText('Phone number')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Send code' })).toBeInTheDocument()
  })

  it('shows an inline error for an invalid phone number', async () => {
    render(<AuthScreen onVerified={vi.fn()} />)
    await userEvent.type(screen.getByLabelText('Phone number'), '123')
    await userEvent.click(screen.getByRole('button', { name: 'Send code' }))
    expect(screen.getByText('Enter a valid phone number.')).toBeInTheDocument()
  })

  it('advances to the OTP step with a valid phone number', async () => {
    render(<AuthScreen onVerified={vi.fn()} />)
    await userEvent.type(screen.getByLabelText('Phone number'), '5551234567')
    await userEvent.click(screen.getByRole('button', { name: 'Send code' }))
    expect(screen.getByRole('button', { name: 'Verify' })).toBeInTheDocument()
  })

  it('calls onVerified once a 6-digit code is entered', async () => {
    const onVerified = vi.fn()
    render(<AuthScreen onVerified={onVerified} />)
    await userEvent.type(screen.getByLabelText('Phone number'), '5551234567')
    await userEvent.click(screen.getByRole('button', { name: 'Send code' }))

    const boxes = screen.getAllByRole('textbox', { name: /Digit/ })
    for (let i = 0; i < 6; i += 1) {
      await userEvent.type(boxes[i], String(i + 1))
    }
    expect(onVerified).toHaveBeenCalledWith('5551234567')
  })

  it('disables the email path (descoped per HUM-1373)', () => {
    render(<AuthScreen onVerified={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Use email instead' })).toBeDisabled()
  })
})
