import api from '@/api/client'
import {
  mockCancelRequirement,
  mockCreateRequirement,
  mockFetchRequirement,
  mockFetchRequirements,
  mockUpdateRequirement,
} from '@/api/mock/requirements'
import type {
  Requirement,
  RequirementCancelPayload,
  RequirementCreatePayload,
  RequirementListParams,
  RequirementListResponse,
  RequirementTreeListResponse,
  RequirementTreeNode,
  RequirementUpdatePayload,
} from '@/api/types/requirement'

/** PM-4.7：需求模块已联调，使用真实 API */
export const USE_MOCK_REQUIREMENTS = false

function stripEmptyChildren(nodes: RequirementTreeNode[]): RequirementTreeNode[] {
  return nodes.map((node) => {
    if (node.children && node.children.length > 0) {
      return { ...node, children: stripEmptyChildren(node.children) }
    }
    const { children: _children, ...rest } = node
    return rest
  })
}

export async function fetchRequirements(
  projectId: number,
  params?: RequirementListParams & { tree?: false },
): Promise<RequirementListResponse>
export async function fetchRequirements(
  projectId: number,
  params: RequirementListParams & { tree: true },
): Promise<RequirementTreeListResponse>
export async function fetchRequirements(
  projectId: number,
  params?: RequirementListParams,
): Promise<RequirementListResponse | RequirementTreeListResponse> {
  if (USE_MOCK_REQUIREMENTS) {
    return mockFetchRequirements(projectId, params)
  }

  const { data } = await api.get<RequirementListResponse | RequirementTreeListResponse>(
    `/projects/${projectId}/requirements`,
    { params },
  )
  if (params?.tree) {
    return {
      ...data,
      items: stripEmptyChildren(data.items as RequirementTreeNode[]),
    }
  }
  return data
}

export async function fetchRequirement(
  projectId: number,
  requirementId: number,
): Promise<Requirement> {
  if (USE_MOCK_REQUIREMENTS) {
    return mockFetchRequirement(projectId, requirementId)
  }

  const { data } = await api.get<Requirement>(
    `/projects/${projectId}/requirements/${requirementId}`,
  )
  return data
}

export async function createRequirement(
  projectId: number,
  payload: RequirementCreatePayload,
): Promise<Requirement> {
  if (USE_MOCK_REQUIREMENTS) {
    return mockCreateRequirement(projectId, payload)
  }

  const { data } = await api.post<Requirement>(
    `/projects/${projectId}/requirements`,
    payload,
  )
  return data
}

export async function updateRequirement(
  projectId: number,
  requirementId: number,
  payload: RequirementUpdatePayload,
): Promise<Requirement> {
  if (USE_MOCK_REQUIREMENTS) {
    return mockUpdateRequirement(projectId, requirementId, payload)
  }

  const { data } = await api.put<Requirement>(
    `/projects/${projectId}/requirements/${requirementId}`,
    payload,
  )
  return data
}

export async function cancelRequirement(
  projectId: number,
  requirementId: number,
  payload: RequirementCancelPayload,
): Promise<Requirement> {
  if (USE_MOCK_REQUIREMENTS) {
    return mockCancelRequirement(projectId, requirementId, payload)
  }

  const { data } = await api.patch<Requirement>(
    `/projects/${projectId}/requirements/${requirementId}/cancel`,
    payload,
  )
  return data
}

export type {
  Requirement,
  RequirementCancelPayload,
  RequirementCreatePayload,
  RequirementListParams,
  RequirementListResponse,
  RequirementPriority,
  RequirementStatus,
  RequirementTreeListResponse,
  RequirementTreeNode,
  RequirementType,
  RequirementUpdatePayload,
} from '@/api/types/requirement'

export {
  getRequirementPath,
  isRequirementLeaf,
  REQUIREMENT_PRIORITY_LABELS,
  REQUIREMENT_STATUS_LABELS,
  REQUIREMENT_TYPE_LABELS,
} from '@/api/types/requirement'
