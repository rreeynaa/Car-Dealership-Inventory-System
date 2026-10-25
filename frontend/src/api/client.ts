import { tokenStorage } from '../auth/tokenStorage'

const BASE_URL = ((import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000')
  .replace(/\/$/, '')

/** An error response from the API (status 0 means the server was unreachable). */
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

type QueryValue = string | number | boolean | null | undefined

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  params?: Record<string, QueryValue>
}

let unauthorizedHandler: (() => void) | null = null

/** Registers what happens when the API rejects a token we sent (expired or invalid). */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler
}

function buildUrl(path: string, params: RequestOptions['params']): string {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined && value !== null && value !== '') query.set(key, String(value))
  }
  const queryString = query.toString()
  return `${BASE_URL}${path}${queryString ? `?${queryString}` : ''}`
}

async function readErrorMessage(response: Response): Promise<string> {
  // slowapi answers 429 with {"error": ...} instead of {"detail": ...}.
  if (response.status === 429) {
    return 'Too many requests. Please wait a moment and try again.'
  }
  try {
    const data = await response.json()
    const detail: unknown = data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail
        .map((item: { msg?: string }) => (item.msg ?? 'Invalid value').replace(/^Value error, /, ''))
        .join('. ')
    }
  } catch {
    // The body was not JSON; fall through to the generic message.
  }
  return `Request failed (${response.status})`
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = tokenStorage.get()
  const headers: Record<string, string> = { Accept: 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  if (options.body !== undefined) headers['Content-Type'] = 'application/json'

  let response: Response
  try {
    response = await fetch(buildUrl(path, options.params), {
      method: options.method ?? 'GET',
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the server. Check your connection and try again.')
  }

  if (!response.ok) {
    // Only a rejected *token* means the session is over; a wrong password is just an error.
    if (response.status === 401 && token) {
      tokenStorage.clear()
      unauthorizedHandler?.()
    }
    throw new ApiError(response.status, await readErrorMessage(response))
  }

  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}