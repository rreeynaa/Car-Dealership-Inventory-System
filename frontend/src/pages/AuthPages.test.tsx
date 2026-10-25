import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { tokenStorage } from '../auth/tokenStorage'
import { fetchMock, json, mockApi, normalUser, page, renderApp } from '../test/utils'

beforeEach(() => vi.stubGlobal('fetch', fetchMock))
afterEach(() => {
  fetchMock.mockReset()
  vi.unstubAllGlobals()
})

describe('routing & auth', () => {
  it('redirects anonymous visitors to the login page', async () => {
    renderApp('/')
    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
  })

  it('logs in, stores the token and shows the inventory', async () => {
    mockApi({
      'POST /api/auth/login': () => json({ access_token: 'tok', token_type: 'bearer', user: normalUser }),
      'GET /api/vehicles/search': () => json(page([])),
    })
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'user@dealership.com')
    await user.type(screen.getByLabelText('Password'), 'Shopper#12345')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('heading', { name: 'Inventory' })).toBeInTheDocument()
    expect(tokenStorage.get()).toBe('tok')
  })

  it('shows the server error for bad credentials', async () => {
    mockApi({ 'POST /api/auth/login': () => json({ detail: 'Invalid email or password' }, 401) })
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'user@dealership.com')
    await user.type(screen.getByLabelText('Password'), 'wrong')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password')
  })

  it('validates the email before calling the API', async () => {
    const user = userEvent.setup()
    renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), 'nope')
    await user.type(screen.getByLabelText('Password'), 'x')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByText('Enter a valid email address')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('restores a session from a stored token', async () => {
    tokenStorage.set('tok')
    mockApi({
      'GET /api/auth/me': () => json(normalUser),
      'GET /api/vehicles/search': () => json(page([])),
    })
    renderApp('/')

    expect(await screen.findByRole('heading', { name: 'Inventory' })).toBeInTheDocument()
    expect(screen.getByText('user@dealership.com')).toBeInTheDocument()
  })

  it('logs out', async () => {
    tokenStorage.set('tok')
    mockApi({
      'GET /api/auth/me': () => json(normalUser),
      'GET /api/vehicles/search': () => json(page([])),
    })
    const user = userEvent.setup()
    renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Log out' }))

    expect(await screen.findByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
    expect(tokenStorage.get()).toBeNull()
  })
})

describe('registration', () => {
  it('blocks weak passwords and mismatches client-side', async () => {
    const user = userEvent.setup()
    renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'new@x.com')
    await user.type(screen.getByLabelText('Password'), 'short')
    await user.type(screen.getByLabelText('Confirm password'), 'different')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(await screen.findByText(/at least 8 characters/i)).toBeInTheDocument()
    expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('registers, then signs in automatically', async () => {
    mockApi({
      'POST /api/auth/register': () => json(normalUser, 201),
      'POST /api/auth/login': () => json({ access_token: 'tok', token_type: 'bearer', user: normalUser }),
      'GET /api/vehicles/search': () => json(page([])),
    })
    const user = userEvent.setup()
    renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'user@dealership.com')
    await user.type(screen.getByLabelText('Password'), 'Shopper123')
    await user.type(screen.getByLabelText('Confirm password'), 'Shopper123')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(await screen.findByRole('heading', { name: 'Inventory' })).toBeInTheDocument()
    await waitFor(() => expect(tokenStorage.get()).toBe('tok'))
  })

  it('surfaces a duplicate email error', async () => {
    mockApi({ 'POST /api/auth/register': () => json({ detail: 'Email already registered' }, 409) })
    const user = userEvent.setup()
    renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'user@dealership.com')
    await user.type(screen.getByLabelText('Password'), 'Shopper123')
    await user.type(screen.getByLabelText('Confirm password'), 'Shopper123')
    await user.click(screen.getByRole('button', { name: 'Create account' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Email already registered')
  })
})
