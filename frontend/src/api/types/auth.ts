export interface TokenResponse {
  access_token: string
  token_type: string
}

export type UserRole = 'pm' | 'dev' | 'test'
export type UserStatus = 'active' | 'inactive'

export interface UserMe {
  id: number
  username: string
  display_name: string
  role: UserRole
  status: UserStatus
  created_at: string
}
