import { describe, expect, it } from 'vitest'
function validatePassword(password: string): string | null {
  if (password.length < 8) return 'Password must be at least 8 characters'
  if (!/[a-z]/i.test(password) || !/\d/.test(password)) {
    return 'Password must contain a letter and one digit'
  }
  if (new TextEncoder().encode(password).length > 72) {
    return 'Password must not exceed 72 bytes'
  }
  return null
}

describe('validatePassword', () => {
  it('accepts a strong password', () => {
    expect(validatePassword('S3cure!pass')).toBeNull()
  })

  it.each([
    ['Ab1', /at least 8/],
    ['onlyletters', /letter and one digit/],
    ['12345678', /letter and one digit/],
  ])('rejects %s', (password, message) => {
    expect(validatePassword(password)).toMatch(message)
  })

  it('rejects passwords longer than the 72-byte bcrypt limit', () => {
    expect(validatePassword('a1'.repeat(40))).toMatch(/72/)
  })
})