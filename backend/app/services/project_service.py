from __future__ import annotations

from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.project import Project, ProjectStatus
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectNotFoundError(Exception):
    pass


class ProjectForbiddenError(Exception):
    pass


def _accessible_projects_query(user_id: int):
    member_project_ids = select(ProjectMember.project_id).where(ProjectMember.user_id == user_id)
    return select(Project).where(
        or_(Project.owner_id == user_id, Project.id.in_(member_project_ids))
    )


def user_can_access_project(db: Session, project_id: int, user_id: int) -> bool:
    query = _accessible_projects_query(user_id).where(Project.id == project_id)
    return db.scalar(query) is not None


def list_projects_for_user(
    db: Session,
    user_id: int,
    *,
    skip: int = 0,
    limit: Optional[int] = None,
) -> tuple[list[Project], int]:
    base_query = _accessible_projects_query(user_id)
    count_query = select(func.count()).select_from(base_query.subquery())

    query = (
        base_query.options(joinedload(Project.owner))
        .order_by(Project.id.desc())
        .offset(skip)
    )
    if limit is not None:
        query = query.limit(limit)

    projects = list(db.scalars(query).unique().all())
    total = db.scalar(count_query) or 0
    return projects, total


def get_project_for_user(db: Session, project_id: int, user_id: int) -> Project:
    query = (
        _accessible_projects_query(user_id)
        .where(Project.id == project_id)
        .options(joinedload(Project.owner))
    )
    project = db.scalar(query)
    if project is None:
        if db.get(Project, project_id) is None:
            raise ProjectNotFoundError
        raise ProjectForbiddenError
    return project


def create_project(db: Session, user_id: int, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        owner_id=user_id,
    )
    db.add(project)
    db.flush()

    owner_member = ProjectMember(
        project_id=project.id,
        user_id=user_id,
        role=ProjectMemberRole.OWNER,
    )
    db.add(owner_member)
    db.commit()
    db.refresh(project)
    return db.scalar(
        select(Project).where(Project.id == project.id).options(joinedload(Project.owner))
    )


def update_project(
    db: Session,
    project_id: int,
    user_id: int,
    data: ProjectUpdate,
) -> Project:
    project = get_project_for_user(db, project_id, user_id)
    if project.owner_id != user_id:
        raise ProjectForbiddenError

    project.name = data.name
    project.description = data.description
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user_id: int) -> None:
    project = get_project_for_user(db, project_id, user_id)
    if project.owner_id != user_id:
        raise ProjectForbiddenError

    project.status = ProjectStatus.ARCHIVED
    db.commit()
