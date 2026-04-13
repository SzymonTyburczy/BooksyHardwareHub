<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Hardware } from '@/types'
import { aiApi } from '@/composables/useApi'
import {
  MOCK_AUDIT_FLAGS,
  MOCK_AUDIT_SUMMARY,
  mockSemanticSearch,
} from '@/composables/useMockData'
import HardwareStatusBadge from '@/components/hardware/HardwareStatusBadge.vue'

const props = defineProps<{ hardware: Hardware[] }>()

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const geminiAvailable = ref(false)

// Check Gemini status on mount
onMounted(async () => {
  if (!USE_MOCK) {
    try {
      const status = await aiApi.status()
      geminiAvailable.value = status.gemini_available
    } catch {
      geminiAvailable.value = false
    }
  }
})

// ── Tabs ─────────────────────────────────────────────────────────────────────
type Tab = 'search' | 'audit'
const activeTab = ref<Tab>('audit')

// ── Audit ─────────────────────────────────────────────────────────────────────
const auditLoading = ref(false)
const auditDone = ref(false)
const auditFlags = ref<{ hardware_id: number; hardware_name: string; issue: string; severity: 'high' | 'medium' | 'low' }[]>([])
const auditSummary = ref('')

async function runAudit() {
  auditLoading.value = true
  auditDone.value = false
  try {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 1200))
      auditFlags.value = MOCK_AUDIT_FLAGS
      auditSummary.value = MOCK_AUDIT_SUMMARY
    } else {
      const data = await aiApi.audit()
      auditFlags.value = data.flags as typeof auditFlags.value
      auditSummary.value = data.summary
    }
    auditDone.value = true
  } catch (err) {
    console.error('Audit failed:', err)
    auditSummary.value = 'Audit failed. Please try again.'
    auditDone.value = true
  } finally {
    auditLoading.value = false
  }
}

// ── Semantic search ────────────────────────────────────────────────────────────
const searchQuery = ref('')
const searchResults = ref<Hardware[]>([])
const searchLoading = ref(false)
const searchDone = ref(false)

async function runSearch() {
  if (!searchQuery.value.trim()) return
  searchLoading.value = true
  searchDone.value = false
  try {
    if (USE_MOCK) {
      await new Promise((r) => setTimeout(r, 800))
      searchResults.value = mockSemanticSearch(searchQuery.value, props.hardware)
    } else {
      searchResults.value = await aiApi.search(searchQuery.value)
    }
    searchDone.value = true
  } catch (err) {
    console.error('Search failed:', err)
    searchResults.value = []
    searchDone.value = true
  } finally {
    searchLoading.value = false
  }
}

const severityConfig = {
  high: { bg: 'bg-[#fef2f2]', border: 'border-[#fecaca]', badge: 'bg-[#fee2e2] text-[#dc2626]' },
  medium: { bg: 'bg-[#fffbeb]', border: 'border-[#fde68a]', badge: 'bg-[#fef3c7] text-[#d97706]' },
  low: { bg: 'bg-[#f8fafc]', border: 'border-[#e2e8f0]', badge: 'bg-[#f1f5f9] text-[#64748b]' },
}
</script>

