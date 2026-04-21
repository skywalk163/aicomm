# -*- coding: utf-8 -*-
"""Create content_flags table

Revision ID: 006_create_content_flags
Revises: 005_create_notifications
Create Date: 2025-01-19
"""

from alembic import op
import sqlalchemy as sa


revision = "006_create_content_flags"
down_revision = "005_create_notifications"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "content_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("content_id", sa.Integer(), nullable=False, index=True),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("principals.id"), nullable=False, index=True),
        sa.Column("reason", sa.String(50), nullable=False),
        sa.Column("details", sa.UnicodeText()),
        sa.Column("status", sa.String(50), default="pending", index=True),
        sa.Column("action_taken", sa.String(50), default="none"),
        sa.Column("moderator_notes", sa.UnicodeText()),
        sa.Column("moderator_id", sa.Integer(), sa.ForeignKey("principals.id")),
        sa.Column("created", sa.DateTime(), server_default=sa.func.now(), index=True),
        sa.Column("resolved_at", sa.DateTime()),
    )

    # Create index for content lookup
    op.create_index(
        "ix_content_flags_content",
        "content_flags",
        ["content_type", "content_id"]
    )

    # Create index for pending flags
    op.create_index(
        "ix_content_flags_pending",
        "content_flags",
        ["status", "created"]
    )


def downgrade():
    op.drop_index("ix_content_flags_pending", "content_flags")
    op.drop_index("ix_content_flags_content", "content_flags")
    op.drop_table("content_flags")
