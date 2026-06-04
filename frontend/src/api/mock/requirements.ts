import type {
  Requirement,
  RequirementCancelPayload,
  RequirementCreatePayload,
  RequirementListParams,
  RequirementListResponse,
  RequirementTreeListResponse,
  RequirementTreeNode,
  RequirementUpdatePayload,
} from '@/api/types/requirement'

const MOCK_DELAY_MS = 120

let nextId = 100
const store = new Map<number, Requirement[]>()

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(value), MOCK_DELAY_MS)
  })
}

function nowIso(): string {
  return new Date().toISOString()
}

function cloneRequirement(item: Requirement): Requirement {
  return { ...item }
}

function seedProjectRequirements(projectId: number): Requirement[] {
  const createdAt = '2026-06-01T08:00:00.000Z'
  const owner = { id: 1, username: 'pm_test_auth', display_name: '测试 PM' }

  const items: Requirement[] = [
    {
      id: 1,
      project_id: projectId,
      parent_id: null,
      title: '用户登录与权限',
      description: '核心认证与授权能力',
      type: 'core',
      priority: 'high',
      status: 'active',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 2,
      project_id: projectId,
      parent_id: 1,
      title: 'JWT 登录',
      description: '用户名密码登录并签发 Token',
      type: 'core',
      priority: 'high',
      status: 'done',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 3,
      project_id: projectId,
      parent_id: 2,
      title: '登录页 UI',
      description: '前端登录表单与错误提示',
      type: 'core',
      priority: 'medium',
      status: 'done',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 4,
      project_id: projectId,
      parent_id: 3,
      title: '记住用户名',
      description: '可选记住上次登录用户名',
      type: 'core',
      priority: 'low',
      status: 'active',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 5,
      project_id: projectId,
      parent_id: 1,
      title: '路由守卫',
      description: '未登录跳转 /login',
      type: 'core',
      priority: 'medium',
      status: 'active',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 6,
      project_id: projectId,
      parent_id: null,
      title: '帮助文档入口',
      description: '非核心：项目内帮助链接',
      type: 'non_core',
      priority: 'low',
      status: 'draft',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 7,
      project_id: projectId,
      parent_id: 6,
      title: 'FAQ 页面',
      description: '常见问题列表',
      type: 'non_core',
      priority: 'low',
      status: 'draft',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
    {
      id: 8,
      project_id: projectId,
      parent_id: 7,
      title: '搜索 FAQ',
      description: '按关键词搜索 FAQ',
      type: 'non_core',
      priority: 'medium',
      status: 'draft',
      owner_id: owner.id,
      owner,
      cancelled_at: null,
      cancel_reason: null,
      created_at: createdAt,
      updated_at: createdAt,
    },
  ]

  return items
}

function getProjectStore(projectId: number): Requirement[] {
  if (!store.has(projectId)) {
    store.set(projectId, seedProjectRequirements(projectId))
  }
  return store.get(projectId)!
}

function filterByType(items: Requirement[], type?: Requirement['type']): Requirement[] {
  if (!type) {
    return items
  }
  return items.filter((item) => item.type === type)
}

function paginate<T>(items: T[], skip = 0, limit?: number): { slice: T[]; total: number } {
  const total = items.length
  const slice = limit == null ? items.slice(skip) : items.slice(skip, skip + limit)
  return { slice, total }
}

function buildTree(items: Requirement[]): RequirementTreeNode[] {
  const nodeMap = new Map<number, RequirementTreeNode>()
  const roots: RequirementTreeNode[] = []

  for (const item of items) {
    nodeMap.set(item.id, { ...cloneRequirement(item), children: [] })
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

  const stripEmpty = (nodes: RequirementTreeNode[]): RequirementTreeNode[] =>
    nodes.map((node) => {
      if (node.children && node.children.length > 0) {
        return { ...node, children: stripEmpty(node.children) }
      }
      const { children: _children, ...rest } = node
      return rest
    })

  return stripEmpty(roots)
}

function assertNoCycle(
  items: Requirement[],
  requirementId: number,
  newParentId: number | null | undefined,
): void {
  if (newParentId == null) {
    return
  }
  if (newParentId === requirementId) {
    throw new Error('Cannot set requirement as its own parent')
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
  collect(requirementId)
  if (descendants.has(newParentId)) {
    throw new Error('Cannot set a descendant as parent')
  }
}

function inheritTypeFromParent(
  items: Requirement[],
  parentId: number | null | undefined,
  explicitType: Requirement['type'] | undefined,
): Requirement['type'] {
  if (explicitType) {
    return explicitType
  }
  if (parentId == null) {
    return 'core'
  }
  const parent = items.find((item) => item.id === parentId)
  return parent?.type ?? 'core'
}

export async function mockFetchRequirements(
  projectId: number,
  params?: RequirementListParams,
): Promise<RequirementListResponse | RequirementTreeListResponse> {
  const items = filterByType(getProjectStore(projectId), params?.type)
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
    items: slice.map(cloneRequirement),
    total,
    skip: params?.skip ?? 0,
    limit: params?.limit ?? null,
  })
}

export async function mockFetchRequirement(
  projectId: number,
  requirementId: number,
): Promise<Requirement> {
  const item = getProjectStore(projectId).find((row) => row.id === requirementId)
  if (!item) {
    throw new Error('Requirement not found')
  }
  return delay(cloneRequirement(item))
}

export async function mockCreateRequirement(
  projectId: number,
  payload: RequirementCreatePayload,
): Promise<Requirement> {
  const items = getProjectStore(projectId)
  const parentId = payload.parent_id ?? null

  if (parentId != null && !items.some((item) => item.id === parentId)) {
    throw new Error('Parent requirement not found')
  }

  const timestamp = nowIso()
  const created: Requirement = {
    id: nextId++,
    project_id: projectId,
    parent_id: parentId,
    title: payload.title,
    description: payload.description ?? null,
    type: inheritTypeFromParent(items, parentId, payload.type),
    priority: payload.priority ?? null,
    status: payload.status ?? 'draft',
    owner_id: payload.owner_id ?? 1,
    owner: { id: 1, username: 'pm_test_auth', display_name: '测试 PM' },
    cancelled_at: null,
    cancel_reason: null,
    created_at: timestamp,
    updated_at: timestamp,
  }

  items.push(created)
  return delay(cloneRequirement(created))
}

export async function mockUpdateRequirement(
  projectId: number,
  requirementId: number,
  payload: RequirementUpdatePayload,
): Promise<Requirement> {
  const items = getProjectStore(projectId)
  const index = items.findIndex((item) => item.id === requirementId)
  if (index === -1) {
    throw new Error('Requirement not found')
  }

  assertNoCycle(items, requirementId, payload.parent_id)

  const current = items[index]
  const updated: Requirement = {
    ...current,
    ...payload,
    description: payload.description !== undefined ? payload.description : current.description,
    priority: payload.priority !== undefined ? payload.priority : current.priority,
    parent_id: payload.parent_id !== undefined ? payload.parent_id : current.parent_id,
    updated_at: nowIso(),
  }

  items[index] = updated
  return delay(cloneRequirement(updated))
}

export async function mockCancelRequirement(
  projectId: number,
  requirementId: number,
  payload: RequirementCancelPayload,
): Promise<Requirement> {
  const items = getProjectStore(projectId)
  const index = items.findIndex((item) => item.id === requirementId)
  if (index === -1) {
    throw new Error('Requirement not found')
  }

  const current = items[index]
  if (current.status === 'cancelled') {
    throw new Error('Requirement already cancelled')
  }

  const timestamp = nowIso()
  const updated: Requirement = {
    ...current,
    status: 'cancelled',
    cancelled_at: timestamp,
    cancel_reason: payload.cancel_reason,
    updated_at: timestamp,
  }

  items[index] = updated
  return delay(cloneRequirement(updated))
}

/** 测试或联调前重置 Mock 数据 */
export function resetMockRequirements(): void {
  store.clear()
  nextId = 100
}
