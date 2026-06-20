import { createContext, useContext } from 'react'

export interface OnboardingState {
  phone: string
  context: { handle?: string; selfSummary?: string }
}

export interface OnboardingContextValue extends OnboardingState {
  setPhone: (phone: string) => void
  setContext: (context: OnboardingState['context']) => void
}

export const OnboardingContext = createContext<OnboardingContextValue | null>(null)

export function useOnboarding(): OnboardingContextValue {
  const ctx = useContext(OnboardingContext)
  if (!ctx) {
    throw new Error('useOnboarding must be used within an OnboardingProvider')
  }
  return ctx
}
