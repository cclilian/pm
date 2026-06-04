<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchDbHealth, fetchHealth } from '@/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const apiStatus = ref<'loading' | 'ok' | 'error'>('loading')
const dbStatus = ref<'loading' | 'ok' | 'error'>('loading')
const errorMessage = ref('')

onMounted(async () => {
  try {
    const health = await fetchHealth()
    apiStatus.value = health.status === 'ok' ? 'ok' : 'error'
  } catch {
    apiStatus.value = 'error'
    errorMessage.value = '无法连接后端 API，请确认 backend 已启动。'
  }

  try {
    const db = await fetchDbHealth()
    dbStatus.value = db.status === 'ok' ? 'ok' : 'error'
  } catch {
    dbStatus.value = 'error'
    if (!errorMessage.value) {
      errorMessage.value = '无法连接数据库，请确认 MySQL 已启动且已创建 agile_pm 库。'
    }
  }
})

function statusTag(type: 'loading' | 'ok' | 'error') {
  if (type === 'loading') return { label: '检测中', effect: 'plain' as const }
  if (type === 'ok') return { label: '正常', type: 'success' as const }
  return { label: '异常', type: 'danger' as const }
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">工作台</h2>
      <el-tag type="info">Phase 1</el-tag>
    </div>

    <el-card shadow="never">
      <p class="desc">Vue3 + FastAPI + MySQL 脚手架已就绪。</p>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="后端 API">
          <el-tag v-bind="statusTag(apiStatus)">{{ statusTag(apiStatus).label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="MySQL">
          <el-tag v-bind="statusTag(dbStatus)">{{ statusTag(dbStatus).label }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="登录态">
          <el-tag v-if="authStore.loading" effect="plain">恢复中</el-tag>
          <el-tag v-else-if="authStore.isAuthenticated" type="success">
            {{ authStore.user?.display_name }}（{{ authStore.user?.username }}）
          </el-tag>
          <el-tag v-else type="info">未登录</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-alert
        v-if="errorMessage"
        class="alert"
        :title="errorMessage"
        type="warning"
        show-icon
        :closable="false"
      />
    </el-card>
  </div>
</template>

<style scoped>
.desc {
  margin: 0 0 20px;
  color: #606266;
}

.alert {
  margin-top: 20px;
}
</style>
