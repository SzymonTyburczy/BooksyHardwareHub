import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Hardware, HardwareStatus, CreateHardwarePayload } from '@/types'
import { hardwareApi } from '@/composables/useApi'
import { MOCK_HARDWARE } from '@/composables/useMockData'
import { useAuthStore } from './auth'
import { useToastStore } from './toast'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const useHardwareStore = defineStore('hardware', () => {
  const items = ref<Hardware[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const statusCounts = computed(() => ({
    Available: items.value.filter((h) => h.status === 'Available').length,
    'In Use': items.value.filter((h) => h.status === 'In Use').length,
    Repair: items.value.filter((h) => h.status === 'Repair').length,
    Unknown: items.value.filter((h) => h.status === 'Unknown').length,
  }))

  const brands = computed(() => {
    const set = new Set(items.value.map((h) => h.brand).filter(Boolean))
    return Array.from(set).sort()
  })

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 400))
        items.value = [...MOCK_HARDWARE]
        return
      }
      items.value = await hardwareApi.getAll()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load hardware'
    } finally {
      loading.value = false
    }
  }

  async function create(payload: CreateHardwarePayload): Promise<boolean> {
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        const newItem: Hardware = {
          id: Math.max(...items.value.map((h) => h.id)) + 1,
          ...payload,
          notes: payload.notes ?? null,
          assigned_to: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }
        items.value.push(newItem)
        useToastStore().add(`"${newItem.name}" added successfully`, 'success')
        return true
      }
      const newItem = await hardwareApi.create(payload)
      items.value.push(newItem)
      useToastStore().add(`"${newItem.name}" added successfully`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to create hardware'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  async function remove(id: number): Promise<boolean> {
    const item = items.value.find((h) => h.id === id)
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        items.value = items.value.filter((h) => h.id !== id)
        useToastStore().add(`"${item?.name}" deleted`, 'success')
        return true
      }
      await hardwareApi.delete(id)
      items.value = items.value.filter((h) => h.id !== id)
      useToastStore().add(`"${item?.name}" deleted`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to delete hardware'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  async function setStatus(id: number, status: HardwareStatus): Promise<boolean> {
    const item = items.value.find((h) => h.id === id)
    if (!item) return false
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        item.status = status
        item.updated_at = new Date().toISOString()
        useToastStore().add(`Status updated to "${status}"`, 'success')
        return true
      }
      const updated = await hardwareApi.setStatus(id, status)
      const idx = items.value.findIndex((h) => h.id === id)
      if (idx !== -1) items.value[idx] = updated
      useToastStore().add(`Status updated to "${status}"`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to update status'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  async function rent(id: number): Promise<boolean> {
    const item = items.value.find((h) => h.id === id)
    if (!item) return false

    // ── Business logic guards ─────────────────────────────────────────────────
    if (item.status === 'Repair') {
      useToastStore().add('Cannot rent equipment that is under repair', 'error')
      return false
    }
    if (item.status === 'In Use') {
      useToastStore().add('This item is already rented by someone', 'error')
      return false
    }
    if (item.status === 'Unknown') {
      useToastStore().add('Cannot rent equipment with unknown status', 'error')
      return false
    }

    const authStore = useAuthStore()
    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        item.status = 'In Use'
        item.assigned_to = authStore.user?.id ?? null
        item.updated_at = new Date().toISOString()
        useToastStore().add(`"${item.name}" rented successfully`, 'success')
        return true
      }
      await hardwareApi.rent(id)
      item.status = 'In Use'
      item.assigned_to = authStore.user?.id ?? null
      useToastStore().add(`"${item.name}" rented successfully`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to rent hardware'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  async function returnHardware(id: number): Promise<boolean> {
    const item = items.value.find((h) => h.id === id)
    if (!item) return false

    // ── Guard: can only return items that are In Use ──────────────────────────
    if (item.status !== 'In Use') {
      useToastStore().add('This item is not currently rented', 'error')
      return false
    }

    try {
      if (USE_MOCK) {
        await new Promise((r) => setTimeout(r, 300))
        item.status = 'Available'
        item.assigned_to = null
        item.updated_at = new Date().toISOString()
        useToastStore().add(`"${item.name}" returned successfully`, 'success')
        return true
      }
      await hardwareApi.return(id)
      item.status = 'Available'
      item.assigned_to = null
      useToastStore().add(`"${item.name}" returned successfully`, 'success')
      return true
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to return hardware'
      useToastStore().add(msg, 'error')
      return false
    }
  }

  return {
    items,
    loading,
    error,
    statusCounts,
    brands,
    fetchAll,
    create,
    remove,
    setStatus,
    rent,
    returnHardware,
  }
})
