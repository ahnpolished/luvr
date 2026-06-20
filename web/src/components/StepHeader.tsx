import logoMono from '../assets/logo-mono.svg'
import './StepHeader.css'

export interface StepHeaderProps {
  currentStep: number
  totalSteps: number
  eyebrow?: string
}

export function StepHeader({ currentStep, totalSteps, eyebrow }: StepHeaderProps) {
  const segments = Array.from({ length: totalSteps }, (_, i) => i < currentStep)

  return (
    <div className="lv-stepheader">
      <div className="lv-stepheader__top">
        <span className="lv-stepheader__wordmark">
          <img className="lv-stepheader__logo" src={logoMono} alt="Luvr" />
          Luvr<span className="lv-stepheader__dot">.</span>
        </span>
        <span className="lv-stepheader__count">
          STEP {currentStep} / {totalSteps}
        </span>
      </div>
      <div className="lv-stepheader__progress" role="progressbar" aria-valuenow={currentStep} aria-valuemin={1} aria-valuemax={totalSteps}>
        {segments.map((filled, i) => (
          <span
            key={i}
            className={[
              'lv-stepheader__segment',
              filled ? 'lv-stepheader__segment--filled' : '',
            ]
              .filter(Boolean)
              .join(' ')}
          />
        ))}
      </div>
      {eyebrow && <span className="lv-stepheader__eyebrow">{eyebrow}</span>}
    </div>
  )
}
