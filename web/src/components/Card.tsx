import type { HTMLAttributes, ReactNode } from 'react'
import './Card.css'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  wide?: boolean
}

export function Card({ children, wide = false, className, ...rest }: CardProps) {
  const classes = ['lv-card', wide ? 'lv-card--wide' : 'lv-card--narrow', className ?? '']
    .filter(Boolean)
    .join(' ')

  return (
    <div className={classes} {...rest}>
      {children}
    </div>
  )
}
