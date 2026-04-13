<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ username: '', password: '' })
const loading = ref(false)

async function handleLogin() {
  if (!form.username.trim() || !form.password) return
  loading.value = true
  const success = await auth.login(form.username, form.password)
  loading.value = false
  if (success) router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-[#f8f9fb] flex items-center justify-center px-4">
    <div class="w-full max-w-[420px]">
      <div class="card p-8 shadow-sm">
        <!-- Icon -->
        <div class="mb-6">
          <div class="h-10 w-10 rounded-xl bg-[#f0f0f5] flex items-center justify-center">
            <svg class="h-5 w-5 text-[#6366f1]" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
        </div>

        <!-- Heading -->
        <h1 class="text-xl font-bold text-[#1e293b] mb-1">Welcome back</h1>
        <p class="text-sm text-[#64748b] mb-8">Sign in to your account</p>

        <!-- Form -->
        <form class="space-y-5" @submit.prevent="handleLogin">
          <div>
            <label for="login-username" class="block text-sm font-semibold text-[#1e293b] mb-2">
              Username
            </label>
            <input
              id="login-username"
              v-model="form.username"
              type="text"
              placeholder="name@booksy.com"
              autocomplete="username"
              required
              class="input-base"
            />
          </div>

          <div>
            <label for="login-password" class="block text-sm font-semibold text-[#1e293b] mb-2">
              Password
            </label>
            <input
              id="login-password"
              v-model="form.password"
              type="password"
              placeholder="Enter your password"
              autocomplete="current-password"
              required
              class="input-base"
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            :disabled="loading || !form.username || !form.password"
            class="btn btn-primary w-full mt-2"
          >
            <span v-if="loading" class="flex items-center gap-2">
              <div class="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              Signing in...
            </span>
            <span v-else>Login</span>
          </button>
        </form>
      </div>

      <!-- Dev credentials hint -->
      <p class="text-center text-xs text-[#9ca3af] mt-5 font-mono">
        admin / admin123 &nbsp;·&nbsp; j.doe / password123
      </p>
    </div>
  </div>
</template>
