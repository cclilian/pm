<script setup lang="ts">
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { nextTick, onMounted, ref } from 'vue'

import {
  fetchRequirements,
  REQUIREMENT_PRIORITY_LABELS,
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_TYPE_LABELS,
  type Requirement,
  type RequirementPriority,
  type RequirementStatus,
  type RequirementTreeNode,
  type RequirementType,
} from '@/api/requirements'
import RequirementDetailDrawer from '@/components/requirements/RequirementDetailDrawer.vue'
import type { DrawerMode } from '@/components/requirements/RequirementDetailDrawer.vue'

const props = defineProps<{
  projectId: number
}>()

const listLoading = ref(false)
const treeData = ref<RequirementTreeNode[]>([])
const allFlatRequirements = ref<Requirement[]>([])
const total = ref(0)

const drawerVisible = ref(false)
const drawerMode = ref<DrawerMode>('view')
const selectedRequirementId = ref<number | null>(null)
const createParentId = ref<number | null>(null)

const tableRef = ref<{ toggleRowExpansion: (row: RequirementTreeNode, expanded?: boolean) => void }>()

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      return detail
    }
  }
  return fallback
}

const statusTagType = (status: RequirementStatus) => {
  const map: Record<RequirementStatus, 'info' | 'success' | 'warning' | 'danger'> = {
    draft: 'info',
    active: 'warning',
    done: 'success',
    cancelled: 'danger',
  }
  return map[status]
}

async function loadAllRequirements() {
  try {
    const result = await fetchRequirements(props.projectId)
    allFlatRequirements.value = result.items
  } catch {
    allFlatRequirements.value = []
  }
}

async function loadRequirements() {
  listLoading.value = true
  try {
    const [treeResult] = await Promise.all([
      fetchRequirements(props.projectId, { tree: true }),
      loadAllRequirements(),
    ])
    treeData.value = treeResult.items
    total.value = treeResult.total
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载需求列表失败'))
  } finally {
    listLoading.value = false
  }
}

function openViewDrawer(requirementId: number) {
  drawerMode.value = 'view'
  selectedRequirementId.value = requirementId
  createParentId.value = null
  drawerVisible.value = true
}

function openCreateDrawer(parentId: number | null = null) {
  drawerMode.value = 'create'
  selectedRequirementId.value = null
  createParentId.value = parentId
  drawerVisible.value = true
}

function handleRowClick(row: RequirementTreeNode) {
  openViewDrawer(row.id)
}

function handleAddSubRequirement(parentId: number) {
  drawerVisible.value = false
  nextTick(() => openCreateDrawer(parentId))
}

function expandAll() {
  const expand = (nodes: RequirementTreeNode[]) => {
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
  const collapse = (nodes: RequirementTreeNode[]) => {
    for (const node of nodes) {
      tableRef.value?.toggleRowExpansion(node, false)
      if (node.children?.length) {
        collapse(node.children)
      }
    }
  }
  collapse(treeData.value)
}

onMounted(loadRequirements)

defineExpose({ reload: loadRequirements })
</script>

<template>
  <div class="requirement-panel">
    <div class="tab-toolbar">
      <span class="list-meta">共 {{ total }} 条需求（含子级）</span>
      <div class="toolbar-actions">
        <el-button type="primary" @click="openCreateDrawer()">新建需求</el-button>
        <el-button @click="collapseAll">全部折叠</el-button>
        <el-button @click="expandAll">全部展开</el-button>
        <el-button @click="loadRequirements">刷新</el-button>
      </div>
    </div>

    <el-table
      ref="tableRef"
      v-loading="listLoading"
      :data="treeData"
      row-key="id"
      stripe
      border
      highlight-current-row
      :tree-props="{ children: 'children' }"
      class="requirement-table"
      @row-click="handleRowClick"
    >
      <el-table-column prop="title" label="需求标题" min-width="220" show-overflow-tooltip />
      <el-table-column label="类型" width="110">
        <template #default="{ row }">
          <el-tag :type="row.type === 'core' ? 'primary' : 'info'" size="small">
            {{ REQUIREMENT_TYPE_LABELS[row.type as RequirementType] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="优先级" width="90">
        <template #default="{ row }">
          {{
            row.priority
              ? REQUIREMENT_PRIORITY_LABELS[row.priority as RequirementPriority]
              : '—'
          }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status as RequirementStatus)" size="small">
            {{ REQUIREMENT_STATUS_LABELS[row.status as RequirementStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="负责人" min-width="120">
        <template #default="{ row }">
          {{ row.owner?.display_name ?? '—' }}
        </template>
      </el-table-column>
      <el-table-column label="描述" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '—' }}
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!listLoading && treeData.length === 0" description="暂无需求">
      <el-button type="primary" @click="openCreateDrawer()">新建需求</el-button>
    </el-empty>

    <RequirementDetailDrawer
      v-model="drawerVisible"
      :project-id="projectId"
      :mode="drawerMode"
      :requirement-id="selectedRequirementId"
      :parent-id="createParentId"
      default-type="core"
      :flat-requirements="allFlatRequirements"
      @saved="loadRequirements"
      @add-sub="handleAddSubRequirement"
    />
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

.requirement-table :deep(.el-table__row) {
  cursor: pointer;
}
</style>
