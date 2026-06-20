import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import { OTPInput } from './OTPInput'

function Controlled({ onComplete }: { onComplete?: (v: string) => void }) {
  const [value, setValue] = useState('')
  return (
    <OTPInput value={value} onChange={setValue} onComplete={onComplete} label="Code" />
  )
}

describe('OTPInput', () => {
  it('renders the configured number of digit boxes', () => {
    render(<OTPInput length={6} value="" onChange={vi.fn()} label="Code" />)
    expect(screen.getAllByRole('textbox')).toHaveLength(6)
  })

  it('auto-advances focus as digits are typed and calls onComplete', async () => {
    const onComplete = vi.fn()
    render(<Controlled onComplete={onComplete} />)
    const boxes = screen.getAllByRole('textbox')
    const digits = '123456'
    for (let i = 0; i < digits.length; i += 1) {
      await userEvent.type(boxes[i], digits[i])
    }
    expect(onComplete).toHaveBeenCalledWith('123456')
  })

  it('moves focus back on backspace from an empty box', async () => {
    render(<Controlled />)
    const boxes = screen.getAllByRole('textbox')
    await userEvent.type(boxes[0], '1')
    expect(boxes[1]).toHaveFocus()
    await userEvent.type(boxes[1], '{backspace}')
    expect(boxes[0]).toHaveFocus()
  })

  it('splits a pasted 6-digit code across all boxes', async () => {
    const onComplete = vi.fn()
    render(<Controlled onComplete={onComplete} />)
    const boxes = screen.getAllByRole('textbox')
    await userEvent.click(boxes[0])
    await userEvent.paste('654321')
    expect(onComplete).toHaveBeenCalledWith('654321')
  })

  it('shows an error message when provided', () => {
    render(<OTPInput value="" onChange={vi.fn()} error="Invalid code" label="Code" />)
    expect(screen.getByText('Invalid code')).toBeInTheDocument()
  })
})
