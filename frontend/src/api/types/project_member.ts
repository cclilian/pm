export type ProjectMemberRole = 'owner' | 'member'

export interface ProjectMemberUser {
  id: number
  username: string
  display_name: string
}

export interface ProjectMember {
  id: number
  project_id: number
  user_id: number
  role: ProjectMemberRole
  user: ProjectMemberUser
}

export interface ProjectMemberListResponse {
  items: ProjectMember[]
  total: number
}

export interface ProjectMemberCreatePayload {
  user_id: number
  role?: ProjectMemberRole
}

export const MEMBER_ROLE_LABELS: Record<ProjectMemberRole, string> = {
  owner: '负责人',
  member: '成员',
}
