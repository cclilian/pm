<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import * as projectsApi from '@/api/projects'
import {
  fetchRequirements,
  REQUIREMENT_PRIORITY_LABELS,
  REQUIREMENT_STATUS_LABELS,
  type RequirementPriority,
  type RequirementStatus,
  type RequirementTreeNode,
  type RequirementType,
} from '@/api/requirements'
import type { Project } from '@/api/types/project'

const route = useRoute()
const router = useRouter()

const projectId = computed(() => Number(route.params.id))
const activeType = ref<RequirementType>('core')

const projectLoading = ref(false)
const listLoading = ref(false)
const project = ref<Project | null>(null)
const treeData = ref<RequirementTreeNode[]>([])
const total = ref(0)

const drawerVisible = ref(false)
const selectedRequirement = ref<RequirementTreeNode | null>(null)

const tableRef = ref<{ toggleRowExpansion: (row: RequirementTreeNode, expanded?: boolean) => void }>()

const statusTagType = (status: RequirementStatus) => {
  const map: Record<RequirementStatus, 'info' | 'success' | 'warning' | 'danger'> = {
    draft: 'info',
    active: 'warning',
    done: 'success',
    cancelled: 'danger',
  }
  return map[status]
}

async function loadProject() {
  projectLoading.value = true
  try {
    project.value = await projectsApi.fetchProject(projectId.value)
  } catch {
    ElMessage.error('加载项目信息失败')
    router.push({ name: 'projects' })
  } finally {
    projectLoading.value = false
  }
}

async function loadRequirements() {
  listLoading.value = true
  try {
    const result = await fetchRequirements(projectId.value, {
      tree: true,
      type: activeType.value,
    })
    treeData.value = result.items
    total.value = result.total
  } catch {
    ElMessage.error('加载需求列表失败')
  } finally {
    listLoading.value = false
  }
}

function handleRowClick(row: RequirementTreeNode) {
  selectedRequirement.value = row
  drawerVisible.value = true
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

watch(activeType, () => {
  drawerVisible.value = false
  selectedRequirement.value = null
  loadRequirements()
})

onMounted(async () => {
  if (!Number.isFinite(projectId.value) || projectId.value <= 0) {
    router.push({ name: 'projects' })
    return
  }
  await loadProject()
  await loadRequirements()
})
</script>

<template>
  <div v-loading="projectLoading" class="page-container">
    <div class="page-header">
      <div class="title-block">
        <el-button link @click="router.push({ name: 'project-detail', params: { id: projectId } })">
          ← 返回项目
        </el-button>
        <h2 class="page-title">{{ project?.name ?? '项目' }} · 需求管理</h2>
      </div>
      <div class="toolbar">
        <el-button @click="collapseAll">全部折叠</el-button>
        <el-button @click="expandAll">全部展开</el-button>
        <el-button @click="loadRequirements">刷新</el-button>
      </div>
    </div>

    <el-tabs v-model="activeType" class="type-tabs">
      <el-tab-pane label="核心业务" name="core" />
      <el-tab-pane label="非核心业务" name="non_core" />
    </el-tabs>

    <div class="list-meta">共 {{ total }} 条需求（含子级）</div>

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
      <el-table-column prop="title" label="需求标题" min-width="240" show-overflow-tooltip />
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

    <el-empty v-if="!listLoading && treeData.length === 0" description="该分类下暂无需求" />

    <el-drawer
      v-model="drawerVisible"
      :title="selectedRequirement?.title ?? '需求详情'"
      size="480px"
      destroy-on-close
    >
      <template v-if="selectedRequirement">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">{{ selectedRequirement.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTagType(selectedRequirement.status)" size="small">
              {{ REQUIREMENT_STATUS_LABELS[selectedRequirement.status] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            {{
              selectedRequirement.priority
                ? REQUIREMENT_PRIORITY_LABELS[selectedRequirement.priority]
                : '—'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ selectedRequirement.owner?.display_name ?? '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ selectedRequirement.description || '—' }}
          </el-descriptions-item>
        </el-descriptions>
        <p class="drawer-hint">完整编辑、子需求与拆解功能将在 PM-4.3 实现。</p>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.title-block {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.type-tabs {
  margin-bottom: 8px;
}

.list-meta {
  margin-bottom: 12px;
  color: #909399;
  font-size: 13px;
}

.requirement-table :deep(.el-table__row) {
  cursor: pointer;
}

.drawer-hint {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
}
</style>
