<script setup lang="ts">
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import * as projectsApi from '@/api/projects'
import RequirementTreePanel from '@/components/requirements/RequirementTreePanel.vue'
import type { Project } from '@/api/types/project'
import {
  MEMBER_ROLE_LABELS,
  type ProjectMember,
  type ProjectMemberRole,
} from '@/api/types/project_member'
import type { User } from '@/api/types/user'
import * as usersApi from '@/api/users'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = computed(() => Number(route.params.id))
const activeTab = ref(route.query.tab === 'members' ? 'members' : 'requirements')

const projectLoading = ref(false)
const membersLoading = ref(false)
const project = ref<Project | null>(null)
const members = ref<ProjectMember[]>([])

const addVisible = ref(false)
const submitting = ref(false)
const userOptions = ref<User[]>([])
const usersLoading = ref(false)

const addFormRef = ref<FormInstance>()
const addForm = reactive({
  user_id: null as number | null,
  role: 'member' as ProjectMemberRole,
})

const roleOptions = Object.entries(MEMBER_ROLE_LABELS).map(([value, label]) => ({
  value: value as ProjectMemberRole,
  label,
}))

const addRules: FormRules = {
  user_id: [{ required: true, message: '请选择用户', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const isOwner = computed(() => {
  if (!project.value || !authStore.user) return false
  return project.value.owner_id === authStore.user.id
})

const availableUsers = computed(() => {
  const memberUserIds = new Set(members.value.map((m) => m.user_id))
  return userOptions.value.filter((u) => !memberUserIds.has(u.id) && u.status === 'active')
})

function getErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') {
      if (detail === 'User is already a project member') return '该用户已是项目成员'
      if (detail === 'Project owner cannot be removed') return '项目负责人不可移除'
      if (detail === 'Only project owner can add members') return '仅项目负责人可添加成员'
      if (detail === 'Only project owner can remove members') return '仅项目负责人可移除成员'
      return detail
    }
  }
  return fallback
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

async function loadMembers() {
  membersLoading.value = true
  try {
    const result = await projectsApi.fetchProjectMembers(projectId.value)
    members.value = result.items
  } catch {
    ElMessage.error('加载成员列表失败')
  } finally {
    membersLoading.value = false
  }
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const result = await usersApi.fetchUsers({ status: 'active', limit: 100 })
    userOptions.value = result.items
  } catch {
    ElMessage.error('加载用户列表失败')
  } finally {
    usersLoading.value = false
  }
}

function openAddDialog() {
  addForm.user_id = null
  addForm.role = 'member'
  addVisible.value = true
  if (userOptions.value.length === 0) {
    loadUsers()
  }
}

async function handleAddMember() {
  if (!addFormRef.value) return
  const valid = await addFormRef.value.validate().catch(() => false)
  if (!valid || addForm.user_id === null) return

  if (addForm.role === 'owner') {
    try {
      await ElMessageBox.confirm(
        '项目负责人只能有一位。指定新负责人后，当前负责人将自动降为普通成员。是否继续？',
        '转让负责人',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' },
      )
    } catch {
      return
    }
  }

  submitting.value = true
  try {
    await projectsApi.addProjectMember(projectId.value, {
      user_id: addForm.user_id,
      role: addForm.role,
    })
    ElMessage.success(addForm.role === 'owner' ? '负责人已变更' : '成员添加成功')
    addVisible.value = false
    await loadProject()
    await loadMembers()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '添加成员失败'))
  } finally {
    submitting.value = false
  }
}

async function handleRemoveMember(member: ProjectMember) {
  if (member.role === 'owner') {
    ElMessage.warning('项目负责人不可移除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定将「${member.user.display_name}」移出项目吗？`,
      '移除成员',
      { type: 'warning', confirmButtonText: '移除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }

  try {
    await projectsApi.removeProjectMember(projectId.value, member.user_id)
    ElMessage.success('成员已移除')
    await loadMembers()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '移除成员失败'))
  }
}

watch(activeTab, (tab) => {
  router.replace({
    name: 'project-detail',
    params: { id: projectId.value },
    query: tab === 'members' ? { tab: 'members' } : { tab: 'requirements' },
  })
})

watch(
  () => route.query.tab,
  (tab) => {
    activeTab.value = tab === 'members' ? 'members' : 'requirements'
  },
)

onMounted(async () => {
  if (!Number.isFinite(projectId.value) || projectId.value <= 0) {
    router.push({ name: 'projects' })
    return
  }
  await loadProject()
  await loadMembers()
})
</script>

<template>
  <div v-loading="projectLoading" class="page-container">
    <div class="page-header">
      <div class="title-row">
        <el-button link @click="router.push({ name: 'projects' })">← 返回列表</el-button>
        <h2 class="page-title">{{ project?.name ?? '项目详情' }}</h2>
      </div>
    </div>
    <p v-if="project?.description" class="project-desc">{{ project.description }}</p>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="需求管理" name="requirements">
        <RequirementTreePanel :project-id="projectId" />
      </el-tab-pane>
      <el-tab-pane label="成员管理" name="members">
        <div class="tab-toolbar">
          <span class="member-count">共 {{ members.length }} 名成员</span>
          <div class="toolbar-actions">
            <el-button @click="loadMembers">刷新</el-button>
            <el-button v-if="isOwner" type="primary" @click="openAddDialog">添加成员</el-button>
          </div>
        </div>

        <el-table v-loading="membersLoading" :data="members" stripe border>
          <el-table-column label="用户名" min-width="120">
            <template #default="{ row }">
              {{ row.user.username }}
            </template>
          </el-table-column>
          <el-table-column label="显示名称" min-width="120">
            <template #default="{ row }">
              {{ row.user.display_name }}
            </template>
          </el-table-column>
          <el-table-column label="角色" width="110">
            <template #default="{ row }">
              <el-tag :type="row.role === 'owner' ? 'warning' : 'info'" size="small">
                {{ MEMBER_ROLE_LABELS[row.role as ProjectMemberRole] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isOwner" label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.role !== 'owner'"
                type="danger"
                link
                @click="handleRemoveMember(row)"
              >
                移除
              </el-button>
              <span v-else class="muted">—</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!membersLoading && members.length === 0" description="暂无成员" />
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="addVisible" title="添加成员" width="480px" destroy-on-close>
      <el-form ref="addFormRef" :model="addForm" :rules="addRules" label-width="90px">
        <el-form-item label="选择用户" prop="user_id">
          <el-select
            v-model="addForm.user_id"
            filterable
            placeholder="搜索并选择用户"
            :loading="usersLoading"
            style="width: 100%"
          >
            <el-option
              v-for="user in availableUsers"
              :key="user.id"
              :label="`${user.display_name}（${user.username}）`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="addForm.role" style="width: 100%">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
          <p v-if="addForm.role === 'owner'" class="role-hint">
            项目只能有一位负责人，指定后将自动替换当前负责人
          </p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAddMember">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-header {
  flex-wrap: wrap;
  gap: 12px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.project-desc {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
}

.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.member-count {
  color: #909399;
  font-size: 13px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.muted {
  color: #c0c4cc;
}

.role-hint {
  margin: 8px 0 0;
  color: #e6a23c;
  font-size: 12px;
  line-height: 1.5;
}
</style>
