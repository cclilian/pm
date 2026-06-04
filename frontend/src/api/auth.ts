import api from '@/api/client'
import type { TokenResponse, UserMe } from '@/api/types/auth'

export async function login(username: string, password: string): Promise<TokenResponse> {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)

  const { data } = await api.post<TokenResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function fetchMe(): Promise<UserMe> {
  const { data } = await api.get<UserMe>('/auth/me')
  return data
}
