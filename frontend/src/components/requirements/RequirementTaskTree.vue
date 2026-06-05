<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { reactive, ref, watch } from 'vue'
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
  requirementId: number
}>()

const loading = ref(false)
const treeData = ref<TaskTreeNode[]>([])
const total = ref(0)

const tableRef = ref<{ toggleRowExpansion: (row: TaskTreeNode, expanded?: boolean) => void }>()

const createVisible = ref(false)
const createSubmitting = ref(false)
const createParentId = ref<number | null>(null)
const createFormRef = ref<FormInstance>()
const createForm = reactive({
  title: '',
  description: '',
})

const createRules: FormRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
}

const createDialogTitle = ref('添加任务')

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
      if (detail === 'Task not found') {
        return '任务不存在'
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

async function loadTasks() {
  loading.value = true
  try {
    const result = await fetchTasks(props.projectId, {
      tree: true,
      requirement_id: props.requirementId,
    })
    treeData.value = result.items
    total.value = result.total
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载关联任务失败'))
    treeData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
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

function openCreateDialog(parentId: number | null) {
  createParentId.value = parentId
  createDialogTitle.value = parentId == null ? '添加顶层任务' : '添加子任务'
  createForm.title = ''
  createForm.description = ''
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
      requirement_id: props.requirementId,
      parent_id: createParentId.value,
      source_type: 'requirement',
    })
    ElMessage.success(createParentId.value == null ? '任务已添加' : '子任务已添加')
    createVisible.value = false
    await loadTasks()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '添加任务失败'))
  } finally {
    createSubmitting.value = false
  }
}

watch(
  () => [props.projectId, props.requirementId] as const,
  () => {
    loadTasks()
  },
  { immediate: true },
)

defineExpose({ reload: loadTasks, expandAll })
</script>

<template>
  <div class="requirement-task-tree">
    <div class="section-header">
      <span class="section-title">关联任务</span>
      <span class="section-meta">共 {{ total }} 条</span>
    </div>

    <div class="toolbar">
      <el-button type="primary" @click="openCreateDialog(null)">添加任务</el-button>
      <el-button @click="collapseAll">全部折叠</el-button>
      <el-button @click="expandAll">全部展开</el-button>
      <el-button @click="loadTasks">刷新</el-button>
    </div>

    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="treeData"
      row-key="id"
      stripe
      border
      :tree-props="{ children: 'children' }"
      class="task-table"
      empty-text="暂无关联任务，可点击「添加任务」"
    >
      <el-table-column prop="title" label="任务标题" min-width="160" show-overflow-tooltip />
      <el-table-column label="状态" width="88">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status as TaskStatus)" size="small">
            {{ TASK_STATUS_LABELS[row.status as TaskStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="88">
        <template #default="{ row }">
          {{ TASK_SOURCE_TYPE_LABELS[row.source_type as TaskSourceType] }}
        </template>
      </el-table-column>
      <el-table-column label="执行人" width="88" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.assignee?.display_name ?? '—' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="88" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            link
            :disabled="row.status === 'cancelled'"
            @click.stop="openCreateDialog(row.id)"
          >
            子任务
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="createVisible"
      :title="createDialogTitle"
      width="420px"
      append-to-body
      destroy-on-close
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="72px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="createForm.title" maxlength="200" show-word-limit />
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
.requirement-task-tree {
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.section-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 12px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.section-meta {
  color: #909399;
  font-size: 13px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.task-table {
  width: 100%;
}
</style>
