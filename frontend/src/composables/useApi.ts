import type {
  Hardware,
  User,
  Rental,
  AuthResponse,
  CreateHardwarePayload,
  CreateUserPayload,
} from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('auth_token')
  return token
    ? { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }
    : { 'Content-Type': 'application/json' }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {}),
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (username: string, password: string) =>
    request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  logout: () =>
    request<void>('/api/auth/logout', { method: 'POST' }),

  me: () => request<User>('/api/auth/me'),
}

// ── Hardware ──────────────────────────────────────────────────────────────────

export const hardwareApi = {
  getAll: (params?: Record<string, string>) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : ''
    return request<Hardware[]>(`/api/hardware${query}`)
  },

  create: (payload: CreateHardwarePayload) =>
    request<Hardware>('/api/hardware', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  delete: (id: number) =>
    request<void>(`/api/hardware/${id}`, { method: 'DELETE' }),

  setStatus: (id: number, status: string) =>
    request<Hardware>(`/api/hardware/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  rent: (id: number) =>
    request<Rental>(`/api/hardware/${id}/rent`, { method: 'POST' }),

  return: (id: number) =>
    request<Rental>(`/api/hardware/${id}/return`, { method: 'POST' }),
}

// ── Users ─────────────────────────────────────────────────────────────────────

export const usersApi = {
  getAll: () => request<User[]>('/api/users'),

  create: (payload: CreateUserPayload) =>
    request<User>('/api/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  delete: (id: number) =>
    request<void>(`/api/users/${id}`, { method: 'DELETE' }),
}

// ── AI ────────────────────────────────────────────────────────────────────────

export const aiApi = {
  search: (query: string) =>
    request<Hardware[]>('/api/ai/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  audit: () => request<{ flags: unknown[]; summary: string }>('/api/ai/audit'),
}
