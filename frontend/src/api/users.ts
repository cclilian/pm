import api from '@/api/client'
import type { UserStatus } from '@/api/types/auth'
import type {
  User,
  UserCreatePayload,
  UserListResponse,
  UserUpdatePayload,
} from '@/api/types/user'

export async function fetchUsers(params?: {
  status?: UserStatus
  skip?: number
  limit?: number
}): Promise<UserListResponse> {
  const { data } = await api.get<UserListResponse>('/users', { params })
  return data
}

export async function createUser(payload: UserCreatePayload): Promise<User> {
  const { data } = await api.post<User>('/users', payload)
  return data
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<User> {
  const { data } = await api.put<User>(`/users/${userId}`, payload)
  return data
}

export async function updateUserPassword(userId: number, password: string): Promise<User> {
  const { data } = await api.patch<User>(`/users/${userId}/password`, { password })
  return data
}
