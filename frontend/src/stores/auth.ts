import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/types'
import { authApi } from '@/composables/useApi'
import { MOCK_USERS } from '@/composables/useMockData'
import { useToastStore } from './toast'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value || !!token.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  async function login(username: string, password: string): Promise<boolean> {
    loading.value = true
    try {
      if (USE_MOCK) {
        // Mock login: admin/admin123 or any user from MOCK_USERS with password "password123"
        await new Promise((r) => setTimeout(r, 600)) // simulate network
        const found = MOCK_USERS.find((u) => u.username === username)
        const validPassword =
          (username === 'admin' && password === 'admin123') ||
          (username !== 'admin' && password === 'password123')

        if (!found || !validPassword) {
          useToastStore().add('Invalid username or password', 'error')
          return false
        }
        user.value = found
        token.value = 'mock-token-' + found.id
        localStorage.setItem('auth_token', token.value)
        localStorage.setItem('auth_user', JSON.stringify(found))
        return true
      }

      const result = await authApi.login(username, password)
      user.value = result.user
      token.value = result.token
      localStorage.setItem('auth_token', result.token)
      localStorage.setItem('auth_user', JSON.stringify(result.user))
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Login failed'
      useToastStore().add(msg, 'error')
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  function restoreSession() {
    const savedUser = localStorage.getItem('auth_user')
    const savedToken = localStorage.getItem('auth_token')
    if (savedUser && savedToken) {
      try {
        user.value = JSON.parse(savedUser) as User
        token.value = savedToken
      } catch {
        logout()
      }
    }
  }

  return { user, token, loading, isAuthenticated, isAdmin, login, logout, restoreSession }
})
