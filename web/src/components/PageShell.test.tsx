import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PageShell } from './PageShell'

describe('PageShell', () => {
  it('renders its children', () => {
    render(
      <PageShell>
        <p>Screen content</p>
      </PageShell>,
    )
    expect(screen.getByText('Screen content')).toBeInTheDocument()
  })
})
