<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Hardware } from '@/types'
import { useHardwareStore } from '@/stores/hardware'
import { useUsersStore } from '@/stores/users'
import AppHeader from '@/components/layout/AppHeader.vue'
import HardwareTable from '@/components/hardware/HardwareTable.vue'
import HardwareModal from '@/components/hardware/HardwareModal.vue'
import CreateUserModal from '@/components/admin/CreateUserModal.vue'

const hardwareStore = useHardwareStore()
const usersStore = useUsersStore()

onMounted(() => {
  hardwareStore.fetchAll()
  usersStore.fetchAll()
})

// ── Tabs ─────────────────────────────────────────────────────────────────────
type Tab = 'hardware' | 'users'
const activeTab = ref<Tab>('hardware')

// ── Hardware ──────────────────────────────────────────────────────────────────
const showHardwareModal = ref(false)
const deleteTarget = ref<Hardware | null>(null)
const deleteLoading = ref(false)

async function handleAddHardware(payload: Parameters<typeof hardwareStore.create>[0]) {
  const ok = await hardwareStore.create(payload)
  if (ok) showHardwareModal.value = false
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  await hardwareStore.remove(deleteTarget.value.id)
  deleteLoading.value = false
  deleteTarget.value = null
}

async function handleStatusChange(item: Hardware) {
  const newStatus = item.status === 'Repair' ? 'Available' : 'Repair'
  await hardwareStore.setStatus(item.id, newStatus)
}

// ── Users ─────────────────────────────────────────────────────────────────────
const showUserModal = ref(false)
const userDeleteTarget = ref<number | null>(null)
const expandedUserId = ref<number | null>(null)

function toggleUserExpand(userId: number) {
  expandedUserId.value = expandedUserId.value === userId ? null : userId
}

const userHardwareMap = computed(() => {
  const map = new Map<number, Hardware[]>()
  for (const item of hardwareStore.items) {
    if (item.assigned_to) {
      const list = map.get(item.assigned_to) ?? []
      list.push(item)
      map.set(item.assigned_to, list)
    }
  }
  return map
})

function getUserDeviceCount(userId: number): number {
  return userHardwareMap.value.get(userId)?.length ?? 0
}

async function handleCreateUser(payload: Parameters<typeof usersStore.create>[0]) {
  const ok = await usersStore.create(payload)
  if (ok) showUserModal.value = false
}

async function confirmDeleteUser() {
  if (!userDeleteTarget.value) return
  await usersStore.remove(userDeleteTarget.value)
  userDeleteTarget.value = null
}
</script>

