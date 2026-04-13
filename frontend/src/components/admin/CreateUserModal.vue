<script setup lang="ts">
import { ref, reactive } from 'vue'

const emit = defineEmits<{
  submit: [payload: { username: string; password: string; is_admin: boolean }]
  close: []
}>()

const loading = ref(false)
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  is_admin: false,
})

const errors = reactive<Record<string, string>>({})

function validate() {
  errors.username = form.username.trim() ? '' : 'Username is required'
  errors.password = form.password.length >= 6 ? '' : 'Min. 6 characters'
  errors.confirmPassword = form.password === form.confirmPassword ? '' : 'Passwords do not match'
  return !Object.values(errors).some(Boolean)
}

async function submit() {
  if (!validate()) return
  loading.value = true
  try {
    emit('submit', {
      username: form.username.trim().toLowerCase(),
      password: form.password,
      is_admin: form.is_admin,
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
              <h2 class="text-lg font-bold text-[#1e293b]">Create Account</h2>
              <p class="text-sm text-[#94a3b8] mt-0.5">Only admins can create new accounts</p>
            </div>
            <button
              id="user-modal-close"
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
                Username <span class="text-red-500">*</span>
              </label>
              <input
                id="user-username"
                v-model="form.username"
                type="text"
                placeholder="e.g. j.smith"
                autocomplete="off"
                :class="['input-base', errors.username ? 'has-error' : '']"
              />
              <p v-if="errors.username" class="mt-1 text-xs text-red-500">{{ errors.username }}</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">
                Password <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  id="user-password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Min. 6 characters"
                  autocomplete="new-password"
                  :class="['input-base pr-10', errors.password ? 'has-error' : '']"
                />
                <button
                  type="button"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-[#9ca3af] hover:text-[#64748b]"
                  @click="showPassword = !showPassword"
                >
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path v-if="showPassword" stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    <template v-else>
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </template>
                  </svg>
                </button>
              </div>
              <p v-if="errors.password" class="mt-1 text-xs text-red-500">{{ errors.password }}</p>
            </div>

            <div>
              <label class="block text-sm font-semibold text-[#1e293b] mb-1.5">
                Confirm Password <span class="text-red-500">*</span>
              </label>
              <input
                id="user-confirm-password"
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Repeat password"
                autocomplete="new-password"
                :class="['input-base', errors.confirmPassword ? 'has-error' : '']"
              />
              <p v-if="errors.confirmPassword" class="mt-1 text-xs text-red-500">{{ errors.confirmPassword }}</p>
            </div>

            <label class="flex items-center gap-3 cursor-pointer p-3 rounded-xl border border-[#e5e7eb] hover:bg-[#f8f9fb] transition-all">
              <input id="user-is-admin" v-model="form.is_admin" type="checkbox" class="accent-[#6366f1] h-4 w-4" />
              <div>
                <p class="text-sm font-semibold text-[#1e293b]">Administrator</p>
                <p class="text-xs text-[#94a3b8]">Can manage hardware and accounts</p>
              </div>
            </label>

            <div class="flex gap-3 pt-1">
              <button id="user-modal-cancel" type="button" class="btn btn-secondary flex-1" @click="emit('close')">Cancel</button>
              <button id="user-modal-submit" type="submit" :disabled="loading" class="btn btn-primary flex-1">
                <span v-if="loading" class="flex items-center gap-2">
                  <div class="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Creating...
                </span>
                <span v-else>Create Account</span>
              </button>
            </div>
          </form>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
