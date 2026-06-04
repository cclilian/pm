from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.user import User
from app.schemas.project_member import ProjectMemberCreate
from app.services.project_service import (
    ProjectForbiddenError,
    ProjectNotFoundError,
    get_project_for_user,
)


class MemberAlreadyExistsError(Exception):
    pass


class MemberNotFoundError(Exception):
    pass


class OwnerCannotBeRemovedError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def _require_project_owner(db: Session, project_id: int, user_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None:
        raise ProjectNotFoundError
    if project.owner_id != user_id:
        raise ProjectForbiddenError
    return project


def list_project_members(
    db: Session,
    project_id: int,
    user_id: int,
) -> tuple[list[ProjectMember], int]:
    get_project_for_user(db, project_id, user_id)

    query = (
        select(ProjectMember)
        .where(ProjectMember.project_id == project_id)
        .options(joinedload(ProjectMember.user))
        .order_by(ProjectMember.id)
    )
    members = list(db.scalars(query).unique().all())
    total = db.scalar(
        select(func.count())
        .select_from(ProjectMember)
        .where(ProjectMember.project_id == project_id)
    ) or 0
    return members, total


def _transfer_project_ownership(
    db: Session,
    project: Project,
    new_owner_user_id: int,
) -> None:
    current_owner_member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id,
            ProjectMember.role == ProjectMemberRole.OWNER,
        )
    )
    if current_owner_member is not None:
        current_owner_member.role = ProjectMemberRole.MEMBER

    project.owner_id = new_owner_user_id


def add_project_member(
    db: Session,
    project_id: int,
    actor_id: int,
    data: ProjectMemberCreate,
) -> ProjectMember:
    project = _require_project_owner(db, project_id, actor_id)

    target_user = db.get(User, data.user_id)
    if target_user is None:
        raise UserNotFoundError

    existing = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == data.user_id,
        )
    )
    if existing is not None:
        raise MemberAlreadyExistsError

    if data.role == ProjectMemberRole.OWNER:
        _transfer_project_ownership(db, project, data.user_id)

    member = ProjectMember(
        project_id=project_id,
        user_id=data.user_id,
        role=data.role,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return db.scalar(
        select(ProjectMember)
        .where(ProjectMember.id == member.id)
        .options(joinedload(ProjectMember.user))
    )


def remove_project_member(
    db: Session,
    project_id: int,
    actor_id: int,
    target_user_id: int,
) -> None:
    _require_project_owner(db, project_id, actor_id)

    member = db.scalar(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id,
        )
    )
    if member is None:
        raise MemberNotFoundError

    if member.role == ProjectMemberRole.OWNER:
        raise OwnerCannotBeRemovedError

    db.delete(member)
    db.commit()
