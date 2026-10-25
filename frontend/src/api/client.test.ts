import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { tokenStorage } from '../auth/tokenStorage'
import { ApiError, apiRequest, setUnauthorizedHandler } from './client'

const fetchMock = vi.fn()

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function lastRequest(): { url: string; init: RequestInit } {
  const [url, init] = fetchMock.mock.calls[fetchMock.mock.calls.length - 1]
  return { url: url as string, init: init as RequestInit }
}

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  fetchMock.mockReset()
  vi.unstubAllGlobals()
  setUnauthorizedHandler(null)
})

describe('apiRequest', () => {
  it('sends the stored token as a bearer header', async () => {
    tokenStorage.set('abc')
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }))

    await apiRequest('/api/auth/me')

    expect(lastRequest().init.headers).toMatchObject({ Authorization: 'Bearer abc' })
  })

  it('sends no Authorization header when logged out', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }))

    await apiRequest('/api/vehicles')

    expect(lastRequest().init.headers).not.toHaveProperty('Authorization')
  })

  it('serializes JSON bodies', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }))

    await apiRequest('/api/auth/login', { method: 'POST', body: { email: 'a@b.co' } })

    const { init } = lastRequest()
    expect(init.method).toBe('POST')
    expect(init.body).toBe('{"email":"a@b.co"}')
    expect(init.headers).toMatchObject({ 'Content-Type': 'application/json' })
  })

  it('builds query strings and skips empty values', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ items: [] }))

    await apiRequest('/api/vehicles', {
      params: { make: 'toy', model: '', limit: 20, min_price: undefined },
    })

    expect(lastRequest().url).toBe('http://localhost:8000/api/vehicles?make=toy&limit=20')
  })

  it('returns undefined for 204 responses', async () => {
    fetchMock.mockResolvedValue(new Response(null, { status: 204 }))

    await expect(apiRequest('/api/vehicles/1', { method: 'DELETE' })).resolves.toBeUndefined()
  })

  it('throws an ApiError carrying the server detail', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: 'Vehicle is out of stock' }, 409))

    const request = apiRequest('/api/vehicles/1/purchase', { method: 'POST' })

    await expect(request).rejects.toBeInstanceOf(ApiError)
    await expect(request).rejects.toMatchObject({
      status: 409,
      message: 'Vehicle is out of stock',
    })
  })

  it('joins validation messages from 422 responses', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        {
          detail: [
            { msg: 'Value error, Password must contain at least one letter and one digit' },
            { msg: 'Field required' },
          ],
        },
        422,
      ),
    )

    await expect(apiRequest('/api/auth/register', { method: 'POST' })).rejects.toMatchObject({
      status: 422,
      message: 'Password must contain at least one letter and one digit. Field required',
    })
  })

  it('shows a friendly message when rate limited', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ error: 'Rate limit exceeded: 3 per 1 minute' }, 429))

    await expect(apiRequest('/api/auth/login', { method: 'POST' })).rejects.toMatchObject({
      status: 429,
      message: expect.stringMatching(/too many requests/i),
    })
  })

  it('reports a network failure as an ApiError with status 0', async () => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(apiRequest('/api/vehicles')).rejects.toMatchObject({ status: 0 })
  })

  it('clears the token and notifies on 401 when a token was sent', async () => {
    const onUnauthorized = vi.fn()
    setUnauthorizedHandler(onUnauthorized)
    tokenStorage.set('expired')
    fetchMock.mockResolvedValue(jsonResponse({ detail: 'Not authenticated' }, 401))

    await expect(apiRequest('/api/vehicles')).rejects.toMatchObject({ status: 401 })

    expect(tokenStorage.get()).toBeNull()
    expect(onUnauthorized).toHaveBeenCalledOnce()
  })

  it('does not notify on 401 when no token was sent (failed login)', async () => {
    const onUnauthorized = vi.fn()
    setUnauthorizedHandler(onUnauthorized)
    fetchMock.mockResolvedValue(jsonResponse({ detail: 'Invalid email or password' }, 401))

    await expect(apiRequest('/api/auth/login', { method: 'POST' })).rejects.toMatchObject({
      message: 'Invalid email or password',
    })

    expect(onUnauthorized).not.toHaveBeenCalled()
  })
})