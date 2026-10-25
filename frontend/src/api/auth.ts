import { apiRequest } from './client'
import type { TokenResponse, User } from './types'

export const authApi = {
  login: (email: string, password: string) =>
    apiRequest<TokenResponse>('/api/auth/login', { method: 'POST', body: { email, password } }),
  register: (email: string, password: string) =>
    apiRequest<User>('/api/auth/register', { method: 'POST', body: { email, password } }),
  me: () => apiRequest<User>('/api/auth/me'),
}
