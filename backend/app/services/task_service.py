from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.requirement import Requirement, RequirementStatus
from app.models.task import Task, TaskSourceType, TaskStatus
from app.models.user import User
from app.schemas.task import (
    DecomposePayload,
    DecomposeTaskInput,
    TaskCreate,
    TaskResponse,
    TaskTreeNode,
    TaskUpdate,
)
from app.services import requirement_service, task_service
from app.services import requirement_service
from app.services.project_service import get_project_for_user


class TaskNotFoundError(Exception):
    pass


class TaskCycleError(Exception):
    pass


class ParentTaskNotFoundError(Exception):
    pass


class RequirementNotFoundError(Exception):
    pass


class AssigneeNotFoundError(Exception):
    pass


class TaskAlreadyCancelledError(Exception):
    pass


class RequirementNotLeafError(Exception):
    pass


def _to_decimal(value: Optional[float]) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


def _task_query(project_id: int):
    return (
        select(Task)
        .where(Task.project_id == project_id)
        .options(joinedload(Task.assignee))
        .order_by(Task.id.asc())
    )


def _collect_descendant_ids(db: Session, task_id: int) -> set[int]:
    descendants: set[int] = set()
    queue = [task_id]
    while queue:
        current_id = queue.pop()
        child_ids = db.scalars(select(Task.id).where(Task.parent_id == current_id)).all()
        for child_id in child_ids:
            if child_id not in descendants:
                descendants.add(child_id)
                queue.append(child_id)
    return descendants


def _validate_parent_id(
    db: Session,
    project_id: int,
    task_id: Optional[int],
    parent_id: Optional[int],
) -> None:
    if parent_id is None:
        return
    if task_id is not None and parent_id == task_id:
        raise TaskCycleError

    parent = db.scalar(
        select(Task).where(Task.id == parent_id, Task.project_id == project_id)
    )
    if parent is None:
        raise ParentTaskNotFoundError

    if task_id is not None:
        descendants = _collect_descendant_ids(db, task_id)
        if parent_id in descendants:
            raise TaskCycleError


def _validate_requirement_id(
    db: Session,
    project_id: int,
    requirement_id: Optional[int],
) -> None:
    if requirement_id is None:
        return
    requirement = db.scalar(
        select(Requirement).where(
            Requirement.id == requirement_id,
            Requirement.project_id == project_id,
        )
    )
    if requirement is None:
        raise RequirementNotFoundError


def _validate_assignee_id(db: Session, assignee_id: Optional[int]) -> None:
    if assignee_id is None:
        return
    if db.get(User, assignee_id) is None:
        raise AssigneeNotFoundError


def _resolve_requirement_id(
    db: Session,
    project_id: int,
    parent_id: Optional[int],
    explicit_requirement_id: Optional[int],
) -> Optional[int]:
    if explicit_requirement_id is not None:
        return explicit_requirement_id
    if parent_id is None:
        return None
    parent = db.scalar(
        select(Task).where(Task.id == parent_id, Task.project_id == project_id)
    )
    return parent.requirement_id if parent else None


def build_task_tree(tasks: list[Task]) -> list[TaskTreeNode]:
    nodes: dict[int, TaskTreeNode] = {}
    for item in tasks:
        base = TaskResponse.model_validate(item)
        nodes[item.id] = TaskTreeNode(**base.model_dump(), children=[])
    roots: list[TaskTreeNode] = []
    for item in tasks:
        node = nodes[item.id]
        if item.parent_id is None or item.parent_id not in nodes:
            roots.append(node)
        else:
            nodes[item.parent_id].children.append(node)
    return roots


