from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserStatus
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserPasswordUpdate,
    UserResponse,
    UserUpdate,
)
from app.services import user_service
from app.services.user_service import UserNotFoundError, UsernameExistsError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users(
    status_filter: Optional[UserStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    users, total = user_service.list_users(
        db,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return UserListResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return user_service.create_user(db, data)
    except UsernameExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return user_service.get_user(db, user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return user_service.update_user(db, user_id, data)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


@router.patch("/{user_id}/password", response_model=UserResponse)
def update_user_password(
    user_id: int,
    data: UserPasswordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return user_service.update_user_password(db, user_id, data)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
