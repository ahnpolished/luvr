import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { LandingScreen } from './screens/LandingScreen'
import { AuthScreen } from './screens/AuthScreen'
import { InstagramContextScreen } from './screens/InstagramContextScreen'
import { TelegramHandoffScreen } from './screens/TelegramHandoffScreen'
import { OnboardingProvider } from './state/OnboardingProvider'
import { useOnboarding } from './state/onboarding-context'

function LandingRoute() {
  const navigate = useNavigate()
  return <LandingScreen onGetStarted={() => navigate('/auth')} />
}

function AuthRoute() {
  const navigate = useNavigate()
  const { setPhone } = useOnboarding()
  return (
    <AuthScreen
      onVerified={(phone) => {
        setPhone(phone)
        navigate('/context')
      }}
    />
  )
}

function ContextRoute() {
  const navigate = useNavigate()
  const { setContext } = useOnboarding()
  return (
    <InstagramContextScreen
      onContinue={async (context) => {
        setContext(context)
        // TODO: VITE_TEST_SESSION_TOKEN is a placeholder until the real
        // alpha-code/linking auth flow is wired up (AuthScreen is still mocked).
        // This call will 403 against the real backend until then.
        try {
          await fetch(`${import.meta.env.VITE_API_URL}/auth/alpha/onboarding`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${import.meta.env.VITE_TEST_SESSION_TOKEN ?? ''}`,
            },
            body: JSON.stringify({
              instagram_handle: context.handle ?? '',
              self_summary: context.selfSummary ?? '',
            }),
          })
        } catch (err) {
          console.error('Failed to submit onboarding context', err)
        }
        navigate('/telegram')
      }}
    />
  )
}

function TelegramRoute() {
  return <TelegramHandoffScreen />
}

function App() {
  return (
    <BrowserRouter>
      <OnboardingProvider>
        <Routes>
          <Route path="/" element={<LandingRoute />} />
          <Route path="/auth" element={<AuthRoute />} />
          <Route path="/context" element={<ContextRoute />} />
          <Route path="/telegram" element={<TelegramRoute />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </OnboardingProvider>
    </BrowserRouter>
  )
}

export default App
