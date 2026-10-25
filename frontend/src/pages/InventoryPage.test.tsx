import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { tokenStorage } from '../auth/tokenStorage'
import { adminUser, fetchMock, json, mockApi, normalUser, page, renderApp, vehicle } from '../test/utils'

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock)
  tokenStorage.set('tok')
})
afterEach(() => {
  fetchMock.mockReset()
  vi.unstubAllGlobals()
})

const cars = [
  vehicle({ id: 1, make: 'Toyota', model: 'Corolla', quantity: 5 }),
  vehicle({ id: 2, make: 'Chevrolet', model: 'Silverado', category: 'Truck', price: 41200, quantity: 0 }),
]

function signedInAs(role: 'admin' | 'user', extra: Parameters<typeof mockApi>[0] = {}) {
  mockApi({
    'GET /api/auth/me': () => json(role === 'admin' ? adminUser : normalUser),
    'GET /api/vehicles/search': () => json(page(cars)),
    ...extra,
  })
}

describe('InventoryPage (shopper)', () => {
  it('lists vehicles, disables Purchase for sold-out ones and hides admin controls', async () => {
    signedInAs('user')
    renderApp('/')

    const corolla = await screen.findByRole('article', { name: 'Toyota Corolla' })
    expect(within(corolla).getByText('$22,450')).toBeInTheDocument()
    expect(within(corolla).getByRole('button', { name: /purchase/i })).toBeEnabled()
    expect(screen.getByRole('button', { name: /silverado is sold out/i })).toBeDisabled()
    expect(screen.queryByRole('button', { name: /add vehicle/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /^edit/i })).not.toBeInTheDocument()
  })

  it('purchases a vehicle and refreshes the list', async () => {
    const purchase = vi.fn(() => json(vehicle({ quantity: 4 })))
    signedInAs('user', { 'POST /api/vehicles/1/purchase': purchase })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Purchase Toyota Corolla' }))

    expect(await screen.findByText(/purchased 1 × toyota corolla/i)).toBeInTheDocument()
    expect(purchase).toHaveBeenCalledOnce()
  })

  it('shows an error toast when the vehicle just sold out', async () => {
    signedInAs('user', { 'POST /api/vehicles/1/purchase': () => json({ detail: 'Vehicle is out of stock' }, 409) })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Purchase Toyota Corolla' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Vehicle is out of stock')
  })

  it('sends debounced filters to the search endpoint', async () => {
    const search = vi.fn(() => json(page(cars)))
    signedInAs('user', { 'GET /api/vehicles/search': search })
    const user = userEvent.setup()
    renderApp('/')
    await screen.findByRole('article', { name: 'Toyota Corolla' })

    await user.type(screen.getByLabelText('Make'), 'toy')

    await waitFor(() => {
      const urls = (search.mock.calls as unknown as [URL][]).map(([u]) => u.searchParams.get('make'))
      expect(urls).toContain('toy')
    })
  })

  it('shows an empty state', async () => {
    signedInAs('user', { 'GET /api/vehicles/search': () => json(page([])) })
    renderApp('/')
    expect(await screen.findByText('No vehicles found')).toBeInTheDocument()
  })

  it('shows an error with retry when loading fails', async () => {
    signedInAs('user', { 'GET /api/vehicles/search': () => json({ detail: 'boom' }, 500) })
    renderApp('/')
    expect(await screen.findByRole('alert')).toHaveTextContent('boom')
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
  })

  it('paginates', async () => {
    const search = vi.fn((url: URL) =>
      json({ items: cars, total: 30, limit: 12, offset: Number(url.searchParams.get('offset')) }),
    )
    signedInAs('user', { 'GET /api/vehicles/search': search })
    const user = userEvent.setup()
    renderApp('/')

    await screen.findByText('Page 1 of 3')
    await user.click(screen.getByRole('button', { name: 'Next' }))

    expect(await screen.findByText('Page 2 of 3')).toBeInTheDocument()
    const offsets = (search.mock.calls as unknown as [URL][]).map(([u]) => u.searchParams.get('offset'))
    expect(offsets).toContain('12')
  })
})

describe('InventoryPage (admin)', () => {
  it('shows admin controls', async () => {
    signedInAs('admin')
    renderApp('/')

    await screen.findByRole('article', { name: 'Toyota Corolla' })
    expect(screen.getByRole('button', { name: /add vehicle/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Edit Toyota Corolla' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Restock Toyota Corolla' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Delete Toyota Corolla' })).toBeInTheDocument()
  })

  it('validates and creates a vehicle', async () => {
    const create = vi.fn((_u: URL, init: RequestInit) => json(vehicle({ id: 9, ...JSON.parse(init.body as string) }), 201))
    signedInAs('admin', { 'POST /api/vehicles': create })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: /add vehicle/i }))
    const dialog = await screen.findByRole('dialog', { hidden: true })
    await user.click(within(dialog).getByRole('button', { name: 'Add vehicle', hidden: true }))
    expect(within(dialog).getAllByText('Required', { exact: false }).length).toBeGreaterThan(0)
    expect(create).not.toHaveBeenCalled()

    await user.type(within(dialog).getByLabelText('Make'), 'Kia')
    await user.type(within(dialog).getByLabelText('Model'), 'EV6')
    await user.type(within(dialog).getByLabelText('Category'), 'Electric')
    await user.type(within(dialog).getByLabelText('Price (USD)'), '44900')
    await user.clear(within(dialog).getByLabelText('Quantity'))
    await user.type(within(dialog).getByLabelText('Quantity'), '4')
    await user.click(within(dialog).getByRole('button', { name: 'Add vehicle', hidden: true }))

    await waitFor(() => expect(create).toHaveBeenCalledOnce())
    expect(JSON.parse((create.mock.calls[0] as [URL, RequestInit])[1].body as string)).toEqual({
      make: 'Kia',
      model: 'EV6',
      category: 'Electric',
      price: 44900,
      quantity: 4,
    })
    expect(await screen.findByText('Vehicle added')).toBeInTheDocument()
  })

  it('restocks a vehicle', async () => {
    const restock = vi.fn(() => json(vehicle({ quantity: 15 })))
    signedInAs('admin', { 'POST /api/vehicles/1/restock': restock })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Restock Toyota Corolla' }))
    const dialog = await screen.findByRole('dialog', { hidden: true })
    await user.clear(within(dialog).getByLabelText('Units to add'))
    await user.type(within(dialog).getByLabelText('Units to add'), '10')
    await user.click(within(dialog).getByRole('button', { name: 'Add stock', hidden: true }))

    expect(await screen.findByText('Added 10 to stock')).toBeInTheDocument()
    expect(restock).toHaveBeenCalledOnce()
  })

  it('asks for confirmation before deleting', async () => {
    const del = vi.fn(() => new Response(null, { status: 204 }))
    signedInAs('admin', { 'DELETE /api/vehicles/1': del })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Delete Toyota Corolla' }))
    expect(del).not.toHaveBeenCalled()
    const dialog = await screen.findByRole('dialog', { hidden: true })
    await user.click(within(dialog).getByRole('button', { name: 'Delete', hidden: true }))

    expect(await screen.findByText('Vehicle deleted')).toBeInTheDocument()
    expect(del).toHaveBeenCalledOnce()
  })
})
