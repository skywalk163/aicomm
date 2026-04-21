# -*- coding: utf-8 -*-
"""创建 ideas 和 resource_items 表

Revision ID: 001
Revises: 
Create Date: 2026-04-17

"""

from alembic import op
import sqlalchemy as sa
from kotti.sqla import JsonType

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建 ideas 表
    op.create_table(
        "ideas",
        sa.Column("id", sa.Integer(), sa.ForeignKey("contents.id"), primary_key=True),
        sa.Column("category", sa.String(50), default="other"),
        sa.Column("difficulty", sa.String(50), default="beginner"),
        sa.Column("status", sa.String(50), default="draft"),
        sa.Column("tags", JsonType, default=list),
        sa.Column("description", sa.UnicodeText()),
        sa.Column("needed_resources", sa.UnicodeText()),
        sa.Column("expected_outcome", sa.UnicodeText()),
        sa.Column("estimated_days", sa.Integer, default=0),
        sa.Column("followers_count", sa.Integer, default=0),
        sa.Column("likes_count", sa.Integer, default=0),
        sa.Column("views_count", sa.Integer, default=0),
        sa.Column("ai_suggestions", sa.UnicodeText()),
    )

    # 创建 resource_items 表
    op.create_table(
        "resource_items",
        sa.Column("id", sa.Integer(), sa.ForeignKey("contents.id"), primary_key=True),
        sa.Column("category", sa.String(50), default="other"),
        sa.Column("access_type", sa.String(50), default="free"),
        sa.Column("tags", JsonType, default=list),
        sa.Column("description", sa.UnicodeText()),
        sa.Column("url", sa.Unicode(500)),
        sa.Column("usage_guide", sa.UnicodeText()),
        sa.Column("limitations", sa.UnicodeText()),
        sa.Column("availability", sa.String(50), default="available"),
        sa.Column("references_count", sa.Integer, default=0),
        sa.Column("likes_count", sa.Integer, default=0),
        sa.Column("views_count", sa.Integer, default=0),
    )


def downgrade():
    op.drop_table("resource_items")
    op.drop_table("ideas")
