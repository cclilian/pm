<script setup lang="ts">
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { computed, reactive, ref, watch } from 'vue'

import {
  cancelRequirement,
  createRequirement,
  fetchRequirement,
  isRequirementLeaf,
  REQUIREMENT_PRIORITY_LABELS,
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_TYPE_LABELS,
  updateRequirement,
  type Requirement,
  type RequirementPriority,
  type RequirementStatus,
  type RequirementType,
} from '@/api/requirements'
import type { User } from '@/api/types/user'
import * as usersApi from '@/api/users'

export type DrawerMode = 'view' | 'edit' | 'create'

const props = defineProps<{
  modelValue: boolean
  projectId: number
  mode: DrawerMode
  requirementId?: number | null
  parentId?: number | null
  defaultType: RequirementType
  flatRequirements: Requirement[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  saved: []
  'add-sub': [parentId: number]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const loading = ref(false)
const submitting = ref(false)
const usersLoading = ref(false)
const userOptions = ref<User[]>([])

const requirement = ref<Requirement | null>(null)
const internalMode = ref<DrawerMode>('view')

const formRef = ref<FormInstance>()
const form = reactive({
  title: '',
  description: '',
  type: props.defaultType as RequirementType,
  priority: null as RequirementPriority | null,
  status: 'draft' as RequirementStatus,
  owner_id: null as number | null,
})

const cancelVisible = ref(false)
const cancelFormRef = ref<FormInstance>()
const cancelForm = reactive({ cancel_reason: '' })

const formRules: FormRules = {
  title: [{ required: true, message: '请输入需求标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择需求类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const cancelRules: FormRules = {
  cancel_reason: [{ required: true, message: '请输入取消原因', trigger: 'blur' }],
}

const drawerTitle = computed(() => {
  if (internalMode.value === 'create') {
    return props.parentId ? '添加子需求' : '新建需求'
  }
  if (internalMode.value === 'edit') {
    return '编辑需求'
  }
  return requirement.value?.title ?? '需求详情'
})

const isCancelled = computed(() => requirement.value?.status === 'cancelled')

const isLeaf = computed(() => {
  if (!requirement.value) return false
  if (props.mode === 'create') return false
  return isRequirementLeaf(requirement.value.id, props.flatRequirements)
})

const canDecompose = computed(
  () => internalMode.value === 'view' && isLeaf.value && !isCancelled.value,
)

const statusOptions = (['draft', 'active', 'done'] as RequirementStatus[]).map((value) => ({
  value,
  label: REQUIREMENT_STATUS_LABELS[value],
}))

const priorityOptions = (Object.keys(REQUIREMENT_PRIORITY_LABELS) as RequirementPriority[]).map(
  (value) => ({ value, label: REQUIREMENT_PRIORITY_LABELS[value] }),
)

const typeOptions = (Object.keys(REQUIREMENT_TYPE_LABELS) as RequirementType[]).map((value) => ({
  value,
  label: REQUIREMENT_TYPE_LABELS[value],
}))

function resetFormFromRequirement(item: Requirement) {
  form.title = item.title
  form.description = item.description ?? ''
  form.type = item.type
  form.priority = item.priority
  form.status = item.status === 'cancelled' ? 'draft' : item.status
  form.owner_id = item.owner_id
}

function resetCreateForm() {
  form.title = ''
  form.description = ''
  form.type = props.defaultType
  form.priority = null
  form.status = 'draft'
  form.owner_id = null
}

async function loadUsers() {
  if (userOptions.value.length > 0) return
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

async function loadRequirement() {
  if (!props.requirementId) {
    requirement.value = null
    return
  }
  loading.value = true
  try {
    requirement.value = await fetchRequirement(props.projectId, props.requirementId)
    resetFormFromRequirement(requirement.value)
  } catch {
    ElMessage.error('加载需求详情失败')
    visible.value = false
  } finally {
    loading.value = false
  }
}

async function openDrawerState() {
  internalMode.value = props.mode
  cancelVisible.value = false
  cancelForm.cancel_reason = ''

  if (props.mode === 'create') {
    requirement.value = null
    resetCreateForm()
    if (props.parentId != null) {
      const parent = props.flatRequirements.find((item) => item.id === props.parentId)
      if (parent) {
        form.type = parent.type
      }
    }
    await loadUsers()
    return
  }

  await loadRequirement()
}

function switchToEdit() {
  if (!requirement.value || isCancelled.value) return
  internalMode.value = 'edit'
  loadUsers()
}

function switchToView() {
  internalMode.value = 'view'
  if (requirement.value) {
    resetFormFromRequirement(requirement.value)
  }
}

async function handleSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (internalMode.value === 'create') {
      await createRequirement(props.projectId, {
        title: form.title,
        description: form.description || null,
        type: form.type,
        priority: form.priority,
        status: form.status,
        parent_id: props.parentId ?? null,
        owner_id: form.owner_id,
      })
      ElMessage.success(props.parentId ? '子需求创建成功' : '需求创建成功')
      visible.value = false
      emit('saved')
      return
    }

    if (!requirement.value) return

    const updated = await updateRequirement(props.projectId, requirement.value.id, {
      title: form.title,
      description: form.description || null,
      type: form.type,
      priority: form.priority,
      status: form.status,
      owner_id: form.owner_id,
    })
    requirement.value = updated
    internalMode.value = 'view'
    ElMessage.success('需求已更新')
    emit('saved')
  } catch (error) {
    const message = error instanceof Error ? error.message : '保存失败'
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}

function openCancelDialog() {
  cancelForm.cancel_reason = ''
  cancelVisible.value = true
}

async function handleCancel() {
  if (!cancelFormRef.value || !requirement.value) return
  const valid = await cancelFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    requirement.value = await cancelRequirement(props.projectId, requirement.value.id, {
      cancel_reason: cancelForm.cancel_reason,
    })
    cancelVisible.value = false
    internalMode.value = 'view'
    ElMessage.success('需求已取消')
    emit('saved')
  } catch (error) {
    const message = error instanceof Error ? error.message : '取消失败'
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}

function handleDecomposePlaceholder() {
  ElMessage.info('拆解为任务功能将在 PM-4.13 实现')
}

watch(
  () => [props.modelValue, props.requirementId, props.mode, props.parentId] as const,
  ([open]) => {
    if (open) {
      openDrawerState()
    }
  },
)

defineExpose({
  requirement,
})
</script>

<template>
  <el-drawer v-model="visible" :title="drawerTitle" size="520px" destroy-on-close>
    <div v-loading="loading">
      <template v-if="internalMode === 'view' && requirement">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            {{ REQUIREMENT_TYPE_LABELS[requirement.type] }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="
                requirement.status === 'cancelled'
                  ? 'danger'
                  : requirement.status === 'done'
                    ? 'success'
                    : requirement.status === 'active'
                      ? 'warning'
                      : 'info'
              "
              size="small"
            >
              {{ REQUIREMENT_STATUS_LABELS[requirement.status] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            {{ requirement.priority ? REQUIREMENT_PRIORITY_LABELS[requirement.priority] : '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ requirement.owner?.display_name ?? '—' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ requirement.description || '—' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="requirement.cancelled_at" label="取消时间">
            {{ new Date(requirement.cancelled_at).toLocaleString('zh-CN') }}
          </el-descriptions-item>
          <el-descriptions-item v-if="requirement.cancel_reason" label="取消原因">
            {{ requirement.cancel_reason }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="drawer-actions">
          <el-button v-if="!isCancelled" type="primary" @click="switchToEdit">编辑</el-button>
          <el-button v-if="!isCancelled" @click="emit('add-sub', requirement.id)">
            添加子需求
          </el-button>
          <el-tooltip
            v-if="!canDecompose && !isCancelled && !isLeaf"
            content="存在子需求时不可拆解，请先在末节点上操作"
            placement="top"
          >
            <span>
              <el-button disabled>拆解为任务</el-button>
            </span>
          </el-tooltip>
          <el-button v-if="canDecompose" type="success" @click="handleDecomposePlaceholder">
            拆解为任务
          </el-button>
          <el-button v-if="!isCancelled" type="danger" plain @click="openCancelDialog">
            取消需求
          </el-button>
        </div>
      </template>

      <template v-else-if="internalMode === 'edit' || internalMode === 'create'">
        <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
          <el-form-item label="标题" prop="title">
            <el-input v-model="form.title" maxlength="200" show-word-limit />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-select v-model="form.type" style="width: 100%">
              <el-option
                v-for="opt in typeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" style="width: 100%">
              <el-option
                v-for="opt in statusOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-select v-model="form.priority" clearable placeholder="可选" style="width: 100%">
              <el-option
                v-for="opt in priorityOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="负责人">
            <el-select
              v-model="form.owner_id"
              clearable
              filterable
              placeholder="可选"
              :loading="usersLoading"
              style="width: 100%"
            >
              <el-option
                v-for="user in userOptions"
                :key="user.id"
                :label="`${user.display_name}（${user.username}）`"
                :value="user.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="4" />
          </el-form-item>
        </el-form>

        <div class="drawer-actions">
          <el-button @click="internalMode === 'create' ? (visible = false) : switchToView()">
            取消
          </el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ internalMode === 'create' ? '创建' : '保存' }}
          </el-button>
        </div>
      </template>
    </div>

    <el-dialog v-model="cancelVisible" title="取消需求" width="440px" append-to-body destroy-on-close>
      <el-form ref="cancelFormRef" :model="cancelForm" :rules="cancelRules" label-width="90px">
        <el-form-item label="取消原因" prop="cancel_reason">
          <el-input
            v-model="cancelForm.cancel_reason"
            type="textarea"
            :rows="4"
            placeholder="请说明取消原因"
          />
        </el-form-item>
        <p class="cancel-hint">取消后不会自动取消子需求，子需求状态保持不变。</p>
      </el-form>
      <template #footer>
        <el-button @click="cancelVisible = false">返回</el-button>
        <el-button type="danger" :loading="submitting" @click="handleCancel">确认取消</el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<style scoped>
.drawer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

.cancel-hint {
  margin: 0;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}
</style>
