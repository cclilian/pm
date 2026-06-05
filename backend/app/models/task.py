from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.requirement import Requirement
    from app.models.user import User


class TaskSourceType(str, enum.Enum):
    REQUIREMENT = "requirement"
    INTERNAL = "internal"
    EXTERNAL = "external"
    ADHOC = "adhoc"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = {"comment": "项目任务表，支持 parent_id 多级树形结构"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="主键 ID")
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
        comment="所属项目 ID",
    )
    requirement_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("requirements.id"),
        nullable=True,
        index=True,
        comment="关联需求 ID，独立任务可为空",
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=True,
        index=True,
        comment="父任务 ID，为空表示顶层任务",
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="任务标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="任务描述")
    source_type: Mapped[TaskSourceType] = mapped_column(
        Enum(TaskSourceType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        comment="任务来源：requirement=需求拆解, internal=项目内, external=项目外, adhoc=临时",
    )
    source_description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="来源说明，如项目外任务背景",
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TaskStatus.TODO,
        comment="任务状态：todo=待办, in_progress=进行中, done=已完成, cancelled=已取消",
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="执行人用户 ID",
    )
    planned_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="计划工时（小时）",
    )
    actual_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="实际工时（小时）",
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

    project: Mapped[Project] = relationship("Project", back_populates="tasks")
    requirement: Mapped[Optional[Requirement]] = relationship(
        "Requirement",
        back_populates="tasks",
        foreign_keys=[requirement_id],
    )
    assignee: Mapped[Optional[User]] = relationship("User", foreign_keys=[assignee_id])
    parent: Mapped[Optional[Task]] = relationship(
        "Task",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[List[Task]] = relationship(
        "Task",
        back_populates="parent",
        foreign_keys=[parent_id],
    )
