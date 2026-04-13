<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Hardware, HardwareStatus, User } from '@/types'
import { useAuthStore } from '@/stores/auth'
import HardwareStatusBadge from './HardwareStatusBadge.vue'

const props = defineProps<{
  items: Hardware[]
  users?: User[]
  loading?: boolean
  adminMode?: boolean
}>()

const userMap = computed(() => {
  const map = new Map<number, string>()
  if (props.users) {
    for (const u of props.users) map.set(u.id, u.username)
  }
  return map
})

function getUserName(id: number | null): string | null {
  if (!id) return null
  return userMap.value.get(id) ?? `User #${id}`
}

const emit = defineEmits<{
  edit: [item: Hardware]
  delete: [item: Hardware]
  rent: [item: Hardware]
  return: [item: Hardware]
  statusChange: [item: Hardware]
}>()

const authStore = useAuthStore()

// ── Sorting ───────────────────────────────────────────────────────────────────
type SortField = 'name' | 'brand' | 'purchase_date' | 'status'
const sortField = ref<SortField>('name')
const sortDir = ref<'asc' | 'desc'>('asc')

function toggleSort(field: SortField) {
  if (sortField.value === field) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDir.value = 'asc'
  }
}

// ── Filtering ─────────────────────────────────────────────────────────────────
const filterStatus = ref<HardwareStatus | ''>('')
const filterBrand = ref('')
const filterSearch = ref('')

const filtered = computed(() => {
  let list = [...props.items]

  if (filterSearch.value) {
    const q = filterSearch.value.toLowerCase()
    list = list.filter(
      (h) =>
        h.name.toLowerCase().includes(q) ||
        h.brand.toLowerCase().includes(q) ||
        (h.notes ?? '').toLowerCase().includes(q),
    )
  }

  if (filterStatus.value) {
    list = list.filter((h) => h.status === filterStatus.value)
  }

  if (filterBrand.value) {
    list = list.filter((h) => h.brand === filterBrand.value)
  }

  list.sort((a, b) => {
    const av = (a[sortField.value] ?? '') as string
    const bv = (b[sortField.value] ?? '') as string
    const cmp = av.localeCompare(bv)
    return sortDir.value === 'asc' ? cmp : -cmp
  })

  return list
})

const uniqueBrands = computed(() => {
  const set = new Set(props.items.map((h) => h.brand).filter(Boolean))
  return Array.from(set).sort()
})

function formatDate(date: string | null) {
  if (!date) return '—'
  const d = new Date(date)
  if (isNaN(d.getTime())) return date
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
}

function isFutureDate(date: string | null): boolean {
  if (!date) return false
  return new Date(date) > new Date()
}

