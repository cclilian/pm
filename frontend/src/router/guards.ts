import type { Router } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const PROTECTED_PREFIXES = ['/projects', '/settings']

function requiresAuth(path: string) {
  return PROTECTED_PREFIXES.some((prefix) => path === prefix || path.startsWith(`${prefix}/`))
}

export function setupRouterGuards(router: Router) {
  router.beforeEach(async (to) => {
    const authStore = useAuthStore()

    if (authStore.token && !authStore.user && !authStore.loading) {
      await authStore.fetchCurrentUser()
    }

    if (to.path === '/login' && authStore.isAuthenticated) {
      const redirect = typeof to.query.redirect === 'string' ? to.query.redirect : '/projects'
      return redirect.startsWith('/') ? redirect : '/projects'
    }

    if (requiresAuth(to.path) && !authStore.isAuthenticated) {
      return {
        path: '/login',
        query: { redirect: to.fullPath },
      }
    }

    return true
  })
}
