const PHONE_DIGITS_RE = /^\d{7,15}$/

export function isValidPhone(rawDigits: string): boolean {
  return PHONE_DIGITS_RE.test(rawDigits)
}

export function formatPhoneDigits(input: string): string {
  return input.replace(/\D/g, '')
}
