# -*- coding: utf-8 -*-
"""Create notifications table

Revision ID: 005_create_notifications
Revises: 004_create_practice_logs
Create Date: 2025-01-19
"""

from alembic import op
import sqlalchemy as sa


revision = "005_create_notifications"
down_revision = "004_create_practice_logs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("principals.id"), nullable=False, index=True),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("title", sa.Unicode(200)),
        sa.Column("message", sa.UnicodeText()),
        sa.Column("link", sa.Unicode(500)),
        sa.Column("related_type", sa.String(50)),
        sa.Column("related_id", sa.Integer()),
        sa.Column("is_read", sa.Boolean(), default=False),
        sa.Column("created", sa.DateTime(), server_default=sa.func.now(), index=True),
    )

    # Create index for user_id + is_read for faster unread queries
    op.create_index("ix_notifications_user_unread", "notifications", ["user_id", "is_read"])


def downgrade():
    op.drop_index("ix_notifications_user_unread", "notifications")
    op.drop_table("notifications")