def list_tasks(
    db: Session,
    project_id: int,
    user_id: int,
    *,
    tree: bool = False,
    requirement_id: Optional[int] = None,
    source_type: Optional[TaskSourceType] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> tuple[list[Task] | list[TaskTreeNode], int]:
    get_project_for_user(db, project_id, user_id)

    query = _task_query(project_id)
    if requirement_id is not None:
        query = query.where(Task.requirement_id == requirement_id)
    if source_type is not None:
        query = query.where(Task.source_type == source_type)

    all_items = list(db.scalars(query).unique().all())
    total = len(all_items)

    if tree:
        tree_roots = build_task_tree(all_items)
        if skip or limit is not None:
            sliced = tree_roots[skip : skip + limit if limit is not None else None]
            return sliced, total
        return tree_roots, total

    sliced = all_items[skip : skip + limit if limit is not None else None]
    return sliced, total


def get_task(db: Session, project_id: int, task_id: int, user_id: int) -> Task:
    get_project_for_user(db, project_id, user_id)
    task = db.scalar(_task_query(project_id).where(Task.id == task_id))
    if task is None:
        raise TaskNotFoundError
    return task


def create_task(
    db: Session,
    project_id: int,
    user_id: int,
    data: TaskCreate,
) -> Task:
    get_project_for_user(db, project_id, user_id)
    _validate_parent_id(db, project_id, None, data.parent_id)
    _validate_assignee_id(db, data.assignee_id)

    requirement_id = _resolve_requirement_id(
        db,
        project_id,
        data.parent_id,
        data.requirement_id,
    )
    _validate_requirement_id(db, project_id, requirement_id)

    if data.source_type == TaskSourceType.REQUIREMENT and requirement_id is None:
        raise RequirementNotFoundError

    task = Task(
        project_id=project_id,
        requirement_id=requirement_id,
        parent_id=data.parent_id,
        title=data.title,
        description=data.description,
        source_type=data.source_type,
        source_description=data.source_description,
        status=data.status,
        assignee_id=data.assignee_id,
        planned_hours=_to_decimal(data.planned_hours),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return get_task(db, project_id, task.id, user_id)


def update_task(
    db: Session,
    project_id: int,
    task_id: int,
    user_id: int,
    data: TaskUpdate,
) -> Task:
    get_project_for_user(db, project_id, user_id)
    task = get_task(db, project_id, task_id, user_id)

    payload = data.model_dump(exclude_unset=True)
    if "parent_id" in payload:
        _validate_parent_id(db, project_id, task_id, payload["parent_id"])
    if "assignee_id" in payload:
        _validate_assignee_id(db, payload["assignee_id"])
    if "planned_hours" in payload:
        payload["planned_hours"] = _to_decimal(payload["planned_hours"])

    for field, value in payload.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return get_task(db, project_id, task_id, user_id)


def _is_requirement_leaf(db: Session, project_id: int, requirement_id: int) -> bool:
    child_id = db.scalar(
        select(Requirement.id)
        .where(
            Requirement.project_id == project_id,
            Requirement.parent_id == requirement_id,
        )
        .limit(1)
    )
    return child_id is None


def _create_decompose_tasks(
    db: Session,
    project_id: int,
    requirement_id: int,
    items: list[DecomposeTaskInput],
    parent_id: Optional[int],
    created: list[Task],
) -> None:
    for item in items:
        task = Task(
            project_id=project_id,
            requirement_id=requirement_id,
            parent_id=parent_id,
            title=item.title,
            description=item.description,
            source_type=TaskSourceType.REQUIREMENT,
            status=TaskStatus.TODO,
            planned_hours=_to_decimal(item.planned_hours),
        )
        db.add(task)
        db.flush()
        created.append(task)
        if item.subtasks:
            _create_decompose_tasks(
                db,
                project_id,
                requirement_id,
                item.subtasks,
                task.id,
                created,
            )


def decompose_requirement(
    db: Session,
    project_id: int,
    requirement_id: int,
    user_id: int,
    data: DecomposePayload,
) -> list[Task]:
    requirement = requirement_service.get_requirement(
        db,
        project_id,
        requirement_id,
        user_id,
    )
    if requirement.status == RequirementStatus.CANCELLED:
        raise requirement_service.RequirementAlreadyCancelledError
    if not _is_requirement_leaf(db, project_id, requirement_id):
        raise RequirementNotLeafError

    created: list[Task] = []
    _create_decompose_tasks(
        db,
        project_id,
        requirement_id,
        data.tasks,
        None,
        created,
    )
    db.commit()

    if not created:
        return []

    created_ids = [task.id for task in created]
    id_order = {task_id: index for index, task_id in enumerate(created_ids)}
    tasks = list(
        db.scalars(_task_query(project_id).where(Task.id.in_(created_ids)))
        .unique()
        .all()
    )
    tasks.sort(key=lambda item: id_order[item.id])
    return tasks


def cancel_task(
    db: Session,
    project_id: int,
    task_id: int,
    user_id: int,
    cancel_reason: str,
) -> Task:
    get_project_for_user(db, project_id, user_id)
    task = get_task(db, project_id, task_id, user_id)

    if task.status == TaskStatus.CANCELLED:
        raise TaskAlreadyCancelledError

    task.status = TaskStatus.CANCELLED
    task.cancelled_at = datetime.now(timezone.utc).replace(tzinfo=None)
    task.cancel_reason = cancel_reason

    db.commit()
    return get_task(db, project_id, task_id, user_id)
