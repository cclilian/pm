<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

import type { UserRole, UserStatus } from '@/api/types/auth'
import { ROLE_LABELS, STATUS_LABELS, type User } from '@/api/types/user'
import * as usersApi from '@/api/users'

const loading = ref(false)
const users = ref<User[]>([])
const total = ref(0)
const statusFilter = ref<UserStatus | ''>('')

const createVisible = ref(false)
const editVisible = ref(false)
const passwordVisible = ref(false)
const submitting = ref(false)
const editingUser = ref<User | null>(null)

const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const createForm = reactive({
  username: '',
  password: '',
  display_name: '',
  role: 'dev' as UserRole,
})

const editForm = reactive({
  display_name: '',
  role: 'dev' as UserRole,
  status: 'active' as UserStatus,
})

const passwordForm = reactive({
  password: '',
  confirmPassword: '',
})

const roleOptions = Object.entries(ROLE_LABELS).map(([value, label]) => ({ value, label }))
const statusOptions = Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label }))

const createRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const editRules: FormRules = {
  display_name: [{ required: true, message: '请输入显示名称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const passwordRules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== passwordForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN')
}

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      if (detail === 'Username already exists') {
        return '用户名已存在'
      }
      return detail
    }
  }
  return fallback
}

async function loadUsers() {
  loading.value = true
  try {
    const result = await usersApi.fetchUsers({
      status: statusFilter.value || undefined,
      limit: 100,
    })
    users.value = result.items
    total.value = result.total
  } catch {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  createForm.username = ''
  createForm.password = ''
  createForm.display_name = ''
  createForm.role = 'dev'
  createVisible.value = true
}

function openEditDialog(user: User) {
  editingUser.value = user
  editForm.display_name = user.display_name
  editForm.role = user.role
  editForm.status = user.status
  editVisible.value = true
}

function openPasswordDialog(user: User) {
  editingUser.value = user
  passwordForm.password = ''
  passwordForm.confirmPassword = ''
  passwordVisible.value = true
}

async function handleCreate() {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await usersApi.createUser({ ...createForm })
    ElMessage.success('用户创建成功')
    createVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '创建用户失败'))
  } finally {
    submitting.value = false
  }
}

async function handleEdit() {
  if (!editFormRef.value || !editingUser.value) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await usersApi.updateUser(editingUser.value.id, { ...editForm })
    ElMessage.success('用户更新成功')
    editVisible.value = false
    await loadUsers()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '更新用户失败'))
  } finally {
    submitting.value = false
  }
}

async function handlePasswordReset() {
  if (!passwordFormRef.value || !editingUser.value) return
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await usersApi.updateUserPassword(editingUser.value.id, passwordForm.password)
    ElMessage.success('密码已重置')
    passwordVisible.value = false
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '重置密码失败'))
  } finally {
    submitting.value = false
  }
}

onMounted(loadUsers)
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <div class="toolbar">
        <el-select
          v-model="statusFilter"
          placeholder="全部状态"
          clearable
          style="width: 120px"
          @change="loadUsers"
        >
          <el-option
            v-for="opt in statusOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-button @click="loadUsers">刷新</el-button>
        <el-button type="primary" @click="openCreateDialog">新建用户</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="users" stripe border>
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="display_name" label="显示名称" min-width="120" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag size="small">{{ ROLE_LABELS[row.role as UserRole] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ STATUS_LABELS[row.status as UserStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
          <el-button type="primary" link @click="openPasswordDialog(row)">改密</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="total > 0" class="table-footer">共 {{ total }} 条</div>
    <el-empty v-else-if="!loading" description="暂无用户，点击「新建用户」添加" />

    <el-dialog v-model="createVisible" title="新建用户" width="480px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" autocomplete="off" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="createForm.password" type="password" show-password autocomplete="new-password" />
        </el-form-item>
        <el-form-item label="显示名称" prop="display_name">
          <el-input v-model="createForm.display_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="编辑用户" width="480px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="90px">
        <el-form-item label="用户名">
          <el-input :model-value="editingUser?.username" disabled />
        </el-form-item>
        <el-form-item label="显示名称" prop="display_name">
          <el-input v-model="editForm.display_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="passwordVisible" title="重置密码" width="480px" destroy-on-close>
      <p class="password-hint">为用户「{{ editingUser?.display_name }}」设置新密码</p>
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="90px">
        <el-form-item label="新密码" prop="password">
          <el-input v-model="passwordForm.password" type="password" show-password autocomplete="new-password" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password autocomplete="new-password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handlePasswordReset">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-footer {
  margin-top: 12px;
  color: #909399;
  font-size: 13px;
}

.password-hint {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
}
</style>
