import type { Router } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const PUBLIC_PATHS = new Set(['/login'])

export function setupRouterGuards(router: Router) {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore()

    if (authStore.token && !authStore.user) {
      await authStore.fetchCurrentUser()
    }

    if (to.path === '/login' && authStore.isAuthenticated) {
      const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : '/'
      return redirect.startsWith('/') ? redirect : '/'
    }

    if (!PUBLIC_PATHS.has(to.path) && !authStore.isAuthenticated) {
      return {
        path: '/login',
        query: { redirect: to.fullPath },
      }
    }

    return true
  })
}
