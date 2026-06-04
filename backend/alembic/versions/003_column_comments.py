"""add column and table comments

Revision ID: 003
Revises: 002
Create Date: 2026-06-03

"""
from typing import Sequence, Union

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS=0")

    op.execute("ALTER TABLE users COMMENT = '系统用户表'")
    op.execute(
        "ALTER TABLE users MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN username VARCHAR(64) NOT NULL "
        "COMMENT '登录用户名，唯一'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL "
        "COMMENT '密码哈希值'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN display_name VARCHAR(128) NOT NULL "
        "COMMENT '显示名称'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN role ENUM('pm','dev','test') NOT NULL "
        "COMMENT '用户角色：pm=项目经理, dev=开发, test=测试'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN status ENUM('active','inactive') NOT NULL "
        "COMMENT '账号状态：active=启用, inactive=停用'"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN created_at DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'"
    )

    op.execute("ALTER TABLE projects COMMENT = '项目表'")
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID'"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN name VARCHAR(128) NOT NULL COMMENT '项目名称'"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN description TEXT NULL COMMENT '项目描述'"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN owner_id INT NOT NULL COMMENT '项目负责人用户 ID'"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN status ENUM('active','archived') NOT NULL "
        "COMMENT '项目状态：active=进行中, archived=已归档'"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN created_at DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'"
    )

    op.execute("ALTER TABLE project_members COMMENT = '项目成员关联表'")
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT '主键 ID'"
    )
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN project_id INT NOT NULL COMMENT '项目 ID'"
    )
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN user_id INT NOT NULL COMMENT '用户 ID'"
    )
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN role ENUM('owner','member') NOT NULL "
        "COMMENT '成员角色：owner=负责人, member=普通成员'"
    )

    op.execute("SET FOREIGN_KEY_CHECKS=1")


def downgrade() -> None:
    op.execute("SET FOREIGN_KEY_CHECKS=0")

    op.execute("ALTER TABLE users COMMENT = ''")
    op.execute("ALTER TABLE users MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT ''")
    op.execute("ALTER TABLE users MODIFY COLUMN username VARCHAR(64) NOT NULL COMMENT ''")
    op.execute("ALTER TABLE users MODIFY COLUMN password_hash VARCHAR(255) NOT NULL COMMENT ''")
    op.execute("ALTER TABLE users MODIFY COLUMN display_name VARCHAR(128) NOT NULL COMMENT ''")
    op.execute("ALTER TABLE users MODIFY COLUMN role ENUM('pm','dev','test') NOT NULL COMMENT ''")
    op.execute(
        "ALTER TABLE users MODIFY COLUMN status ENUM('active','inactive') NOT NULL COMMENT ''"
    )
    op.execute(
        "ALTER TABLE users MODIFY COLUMN created_at DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP COMMENT ''"
    )

    op.execute("ALTER TABLE projects COMMENT = ''")
    op.execute("ALTER TABLE projects MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT ''")
    op.execute("ALTER TABLE projects MODIFY COLUMN name VARCHAR(128) NOT NULL COMMENT ''")
    op.execute("ALTER TABLE projects MODIFY COLUMN description TEXT NULL COMMENT ''")
    op.execute("ALTER TABLE projects MODIFY COLUMN owner_id INT NOT NULL COMMENT ''")
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN status ENUM('active','archived') NOT NULL COMMENT ''"
    )
    op.execute(
        "ALTER TABLE projects MODIFY COLUMN created_at DATETIME NOT NULL "
        "DEFAULT CURRENT_TIMESTAMP COMMENT ''"
    )

    op.execute("ALTER TABLE project_members COMMENT = ''")
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT COMMENT ''"
    )
    op.execute("ALTER TABLE project_members MODIFY COLUMN project_id INT NOT NULL COMMENT ''")
    op.execute("ALTER TABLE project_members MODIFY COLUMN user_id INT NOT NULL COMMENT ''")
    op.execute(
        "ALTER TABLE project_members MODIFY COLUMN role ENUM('owner','member') NOT NULL COMMENT ''"
    )

    op.execute("SET FOREIGN_KEY_CHECKS=1")
