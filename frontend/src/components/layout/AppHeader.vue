<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-white border-b border-gray-200">
    <div class="mx-auto max-w-7xl px-6">
      <div class="flex h-14 items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2.5">
          <div class="h-8 w-8 rounded-lg bg-[#f0f0f5] flex items-center justify-center">
            <svg class="h-4 w-4 text-[#6366f1]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <span class="text-sm font-bold text-[#1e293b]">HardwareHub</span>
        </RouterLink>

        <!-- Nav links -->
        <nav class="flex items-center gap-1">
          <RouterLink
            to="/"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              $route.name === 'dashboard'
                ? 'bg-[#f1f5f9] text-[#1e293b]'
                : 'text-[#64748b] hover:text-[#1e293b] hover:bg-[#f8fafc]',
            ]"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            v-if="auth.isAdmin"
            to="/admin"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
              $route.name === 'admin'
                ? 'bg-[#f1f5f9] text-[#1e293b]'
                : 'text-[#64748b] hover:text-[#1e293b] hover:bg-[#f8fafc]',
            ]"
          >
            Admin
          </RouterLink>
        </nav>

        <!-- User info + logout -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <div class="h-7 w-7 rounded-full bg-[#eef2ff] flex items-center justify-center">
              <span class="text-xs font-semibold text-[#6366f1]">
                {{ auth.user?.username?.[0]?.toUpperCase() ?? '?' }}
              </span>
            </div>
            <div class="hidden sm:block">
              <p class="text-xs font-medium text-[#1e293b] leading-none">{{ auth.user?.username }}</p>
              <p class="text-[10px] text-[#94a3b8] mt-0.5">{{ auth.isAdmin ? 'Admin' : 'User' }}</p>
            </div>
          </div>
          <button
            id="logout-btn"
            class="text-xs font-medium text-[#94a3b8] hover:text-[#ef4444] transition-colors"
            @click="logout"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  </header>
</template>
