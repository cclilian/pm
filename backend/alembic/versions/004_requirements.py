"""requirements table

Revision ID: 004
Revises: 003
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "requirements",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键 ID"),
        sa.Column("project_id", sa.Integer(), nullable=False, comment="所属项目 ID"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父需求 ID，为空表示顶层需求"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="需求标题"),
        sa.Column("description", sa.Text(), nullable=True, comment="需求描述"),
        sa.Column(
            "type",
            sa.Enum("core", "non_core", name="requirementtype"),
            nullable=False,
            comment="需求类型：core=核心业务, non_core=非核心业务",
        ),
        sa.Column(
            "priority",
            sa.Enum("low", "medium", "high", "urgent", name="requirementpriority"),
            nullable=True,
            comment="优先级：low/medium/high/urgent",
        ),
        sa.Column(
            "status",
            sa.Enum("draft", "active", "done", "cancelled", name="requirementstatus"),
            nullable=False,
            server_default="draft",
            comment="需求状态",
        ),
        sa.Column("owner_id", sa.Integer(), nullable=True, comment="负责人用户 ID"),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True, comment="取消时间"),
        sa.Column("cancel_reason", sa.Text(), nullable=True, comment="取消原因"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["requirements.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="项目需求表，支持 parent_id 多级树形结构",
    )
    op.create_index(op.f("ix_requirements_project_id"), "requirements", ["project_id"], unique=False)
    op.create_index(op.f("ix_requirements_parent_id"), "requirements", ["parent_id"], unique=False)
    op.create_index(op.f("ix_requirements_owner_id"), "requirements", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_requirements_owner_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_parent_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_project_id"), table_name="requirements")
    op.drop_table("requirements")
