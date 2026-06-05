from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.models.task import TaskSourceType, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    requirement_id: Optional[int] = None
    parent_id: Optional[int] = None
    source_type: TaskSourceType
    source_description: Optional[str] = None
    assignee_id: Optional[int] = None
    planned_hours: Optional[float] = Field(default=None, ge=0)
    status: TaskStatus = TaskStatus.TODO


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    assignee_id: Optional[int] = None
    planned_hours: Optional[float] = Field(default=None, ge=0)
    status: Optional[TaskStatus] = None


class DecomposeTaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    planned_hours: Optional[float] = Field(default=None, ge=0)
    subtasks: List["DecomposeTaskInput"] = []


class DecomposePayload(BaseModel):
    tasks: List[DecomposeTaskInput] = Field(min_length=1)


class TaskCancel(BaseModel):
    cancel_reason: str = Field(min_length=1)


class TaskAssigneeBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    requirement_id: Optional[int]
    parent_id: Optional[int]
    title: str
    description: Optional[str]
    source_type: TaskSourceType
    source_description: Optional[str]
    status: TaskStatus
    assignee_id: Optional[int]
    assignee: Optional[TaskAssigneeBrief] = None
    planned_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    cancelled_at: Optional[datetime]
    cancel_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    @field_serializer("planned_hours", "actual_hours")
    def serialize_hours(self, value: Optional[Decimal]) -> Optional[float]:
        if value is None:
            return None
        return float(value)


class TaskTreeNode(TaskResponse):
    children: List[TaskTreeNode] = []


class TaskListResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    skip: int
    limit: Optional[int]


class TaskTreeListResponse(BaseModel):
    items: List[TaskTreeNode]
    total: int
    skip: int
    limit: Optional[int]


DecomposeTaskInput.model_rebuild()
TaskTreeNode.model_rebuild()
