import { describe, expect, it } from 'vitest'
import { tokenStorage } from './tokenStorage'

describe('tokenStorage', () => {
  it('returns null when nothing is stored', () => {
    expect(tokenStorage.get()).toBeNull()
  })

  it('stores and returns a token', () => {
    tokenStorage.set('abc')

    expect(tokenStorage.get()).toBe('abc')
  })

  it('clears the token', () => {
    tokenStorage.set('abc')

    tokenStorage.clear()

    expect(tokenStorage.get()).toBeNull()
  })
})