import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import * as authApi from '@/api/auth'
import type { UserMe } from '@/api/types/auth'

export const TOKEN_STORAGE_KEY = 'access_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))
  const user = ref<UserMe | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_STORAGE_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    }
  }

  function clearAuth() {
    setToken(null)
    user.value = null
  }

  async function login(username: string, password: string) {
    const { access_token } = await authApi.login(username, password)
    setToken(access_token)
    await fetchCurrentUser()
  }

  async function fetchCurrentUser() {
    if (!token.value) {
      user.value = null
      return null
    }

    loading.value = true
    try {
      user.value = await authApi.fetchMe()
      return user.value
    } catch {
      clearAuth()
      return null
    } finally {
      loading.value = false
    }
  }

  async function bootstrap() {
    if (token.value) {
      await fetchCurrentUser()
    }
  }

  function logout() {
    clearAuth()
  }

  return {
    token,
    user,
    loading,
    isAuthenticated,
    login,
    fetchCurrentUser,
    bootstrap,
    logout,
    clearAuth,
    setToken,
  }
})
