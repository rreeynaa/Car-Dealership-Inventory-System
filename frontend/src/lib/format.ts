const currency = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

export const formatPrice = (value: number): string => currency.format(value)

export function stockStatus(quantity: number): { label: string; tone: 'out' | 'low' | 'in' } {
  if (quantity === 0) return { label: 'Sold out', tone: 'out' }
  if (quantity <= 3) return { label: `Only ${quantity} left`, tone: 'low' }
  return { label: `${quantity} in stock`, tone: 'in' }
}
