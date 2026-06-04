<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const collapsed = ref(false)

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const map: Record<string, string> = {
    '/': '工作台',
    '/projects': '项目列表',
    '/settings/users': '用户管理',
  }
  return [{ title: '首页', path: '/' }, { title: map[route.path] ?? '页面' }]
})

async function handleLogout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <el-container class="admin-layout">
    <el-aside :width="collapsed ? '64px' : '220px'" class="admin-aside">
      <div class="logo">
        <span v-if="!collapsed" class="logo-text">PM 管理平台</span>
        <span v-else class="logo-icon">PM</span>
      </div>

      <el-menu
        :collapse="collapsed"
        :default-active="activeMenu"
        :collapse-transition="false"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        router
        class="admin-menu"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>

        <el-sub-menu index="settings">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/settings/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container class="admin-main-container">
      <el-header class="admin-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed">
            <Expand v-if="collapsed" />
            <Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="item.path"
              :to="index < breadcrumbs.length - 1 ? item.path : undefined"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click" @command="(cmd: string) => cmd === 'logout' && handleLogout()">
            <span class="user-dropdown">
              <el-avatar :size="32" class="user-avatar">
                {{ authStore.user?.display_name?.charAt(0) ?? 'U' }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.display_name }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.user?.username }} · {{ authStore.user?.role }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="admin-content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.admin-aside {
  background-color: #304156;
  transition: width 0.2s;
  overflow: hidden;
}

.logo {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
  letter-spacing: 0.5px;
}

.logo-icon {
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.admin-menu {
  border-right: none;
}

.admin-menu:not(.el-menu--collapse) {
  width: 220px;
}

.admin-main-container {
  background-color: #f0f2f5;
}

.admin-header {
  height: 50px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.collapse-btn:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}

.user-avatar {
  background-color: #409eff;
  color: #fff;
  font-size: 14px;
}

.user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.admin-content {
  padding: 16px;
  min-height: calc(100vh - 50px);
  box-sizing: border-box;
}
</style>
