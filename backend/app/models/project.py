from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project_member import ProjectMember
    from app.models.requirement import Requirement
    from app.models.task import Task
    from app.models.user import User


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"comment": "项目表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="项目名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="项目描述")
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True, comment="项目负责人用户 ID"
    )
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProjectStatus.ACTIVE,
        comment="项目状态：active=进行中, archived=已归档",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )

    owner: Mapped[User] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )
    members: Mapped[List[ProjectMember]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    requirements: Mapped[List[Requirement]] = relationship(
        "Requirement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[List[Task]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
