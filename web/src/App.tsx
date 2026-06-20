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
      onContinue={(context) => {
        setContext(context)
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
