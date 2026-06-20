import { useRef } from 'react'
import './OTPInput.css'

export interface OTPInputProps {
  length?: number
  value: string
  onChange: (value: string) => void
  onComplete?: (value: string) => void
  error?: string
  label?: string
}

export function OTPInput({
  length = 6,
  value,
  onChange,
  onComplete,
  error,
  label,
}: OTPInputProps) {
  const inputsRef = useRef<Array<HTMLInputElement | null>>([])
  const digits = Array.from({ length }, (_, i) => value[i] ?? '')

  const setDigit = (index: number, digit: string) => {
    const next = digits.slice()
    next[index] = digit
    const joined = next.join('').slice(0, length)
    onChange(joined)
    if (joined.length === length) onComplete?.(joined)
  }

  const handleChange = (index: number, raw: string) => {
    const digit = raw.replace(/\D/g, '').slice(-1)
    setDigit(index, digit)
    if (digit && index < length - 1) {
      inputsRef.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputsRef.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length)
    if (!pasted) return
    e.preventDefault()
    onChange(pasted)
    if (pasted.length === length) onComplete?.(pasted)
    const focusIndex = Math.min(pasted.length, length - 1)
    inputsRef.current[focusIndex]?.focus()
  }

  return (
    <div className="lv-otp">
      {label && <span className="lv-otp__label">{label}</span>}
      <div className="lv-otp__boxes" role="group" aria-label={label ?? 'Verification code'}>
        {digits.map((digit, index) => (
          <input
            key={index}
            ref={(el) => {
              inputsRef.current[index] = el
            }}
            className={['lv-otp__box', error ? 'lv-otp__box--error' : '']
              .filter(Boolean)
              .join(' ')}
            inputMode="numeric"
            maxLength={1}
            value={digit}
            aria-label={`Digit ${index + 1}`}
            onChange={(e) => handleChange(index, e.target.value)}
            onKeyDown={(e) => handleKeyDown(index, e)}
            onPaste={handlePaste}
          />
        ))}
      </div>
      {error && <p className="lv-otp__error">{error}</p>}
    </div>
  )
}
