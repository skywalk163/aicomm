# -*- coding: utf-8 -*-
"""Add database indexes and constraints

Revision ID: 007_add_indexes_constraints
Revises: 006_create_content_flags
Create Date: 2025-01-19
"""

from alembic import op


revision = "007_add_indexes_constraints"
down_revision = "006_create_content_flags"
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes for frequently queried columns
    # Ideas
    op.create_index("ix_ideas_status", "ideas", ["status"])
    op.create_index("ix_ideas_category", "ideas", ["category"])
    op.create_index("ix_ideas_owner_id", "ideas", ["owner_id"])
    
    # Resources
    op.create_index("ix_resource_items_category", "resource_items", ["category"])
    op.create_index("ix_resource_items_access_type", "resource_items", ["access_type"])
    op.create_index("ix_resource_items_owner_id", "resource_items", ["owner_id"])
    
    # Projects
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_visibility", "projects", ["visibility"])
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    
    # Project Members
    op.create_index("ix_project_members_project_id", "project_members", ["project_id"])
    op.create_index("ix_project_members_user_id", "project_members", ["user_id"])
    
    # Practice Logs
    op.create_index("ix_practice_logs_project_id", "practice_logs", ["project_id"])
    op.create_index("ix_practice_logs_owner_id", "practice_logs", ["owner_id"])
    
    # Milestones
    op.create_index("ix_milestones_project_id", "milestones", ["project_id"])
    
    # User Profiles
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])


def downgrade():
    # Drop indexes
    op.drop_index("ix_ideas_status", "ideas")
    op.drop_index("ix_ideas_category", "ideas")
    op.drop_index("ix_ideas_owner_id", "ideas")
    
    op.drop_index("ix_resource_items_category", "resource_items")
    op.drop_index("ix_resource_items_access_type", "resource_items")
    op.drop_index("ix_resource_items_owner_id", "resource_items")
    
    op.drop_index("ix_projects_status", "projects")
    op.drop_index("ix_projects_visibility", "projects")
    op.drop_index("ix_projects_owner_id", "projects")
    
    op.drop_index("ix_project_members_project_id", "project_members")
    op.drop_index("ix_project_members_user_id", "project_members")
    
    op.drop_index("ix_practice_logs_project_id", "practice_logs")
    op.drop_index("ix_practice_logs_owner_id", "practice_logs")
    
    op.drop_index("ix_milestones_project_id", "milestones")
    
    op.drop_index("ix_user_profiles_user_id", "user_profiles")
