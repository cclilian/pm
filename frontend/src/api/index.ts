import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export default api

export async function fetchHealth() {
  const { data } = await api.get<{ status: string }>('/health')
  return data
}

export async function fetchDbHealth() {
  const { data } = await api.get<{ status: string; database: string }>('/health/db')
  return data
}
