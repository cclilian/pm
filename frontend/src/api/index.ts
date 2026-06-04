import { getActivePinia } from 'pinia'

import api from '@/api/client'
import router from '@/router'
import { TOKEN_STORAGE_KEY, useAuthStore } from '@/stores/auth'

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const requestUrl = error.config?.url ?? ''
    const isLoginRequest = requestUrl.includes('/auth/login')

    if (status === 401 && !isLoginRequest) {
      localStorage.removeItem(TOKEN_STORAGE_KEY)

      const pinia = getActivePinia()
      if (pinia) {
        useAuthStore(pinia).clearAuth()
      }

      const currentPath = router.currentRoute.value.fullPath
      if (currentPath !== '/login') {
        router.push({
          path: '/login',
          query: { redirect: currentPath },
        })
      }
    }

    return Promise.reject(error)
  },
)

export default api

export async function fetchHealth() {
  const { data } = await api.get<{ status: string }>('/health')
  return data
}

export async function fetchDbHealth() {
  const { data } = await api.get<{ status: string; database: string }>('/health/db')
  return data
}
