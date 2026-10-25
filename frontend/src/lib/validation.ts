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