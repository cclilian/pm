from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.project_member import ProjectMember


class UserRole(str, enum.Enum):
    PM = "pm"
    DEV = "dev"
    TEST = "test"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "系统用户表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True, comment="登录用户名，唯一"
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希值")
    display_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="显示名称")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserRole.DEV,
        comment="用户角色：pm=项目经理, dev=开发, test=测试",
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=UserStatus.ACTIVE,
        comment="账号状态：active=启用, inactive=停用",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    owned_projects: Mapped[List[Project]] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id",
    )
    project_memberships: Mapped[List[ProjectMember]] = relationship(
        "ProjectMember",
        back_populates="user",
    )
