import { useState } from 'react'
import { Button, Card, OTPInput, PageShell, StepHeader, TextInput } from '../components'
import { formatPhoneDigits, isValidPhone } from '../lib/validation'
import './AuthScreen.css'

export interface AuthScreenProps {
  onVerified: (phone: string) => void
}

type AuthStage = 'phone' | 'otp'

export function AuthScreen({ onVerified }: AuthScreenProps) {
  const [stage, setStage] = useState<AuthStage>('phone')
  const [phone, setPhone] = useState('')
  const [phoneError, setPhoneError] = useState<string | undefined>()
  const [code, setCode] = useState('')
  const [codeError, setCodeError] = useState<string | undefined>()

  const handleSendCode = () => {
    const digits = formatPhoneDigits(phone)
    if (!isValidPhone(digits)) {
      setPhoneError('Enter a valid phone number.')
      return
    }
    setPhoneError(undefined)
    setStage('otp')
  }

  const handleVerify = (value: string) => {
    if (value.length !== 6) {
      setCodeError('Enter all 6 digits.')
      return
    }
    setCodeError(undefined)
    onVerified(formatPhoneDigits(phone))
  }

  return (
    <PageShell>
      <Card>
        <StepHeader currentStep={1} totalSteps={3} />
        <div className="lv-auth__body">
          {stage === 'phone' ? (
            <>
              <span className="lv-auth__eyebrow">Welcome</span>
              <h2>Let&apos;s get you set up.</h2>
              <p className="lv-auth__lede">
                Enter your number — we&apos;ll text you a code. No passwords, ever.
              </p>

              <TextInput
                label="Phone number"
                placeholder="(555) 012 3456"
                adornment="+1"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                error={phoneError}
                helperText={phoneError ? undefined : 'Standard message rates may apply.'}
              />

              <Button fullWidth onClick={handleSendCode} className="lv-auth__primary-action">
                Send code
              </Button>

              <div className="lv-auth__divider">
                <span className="lv-auth__divider-line" />
                <span className="lv-auth__divider-label">or</span>
                <span className="lv-auth__divider-line" />
              </div>

              <Button variant="secondary" fullWidth disabled title="Coming soon">
                Use email instead
              </Button>

              <p className="lv-auth__fineprint">
                By continuing you agree to the Terms and Privacy Policy.
              </p>
            </>
          ) : (
            <>
              <span className="lv-auth__eyebrow">Verify</span>
              <h2>Enter your code.</h2>
              <p className="lv-auth__lede">
                We sent a 6-digit code to +1 {phone}.
              </p>

              <OTPInput
                label="Verification code"
                value={code}
                onChange={(value) => {
                  setCode(value)
                  setCodeError(undefined)
                }}
                onComplete={handleVerify}
                error={codeError}
              />

              <Button
                fullWidth
                onClick={() => handleVerify(code)}
                className="lv-auth__primary-action"
              >
                Verify
              </Button>

              <Button variant="ghost" onClick={() => setStage('phone')}>
                Use a different number
              </Button>
            </>
          )}
        </div>
      </Card>
    </PageShell>
  )
}
