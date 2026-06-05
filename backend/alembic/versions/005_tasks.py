"""tasks table

Revision ID: 005
Revises: 004
Create Date: 2026-06-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS=0")
    op.execute("DROP TABLE IF EXISTS tasks")
    op.execute("SET FOREIGN_KEY_CHECKS=1")

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键 ID"),
        sa.Column("project_id", sa.Integer(), nullable=False, comment="所属项目 ID"),
        sa.Column("requirement_id", sa.Integer(), nullable=True, comment="关联需求 ID，独立任务可为空"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父任务 ID，为空表示顶层任务"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="任务标题"),
        sa.Column("description", sa.Text(), nullable=True, comment="任务描述"),
        sa.Column(
            "source_type",
            sa.Enum("requirement", "internal", "external", "adhoc", name="tasksourcetype"),
            nullable=False,
            comment="任务来源：requirement=需求拆解, internal=项目内, external=项目外, adhoc=临时",
        ),
        sa.Column("source_description", sa.Text(), nullable=True, comment="来源说明，如项目外任务背景"),
        sa.Column(
            "status",
            sa.Enum("todo", "in_progress", "done", "cancelled", name="taskstatus"),
            nullable=False,
            server_default="todo",
            comment="任务状态：todo=待办, in_progress=进行中, done=已完成, cancelled=已取消",
        ),
        sa.Column("assignee_id", sa.Integer(), nullable=True, comment="执行人用户 ID"),
        sa.Column("planned_hours", sa.Numeric(precision=10, scale=2), nullable=True, comment="计划工时（小时）"),
        sa.Column("actual_hours", sa.Numeric(precision=10, scale=2), nullable=True, comment="实际工时（小时）"),
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
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["tasks.id"]),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        comment="项目任务表，支持 parent_id 多级树形结构",
    )
    op.create_index(op.f("ix_tasks_project_id"), "tasks", ["project_id"], unique=False)
    op.create_index(op.f("ix_tasks_requirement_id"), "tasks", ["requirement_id"], unique=False)
    op.create_index(op.f("ix_tasks_parent_id"), "tasks", ["parent_id"], unique=False)
    op.create_index(op.f("ix_tasks_assignee_id"), "tasks", ["assignee_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_assignee_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_parent_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_requirement_id"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_project_id"), table_name="tasks")
    op.drop_table("tasks")
