<script setup lang="ts">
import type { HardwareStatus } from '@/types'

const props = defineProps<{ status: HardwareStatus }>()

const config: Record<HardwareStatus, { label: string; dot: string; text: string }> = {
  Available: { label: 'Available', dot: 'bg-[#16a34a]', text: 'text-[#16a34a]' },
  'In Use': { label: 'In Use', dot: 'bg-[#2563eb]', text: 'text-[#2563eb]' },
  Repair: { label: 'Repair', dot: 'bg-[#d97706]', text: 'text-[#d97706]' },
  Unknown: { label: 'Unknown', dot: 'bg-[#9ca3af]', text: 'text-[#9ca3af]' },
}

const c = config[props.status] ?? config.Unknown
</script>

<template>
  <span class="inline-flex items-center gap-1.5 text-sm font-medium" :class="c.text">
    <span :class="['h-2 w-2 rounded-full', c.dot]" />
    {{ c.label }}
  </span>
</template>
