import type {
  DecomposePayload,
  Task,
  TaskCancelPayload,
  TaskCreatePayload,
  TaskListParams,
  TaskListResponse,
  TaskTreeListResponse,
  TaskTreeNode,
  TaskUpdatePayload,
} from '@/api/types/task'

const MOCK_DELAY_MS = 120

let nextId = 1000
const store = new Map<number, Task[]>()

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(value), MOCK_DELAY_MS)
  })
}

function nowIso(): string {
  return new Date().toISOString()
}

function cloneTask(item: Task): Task {
  return { ...item }
}

function seedProjectTasks(projectId: number): Task[] {
  const createdAt = '2026-06-02T09:00:00.000Z'
  const assignee = { id: 2, username: 'dev', display_name: '开发工程师' }

  return [
    {
      id: 101,
      project_id: projectId,
      requirement_id: 4,
      parent_id: null,
      title: '实现记住用户名',
      description: '登录成功后持久化用户名',
      source_type: 'requirement',
      source_description: null,
      status: 'in_progress',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 8,
      actual_hours: 2,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 102,
      project_id: projectId,
      requirement_id: 4,
      parent_id: 101,
      title: 'localStorage 读写封装',
      description: '封装 set/get/remove',
      source_type: 'requirement',
      source_description: null,
      status: 'done',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 3,
      actual_hours: 3,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 103,
      project_id: projectId,
      requirement_id: 4,
      parent_id: 102,
      title: '过期与清空策略',
      description: '30 天未登录自动清除',
      source_type: 'requirement',
      source_description: null,
      status: 'todo',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 2,
      actual_hours: null,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 201,
      project_id: projectId,
      requirement_id: 3,
      parent_id: null,
      title: '登录页布局',
      description: '居中卡片 + 品牌区',
      source_type: 'requirement',
      source_description: null,
      status: 'done',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 4,
      actual_hours: 4,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 202,
      project_id: projectId,
      requirement_id: 3,
      parent_id: 201,
      title: '表单组件',
      description: '用户名/密码输入框',
      source_type: 'requirement',
      source_description: null,
      status: 'done',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 6,
      actual_hours: 5,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 203,
      project_id: projectId,
      requirement_id: 3,
      parent_id: 202,
      title: '密码可见切换',
      description: '眼睛图标切换明文/密文',
      source_type: 'requirement',
      source_description: null,
      status: 'in_progress',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 2,
      actual_hours: 1,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 301,
      project_id: projectId,
      requirement_id: null,
      parent_id: null,
      title: '升级 Element Plus 补丁',
      description: '项目内技术债',
      source_type: 'internal',
      source_description: '依赖安全更新',
      status: 'todo',
      assignee_id: assignee.id,
      assignee,
      planned_hours: 1,
      actual_hours: null,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
  ]
}

function getProjectStore(projectId: number): Task[] {
  if (!store.has(projectId)) {
    store.set(projectId, seedProjectTasks(projectId))
  }
  return store.get(projectId)!
}

function filterTasks(items: Task[], params?: TaskListParams): Task[] {
  let result = items
  if (params?.requirement_id != null) {
    result = result.filter((item) => item.requirement_id === params.requirement_id)
  }
  if (params?.source_type) {
    result = result.filter((item) => item.source_type === params.source_type)
  }
  return result
}

function paginate<T>(items: T[], skip = 0, limit?: number): { slice: T[]; total: number } {
  const total = items.length
  const slice = limit == null ? items.slice(skip) : items.slice(skip, skip + limit)
  return { slice, total }
}

function buildTree(items: Task[]): TaskTreeNode[] {
  const nodeMap = new Map<number, TaskTreeNode>()
  const roots: TaskTreeNode[] = []

  for (const item of items) {
    nodeMap.set(item.id, { ...cloneTask(item), children: [] })
  }

  for (const node of nodeMap.values()) {
    if (node.parent_id == null) {
      roots.push(node)
      continue
    }
    const parent = nodeMap.get(node.parent_id)
    if (parent) {
      parent.children!.push(node)
    } else {
      roots.push(node)
    }
  }

  const stripEmpty = (nodes: TaskTreeNode[]): TaskTreeNode[] =>
    nodes.map((node) => {
      if (node.children && node.children.length > 0) {
        return { ...node, children: stripEmpty(node.children) }
      }
      const { children: _children, ...rest } = node
      return rest
    })

  return stripEmpty(roots)
}

function assertNoCycle(items: Task[], taskId: number, newParentId: number | null | undefined): void {
  if (newParentId == null) {
    return
  }
  if (newParentId === taskId) {
    throw new Error('Cannot set task as its own parent')
  }
  const descendants = new Set<number>()
  const collect = (id: number) => {
    for (const item of items) {
      if (item.parent_id === id) {
        descendants.add(item.id)
        collect(item.id)
      }
    }
  }
  collect(taskId)
  if (descendants.has(newParentId)) {
    throw new Error('Cannot set a descendant as parent')
  }
}

function resolveRequirementId(
  items: Task[],
  parentId: number | null | undefined,
  explicitRequirementId: number | null | undefined,
): number | null {
  if (explicitRequirementId !== undefined) {
    return explicitRequirementId
  }
  if (parentId == null) {
    return null
  }
  return items.find((item) => item.id === parentId)?.requirement_id ?? null
}

function createTaskFromDecomposeInput(
  projectId: number,
  requirementId: number,
  input: DecomposePayload['tasks'][number],
  parentId: number | null,
  assignee: Task['assignee'],
): Task[] {
  const timestamp = nowIso()
  const created: Task = {
    id: nextId++,
    project_id: projectId,
    requirement_id: requirementId,
    parent_id: parentId,
    title: input.title,
    description: input.description ?? null,
    source_type: 'requirement',
    source_description: null,
    status: 'todo',
    assignee_id: assignee?.id ?? null,
    assignee: assignee ?? null,
    planned_hours: input.planned_hours ?? null,
    actual_hours: null,
    cancelled_at: null,
    cancel_reason: null,
    created_at: timestamp,
    updated_at: timestamp,
  }

  const result = [created]
  for (const child of input.subtasks ?? []) {
    result.push(...createTaskFromDecomposeInput(projectId, requirementId, child, created.id, assignee))
  }
  return result
}

export async function mockFetchTasks(
  projectId: number,
  params?: TaskListParams,
): Promise<TaskListResponse | TaskTreeListResponse> {
  const items = filterTasks(getProjectStore(projectId), params)
  const { slice, total } = paginate(items, params?.skip, params?.limit)

  if (params?.tree) {
    return delay({
      items: buildTree(slice),
      total,
      skip: params?.skip ?? 0,
      limit: params?.limit ?? null,
    })
  }

  return delay({
    items: slice.map(cloneTask),
    total,
    skip: params?.skip ?? 0,
    limit: params?.limit ?? null,
  })
}

export async function mockFetchTask(projectId: number, taskId: number): Promise<Task> {
  const item = getProjectStore(projectId).find((row) => row.id === taskId)
  if (!item) {
    throw new Error('Task not found')
  }
  return delay(cloneTask(item))
}

export async function mockCreateTask(projectId: number, payload: TaskCreatePayload): Promise<Task> {
  const items = getProjectStore(projectId)
  const parentId = payload.parent_id ?? null

  if (parentId != null && !items.some((item) => item.id === parentId)) {
    throw new Error('Parent task not found')
  }

  const assignee = payload.assignee_id
    ? { id: payload.assignee_id, username: 'dev', display_name: '开发工程师' }
    : null
  const timestamp = nowIso()
  const created: Task = {
    id: nextId++,
    project_id: projectId,
    requirement_id: resolveRequirementId(items, parentId, payload.requirement_id),
    parent_id: parentId,
    title: payload.title,
    description: payload.description ?? null,
    source_type: payload.source_type,
    source_description: payload.source_description ?? null,
    status: payload.status ?? 'todo',
    assignee_id: payload.assignee_id ?? null,
    assignee,
    planned_hours: payload.planned_hours ?? null,
    actual_hours: null,
    cancelled_at: null,
    cancel_reason: null,
    created_at: timestamp,
    updated_at: timestamp,
  }

  items.push(created)
  return delay(cloneTask(created))
}

export async function mockUpdateTask(
  projectId: number,
  taskId: number,
  payload: TaskUpdatePayload,
): Promise<Task> {
  const items = getProjectStore(projectId)
  const index = items.findIndex((item) => item.id === taskId)
  if (index === -1) {
    throw new Error('Task not found')
  }

  assertNoCycle(items, taskId, payload.parent_id)

  const current = items[index]
  const assignee =
    payload.assignee_id !== undefined
      ? payload.assignee_id
        ? { id: payload.assignee_id, username: 'dev', display_name: '开发工程师' }
        : null
      : current.assignee ?? null

  const updated: Task = {
    ...current,
    ...payload,
    description: payload.description !== undefined ? payload.description : current.description,
    parent_id: payload.parent_id !== undefined ? payload.parent_id : current.parent_id,
    assignee_id: payload.assignee_id !== undefined ? payload.assignee_id : current.assignee_id,
    assignee,
    planned_hours: payload.planned_hours !== undefined ? payload.planned_hours : current.planned_hours,
    updated_at: nowIso(),
  }

  items[index] = updated
  return delay(cloneTask(updated))
}

export async function mockCancelTask(
  projectId: number,
  taskId: number,
  payload: TaskCancelPayload,
): Promise<Task> {
  const items = getProjectStore(projectId)
  const index = items.findIndex((item) => item.id === taskId)
  if (index === -1) {
    throw new Error('Task not found')
  }

  const current = items[index]
  if (current.status === 'cancelled') {
    throw new Error('Task already cancelled')
  }

  const timestamp = nowIso()
  const updated: Task = {
    ...current,
    status: 'cancelled',
    cancelled_at: timestamp,
    cancel_reason: payload.cancel_reason,
    updated_at: timestamp,
  }

  items[index] = updated
  return delay(cloneTask(updated))
}

/** PM-4.13/4.14 联调前：Mock 递归拆解创建任务树 */
export async function mockDecomposeRequirement(
  projectId: number,
  requirementId: number,
  payload: DecomposePayload,
): Promise<Task[]> {
  const items = getProjectStore(projectId)
  const assignee = { id: 2, username: 'dev', display_name: '开发工程师' }
  const created: Task[] = []

  for (const input of payload.tasks) {
    created.push(...createTaskFromDecomposeInput(projectId, requirementId, input, null, assignee))
  }

  items.push(...created)
  return delay(created.map(cloneTask))
}

/** 测试或联调前重置 Mock 数据 */
export function resetMockTasks(): void {
  store.clear()
  nextId = 1000
}
