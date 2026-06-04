<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <div class="projects-placeholder">
    <el-card shadow="hover">
      <template #header>
        <span>项目列表</span>
      </template>
      <p>项目列表页（PM-3.10 实现）</p>
      <p v-if="authStore.user">当前用户：{{ authStore.user.display_name }}（{{ authStore.user.username }}）</p>
    </el-card>
  </div>
</template>

<style scoped>
.projects-placeholder {
  max-width: 960px;
  margin: 48px auto;
  padding: 0 16px;
}
</style>
