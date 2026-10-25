import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'
import App from '../App'
import { AuthProvider } from '../auth/AuthContext'
import ToastProvider from '../components/ToastProvider'

export const fetchMock = vi.fn()

export function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

export const adminUser = { id: 1, email: 'admin@dealership.com', role: 'admin', created_at: '2025-01-01T00:00:00Z' }
export const normalUser = { id: 2, email: 'user@dealership.com', role: 'user', created_at: '2025-01-01T00:00:00Z' }

export function vehicle(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    id: 1,
    make: 'Toyota',
    model: 'Corolla',
    category: 'Sedan',
    price: 22450,
    quantity: 5,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    ...overrides,
  }
}

export const page = (items: unknown[], total = items.length) => ({ items, total, limit: 12, offset: 0 })

/** Routes fetch calls by "METHOD /path" prefix to canned responses. */
export function mockApi(routes: Record<string, (url: URL, init: RequestInit) => Response>) {
  fetchMock.mockImplementation(async (input: string, init: RequestInit = {}) => {
    const url = new URL(input)
    const key = `${init.method ?? 'GET'} ${url.pathname}`
    const handler = routes[key]
    if (!handler) throw new Error(`Unmocked request: ${key}`)
    return handler(url, init)
  })
}

export function renderApp(route = '/', ui: ReactElement = <App />) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <ToastProvider>
          <AuthProvider>{ui}</AuthProvider>
        </ToastProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
