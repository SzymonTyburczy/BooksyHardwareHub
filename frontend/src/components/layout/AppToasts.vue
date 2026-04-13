<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import type { Toast } from '@/types'

const toastStore = useToastStore()

const toastConfig: Record<Toast['type'], { bg: string; icon: string }> = {
  success: { bg: 'bg-[#16a34a]', icon: '✓' },
  error: { bg: 'bg-[#dc2626]', icon: '✕' },
  warning: { bg: 'bg-[#d97706]', icon: '⚠' },
  info: { bg: 'bg-[#2563eb]', icon: 'ℹ' },
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 w-80">
      <TransitionGroup name="slide-up">
        <div
          v-for="toast in toastStore.toasts"
          :key="toast.id"
          :class="[
            'flex items-start gap-3 px-4 py-3 rounded-xl text-sm font-medium text-white shadow-lg cursor-pointer',
            toastConfig[toast.type].bg,
          ]"
          @click="toastStore.remove(toast.id)"
        >
          <span class="text-base leading-none mt-0.5 opacity-80">{{ toastConfig[toast.type].icon }}</span>
          <span class="flex-1 leading-snug">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
