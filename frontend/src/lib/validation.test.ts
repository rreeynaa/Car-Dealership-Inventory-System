import { describe, expect, it } from 'vitest'
import { validateEmail, validatePassword, validateVehicleForm } from './validation'

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

describe('validateEmail', () => {
  it('accepts a normal address', () => expect(validateEmail('a@b.co')).toBeNull())
  it.each(['', 'nope', 'a@b', 'a b@c.com'])('rejects %j', (v) => {
    expect(validateEmail(v)).not.toBeNull()
  })
})

describe('validateVehicleForm', () => {
  const valid = { make: 'Toyota', model: 'Corolla', category: 'Sedan', price: '22450.50', quantity: '3' }

  it('accepts valid input', () => expect(validateVehicleForm(valid)).toEqual({}))

  it('requires text fields', () => {
    const errors = validateVehicleForm({ ...valid, make: ' ', model: '', category: '' })
    expect(Object.keys(errors).sort()).toEqual(['category', 'make', 'model'])
  })

  it.each(['', '0', '-5', 'abc', '10.999'])('rejects price %j', (price) => {
    expect(validateVehicleForm({ ...valid, price }).price).toBeDefined()
  })

  it.each(['', '-1', '1.5', 'x', '1000001'])('rejects quantity %j', (quantity) => {
    expect(validateVehicleForm({ ...valid, quantity }).quantity).toBeDefined()
  })

  it('allows zero quantity', () => {
    expect(validateVehicleForm({ ...valid, quantity: '0' })).toEqual({})
  })
})
