<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { HardwareStatus } from '@/types'

const emit = defineEmits<{
  submit: [payload: {
    name: string
    brand: string
    purchase_date: string | null
    status: HardwareStatus
    notes: string
  }]
  close: []
}>()

const loading = ref(false)

const form = reactive({
  name: '',
  brand: '',
  purchase_date: '',
  status: 'Available' as HardwareStatus,
  notes: '',
})

const errors = reactive<Record<string, string>>({})

function validate() {
  errors.name = form.name.trim() ? '' : 'Name is required'
  errors.brand = form.brand.trim() ? '' : 'Brand is required'
  return !Object.values(errors).some(Boolean)
}

async function submit() {
  if (!validate()) return
  loading.value = true
  try {
    emit('submit', {
      name: form.name.trim(),
      brand: form.brand.trim(),
      purchase_date: form.purchase_date || null,
      status: form.status,
      notes: form.notes.trim(),
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/40" @click="emit('close')" />
      <Transition name="modal" appear>
        <div class="relative z-10 w-full max-w-md card p-6 shadow-xl">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-lg font-bold text-[#1e293b]">Add Hardware</h2>
              <p class="text-sm text-[#94a3b8] mt-0.5">Add new equipment to inventory</p>
            </div>
            <button
              id="hardware-modal-close"
              class="p-2 rounded-lg text-[#9ca3af] hover:text-[#1e293b] hover:bg-[#f1f5f9] transition-all"
              @click="emit('close')"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">
                Device Name <span class="text-red-500">*</span>
              </label>
              <input
                id="hw-name"
                v-model="form.name"
                type="text"
                placeholder="e.g. MacBook Pro 14"
                :class="['input-base', errors.name ? 'has-error' : '']"
              />
              <p v-if="errors.name" class="mt-1 text-xs text-red-500">{{ errors.name }}</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">
                Brand <span class="text-red-500">*</span>
              </label>
              <input
                id="hw-brand"
                v-model="form.brand"
                type="text"
                placeholder="e.g. Apple"
                :class="['input-base', errors.brand ? 'has-error' : '']"
              />
              <p v-if="errors.brand" class="mt-1 text-xs text-red-500">{{ errors.brand }}</p>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">Purchase Date</label>
                <input id="hw-date" v-model="form.purchase_date" type="date" class="input-base" />
              </div>
              <div>
                <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">Status</label>
                <select id="hw-status" v-model="form.status" class="input-base">
                  <option value="Available">Available</option>
                  <option value="In Use">In Use</option>
                  <option value="Repair">Repair</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">Notes</label>
              <textarea
                id="hw-notes"
                v-model="form.notes"
                rows="2"
                placeholder="Optional notes..."
                class="input-base resize-none"
              />
            </div>

            <div class="flex gap-3 pt-2">
              <button id="hw-modal-cancel" type="button" class="btn btn-secondary flex-1" @click="emit('close')">
                Cancel
              </button>
              <button id="hw-modal-submit" type="submit" :disabled="loading" class="btn btn-primary flex-1">
                <span v-if="loading" class="flex items-center gap-2">
                  <div class="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Adding...
                </span>
                <span v-else>Add Hardware</span>
              </button>
            </div>
          </form>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
