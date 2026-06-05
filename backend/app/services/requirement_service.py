from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.requirement import Requirement, RequirementStatus, RequirementType
from app.models.user import User
from app.schemas.requirement import RequirementCreate, RequirementResponse, RequirementTreeNode, RequirementUpdate
from app.services.project_service import (
    ProjectForbiddenError,
    ProjectNotFoundError,
    get_project_for_user,
)


class RequirementNotFoundError(Exception):
    pass


class RequirementCycleError(Exception):
    pass


class ParentNotFoundError(Exception):
    pass


class OwnerNotFoundError(Exception):
    pass


class RequirementAlreadyCancelledError(Exception):
    pass


def _requirement_query(project_id: int):
    return (
        select(Requirement)
        .where(Requirement.project_id == project_id)
        .options(joinedload(Requirement.owner))
        .order_by(Requirement.id.asc())
    )


def _collect_descendant_ids(db: Session, requirement_id: int) -> set[int]:
    descendants: set[int] = set()
    queue = [requirement_id]
    while queue:
        current_id = queue.pop()
        child_ids = db.scalars(
            select(Requirement.id).where(Requirement.parent_id == current_id)
        ).all()
        for child_id in child_ids:
            if child_id not in descendants:
                descendants.add(child_id)
                queue.append(child_id)
    return descendants


def _validate_parent_id(
    db: Session,
    project_id: int,
    requirement_id: Optional[int],
    parent_id: Optional[int],
) -> None:
    if parent_id is None:
        return
    if requirement_id is not None and parent_id == requirement_id:
        raise RequirementCycleError

    parent = db.scalar(
        select(Requirement).where(
            Requirement.id == parent_id,
            Requirement.project_id == project_id,
        )
    )
    if parent is None:
        raise ParentNotFoundError

    if requirement_id is not None:
        descendants = _collect_descendant_ids(db, requirement_id)
        if parent_id in descendants:
            raise RequirementCycleError


def _validate_owner_id(db: Session, owner_id: Optional[int]) -> None:
    if owner_id is None:
        return
    if db.get(User, owner_id) is None:
        raise OwnerNotFoundError


def build_requirement_tree(requirements: list[Requirement]) -> list[RequirementTreeNode]:
    nodes: dict[int, RequirementTreeNode] = {}
    for item in requirements:
        base = RequirementResponse.model_validate(item)
        nodes[item.id] = RequirementTreeNode(**base.model_dump(), children=[])
    roots: list[RequirementTreeNode] = []
    for item in requirements:
        node = nodes[item.id]
        if item.parent_id is None or item.parent_id not in nodes:
            roots.append(node)
        else:
            nodes[item.parent_id].children.append(node)
    return roots


def list_requirements(
    db: Session,
    project_id: int,
    user_id: int,
    *,
    tree: bool = False,
    req_type: Optional[RequirementType] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> tuple[list[Requirement] | list[RequirementTreeNode], int]:
    get_project_for_user(db, project_id, user_id)

    query = _requirement_query(project_id)
    if req_type is not None:
        query = query.where(Requirement.type == req_type)

    all_items = list(db.scalars(query).unique().all())
    total = len(all_items)

    if tree:
        tree_roots = build_requirement_tree(all_items)
        if skip or limit is not None:
            sliced = tree_roots[skip : skip + limit if limit is not None else None]
            return sliced, total
        return tree_roots, total

    sliced = all_items[skip : skip + limit if limit is not None else None]
    return sliced, total


def get_requirement(
    db: Session,
    project_id: int,
    requirement_id: int,
    user_id: int,
) -> Requirement:
    get_project_for_user(db, project_id, user_id)

    requirement = db.scalar(
        _requirement_query(project_id).where(Requirement.id == requirement_id)
    )
    if requirement is None:
        raise RequirementNotFoundError
    return requirement


def create_requirement(
    db: Session,
    project_id: int,
    user_id: int,
    data: RequirementCreate,
) -> Requirement:
    get_project_for_user(db, project_id, user_id)
    _validate_parent_id(db, project_id, None, data.parent_id)
    _validate_owner_id(db, data.owner_id)

    req_type = data.type
    if data.parent_id is not None:
        parent = db.get(Requirement, data.parent_id)
        if parent is not None:
            req_type = parent.type

    requirement = Requirement(
        project_id=project_id,
        parent_id=data.parent_id,
        title=data.title,
        description=data.description,
        type=req_type,
        priority=data.priority,
        status=data.status,
        owner_id=data.owner_id,
    )
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return get_requirement(db, project_id, requirement.id, user_id)


def update_requirement(
    db: Session,
    project_id: int,
    requirement_id: int,
    user_id: int,
    data: RequirementUpdate,
) -> Requirement:
    get_project_for_user(db, project_id, user_id)
    requirement = get_requirement(db, project_id, requirement_id, user_id)

    payload = data.model_dump(exclude_unset=True)
    if "parent_id" in payload:
        _validate_parent_id(db, project_id, requirement_id, payload["parent_id"])
    if "owner_id" in payload:
        _validate_owner_id(db, payload["owner_id"])

    for field, value in payload.items():
        setattr(requirement, field, value)

    db.commit()
    db.refresh(requirement)
    return get_requirement(db, project_id, requirement_id, user_id)


def cancel_requirement(
    db: Session,
    project_id: int,
    requirement_id: int,
    user_id: int,
    cancel_reason: str,
) -> Requirement:
    get_project_for_user(db, project_id, user_id)
    requirement = get_requirement(db, project_id, requirement_id, user_id)

    if requirement.status == RequirementStatus.CANCELLED:
        raise RequirementAlreadyCancelledError

    requirement.status = RequirementStatus.CANCELLED
    requirement.cancelled_at = datetime.now(timezone.utc).replace(tzinfo=None)
    requirement.cancel_reason = cancel_reason

    db.commit()
    return get_requirement(db, project_id, requirement_id, user_id)
