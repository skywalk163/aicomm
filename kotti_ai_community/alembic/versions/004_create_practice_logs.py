# -*- coding: utf-8 -*-
"""create practice_logs and milestones tables

Revision ID: 004
Revises: 003_create_projects
Create Date: 2024-01-01

"""

from alembic import op
import sqlalchemy as sa
from kotti.sqla import JsonType

# revision identifiers
revision = "004"
down_revision = "003_create_projects"


def upgrade():
    # Create practice_logs table
    op.create_table(
        "practice_logs",
        sa.Column("id", sa.Integer(), sa.ForeignKey("contents.id"), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("log_type", sa.String(50), default="progress"),
        sa.Column("log_date", sa.Integer(), default=0),
        sa.Column("content", sa.UnicodeText()),
        sa.Column("progress_change", sa.Integer(), default=0),
        sa.Column("new_progress", sa.Integer(), default=0),
        sa.Column("time_spent", sa.Integer(), default=0),
        sa.Column("tags", JsonType, default=list),
        sa.Column("attachments", JsonType, default=list),
        sa.Column("visibility", sa.String(50), default="public"),
        sa.Column("likes_count", sa.Integer(), default=0),
        sa.Column("comments_count", sa.Integer(), default=0),
    )

    # Create milestones table
    op.create_table(
        "milestones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("title", sa.Unicode(200), nullable=False),
        sa.Column("description", sa.UnicodeText()),
        sa.Column("target_date", sa.Integer(), default=0),
        sa.Column("completed_date", sa.Integer(), default=0),
        sa.Column("status", sa.String(50), default="planned"),
        sa.Column("progress", sa.Integer(), default=0),
        sa.Column("order_index", sa.Integer(), default=0),
        sa.Column("created_by", sa.Integer(), default=0),
        sa.Column("created_at", sa.Integer(), default=0),
    )


def downgrade():
    op.drop_table("practice_logs")
    op.drop_table("milestones")
