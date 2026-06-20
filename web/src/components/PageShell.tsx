import type { ReactNode } from 'react'
import './PageShell.css'

export interface PageShellProps {
  children: ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <div className="lv-pageshell">
      <div className="lv-pageshell__glow" aria-hidden="true" />
      <div className="lv-pageshell__content">{children}</div>
    </div>
  )
}
