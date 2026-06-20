import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StepHeader } from './StepHeader'

describe('StepHeader', () => {
  it('renders the wordmark and step count', () => {
    render(<StepHeader currentStep={2} totalSteps={3} />)
    expect(screen.getByText('Luvr')).toBeInTheDocument()
    expect(screen.getByText('STEP 2 / 3')).toBeInTheDocument()
  })

  it('fills the correct number of progress segments', () => {
    render(<StepHeader currentStep={2} totalSteps={3} />)
    const progress = screen.getByRole('progressbar')
    const filled = progress.querySelectorAll('.lv-stepheader__segment--filled')
    expect(filled).toHaveLength(2)
  })

  it('renders an eyebrow label when provided', () => {
    render(<StepHeader currentStep={1} totalSteps={3} eyebrow="Context" />)
    expect(screen.getByText('Context')).toBeInTheDocument()
  })

  it('exposes progress bounds for assistive tech', () => {
    render(<StepHeader currentStep={3} totalSteps={3} />)
    const progress = screen.getByRole('progressbar')
    expect(progress).toHaveAttribute('aria-valuenow', '3')
    expect(progress).toHaveAttribute('aria-valuemax', '3')
  })
})