function sortIcon(field: SortField) {
  if (sortField.value !== field) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

const canRent = (item: Hardware) => item.status === 'Available'
const canReturn = (item: Hardware) =>
  item.status === 'In Use' &&
  (!item.assigned_to || item.assigned_to === authStore.user?.id || authStore.isAdmin)
</script>

<template>
  <div class="space-y-4">
    <!-- Filters bar -->
    <div class="flex flex-wrap gap-3 items-center">
      <div class="relative flex-1 min-w-52">
        <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#9ca3af]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          id="hardware-search"
          v-model="filterSearch"
          type="text"
          placeholder="Search hardware..."
          class="input-base pl-10"
        />
      </div>

      <select
        id="filter-status"
        v-model="filterStatus"
        class="input-base w-auto min-w-36"
      >
        <option value="">All statuses</option>
        <option value="Available">Available</option>
        <option value="In Use">In Use</option>
        <option value="Repair">Repair</option>
        <option value="Unknown">Unknown</option>
      </select>

      <select
        id="filter-brand"
        v-model="filterBrand"
        class="input-base w-auto min-w-36"
      >
        <option value="">All brands</option>
        <option v-for="brand in uniqueBrands" :key="brand" :value="brand">{{ brand }}</option>
      </select>

      <span class="text-xs text-[#9ca3af] ml-auto whitespace-nowrap">
        {{ filtered.length }} of {{ items.length }} items
      </span>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-[#f1f5f9]">
            <th
              v-for="col in [
                { field: 'name', label: 'Name' },
                { field: 'brand', label: 'Brand' },
                { field: 'purchase_date', label: 'Purchase Date' },
                { field: 'status', label: 'Status' },
              ]"
              :key="col.field"
              class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider cursor-pointer select-none hover:text-[#1e293b] transition-colors"
              @click="toggleSort(col.field as SortField)"
            >
              {{ col.label }}
              <span class="ml-0.5 text-[10px] opacity-40">{{ sortIcon(col.field as SortField) }}</span>
            </th>
            <th v-if="adminMode" class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">Assigned To</th>
            <th class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">Notes</th>
            <th class="px-5 py-3 text-right text-xs font-semibold text-[#64748b] uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- Loading -->
          <tr v-if="loading">
            <td :colspan="adminMode ? 7 : 6" class="py-20 text-center text-[#9ca3af]">
              <div class="flex items-center justify-center gap-2">
                <div class="h-4 w-4 rounded-full border-2 border-[#6366f1] border-t-transparent animate-spin" />
                <span class="text-sm">Loading hardware...</span>
              </div>
            </td>
          </tr>

          <!-- Empty -->
          <tr v-else-if="filtered.length === 0">
            <td :colspan="adminMode ? 7 : 6" class="py-20 text-center">
              <p class="text-sm text-[#9ca3af]">No hardware found</p>
              <p class="text-xs text-[#d1d5db] mt-1">Try changing your filters</p>
            </td>
          </tr>

          <!-- Rows -->
          <template v-else>
            <tr
              v-for="item in filtered"
              :key="item.id"
              class="border-b border-[#f1f5f9] last:border-0 hover:bg-[#fafbfc] transition-colors"
            >
              <td class="px-5 py-4">
                <div class="font-medium text-[#1e293b]">{{ item.name }}</div>
              </td>
              <td class="px-5 py-4 text-[#64748b]">{{ item.brand || '—' }}</td>
              <td class="px-5 py-4">
                <span
                  :class="[
                    'text-sm',
                    isFutureDate(item.purchase_date) ? 'text-[#d97706] font-medium' : 'text-[#64748b]',
                  ]"
                >
                  {{ formatDate(item.purchase_date) }}
                </span>
                <span v-if="isFutureDate(item.purchase_date)" class="ml-1 text-xs text-[#d97706]">⚠</span>
              </td>
              <td class="px-5 py-4">
                <HardwareStatusBadge :status="item.status" />
              </td>
              <td v-if="adminMode" class="px-5 py-4">
                <template v-if="getUserName(item.assigned_to)">
                  <div class="flex items-center gap-2">
                    <div class="h-6 w-6 rounded-full bg-[#eef2ff] flex items-center justify-center flex-shrink-0">
                      <span class="text-[10px] font-bold text-[#6366f1]">
                        {{ getUserName(item.assigned_to)?.[0]?.toUpperCase() ?? '?' }}
                      </span>
                    </div>
                    <span class="text-sm text-[#1e293b] font-medium">{{ getUserName(item.assigned_to) }}</span>
                  </div>
                </template>
                <span v-else class="text-[#d1d5db] text-xs">—</span>
              </td>
              <td class="px-5 py-4 max-w-48">
                <span v-if="item.notes" class="text-xs text-[#94a3b8] truncate block" :title="item.notes">
                  {{ item.notes }}
                </span>
                <span v-else class="text-[#d1d5db]">—</span>
              </td>
              <td class="px-5 py-4">
                <div class="flex items-center justify-end gap-2">
                  <template v-if="!adminMode">
                    <button
                      v-if="canRent(item)"
                      :id="`rent-btn-${item.id}`"
                      class="btn btn-sm btn-primary"
                      @click="emit('rent', item)"
                    >
                      Rent
                    </button>
                    <button
                      v-if="canReturn(item)"
                      :id="`return-btn-${item.id}`"
                      class="btn btn-sm btn-secondary"
                      @click="emit('return', item)"
                    >
                      Return
                    </button>
                    <span v-if="!canRent(item) && !canReturn(item)" class="text-[#d1d5db] text-xs">—</span>
                  </template>

                  <template v-else>
                    <button
                      :id="`toggle-repair-btn-${item.id}`"
                      :class="[
                        'btn btn-sm',
                        item.status === 'Repair'
                          ? 'bg-[#f0fdf4] text-[#16a34a] border border-[#bbf7d0] hover:bg-[#dcfce7]'
                          : 'bg-[#fffbeb] text-[#d97706] border border-[#fde68a] hover:bg-[#fef3c7]',
                      ]"
                      @click="emit('statusChange', item)"
                    >
                      {{ item.status === 'Repair' ? 'Mark Available' : 'Send to Repair' }}
                    </button>
                    <button
                      :id="`delete-btn-${item.id}`"
                      class="p-2 rounded-lg text-[#d1d5db] hover:text-[#ef4444] hover:bg-[#fef2f2] transition-all"
                      title="Delete"
                      @click="emit('delete', item)"
                    >
                      <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </template>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
