<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import * as projectsApi from '@/api/projects'
import {
  fetchRequirements,
  REQUIREMENT_PRIORITY_LABELS,
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_TYPE_LABELS,
} from '@/api/requirements'
import type { Project } from '@/api/types/project'
import type {
  RequirementPriority,
  RequirementStatus,
  RequirementTreeNode,
  RequirementType,
} from '@/api/types/requirement'

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

const statusTagType: Record<RequirementStatus, 'info' | 'success' | 'warning' | 'danger'> = {
  draft: 'info',
  active: 'success',
  done: 'success',
  cancelled: 'danger',
}

function formatTime(value: string) {
  return new Date(value).toLocaleString('zh-CN')
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

function openDetail(row: RequirementTreeNode) {
  selectedRequirement.value = row
  drawerVisible.value = true
}

function handleTabChange() {
  loadRequirements()
}

watch(projectId, async (id) => {
  if (!Number.isFinite(id) || id <= 0) {
    router.push({ name: 'projects' })
    return
  }
  await loadProject()
  await loadRequirements()
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
      <div class="title-row">
        <el-button link @click="router.push({ name: 'project-detail', params: { id: projectId } })">
          ← 返回项目
        </el-button>
        <h2 class="page-title">{{ project?.name ?? '项目' }} · 需求管理</h2>
      </div>
    </div>

    <el-tabs v-model="activeType" @tab-change="handleTabChange">
      <el-tab-pane
        :label="REQUIREMENT_TYPE_LABELS.core"
        name="core"
      />
      <el-tab-pane
        :label="REQUIREMENT_TYPE_LABELS.non_core"
        name="non_core"
      />
    </el-tabs>

    <div class="tab-toolbar">
      <span class="list-count">共 {{ total }} 条{{ REQUIREMENT_TYPE_LABELS[activeType] }}需求</span>
      <el-button @click="loadRequirements">刷新</el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="treeData"
      row-key="id"
      default-expand-all
      stripe
      border
      :tree-props="{ children: 'children' }"
      class="requirement-table"
      @row-click="openDetail"
    >
      <el-table-column prop="title" label="需求标题" min-width="240" show-overflow-tooltip />
      <el-table-column label="优先级" width="90">
        <template #default="{ row }">
          <span v-if="row.priority">
            {{ REQUIREMENT_PRIORITY_LABELS[row.priority as RequirementPriority] }}
          </span>
          <span v-else class="muted">—</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType[row.status as RequirementStatus]" size="small">
            {{ REQUIREMENT_STATUS_LABELS[row.status as RequirementStatus] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="负责人" width="120">
        <template #default="{ row }">
          {{ row.owner?.display_name ?? '—' }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="170">
        <template #default="{ row }">
          {{ formatTime(row.updated_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click.stop="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!listLoading && treeData.length === 0" description="暂无需求">
      <p class="empty-hint">可在详情抽屉中创建需求（PM-4.3）</p>
    </el-empty>

    <el-drawer
      v-model="drawerVisible"
      :title="selectedRequirement?.title ?? '需求详情'"
      size="480px"
      destroy-on-close
    >
      <template v-if="selectedRequirement">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            {{ REQUIREMENT_TYPE_LABELS[selectedRequirement.type] }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ REQUIREMENT_STATUS_LABELS[selectedRequirement.status] }}
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
        <p class="drawer-hint">完整编辑、子需求与取消功能将在 PM-4.3 实现。</p>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.list-count {
  color: #909399;
  font-size: 13px;
}

.requirement-table :deep(.el-table__row) {
  cursor: pointer;
}

.muted {
  color: #c0c4cc;
}

.empty-hint {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.drawer-hint {
  margin-top: 16px;
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
}
</style>
