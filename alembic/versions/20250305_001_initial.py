"""Initial schema: projects, tasks, task_status_history

Revision ID: 20250305_001
Revises:
Create Date: 2025-03-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20250305_001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_priority = sa.Enum("low", "medium", "high", "critical", name="task_priority")
task_status = sa.Enum("created", "in_progress", "review", "done", "cancelled", name="task_status")


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("idx_projects_owner_id"), "projects", ["owner_id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("priority", task_priority, nullable=False, server_default="medium"),
        sa.Column("status", task_status, nullable=False, server_default="created"),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("idx_tasks_assignee_id"), "tasks", ["assignee_id"], unique=False)
    op.create_index(op.f("idx_tasks_created_at"), "tasks", ["created_at"], unique=False)
    op.create_index(op.f("idx_tasks_priority"), "tasks", ["priority"], unique=False)
    op.create_index(op.f("idx_tasks_project_id"), "tasks", ["project_id"], unique=False)
    op.create_index(op.f("idx_tasks_project_status"), "tasks", ["project_id", "status"], unique=False)
    op.create_index(op.f("idx_tasks_status"), "tasks", ["status"], unique=False)

    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_members_project_id_user_id"),
    )
    op.create_index(op.f("idx_project_members_project_id"), "project_members", ["project_id"], unique=False)
    op.create_index(op.f("idx_project_members_user_id"), "project_members", ["user_id"], unique=False)

    op.create_table(
        "task_status_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("from_status", task_status, nullable=False),
        sa.Column("to_status", task_status, nullable=False),
        sa.Column("changed_by_id", sa.Integer(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("idx_task_status_history_task_id"), "task_status_history", ["task_id"], unique=False)
    op.create_index(
        op.f("idx_task_status_history_changed_at"),
        "task_status_history",
        ["task_id", "changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("idx_task_status_history_changed_at"), table_name="task_status_history")
    op.drop_index(op.f("idx_task_status_history_task_id"), table_name="task_status_history")
    op.drop_table("task_status_history")
    op.drop_index(op.f("idx_project_members_user_id"), table_name="project_members")
    op.drop_index(op.f("idx_project_members_project_id"), table_name="project_members")
    op.drop_table("project_members")
    op.drop_index(op.f("idx_tasks_status"), table_name="tasks")
    op.drop_index(op.f("idx_tasks_project_status"), table_name="tasks")
    op.drop_index(op.f("idx_tasks_project_id"), table_name="tasks")
    op.drop_index(op.f("idx_tasks_priority"), table_name="tasks")
    op.drop_index(op.f("idx_tasks_created_at"), table_name="tasks")
    op.drop_index(op.f("idx_tasks_assignee_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_index(op.f("idx_projects_owner_id"), table_name="projects")
    op.drop_table("projects")
