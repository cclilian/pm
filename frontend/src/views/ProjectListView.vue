<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import * as projectsApi from '@/api/projects'
import { STATUS_LABELS, type Project, type ProjectStatus } from '@/api/types/project'

const router = useRouter()

const loading = ref(false)
const projects = ref<Project[]>([])
const total = ref(0)
const createVisible = ref(false)
const submitting = ref(false)

const createFormRef = ref<FormInstance>()

const createForm = reactive({
  name: '',
  description: '',
})

const createRules: FormRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN')
}

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return fallback
}

async function loadProjects() {
  loading.value = true
  try {
    const result = await projectsApi.fetchProjects({ limit: 100 })
    projects.value = result.items
    total.value = result.total
  } catch {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  createForm.name = ''
  createForm.description = ''
  createVisible.value = true
}

async function handleCreate() {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await projectsApi.createProject({
      name: createForm.name,
      description: createForm.description || null,
    })
    ElMessage.success('项目创建成功')
    createVisible.value = false
    await loadProjects()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '创建项目失败'))
  } finally {
    submitting.value = false
  }
}

function goToProject(project: Project) {
  router.push({ name: 'project-detail', params: { id: project.id } })
}

onMounted(loadProjects)
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">项目列表</h2>
      <div class="toolbar">
        <el-button @click="loadProjects">刷新</el-button>
        <el-button type="primary" @click="openCreateDialog">新建项目</el-button>
      </div>
    </div>

    <el-table v-if="total > 0 || loading" v-loading="loading" :data="projects" stripe border>
      <el-table-column label="项目名称" min-width="180">
        <template #default="{ row }">
          <el-button type="primary" link @click="goToProject(row)">
            {{ row.name }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="负责人" min-width="120">
        <template #default="{ row }">
          {{ row.owner.display_name }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ STATUS_LABELS[row.status as ProjectStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" min-width="170">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goToProject(row)">进入</el-button>
        <el-button
          type="primary"
          link
          @click="router.push({ name: 'project-requirements', params: { id: row.id } })"
        >
          需求
        </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="total > 0" class="table-footer">共 {{ total }} 个项目</div>

    <el-empty v-else-if="!loading" description="暂无项目">
      <p class="empty-hint">创建第一个项目，开始管理需求与任务</p>
      <el-button type="primary" @click="openCreateDialog">新建项目</el-button>
    </el-empty>

    <el-dialog v-model="createVisible" title="新建项目" width="520px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="createForm.name" maxlength="128" show-word-limit />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            placeholder="可选，简要说明项目背景与目标"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreate">创建</el-button>
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

.empty-hint {
  margin: 0 0 16px;
  color: #909399;
  font-size: 14px;
}
</style>
