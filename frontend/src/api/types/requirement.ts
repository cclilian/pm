export type RequirementType = 'core' | 'non_core'

export type RequirementStatus = 'draft' | 'active' | 'done' | 'cancelled'

export type RequirementPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface RequirementOwner {
  id: number
  username: string
  display_name: string
}

export interface Requirement {
  id: number
  project_id: number
  parent_id: number | null
  title: string
  description: string | null
  type: RequirementType
  priority: RequirementPriority | null
  status: RequirementStatus
  owner_id: number | null
  owner?: RequirementOwner | null
  cancelled_at: string | null
  cancel_reason: string | null
  created_at: string
  updated_at: string
}

export interface RequirementTreeNode extends Requirement {
  children?: RequirementTreeNode[]
}

export interface RequirementListParams {
  tree?: boolean
  type?: RequirementType
  skip?: number
  limit?: number
}

export interface RequirementListResponse {
  items: Requirement[]
  total: number
  skip: number
  limit: number | null
}

export interface RequirementTreeListResponse {
  items: RequirementTreeNode[]
  total: number
  skip: number
  limit: number | null
}

export interface RequirementCreatePayload {
  title: string
  description?: string | null
  type: RequirementType
  priority?: RequirementPriority | null
  parent_id?: number | null
  owner_id?: number | null
  status?: RequirementStatus
}

export interface RequirementUpdatePayload {
  title?: string
  description?: string | null
  type?: RequirementType
  priority?: RequirementPriority | null
  parent_id?: number | null
  owner_id?: number | null
  status?: RequirementStatus
}

export interface RequirementCancelPayload {
  cancel_reason: string
}

export const REQUIREMENT_TYPE_LABELS: Record<RequirementType, string> = {
  core: '核心业务',
  non_core: '非核心业务',
}

export const REQUIREMENT_STATUS_LABELS: Record<RequirementStatus, string> = {
  draft: '草稿',
  active: '进行中',
  done: '已完成',
  cancelled: '已取消',
}

export const REQUIREMENT_PRIORITY_LABELS: Record<RequirementPriority, string> = {
  low: '低',
  medium: '中',
  high: '高',
  urgent: '紧急',
}

/** 末节点：不存在以本需求为 parent 的子需求 */
export function isRequirementLeaf(
  requirementId: number,
  requirements: Requirement[],
): boolean {
  return !requirements.some((item) => item.parent_id === requirementId)
}