<template>
  <div class="min-h-screen bg-[#f8f9fb] flex flex-col">
    <AppHeader />

    <main class="flex-1 mx-auto w-full max-w-7xl px-6 py-8">
      <!-- Page header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-[#1e293b]">Admin Panel</h1>
        <p class="text-sm text-[#94a3b8] mt-1">Manage hardware inventory and user accounts.</p>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 p-1 rounded-xl bg-white border border-[#e5e7eb] w-fit mb-6">
        <button
          v-for="tab in [
            { id: 'hardware', label: 'Hardware', icon: '🖥️' },
            { id: 'users', label: 'Users', icon: '👥' },
          ]"
          :key="tab.id"
          :id="`tab-${tab.id}`"
          :class="[
            'px-4 py-2 rounded-lg text-sm font-semibold transition-all',
            activeTab === tab.id
              ? 'bg-[#f1f5f9] text-[#1e293b]'
              : 'text-[#94a3b8] hover:text-[#64748b]',
          ]"
          @click="activeTab = tab.id as Tab"
        >
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <!-- ── Hardware tab ───────────────────────────────────────────────────── -->
      <div v-if="activeTab === 'hardware'">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-sm font-bold text-[#1e293b]">Inventory Management</h2>
            <p class="text-xs text-[#94a3b8] mt-0.5">{{ hardwareStore.items.length }} items total</p>
          </div>
          <button
            id="add-hardware-btn"
            class="btn btn-primary btn-sm"
            @click="showHardwareModal = true"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Add Hardware
          </button>
        </div>

        <HardwareTable
          :items="hardwareStore.items"
          :users="usersStore.users"
          :loading="hardwareStore.loading"
          :admin-mode="true"
          @delete="(item) => (deleteTarget = item)"
          @status-change="handleStatusChange"
        />

        <!-- Delete confirmation -->
        <Teleport v-if="deleteTarget" to="body">
          <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/40" @click="deleteTarget = null" />
            <Transition name="modal" appear>
              <div class="relative z-10 w-full max-w-sm card p-6 shadow-xl text-center">
                <h2 class="text-lg font-bold text-[#1e293b] mb-2">Delete Hardware</h2>
                <p class="text-sm text-[#64748b] mb-6">
                  Are you sure you want to delete
                  <span class="font-semibold text-[#1e293b]">{{ deleteTarget.name }}</span>?
                  This cannot be undone.
                </p>
                <div class="flex gap-3">
                  <button id="delete-cancel-btn" class="btn btn-secondary flex-1" @click="deleteTarget = null">Cancel</button>
                  <button
                    id="delete-confirm-btn"
                    :disabled="deleteLoading"
                    class="btn btn-danger flex-1"
                    @click="confirmDelete"
                  >
                    {{ deleteLoading ? 'Deleting...' : 'Delete' }}
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </Teleport>
      </div>

      <!-- ── Users tab ─────────────────────────────────────────────────────── -->
      <div v-else>
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-sm font-bold text-[#1e293b]">User Accounts</h2>
            <p class="text-xs text-[#94a3b8] mt-0.5">{{ usersStore.users.length }} accounts</p>
          </div>
          <button
            id="add-user-btn"
            class="btn btn-primary btn-sm"
            @click="showUserModal = true"
          >
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
            Create Account
          </button>
        </div>

        <div class="card overflow-hidden">
          <div v-if="usersStore.loading" class="py-20 text-center text-[#94a3b8] text-sm">
            <div class="flex items-center justify-center gap-2">
              <div class="h-4 w-4 rounded-full border-2 border-[#6366f1] border-t-transparent animate-spin" />
              Loading users...
            </div>
          </div>
          <table v-else class="w-full text-sm">
            <thead>
              <tr class="border-b border-[#f1f5f9]">
                <th class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">User</th>
                <th class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">Role</th>
                <th class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">Devices</th>
                <th class="px-5 py-3 text-left text-xs font-semibold text-[#64748b] uppercase tracking-wider">Created</th>
                <th class="px-5 py-3 text-right text-xs font-semibold text-[#64748b] uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="user in usersStore.users" :key="user.id">
                <tr
                  class="border-b border-[#f1f5f9] last:border-0 hover:bg-[#fafbfc] transition-colors cursor-pointer"
                  @click="toggleUserExpand(user.id)"
                >
                  <td class="px-5 py-4">
                    <div class="flex items-center gap-3">
                      <div class="h-8 w-8 rounded-full bg-[#eef2ff] flex items-center justify-center">
                        <span class="text-xs font-bold text-[#6366f1]">
                          {{ user.username[0]?.toUpperCase() }}
                        </span>
                      </div>
                      <div>
                        <span class="font-medium text-[#1e293b]">{{ user.username }}</span>
                      </div>
                    </div>
                  </td>
                  <td class="px-5 py-4">
                    <span
                      :class="[
                        'px-2.5 py-1 rounded-full text-xs font-semibold',
                        user.is_admin
                          ? 'bg-[#eef2ff] text-[#6366f1]'
                          : 'bg-[#f1f5f9] text-[#64748b]',
                      ]"
                    >
                      {{ user.is_admin ? 'Admin' : 'User' }}
                    </span>
                  </td>
                  <td class="px-5 py-4">
                    <span v-if="getUserDeviceCount(user.id) > 0" class="text-sm font-semibold text-[#1e293b]">
                      {{ getUserDeviceCount(user.id) }}
                      <span class="text-xs font-normal text-[#94a3b8] ml-0.5">rented</span>
                    </span>
                    <span v-else class="text-xs text-[#d1d5db]">None</span>
                  </td>
                  <td class="px-5 py-4 text-[#94a3b8] text-xs">
                    {{ new Date(user.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) }}
                  </td>
                  <td class="px-5 py-4 text-right" @click.stop>
                    <div class="flex items-center justify-end gap-2">
                      <button
                        class="p-2 rounded-lg transition-all"
                        :class="expandedUserId === user.id ? 'text-[#6366f1] bg-[#eef2ff]' : 'text-[#d1d5db] hover:text-[#6366f1] hover:bg-[#eef2ff]'"
                        title="View rented devices"
                        @click="toggleUserExpand(user.id)"
                      >
                        <svg class="h-4 w-4 transition-transform" :style="{ transform: expandedUserId === user.id ? 'rotate(180deg)' : '' }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                        </svg>
                      </button>
                      <button
                        v-if="user.id !== 1"
                        :id="`delete-user-btn-${user.id}`"
                        class="p-2 rounded-lg text-[#d1d5db] hover:text-[#ef4444] hover:bg-[#fef2f2] transition-all"
                        title="Delete user"
                        @click="userDeleteTarget = user.id"
                      >
                        <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                      <span v-if="user.id === 1" class="text-xs text-[#d1d5db]">Protected</span>
                    </div>
                  </td>
                </tr>
                <!-- Expanded: rented devices -->
                <tr v-if="expandedUserId === user.id">
                  <td colspan="5" class="px-5 py-0">
                    <div class="py-4 pl-11">
                      <div v-if="getUserDeviceCount(user.id) === 0" class="text-sm text-[#94a3b8] italic">
                        No devices currently rented.
                      </div>
                      <div v-else class="space-y-2">
                        <p class="text-xs font-semibold text-[#64748b] uppercase tracking-wider mb-2">Rented Devices</p>
                        <div
                          v-for="device in userHardwareMap.get(user.id)"
                          :key="device.id"
                          class="flex items-center gap-4 px-4 py-3 rounded-lg bg-[#f8f9fb] border border-[#e5e7eb]"
                        >
                          <div class="flex-1">
                            <span class="text-sm font-medium text-[#1e293b]">{{ device.name }}</span>
                            <span class="text-xs text-[#94a3b8] ml-2">{{ device.brand }}</span>
                          </div>
                          <span class="flex items-center gap-1.5 text-xs">
                            <span class="h-1.5 w-1.5 rounded-full" :class="{
                              'bg-[#3b82f6]': device.status === 'In Use',
                              'bg-[#22c55e]': device.status === 'Available',
                              'bg-[#f97316]': device.status === 'Repair',
                              'bg-[#94a3b8]': device.status === 'Unknown',
                            }" />
                            <span :class="{
                              'text-[#3b82f6]': device.status === 'In Use',
                              'text-[#22c55e]': device.status === 'Available',
                              'text-[#f97316]': device.status === 'Repair',
                              'text-[#94a3b8]': device.status === 'Unknown',
                            }">{{ device.status }}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>

        <!-- Delete user confirmation -->
        <Teleport v-if="userDeleteTarget" to="body">
          <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/40" @click="userDeleteTarget = null" />
            <Transition name="modal" appear>
              <div class="relative z-10 w-full max-w-sm card p-6 shadow-xl text-center">
                <h2 class="text-lg font-bold text-[#1e293b] mb-2">Delete User</h2>
                <p class="text-sm text-[#64748b] mb-6">
                  This will permanently remove this account.
                </p>
                <div class="flex gap-3">
                  <button id="delete-user-cancel" class="btn btn-secondary flex-1" @click="userDeleteTarget = null">Cancel</button>
                  <button id="delete-user-confirm" class="btn btn-danger flex-1" @click="confirmDeleteUser">Delete</button>
                </div>
              </div>
            </Transition>
          </div>
        </Teleport>
      </div>
    </main>

    <HardwareModal v-if="showHardwareModal" @submit="handleAddHardware" @close="showHardwareModal = false" />
    <CreateUserModal v-if="showUserModal" @submit="handleCreateUser" @close="showUserModal = false" />
  </div>
</template>
