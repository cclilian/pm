from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.requirement import (
    RequirementPriority,
    RequirementStatus,
    RequirementType,
)


class RequirementCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    type: RequirementType
    priority: Optional[RequirementPriority] = None
    parent_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: RequirementStatus = RequirementStatus.DRAFT


class RequirementUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    type: Optional[RequirementType] = None
    priority: Optional[RequirementPriority] = None
    parent_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: Optional[RequirementStatus] = None


class RequirementCancel(BaseModel):
    cancel_reason: str = Field(min_length=1)


class RequirementOwnerBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str


class RequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    parent_id: Optional[int]
    title: str
    description: Optional[str]
    type: RequirementType
    priority: Optional[RequirementPriority]
    status: RequirementStatus
    owner_id: Optional[int]
    owner: Optional[RequirementOwnerBrief] = None
    cancelled_at: Optional[datetime]
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime


class RequirementTreeNode(RequirementResponse):
    children: List[RequirementTreeNode] = []


class RequirementListResponse(BaseModel):
    items: List[RequirementResponse]
    total: int
    skip: int
    limit: Optional[int]


class RequirementTreeListResponse(BaseModel):
    items: List[RequirementTreeNode]
    total: int
    skip: int
    limit: Optional[int]


RequirementTreeNode.model_rebuild()
