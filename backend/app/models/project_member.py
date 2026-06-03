from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class ProjectMemberRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[ProjectMemberRole] = mapped_column(
        Enum(ProjectMemberRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=ProjectMemberRole.MEMBER,
    )

    project: Mapped[Project] = relationship("Project", back_populates="members")
    user: Mapped[User] = relationship("User", back_populates="project_memberships")
