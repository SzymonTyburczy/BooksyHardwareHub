<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Hardware, HardwareStatus } from '@/types'
import { useHardwareStore } from '@/stores/hardware'
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/layout/AppHeader.vue'
import HardwareTable from '@/components/hardware/HardwareTable.vue'
import RentModal from '@/components/hardware/RentModal.vue'
import AiAssistant from '@/components/ai/AiAssistant.vue'

const hardwareStore = useHardwareStore()
const authStore = useAuthStore()

const rentTarget = ref<Hardware | null>(null)
const rentAction = ref<'rent' | 'return'>('rent')
const rentLoading = ref(false)

onMounted(() => hardwareStore.fetchAll())

function openRent(item: Hardware) {
  rentTarget.value = item
  rentAction.value = 'rent'
}

function openReturn(item: Hardware) {
  rentTarget.value = item
  rentAction.value = 'return'
}

async function confirmRentAction() {
  if (!rentTarget.value) return
  rentLoading.value = true
  const ok =
    rentAction.value === 'rent'
      ? await hardwareStore.rent(rentTarget.value.id)
      : await hardwareStore.returnHardware(rentTarget.value.id)
  rentLoading.value = false
  if (ok) rentTarget.value = null
}

const statusCards: { status: HardwareStatus; label: string; color: string; bg: string }[] = [
  { status: 'Available', label: 'Available', color: '#16a34a', bg: '#f0fdf4' },
  { status: 'In Use', label: 'In Use', color: '#2563eb', bg: '#eff6ff' },
  { status: 'Repair', label: 'Repair', color: '#d97706', bg: '#fffbeb' },
  { status: 'Unknown', label: 'Unknown', color: '#6b7280', bg: '#f9fafb' },
]
</script>

<template>
  <div class="min-h-screen bg-[#f8f9fb] flex flex-col">
    <AppHeader />

    <main class="flex-1 mx-auto w-full max-w-7xl px-6 py-8">
      <!-- Page header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-[#1e293b]">Equipment Dashboard</h1>
        <p class="text-sm text-[#94a3b8] mt-1">
          Browse and rent company hardware. Welcome, <span class="font-medium text-[#64748b]">{{ authStore.user?.username }}</span>.
        </p>
      </div>

      <!-- Status summary cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        <div
          v-for="card in statusCards"
          :key="card.status"
          class="card p-4 flex items-center gap-4"
        >
          <div
            class="h-10 w-10 rounded-xl flex items-center justify-center text-lg font-bold"
            :style="{ backgroundColor: card.bg, color: card.color }"
          >
            {{ hardwareStore.statusCounts[card.status] }}
          </div>
          <div>
            <div class="text-xs font-semibold text-[#64748b] uppercase tracking-wider">{{ card.label }}</div>
          </div>
        </div>
      </div>

      <!-- Main content grid -->
      <div class="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-6">
        <div class="min-w-0">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-bold text-[#1e293b]">All Equipment</h2>
            <button
              class="text-xs text-[#94a3b8] hover:text-[#1e293b] transition-colors flex items-center gap-1"
              @click="hardwareStore.fetchAll()"
            >
              <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
          <HardwareTable
            :items="hardwareStore.items"
            :loading="hardwareStore.loading"
            @rent="openRent"
            @return="openReturn"
          />
        </div>

        <div class="xl:sticky xl:top-20 xl:self-start">
          <AiAssistant :hardware="hardwareStore.items" />
        </div>
      </div>
    </main>

    <RentModal
      v-if="rentTarget"
      :item="rentTarget"
      :action="rentAction"
      :loading="rentLoading"
      @confirm="confirmRentAction"
      @close="rentTarget = null"
    />
  </div>
</template>
