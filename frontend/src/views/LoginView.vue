<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const submitting = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

function resolveRedirectPath() {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.startsWith('/') ? redirect : '/'
}

async function handleSubmit() {
  if (!formRef.value) return

  errorMessage.value = ''
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await authStore.login(form.username, form.password)
    await router.replace(resolveRedirectPath())
  } catch (error) {
    errorMessage.value = getLoginErrorMessage(error)
  } finally {
    submitting.value = false
  }
}

function getLoginErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      if (detail === 'Incorrect username or password') {
        return '用户名或密码错误'
      }
      if (detail === 'Inactive user') {
        return '账号已停用，请联系管理员'
      }
      return detail
    }
    if (error.response?.status === 401) {
      return '用户名或密码错误'
    }
  }
  return '登录失败，请稍后重试'
}

onMounted(async () => {
  if (authStore.loading) {
    await authStore.bootstrap()
  }
  if (authStore.isAuthenticated) {
    await router.replace(resolveRedirectPath())
  }
})
</script>

<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-title">PM 项目管理平台</div>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="handleSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" autocomplete="username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-alert
          v-if="errorMessage"
          class="login-error"
          :title="errorMessage"
          type="error"
          show-icon
          :closable="false"
        />

        <el-button class="login-button" type="primary" :loading="submitting" @click="handleSubmit">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 420px;
}

.login-title {
  font-size: 20px;
  font-weight: 600;
  text-align: center;
}

.login-error {
  margin-bottom: 16px;
}

.login-button {
  width: 100%;
}
</style>
