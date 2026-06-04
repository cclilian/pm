export type ProjectStatus = 'active' | 'archived'

export interface ProjectOwner {
  id: number
  username: string
  display_name: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  owner_id: number
  status: ProjectStatus
  created_at: string
  owner: ProjectOwner
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  skip: number
  limit: number | null
}

export interface ProjectCreatePayload {
  name: string
  description?: string | null
}

export const STATUS_LABELS: Record<ProjectStatus, string> = {
  active: '进行中',
  archived: '已归档',
}