<template>
  <div class="card overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-4 border-b border-[#f1f5f9] flex items-center gap-3">
      <div class="h-8 w-8 rounded-lg bg-[#eef2ff] flex items-center justify-center">
        <svg class="h-4 w-4 text-[#6366f1]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      <div class="flex-1">
        <h2 class="text-sm font-bold text-[#1e293b]">AI Assistant</h2>
        <p class="text-[11px] text-[#94a3b8] flex items-center gap-1.5">
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="USE_MOCK ? 'bg-[#94a3b8]' : geminiAvailable ? 'bg-[#22c55e]' : 'bg-[#f59e0b]'"
          />
          {{ USE_MOCK ? 'Mock mode' : geminiAvailable ? 'Gemini AI connected' : 'Keyword fallback' }}
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-[#f1f5f9]">
      <button
        v-for="tab in [{ id: 'audit', label: '🔍 Audit' }, { id: 'search', label: '💬 Search' }]"
        :key="tab.id"
        :class="[
          'flex-1 py-2.5 text-xs font-semibold transition-colors',
          activeTab === tab.id
            ? 'text-[#1e293b] border-b-2 border-[#6366f1]'
            : 'text-[#94a3b8] hover:text-[#64748b]',
        ]"
        @click="activeTab = tab.id as Tab"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Audit tab -->
    <div v-if="activeTab === 'audit'" class="p-5 space-y-4">
      <p class="text-xs text-[#94a3b8] leading-relaxed">
        AI scans inventory for data anomalies, safety concerns, and stale records.
      </p>

      <div v-if="auditDone && auditSummary" class="rounded-lg bg-[#eef2ff] border border-[#c7d2fe] p-3">
        <p class="text-xs text-[#4338ca] leading-relaxed">{{ auditSummary }}</p>
      </div>

      <button
        id="run-audit-btn"
        :disabled="auditLoading"
        class="btn btn-secondary btn-sm w-full"
        @click="runAudit"
      >
        <span v-if="auditLoading" class="flex items-center gap-2">
          <div class="h-3 w-3 rounded-full border-2 border-[#6366f1]/30 border-t-[#6366f1] animate-spin" />
          Analyzing...
        </span>
        <span v-else>{{ auditDone ? '🔄 Re-run Audit' : '▶ Run Audit' }}</span>
      </button>

      <div v-if="auditDone" class="space-y-2">
        <p class="text-xs font-semibold text-[#64748b]">{{ auditFlags.length }} issues found</p>
        <div
          v-for="flag in auditFlags"
          :key="flag.hardware_id"
          :class="['rounded-lg border p-3 space-y-1', severityConfig[flag.severity].bg, severityConfig[flag.severity].border]"
        >
          <div class="flex items-center gap-2">
            <span :class="['px-1.5 py-0.5 rounded text-[10px] font-bold uppercase', severityConfig[flag.severity].badge]">
              {{ flag.severity }}
            </span>
            <span class="text-xs font-semibold text-[#1e293b]">{{ flag.hardware_name }}</span>
          </div>
          <p class="text-xs text-[#64748b] leading-relaxed">{{ flag.issue }}</p>
        </div>
      </div>
    </div>

    <!-- Search tab -->
    <div v-else class="p-5 space-y-4">
      <p class="text-xs text-[#94a3b8] leading-relaxed">
        Find equipment using natural language.
      </p>

      <div class="flex gap-2">
        <input
          id="ai-search-input"
          v-model="searchQuery"
          type="text"
          placeholder="e.g. 'test mobile apps'..."
          class="input-base text-xs"
          @keydown.enter="runSearch"
        />
        <button
          id="ai-search-btn"
          :disabled="searchLoading || !searchQuery.trim()"
          class="btn btn-primary btn-sm whitespace-nowrap"
          @click="runSearch"
        >
          Search
        </button>
      </div>

      <div v-if="searchDone" class="space-y-2">
        <p class="text-xs text-[#64748b]">
          {{ searchResults.length }} result{{ searchResults.length !== 1 ? 's' : '' }}
        </p>
        <div v-if="searchResults.length === 0" class="text-xs text-[#94a3b8] text-center py-4">
          No matching hardware found
        </div>
        <div
          v-for="item in searchResults"
          :key="item.id"
          class="flex items-center justify-between rounded-lg border border-[#f1f5f9] bg-[#fafbfc] px-3 py-2.5"
        >
          <div>
            <p class="text-xs font-medium text-[#1e293b]">{{ item.name }}</p>
            <p class="text-[10px] text-[#94a3b8]">{{ item.brand }}</p>
          </div>
          <HardwareStatusBadge :status="item.status" />
        </div>
      </div>

      <div v-if="!searchDone" class="space-y-1.5">
        <p class="text-[10px] text-[#94a3b8] uppercase tracking-wider font-semibold">Try asking:</p>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="example in ['test mobile app', 'wireless audio', 'laptop for coding', 'mouse']"
            :key="example"
            class="px-2.5 py-1 rounded-lg border border-[#e5e7eb] bg-white text-[11px] text-[#64748b] hover:text-[#1e293b] hover:bg-[#f8f9fb] transition-all"
            @click="searchQuery = example; runSearch()"
          >
            {{ example }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
