import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { User, CreateUserPayload } from '@/types'
import { usersApi } from '@/composables/useApi'
import { MOCK_USERS } from '@/composables/useMockData'
import { useToastStore } from './toast'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        users.value = [...MOCK_USERS]
        return
      }
      users.value = await usersApi.getAll()
    } finally {
      loading.value = false
    }
  }

  async function create(payload: CreateUserPayload): Promise<boolean> {
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 400))
        const newUser: User = {
          id: Math.max(...users.value.map((u) => u.id)) + 1,
          username: payload.username,
          is_admin: payload.is_admin,
          created_at: new Date().toISOString(),
        }
        users.value.push(newUser)
        useToastStore().add(`User "${newUser.username}" created`, 'success')
        return true
      }
      const newUser = await usersApi.create(payload)
      users.value.push(newUser)
      useToastStore().add(`User "${newUser.username}" created`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create user'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  async function remove(id: number): Promise<boolean> {
    const user = users.value.find((u) => u.id === id)
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        users.value = users.value.filter((u) => u.id !== id)
        useToastStore().add(`User "${user?.username}" deleted`, 'success')
        return true
      }
      await usersApi.delete(id)
      users.value = users.value.filter((u) => u.id !== id)
      useToastStore().add(`User "${user?.username}" deleted`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to delete user'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  return { users, loading, fetchAll, create, remove }
})
