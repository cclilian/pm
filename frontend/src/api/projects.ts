import api from '@/api/client'
import type {
  ProjectMember,
  ProjectMemberCreatePayload,
  ProjectMemberListResponse,
} from '@/api/types/project_member'
import type {
  Project,
  ProjectCreatePayload,
  ProjectListResponse,
} from '@/api/types/project'

export async function fetchProjects(params?: {
  skip?: number
  limit?: number
}): Promise<ProjectListResponse> {
  const { data } = await api.get<ProjectListResponse>('/projects', { params })
  return data
}

export async function createProject(payload: ProjectCreatePayload): Promise<Project> {
  const { data } = await api.post<Project>('/projects', payload)
  return data
}

export async function fetchProject(projectId: number): Promise<Project> {
  const { data } = await api.get<Project>(`/projects/${projectId}`)
  return data
}

export async function fetchProjectMembers(projectId: number): Promise<ProjectMemberListResponse> {
  const { data } = await api.get<ProjectMemberListResponse>(`/projects/${projectId}/members`)
  return data
}

export async function addProjectMember(
  projectId: number,
  payload: ProjectMemberCreatePayload,
): Promise<ProjectMember> {
  const { data } = await api.post<ProjectMember>(`/projects/${projectId}/members`, payload)
  return data
}

export async function removeProjectMember(projectId: number, userId: number): Promise<void> {
  await api.delete(`/projects/${projectId}/members/${userId}`)
}
