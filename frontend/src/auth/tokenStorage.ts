const KEY = 'dealership.token'

/** Thin wrapper over localStorage so the rest of the app never touches it directly. */
export const tokenStorage = {
  get(): string | null {
    try {
      return localStorage.getItem(KEY)
    } catch {
      return null
    }
  },
  set(token: string): void {
    try {
      localStorage.setItem(KEY, token)
    } catch {
      // Storage unavailable (private mode); the session simply won't persist.
    }
  },
  clear(): void {
    try {
      localStorage.removeItem(KEY)
    } catch {
      // ignore
    }
  },
}
