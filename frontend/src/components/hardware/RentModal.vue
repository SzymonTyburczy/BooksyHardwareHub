<script setup lang="ts">
import type { Hardware } from '@/types'
import HardwareStatusBadge from './HardwareStatusBadge.vue'

const props = defineProps<{
  item: Hardware
  action: 'rent' | 'return'
  loading?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  close: []
}>()

const cfg = {
  rent: {
    title: 'Confirm Rental',
    description: 'This device will be assigned to you and marked as "In Use".',
    btnLabel: 'Confirm Rent',
    btnClass: 'btn-primary',
  },
  return: {
    title: 'Confirm Return',
    description: 'This device will be marked as "Available" and unassigned.',
    btnLabel: 'Confirm Return',
    btnClass: 'btn-primary',
  },
}[props.action]
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40" @click="emit('close')" />
      <Transition name="modal" appear>
        <div class="relative z-10 w-full max-w-sm card p-6 shadow-xl">
          <h2 class="text-lg font-bold text-[#1e293b] mb-1">{{ cfg.title }}</h2>
          <p class="text-sm text-[#94a3b8] mb-5">{{ cfg.description }}</p>

          <!-- Device info -->
          <div class="rounded-xl bg-[#f8f9fb] border border-[#e5e7eb] p-4 mb-6 space-y-2.5">
            <div class="flex justify-between text-sm">
              <span class="text-[#94a3b8]">Device</span>
              <span class="font-medium text-[#1e293b]">{{ item.name }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-[#94a3b8]">Brand</span>
              <span class="text-[#64748b]">{{ item.brand }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-[#94a3b8]">Status</span>
              <HardwareStatusBadge :status="item.status" />
            </div>
            <div v-if="item.notes" class="pt-2 border-t border-[#e5e7eb]">
              <p class="text-xs text-[#d97706]">⚠ {{ item.notes }}</p>
            </div>
          </div>

          <div class="flex gap-3">
            <button id="rent-modal-cancel" class="btn btn-secondary flex-1" @click="emit('close')">Cancel</button>
            <button
              id="rent-modal-confirm"
              :disabled="loading"
              :class="['btn flex-1', cfg.btnClass]"
              @click="emit('confirm')"
            >
              <span v-if="loading" class="flex items-center gap-2">
                <div class="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                Processing...
              </span>
              <span v-else>{{ cfg.btnLabel }}</span>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
