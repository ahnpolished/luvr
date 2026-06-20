import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Card } from './Card'

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Hello</Card>)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('defaults to the narrow (mobile-card) variant', () => {
    render(<Card>Content</Card>)
    expect(screen.getByText('Content')).toHaveClass('lv-card--narrow')
  })

  it('applies the wide variant when requested', () => {
    render(<Card wide>Content</Card>)
    expect(screen.getByText('Content')).toHaveClass('lv-card--wide')
  })
})
