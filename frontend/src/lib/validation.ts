const BCRYPT_MAX_BYTES = 72

/** Mirrors the API's password rules. Returns an error message, or null when valid. */
export function validatePassword(password: string): string | null {
  if (password.length < 8) return 'Password must be at least 8 characters'
  if (new TextEncoder().encode(password).length > BCRYPT_MAX_BYTES) {
    return 'Password must be at most 72 bytes'
  }
  if (!/[A-Za-z]/.test(password) || !/\d/.test(password)) {
    return 'Password must contain at least one letter and one digit'
  }
  return null
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function validateEmail(email: string): string | null {
  return EMAIL_RE.test(email.trim()) ? null : 'Enter a valid email address'
}

export interface VehicleFormValues {
  make: string
  model: string
  category: string
  price: string
  quantity: string
}

export type VehicleFormErrors = Partial<Record<keyof VehicleFormValues, string>>

/** Mirrors the API's vehicle rules (lengths, price > 0 with 2 decimals, quantity 0..1,000,000). */
export function validateVehicleForm(values: VehicleFormValues): VehicleFormErrors {
  const errors: VehicleFormErrors = {}
  const limits = { make: 100, model: 100, category: 50 } as const
  for (const field of ['make', 'model', 'category'] as const) {
    const value = values[field].trim()
    if (!value) errors[field] = 'Required'
    else if (value.length > limits[field]) errors[field] = `At most ${limits[field]} characters`
  }
  const price = Number(values.price)
  if (values.price.trim() === '' || !Number.isFinite(price) || price <= 0) {
    errors.price = 'Enter a price greater than 0'
  } else if (!/^\d+(\.\d{1,2})?$/.test(values.price.trim())) {
    errors.price = 'Use at most 2 decimal places'
  } else if (price >= 100_000_000) {
    errors.price = 'Price is too large'
  }
  const quantity = Number(values.quantity)
  if (values.quantity.trim() === '' || !Number.isInteger(quantity) || quantity < 0) {
    errors.quantity = 'Enter a whole number, 0 or more'
  } else if (quantity > 1_000_000) {
    errors.quantity = 'At most 1,000,000'
  }
  return errors
}
