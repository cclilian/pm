import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
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

  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }

  app.use(pinia)

  const authStore = useAuthStore()
  await authStore.bootstrap()

  setupRouterGuards(router)
  app.use(router)
  app.use(ElementPlus)
  app.mount('#app')
}

bootstrap()
