import type { InputHTMLAttributes, ReactNode } from 'react'
import { useId } from 'react'
import './TextInput.css'

export interface TextInputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label?: string
  error?: string
  helperText?: string
  adornment?: ReactNode
}

export function TextInput({
  label,
  error,
  helperText,
  adornment,
  className,
  ...rest
}: TextInputProps) {
  const id = useId()
  const helperId = `${id}-helper`

  return (
    <div className={['lv-textinput', className ?? ''].filter(Boolean).join(' ')}>
      {label && (
        <label className="lv-textinput__label" htmlFor={id}>
          {label}
        </label>
      )}
      <div
        className={[
          'lv-textinput__field',
          error ? 'lv-textinput__field--error' : '',
        ]
          .filter(Boolean)
          .join(' ')}
      >
        {adornment && <span className="lv-textinput__adornment">{adornment}</span>}
        <input
          id={id}
          className="lv-textinput__input"
          aria-invalid={Boolean(error)}
          aria-describedby={error || helperText ? helperId : undefined}
          {...rest}
        />
      </div>
      {(error || helperText) && (
        <p
          id={helperId}
          className={error ? 'lv-textinput__error' : 'lv-textinput__helper'}
        >
          {error || helperText}
        </p>
      )}
    </div>
  )
}
