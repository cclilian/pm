<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

import { fetchRequirements, getRequirementPath, type Requirement } from '@/api/requirements'
import {
  createTask,
  fetchTasks,
  TASK_SOURCE_TYPE_LABELS,
  TASK_STATUS_LABELS,
  type TaskSourceType,
  type TaskStatus,
  type TaskTreeNode,
} from '@/api/tasks'

const props = defineProps<{
  projectId: number
}>()

const listLoading = ref(false)
const treeData = ref<TaskTreeNode[]>([])
const total = ref(0)
const requirements = ref<Requirement[]>([])

const tableRef = ref<{ toggleRowExpansion: (row: TaskTreeNode, expanded?: boolean) => void }>()

const createVisible = ref(false)
const createSubmitting = ref(false)
const createParentId = ref<number | null>(null)
const createParentTask = ref<TaskTreeNode | null>(null)
const createFormRef = ref<FormInstance>()
const createForm = reactive({
  title: '',
  description: '',
  source_type: 'internal' as TaskSourceType,
})

const createRules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  source_type: [{ required: true, message: '请选择任务来源', trigger: 'change' }],
}

const createDialogTitle = ref('新建任务')

const sourceTypeOptions = (['internal', 'external', 'adhoc'] as TaskSourceType[]).map((value) => ({
  value,
  label: TASK_SOURCE_TYPE_LABELS[value],
}))

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      if (detail === 'Invalid parent_id: cycle detected') {
        return '父任务无效：存在循环引用'
      }
      if (detail === 'Parent task not found') {
        return '父任务不存在'
      }
      if (detail === 'Requirement not found') {
        return '关联需求不存在'
      }
      if (detail === 'Not allowed to access this project') {
        return '无权访问该项目'
      }
      return detail
    }
  }
  return fallback
}

const statusTagType = (status: TaskStatus) => {
  const map: Record<TaskStatus, 'info' | 'success' | 'warning' | 'danger'> = {
    todo: 'info',
    in_progress: 'warning',
    done: 'success',
    cancelled: 'danger',
  }
  return map[status]
}

async function loadRequirements() {
  try {
    const result = await fetchRequirements(props.projectId)
    requirements.value = result.items
  } catch {
    requirements.value = []
  }
}

async function loadTasks() {
  listLoading.value = true
  try {
    const result = await fetchTasks(props.projectId, { tree: true })
    treeData.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载任务列表失败'))
    treeData.value = []
    total.value = 0
  } finally {
    listLoading.value = false
  }
}

async function reload() {
  await Promise.all([loadTasks(), loadRequirements()])
}

function expandAll() {
  const expand = (nodes: TaskTreeNode[]) => {
    for (const node of nodes) {
      tableRef.value?.toggleRowExpansion(node, true)
      if (node.children?.length) {
        expand(node.children)
      }
    }
  }
  expand(treeData.value)
}

function collapseAll() {
  const collapse = (nodes: TaskTreeNode[]) => {
    for (const node of nodes) {
      tableRef.value?.toggleRowExpansion(node, false)
      if (node.children?.length) {
        collapse(node.children)
      }
    }
  }
  collapse(treeData.value)
}

function openCreateDialog(parent: TaskTreeNode | null = null) {
  createParentId.value = parent?.id ?? null
  createParentTask.value = parent
  createDialogTitle.value = parent == null ? '新建任务' : '添加子任务'
  createForm.title = ''
  createForm.description = ''
  createForm.source_type = parent?.source_type ?? 'internal'
  createVisible.value = true
}

async function handleCreateTask() {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  createSubmitting.value = true
  try {
    await createTask(props.projectId, {
      title: createForm.title,
      description: createForm.description || null,
      requirement_id: createParentTask.value?.requirement_id ?? null,
      parent_id: createParentId.value,
      source_type: createParentTask.value?.source_type ?? createForm.source_type,
    })
    ElMessage.success(createParentId.value == null ? '任务已创建' : '子任务已添加')
    createVisible.value = false
    await loadTasks()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '创建任务失败'))
  } finally {
    createSubmitting.value = false
  }
}

function formatRequirement(requirementId: number | null) {
  if (requirementId == null) return '—'
  return getRequirementPath(requirementId, requirements.value)
}

onMounted(reload)

defineExpose({ reload })
</script>

<template>
  <div class="task-panel">
    <div class="tab-toolbar">
      <span class="list-meta">共 {{ total }} 条任务（含子级）</span>
      <div class="toolbar-actions">
        <el-button type="primary" @click="openCreateDialog()">新建任务</el-button>
        <el-button @click="collapseAll">全部折叠</el-button>
        <el-button @click="expandAll">全部展开</el-button>
        <el-button @click="reload">刷新</el-button>
      </div>
    </div>

    <el-table
      ref="tableRef"
      v-loading="listLoading"
      :data="treeData"
      row-key="id"
      stripe
      border
      :tree-props="{ children: 'children' }"
      class="task-table"
      empty-text="暂无任务"
    >
      <el-table-column prop="title" label="任务标题" min-width="220" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status as TaskStatus)" size="small">
            {{ TASK_STATUS_LABELS[row.status as TaskStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="100">
        <template #default="{ row }">
          {{ TASK_SOURCE_TYPE_LABELS[row.source_type as TaskSourceType] }}
        </template>
      </el-table-column>
      <el-table-column label="关联需求" min-width="240" show-overflow-tooltip>
        <template #default="{ row }">
          {{ formatRequirement(row.requirement_id) }}
        </template>
      </el-table-column>
      <el-table-column label="执行人" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.assignee?.display_name ?? '—' }}
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '—' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="88" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            size="small"
            :disabled="row.status === 'cancelled'"
            @click.stop="openCreateDialog(row)"
          >
            子任务
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!listLoading && treeData.length === 0" description="暂无任务">
      <el-button type="primary" @click="openCreateDialog()">新建任务</el-button>
    </el-empty>

    <el-dialog
      v-model="createVisible"
      :title="createDialogTitle"
      width="480px"
      append-to-body
      destroy-on-close
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item v-if="createParentId == null" label="来源" prop="source_type">
          <el-select v-model="createForm.source_type" style="width: 100%">
            <el-option
              v-for="opt in sourceTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" :loading="createSubmitting" @click="handleCreateTask">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 12px;
  flex-wrap: wrap;
}

.list-meta {
  color: #909399;
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.task-table {
  width: 100%;
}
</style>
