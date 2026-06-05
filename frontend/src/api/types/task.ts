export type TaskSourceType = 'requirement' | 'internal' | 'external' | 'adhoc'

export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'cancelled'

export interface TaskAssignee {
  id: number
  username: string
  display_name: string
}

export interface Task {
  id: number
  project_id: number
  requirement_id: number | null
  parent_id: number | null
  title: string
  description: string | null
  source_type: TaskSourceType
  source_description: string | null
  status: TaskStatus
  assignee_id: number | null
  assignee?: TaskAssignee | null
  planned_hours: number | null
  actual_hours: number | null
  cancelled_at: string | null
  cancel_reason: string | null
  created_at: string
  updated_at: string
}

export interface TaskTreeNode extends Task {
  children?: TaskTreeNode[]
}

/** 拆解弹窗 / decompose API 递归输入（仅 title 等编辑字段，无 id） */
export interface DecomposeTaskInput {
  title: string
  description?: string | null
  planned_hours?: number | null
  subtasks?: DecomposeTaskInput[]
}

export interface DecomposePayload {
  tasks: DecomposeTaskInput[]
}

export interface TaskListParams {
  tree?: boolean
  requirement_id?: number
  source_type?: TaskSourceType
  skip?: number
  limit?: number
}

export interface TaskListResponse {
  items: Task[]
  total: number
  skip: number
  limit: number | null
}

export interface TaskTreeListResponse {
  items: TaskTreeNode[]
  total: number
  skip: number
  limit: number | null
}

export interface TaskCreatePayload {
  title: string
  description?: string | null
  requirement_id?: number | null
  parent_id?: number | null
  source_type: TaskSourceType
  source_description?: string | null
  assignee_id?: number | null
  planned_hours?: number | null
  status?: TaskStatus
}

export interface TaskUpdatePayload {
  title?: string
  description?: string | null
  parent_id?: number | null
  assignee_id?: number | null
  planned_hours?: number | null
  status?: TaskStatus
}

export interface TaskCancelPayload {
  cancel_reason: string
}

export const TASK_SOURCE_TYPE_LABELS: Record<TaskSourceType, string> = {
  requirement: '需求拆解',
  internal: '项目内',
  external: '项目外',
  adhoc: '临时任务',
}

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  todo: '待办',
  in_progress: '进行中',
  done: '已完成',
  cancelled: '已取消',
}
