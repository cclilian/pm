import type { UserRole, UserStatus } from '@/api/types/auth'

export interface User {
  id: number
  username: string
  display_name: string
  role: UserRole
  status: UserStatus
  created_at: string
}

export interface UserListResponse {
  items: User[]
  total: number
  skip: number
  limit: number | null
}

export interface UserCreatePayload {
  username: string
  password: string
  display_name: string
  role: UserRole
}

export interface UserUpdatePayload {
  display_name: string
  role: UserRole
  status: UserStatus
}

export const ROLE_LABELS: Record<UserRole, string> = {
  pm: '项目经理',
  dev: '开发',
  test: '测试',
}

export const STATUS_LABELS: Record<UserStatus, string> = {
  active: '启用',
  inactive: '停用',
}
