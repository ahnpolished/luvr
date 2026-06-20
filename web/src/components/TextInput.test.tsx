import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TextInput } from './TextInput'

describe('TextInput', () => {
  it('renders a label associated with the input', () => {
    render(<TextInput label="Phone number" placeholder="(555) 012 3456" />)
    expect(screen.getByLabelText('Phone number')).toBeInTheDocument()
  })

  it('renders an adornment', () => {
    render(<TextInput label="Phone number" adornment="+1" />)
    expect(screen.getByText('+1')).toBeInTheDocument()
  })

  it('shows helper text when no error is present', () => {
    render(<TextInput label="Instagram handle" helperText="Public profiles only." />)
    expect(screen.getByText('Public profiles only.')).toBeInTheDocument()
  })

  it('shows error text and marks the input invalid', () => {
    render(<TextInput label="Phone number" error="Enter a valid phone number" />)
    expect(screen.getByText('Enter a valid phone number')).toBeInTheDocument()
    expect(screen.getByLabelText('Phone number')).toHaveAttribute(
      'aria-invalid',
      'true',
    )
  })

  it('calls onChange as the user types', async () => {
    const onChange = vi.fn()
    render(<TextInput label="Instagram handle" onChange={onChange} />)
    await userEvent.type(screen.getByLabelText('Instagram handle'), 'abc')
    expect(onChange).toHaveBeenCalledTimes(3)
  })
})
