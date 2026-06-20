import { useState, type ReactNode } from 'react'
import { OnboardingContext, type OnboardingState } from './onboarding-context'

export function OnboardingProvider({ children }: { children: ReactNode }) {
  const [phone, setPhone] = useState('')
  const [context, setContext] = useState<OnboardingState['context']>({})

  return (
    <OnboardingContext.Provider value={{ phone, setPhone, context, setContext }}>
      {children}
    </OnboardingContext.Provider>
  )
}
