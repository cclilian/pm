import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import '@/api'
import App from '@/App.vue'
import router from '@/router'
import { setupRouterGuards } from '@/router/guards'
import { useAuthStore } from '@/stores/auth'
import './style.css'

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  const authStore = useAuthStore()
  await authStore.bootstrap()

  setupRouterGuards(router)
  app.use(router)
  app.use(ElementPlus)
  app.mount('#app')
}

bootstrap()
