from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: Optional[str] = None


class ProjectOwnerBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    owner_id: int
    status: ProjectStatus
    created_at: datetime
    owner: ProjectOwnerBrief


class ProjectListResponse(BaseModel):
    items: List[ProjectResponse]
    total: int
    skip: int
    limit: Optional[int]
