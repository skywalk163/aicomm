# -*- coding: utf-8 -*-
"""create projects and project_members tables

Revision ID: 003
Revises: 002_create_user_profiles
Create Date: 2024-01-01

"""

from alembic import op
import sqlalchemy as sa
from kotti.sqla import JsonType

# revision identifiers
revision = "003"
down_revision = "002_create_user_profiles"


def upgrade():
    # Create project_members table first (no foreign key to projects yet)
    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("principals.id"), nullable=False),
        sa.Column("role", sa.String(50), default="member"),
        sa.Column("joined_at", sa.Integer(), default=0),
        sa.Column("contribution_summary", sa.UnicodeText()),
        sa.Column("is_active", sa.Integer(), default=1),
    )

    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), sa.ForeignKey("contents.id"), primary_key=True),
        sa.Column("idea_id", sa.Integer(), sa.ForeignKey("ideas.id"), nullable=True),
        sa.Column("description", sa.UnicodeText()),
        sa.Column("status", sa.String(50), default="planning"),
        sa.Column("visibility", sa.String(50), default="public"),
        sa.Column("tags", JsonType, default=list),
        sa.Column("goals", JsonType, default=list),
        sa.Column("milestones", JsonType, default=list),
        sa.Column("required_roles", JsonType, default=list),
        sa.Column("repo_url", sa.Unicode(500)),
        sa.Column("demo_url", sa.Unicode(500)),
        sa.Column("doc_url", sa.Unicode(500)),
        sa.Column("start_date", sa.Integer(), default=0),
        sa.Column("end_date", sa.Integer(), default=0),
        sa.Column("actual_end_date", sa.Integer(), default=0),
        sa.Column("max_members", sa.Integer(), default=10),
        sa.Column("members_count", sa.Integer(), default=1),
        sa.Column("followers_count", sa.Integer(), default=0),
        sa.Column("stars_count", sa.Integer(), default=0),
        sa.Column("views_count", sa.Integer(), default=0),
        sa.Column("progress", sa.Integer(), default=0),
        sa.Column("results", sa.UnicodeText()),
        sa.Column("lessons", sa.UnicodeText()),
    )


def downgrade():
    op.drop_table("project_members")
    op.drop_table("projects")
