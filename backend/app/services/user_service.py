from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User, UserStatus
from app.schemas.user import UserCreate, UserPasswordUpdate, UserUpdate


class UsernameExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundError
    return user


def list_users(
    db: Session,
    *,
    status: Optional[UserStatus] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> tuple[list[User], int]:
    query = select(User)
    count_query = select(func.count()).select_from(User)

    if status is not None:
        query = query.where(User.status == status)
        count_query = count_query.where(User.status == status)

    query = query.order_by(User.id).offset(skip)
    if limit is not None:
        query = query.limit(limit)

    users = list(db.scalars(query).all())
    total = db.scalar(count_query) or 0
    return users, total


def create_user(db: Session, data: UserCreate) -> User:
    existing = db.scalar(select(User).where(User.username == data.username))
    if existing is not None:
        raise UsernameExistsError

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = get_user(db, user_id)
    user.display_name = data.display_name
    user.role = data.role
    user.status = data.status
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, user_id: int, data: UserPasswordUpdate) -> User:
    user = get_user(db, user_id)
    user.password_hash = hash_password(data.password)
    db.commit()
    db.refresh(user)
    return user
