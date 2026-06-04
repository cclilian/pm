<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const isLoginPage = computed(() => route.path === '/login')
const showUserBar = computed(() => !isLoginPage.value && authStore.isAuthenticated)

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <el-container class="layout">
    <el-header height="56px">
      <div class="header-inner">
        <div class="brand">PM</div>

        <div v-if="showUserBar" class="user-bar">
          <span class="user-name">{{ authStore.user?.display_name }}</span>
          <el-button type="primary" link @click="handleLogout">退出</el-button>
        </div>
      </div>
    </el-header>

    <el-main>
      <RouterView />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.el-header {
  border-bottom: 1px solid #ebeef5;
  background: #fff;
}

.header-inner {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

.user-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  color: #606266;
  font-size: 14px;
}
</style>
