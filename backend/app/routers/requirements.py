from __future__ import annotations

from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.requirement import RequirementType
from app.models.user import User
from app.schemas.requirement import (
    RequirementCancel,
    RequirementCreate,
    RequirementListResponse,
    RequirementResponse,
    RequirementTreeListResponse,
    RequirementUpdate,
)
from app.schemas.task import DecomposePayload, TaskResponse
from app.services import requirement_service, task_service
from app.services.project_service import ProjectForbiddenError, ProjectNotFoundError
from app.services.requirement_service import (
    OwnerNotFoundError,
    ParentNotFoundError,
    RequirementAlreadyCancelledError,
    RequirementCycleError,
    RequirementNotFoundError,
)
from app.services.task_service import RequirementNotLeafError

router = APIRouter(prefix="/projects/{project_id}/requirements", tags=["requirements"])


@router.get("", response_model=Union[RequirementListResponse, RequirementTreeListResponse])
def list_requirements(
    project_id: int,
    tree: bool = Query(False),
    type: Optional[RequirementType] = Query(None, alias="type"),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        items, total = requirement_service.list_requirements(
            db,
            project_id,
            current_user.id,
            tree=tree,
            req_type=type,
            skip=skip,
            limit=limit,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )

    if tree:
        return RequirementTreeListResponse(items=items, total=total, skip=skip, limit=limit)
    return RequirementListResponse(items=items, total=total, skip=skip, limit=limit)


@router.post("", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
def create_requirement(
    project_id: int,
    data: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return requirement_service.create_requirement(
            db,
            project_id,
            current_user.id,
            data,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )
    except ParentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent requirement not found",
        )
    except RequirementCycleError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent_id: cycle detected",
        )
    except OwnerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found",
        )


@router.get("/{requirement_id}", response_model=RequirementResponse)
def get_requirement(
    project_id: int,
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return requirement_service.get_requirement(
            db,
            project_id,
            requirement_id,
            current_user.id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )
    except RequirementNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found",
        )


@router.put("/{requirement_id}", response_model=RequirementResponse)
def update_requirement(
    project_id: int,
    requirement_id: int,
    data: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return requirement_service.update_requirement(
            db,
            project_id,
            requirement_id,
            current_user.id,
            data,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )
    except RequirementNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found",
        )
    except ParentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent requirement not found",
        )
    except RequirementCycleError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parent_id: cycle detected",
        )
    except OwnerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found",
        )


@router.patch("/{requirement_id}/cancel", response_model=RequirementResponse)
def cancel_requirement(
    project_id: int,
    requirement_id: int,
    data: RequirementCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return requirement_service.cancel_requirement(
            db,
            project_id,
            requirement_id,
            current_user.id,
            data.cancel_reason,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )
    except RequirementNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found",
        )
    except RequirementAlreadyCancelledError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement already cancelled",
        )


@router.post(
    "/{requirement_id}/decompose",
    response_model=List[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
def decompose_requirement(
    project_id: int,
    requirement_id: int,
    data: DecomposePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.decompose_requirement(
            db,
            project_id,
            requirement_id,
            current_user.id,
            data,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    except ProjectForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this project",
        )
    except RequirementNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found",
        )
    except RequirementAlreadyCancelledError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement already cancelled",
        )
    except RequirementNotLeafError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement is not a leaf node",
        )
