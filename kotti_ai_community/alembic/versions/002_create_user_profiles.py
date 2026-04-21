# -*- coding: utf-8 -*-
"""create user_profiles table

Revision ID: 002
Revises: 001_create_community_tables
Create Date: 2024-01-01

"""

from alembic import op
import sqlalchemy as sa
from kotti.sqla import JsonType

# revision identifiers
revision = "002"
down_revision = "001_create_community_tables"


def upgrade():
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("principals.id"), unique=True, nullable=False),
        sa.Column("display_name", sa.Unicode(100)),
        sa.Column("bio", sa.UnicodeText()),
        sa.Column("skills", JsonType, default=list),
        sa.Column("interests", JsonType, default=list),
        sa.Column("avatar_url", sa.Unicode(500)),
        sa.Column("social_links", JsonType, default=dict),
        sa.Column("location", sa.Unicode(100)),
        sa.Column("website", sa.Unicode(500)),
        sa.Column("points", sa.Integer(), default=0),
        sa.Column("badges", JsonType, default=list),
        sa.Column("ideas_count", sa.Integer(), default=0),
        sa.Column("resources_count", sa.Integer(), default=0),
        sa.Column("projects_count", sa.Integer(), default=0),
        sa.Column("last_activity", sa.DateTime()),
        sa.Column("created", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("user_profiles")
