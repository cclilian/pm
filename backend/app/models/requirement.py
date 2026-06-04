from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class RequirementType(str, enum.Enum):
    CORE = "core"
    NON_CORE = "non_core"


class RequirementStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DONE = "done"
    CANCELLED = "cancelled"


class RequirementPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = {"comment": "项目需求表，支持 parent_id 多级树形结构"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="所属项目 ID",
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("requirements.id"),
        nullable=True,
        index=True,
        comment="父需求 ID，为空表示顶层需求",
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="需求标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="需求描述")
    type: Mapped[RequirementType] = mapped_column(
        Enum(RequirementType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="需求类型：core=核心业务, non_core=非核心业务",
    )
    priority: Mapped[Optional[RequirementPriority]] = mapped_column(
        Enum(RequirementPriority, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        comment="优先级：low/medium/high/urgent",
    )
    status: Mapped[RequirementStatus] = mapped_column(
        Enum(RequirementStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=RequirementStatus.DRAFT,
        comment="需求状态",
    )
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="负责人用户 ID",
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="取消时间",
    )
    cancel_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="取消原因",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    project: Mapped[Project] = relationship("Project", back_populates="requirements")
    owner: Mapped[Optional[User]] = relationship("User", foreign_keys=[owner_id])
    parent: Mapped[Optional[Requirement]] = relationship(
        "Requirement",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[List[Requirement]] = relationship(
        "Requirement",
        back_populates="parent",
        foreign_keys=[parent_id],
    )
