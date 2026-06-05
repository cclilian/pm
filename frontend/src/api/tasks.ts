import api from '@/api/client'
import {
  mockCancelTask,
  mockCreateTask,
  mockDecomposeRequirement,
  mockFetchTask,
  mockFetchTasks,
  mockUpdateTask,
} from '@/api/mock/tasks'
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

/** PM-4.12：任务模块已联调，使用真实 API */
export const USE_MOCK_TASKS = false

function stripEmptyChildren(nodes: TaskTreeNode[]): TaskTreeNode[] {
  return nodes.map((node) => {
    if (node.children && node.children.length > 0) {
      return { ...node, children: stripEmptyChildren(node.children) }
    }
    const { children: _children, ...rest } = node
    return rest
  })
}

export async function fetchTasks(
  projectId: number,
  params?: TaskListParams & { tree?: false },
): Promise<TaskListResponse>
export async function fetchTasks(
  projectId: number,
  params: TaskListParams & { tree: true },
): Promise<TaskTreeListResponse>
export async function fetchTasks(
  projectId: number,
  params?: TaskListParams,
): Promise<TaskListResponse | TaskTreeListResponse> {
  if (USE_MOCK_TASKS) {
    return mockFetchTasks(projectId, params)
  }

  const { data } = await api.get<TaskListResponse | TaskTreeListResponse>(
    `/projects/${projectId}/tasks`,
    { params },
  )
  if (params?.tree) {
    return {
      ...data,
      items: stripEmptyChildren(data.items as TaskTreeNode[]),
    }
  }
  return data
}

export async function fetchTask(projectId: number, taskId: number): Promise<Task> {
  if (USE_MOCK_TASKS) {
    return mockFetchTask(projectId, taskId)
  }

  const { data } = await api.get<Task>(`/projects/${projectId}/tasks/${taskId}`)
  return data
}

export async function createTask(projectId: number, payload: TaskCreatePayload): Promise<Task> {
  if (USE_MOCK_TASKS) {
    return mockCreateTask(projectId, payload)
  }

  const { data } = await api.post<Task>(`/projects/${projectId}/tasks`, payload)
  return data
}

export async function updateTask(
  projectId: number,
  taskId: number,
  payload: TaskUpdatePayload,
): Promise<Task> {
  if (USE_MOCK_TASKS) {
    return mockUpdateTask(projectId, taskId, payload)
  }

  const { data } = await api.put<Task>(`/projects/${projectId}/tasks/${taskId}`, payload)
  return data
}

export async function cancelTask(
  projectId: number,
  taskId: number,
  payload: TaskCancelPayload,
): Promise<Task> {
  if (USE_MOCK_TASKS) {
    return mockCancelTask(projectId, taskId, payload)
  }

  const { data } = await api.patch<Task>(
    `/projects/${projectId}/tasks/${taskId}/cancel`,
    payload,
  )
  return data
}

export async function decomposeRequirement(
  projectId: number,
  requirementId: number,
  payload: DecomposePayload,
): Promise<Task[]> {
  if (USE_MOCK_TASKS) {
    return mockDecomposeRequirement(projectId, requirementId, payload)
  }

  const { data } = await api.post<Task[]>(
    `/projects/${projectId}/requirements/${requirementId}/decompose`,
    payload,
  )
  return data
}

export type {
  DecomposePayload,
  DecomposeTaskInput,
  Task,
  TaskCancelPayload,
  TaskCreatePayload,
  TaskListParams,
  TaskListResponse,
  TaskSourceType,
  TaskStatus,
  TaskTreeListResponse,
  TaskTreeNode,
  TaskUpdatePayload,
} from '@/api/types/task'

export {
  TASK_SOURCE_TYPE_LABELS,
  TASK_STATUS_LABELS,
} from '@/api/types/task'
