from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.project_member import ProjectMemberRole


class ProjectMemberUserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    user_id: int
    role: ProjectMemberRole
    user: ProjectMemberUserBrief


class ProjectMemberListResponse(BaseModel):
    items: List[ProjectMemberResponse]
    total: int


class ProjectMemberCreate(BaseModel):
    user_id: int = Field(gt=0)
    role: ProjectMemberRole = ProjectMemberRole.MEMBER
