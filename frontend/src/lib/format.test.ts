import { describe, expect, it } from 'vitest'
import { formatPrice, stockStatus } from './format'

describe('format', () => {
  it('formats prices as whole dollars', () => expect(formatPrice(22450)).toBe('$22,450'))

  it('describes stock levels', () => {
    expect(stockStatus(0)).toEqual({ label: 'Sold out', tone: 'out' })
    expect(stockStatus(2)).toEqual({ label: 'Only 2 left', tone: 'low' })
    expect(stockStatus(10)).toEqual({ label: '10 in stock', tone: 'in' })
  })
})
