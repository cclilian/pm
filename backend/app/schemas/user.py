from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    display_name: str = Field(min_length=1, max_length=128)
    role: UserRole = UserRole.DEV


class UserUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=128)
    role: UserRole
    status: UserStatus


class UserPasswordUpdate(BaseModel):
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    skip: int
    limit: Optional[int]
