<script setup lang="ts">
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { computed, ref, watch } from 'vue'

import { decomposeRequirement } from '@/api/tasks'
import type { DecomposePayload, DecomposeTaskInput } from '@/api/types/task'
import DecomposeEditorNode, {
  type DecomposeEditorNodeData,
} from '@/components/requirements/DecomposeEditorNode.vue'

const props = defineProps<{
  modelValue: boolean
  projectId: number
  requirementId: number
  requirementTitle: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const submitting = ref(false)
let nextKey = 1

function createEditorNode(title = ''): DecomposeEditorNodeData {
  nextKey += 1
  return {
    key: `task-${nextKey}`,
    title,
    subtasks: [],
  }
}

const rootNodes = ref<DecomposeEditorNodeData[]>([])

function resetEditor() {
  nextKey = 1
  rootNodes.value = [
    createEditorNode(),
    createEditorNode(),
  ]
}

function addRootNode() {
  rootNodes.value.push(createEditorNode())
}

function removeRootNode(key: string) {
  rootNodes.value = rootNodes.value.filter((node) => node.key !== key)
}

function handleAddSub(parent: DecomposeEditorNodeData) {
  parent.subtasks.push(createEditorNode())
}

function collectPayload(nodes: DecomposeEditorNodeData[]): DecomposeTaskInput[] {
  return nodes
    .filter((node) => node.title.trim())
    .map((node) => ({
      title: node.title.trim(),
      subtasks: collectPayload(node.subtasks),
    }))
}

function validateNodes(nodes: DecomposeEditorNodeData[]): boolean {
  for (const node of nodes) {
    if (!node.title.trim()) {
      return false
    }
    if (!validateNodes(node.subtasks)) {
      return false
    }
  }
  return true
}

function getMaxDepth(nodes: DecomposeEditorNodeData[], depth = 1): number {
  let max = depth
  for (const node of nodes) {
    if (node.subtasks.length > 0) {
      max = Math.max(max, getMaxDepth(node.subtasks, depth + 1))
    }
  }
  return max
}

const DECOMPOSE_ERROR_MESSAGES: Record<string, string> = {
  'Requirement is not a leaf node': '存在子需求时不可拆解，请在末节点上操作',
  'Requirement already cancelled': '需求已取消，无法拆解',
  'Requirement not found': '需求不存在',
  'Not allowed to access this project': '无权访问该项目',
  'Project not found': '项目不存在',
}

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return DECOMPOSE_ERROR_MESSAGES[detail] ?? detail
    }
  }
  return fallback
}

async function handleSubmit() {
  if (rootNodes.value.length === 0) {
    ElMessage.warning('请至少添加一条顶层任务')
    return
  }
  if (!validateNodes(rootNodes.value)) {
    ElMessage.warning('请填写所有任务标题')
    return
  }

  const payload: DecomposePayload = {
    tasks: collectPayload(rootNodes.value),
  }
  if (payload.tasks.length === 0) {
    ElMessage.warning('请至少填写一条有效任务')
    return
  }

  submitting.value = true
  try {
    await decomposeRequirement(props.projectId, props.requirementId, payload)
    ElMessage.success('拆解任务已创建')
    visible.value = false
    emit('success')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '拆解提交失败'))
  } finally {
    submitting.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      resetEditor()
    }
  },
)
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="`拆解为任务：${requirementTitle}`"
    width="640px"
    append-to-body
    destroy-on-close
  >
    <p class="dialog-hint">可添加多层子任务，支持至少 3 层结构。</p>

    <div class="editor-toolbar">
      <el-button type="primary" link @click="addRootNode">添加顶层任务</el-button>
      <span class="depth-hint">当前最大层级：{{ getMaxDepth(rootNodes) }}</span>
    </div>

    <DecomposeEditorNode
      v-for="node in rootNodes"
      :key="node.key"
      :node="node"
      :depth="0"
      :can-remove="rootNodes.length > 1"
      @remove="removeRootNode(node.key)"
      @add-sub="handleAddSub"
    />

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确认拆解</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-hint {
  margin: 0 0 12px;
  color: #909399;
  font-size: 13px;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.depth-hint {
  color: #909399;
  font-size: 12px;
}
</style>
