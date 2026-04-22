# -*- coding: utf-8 -*-
"""
Project views for AI Community
"""

import time

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.security import get_principals
from kotti.views.util import template_api

from kotti_ai_community.resources import Project
from kotti_ai_community.resources import ProjectMember
from kotti_ai_community.resources import PROJECT_STATUS
from kotti_ai_community.resources import PROJECT_VISIBILITY
from kotti_ai_community.resources import MEMBER_ROLES
from kotti_ai_community.resources import Idea
from kotti_ai_community.user_profile import get_profile
from kotti_ai_community.user_profile import update_stats
from kotti_ai_community.views.user import check_and_award_badges
from kotti_ai_community.notification import create_notification
from kotti_ai_community.notification import notify_project_members
from kotti_ai_community.utils import safe_int, truncate_string, can_edit, is_admin, validate_csrf_token, Pagination


# ============================================================================
# Project Views
# ============================================================================
@view_defaults(context=Project, permission="view")
class ProjectViews:
    """Project views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name="view", renderer="kotti_ai_community:templates/project_view.pt")
    def view(self):
        """Project detail view."""
        self.context.views_count += 1
        session = DBSession()
        user = self.request.user

        # Get team members
        members = self.context.get_members(session)

        # Check user's role
        user_role = None
        is_member = False
        if user:
            is_member = self.context.is_member(user.id, session)
            user_role = self.context.get_member_role(user.id, session)

        return {
            "api": template_api(self.context, self.request),
            "members": members,
            "is_member": is_member,
            "user_role": user_role,
            "statuses": PROJECT_STATUS,
            "visibilities": PROJECT_VISIBILITY,
            "member_roles": MEMBER_ROLES,
        }

    @view_config(name="edit", renderer="kotti_ai_community:templates/project_edit.pt", permission="edit")
    def edit(self):
        """Project edit view."""
        session = DBSession()
        user = self.request.user

        # Check permission
        if user:
            role = self.context.get_member_role(user.id, session)
            if role not in ("owner", "admin") and "role:admin" not in user.groups:
                raise HTTPForbidden()
        else:
            raise HTTPForbidden()

        if self.request.method == "POST":
            # Validate CSRF token
            if not validate_csrf_token(self.request):
                raise HTTPForbidden("Invalid CSRF token")

            self.context.title = truncate_string(self.request.params.get("title", ""), 200)
            self.context.description = self.request.params.get("description", "")
            self.context.status = self.request.params.get("status", self.context.status)
            self.context.visibility = self.request.params.get("visibility", self.context.visibility)
            self.context.repo_url = self.request.params.get("repo_url", "")
            self.context.demo_url = self.request.params.get("demo_url", "")
            self.context.doc_url = self.request.params.get("doc_url", "")
            self.context.progress = safe_int(self.request.params.get("progress"), 0)
            self.context.results = self.request.params.get("results", "")
            self.context.lessons = self.request.params.get("lessons", "")

            # Parse tags (limit to 10 tags, each max 50 chars)
            tags_str = self.request.params.get("tags", "")
            self.context.tags = [t.strip()[:50] for t in tags_str.split(",") if t.strip()][:10]

            return HTTPFound(location=self.request.resource_url(self.context))

        return {
            "api": template_api(self.context, self.request),
            "statuses": PROJECT_STATUS,
            "visibilities": PROJECT_VISIBILITY,
        }


# ============================================================================
# Project List View
# ============================================================================
@view_config(
    name="projects",
    context=IContent,
    renderer="kotti_ai_community:templates/project_list.pt",
    permission="view",
)
def project_list(context, request):
    """Project list view."""
    session = DBSession()

    status = request.params.get("status", "")
    search = request.params.get("search", "")

    query = session.query(Project)

    # Only show public projects to non-members
    user = request.user
    if not user or "role:admin" not in user.groups:
        query = query.filter(Project.visibility == "public")

    if status:
        query = query.filter(Project.status == status)
    if search:
        query = query.filter(
            Project.title.contains(search) | Project.description.contains(search)
        )

    # Get total count for pagination
    total = query.count()

    # Pagination
    page = safe_int(request.params.get("page"), 1)
    per_page = 20
    pagination = Pagination(total, page, per_page)

    sort = request.params.get("sort", "created")
    if sort == "created":
        query = query.order_by(Project.creation_date.desc())
    elif sort == "members":
        query = query.order_by(Project.members_count.desc())
    elif sort == "stars":
        query = query.order_by(Project.stars_count.desc())
    elif sort == "progress":
        query = query.order_by(Project.progress.desc())

    projects = query.offset(pagination.offset).limit(pagination.per_page).all()

    return {
        "api": template_api(context, request),
        "projects": projects,
        "statuses": PROJECT_STATUS,
        "filters": {
            "status": status,
            "search": search,
            "sort": sort,
        },
        "pagination": pagination,
    }


# ============================================================================
# Create Project View
# ============================================================================
@view_config(
    name="add_project",
    context=IContent,
    renderer="kotti_ai_community:templates/project_add.pt",
    permission="edit",
)
def add_project(context, request):
    """Create a new project."""
    user = request.user
    if not user:
        return HTTPFound(location=request.application_url + "/@@login")

    session = DBSession()

    # Check if creating from an idea
    idea_id = safe_int(request.params.get("idea_id"), 0)
    idea = None
    if idea_id > 0:
        idea = session.query(Idea).filter(Idea.id == idea_id).first()

    if request.method == "POST":
        # Validate CSRF token
        if not validate_csrf_token(request):
            raise HTTPForbidden("Invalid CSRF token")
        
        project = Project(
            title=truncate_string(request.params.get("title", ""), 200),
            description=request.params.get("description", ""),
            status=request.params.get("status", "planning"),
            visibility=request.params.get("visibility", "public"),
            repo_url=request.params.get("repo_url", ""),
            demo_url=request.params.get("demo_url", ""),
        )

        # Parse tags
        tags_str = request.params.get("tags", "")
        project.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Link to idea
        if idea:
            project.idea_id = idea.id

        # Set owner
        project.owner_id = user.id

        session.add(project)
        session.flush()

        # Add creator as owner
        project.add_member(user.id, "owner", session)

        # Update user profile
        profile = get_profile(user.id)
        profile.add_points(20, "Created a project")
        update_stats(user.id)
        check_and_award_badges(user.id)

        return HTTPFound(location=request.resource_url(project))

    return {
        "api": template_api(context, request),
        "idea": idea,
        "statuses": PROJECT_STATUS,
        "visibilities": PROJECT_VISIBILITY,
    }


# ============================================================================
# Join Project View
# ============================================================================
@view_config(
    name="join",
    context=Project,
    permission="view",
)
def join_project(context, request):
    """Join a project."""
    user = request.user
    if not user:
        return HTTPFound(location=request.application_url + "/@@login")

    session = DBSession()

    # Check if already a member
    if context.is_member(user.id, session):
        request.session.flash("You are already a member of this project.", "info")
        return HTTPFound(location=request.resource_url(context))

    # Check if project is full
    if context.members_count >= context.max_members:
        request.session.flash("This project has reached its maximum member limit.", "error")
        return HTTPFound(location=request.resource_url(context))

    # Check visibility
    if context.visibility == "invite_only":
        request.session.flash("This project is invite-only.", "error")
        return HTTPFound(location=request.resource_url(context))

    # Add as member
    context.add_member(user.id, "member", session)

    # Notify project owner and admins
    from kotti.security import Principal
    owner = session.query(Principal).filter(Principal.id == context.owner_id).first()
    if owner:
        create_notification(
            context.owner_id,
            "project_member_joined",
            title="New Team Member",
            message=f"{user.title or user.name} joined your project '{context.title}'",
            link=request.resource_url(context),
            related_type="project",
            related_id=context.id,
        )

    # Update user profile
    profile = get_profile(user.id)
    profile.add_points(5, "Joined a project")
    update_stats(user.id)
    check_and_award_badges(user.id)

    request.session.flash("You have joined the project!", "success")
    return HTTPFound(location=request.resource_url(context))


# ============================================================================
# Leave Project View
# ============================================================================
@view_config(
    name="leave",
    context=Project,
    permission="view",
)
def leave_project(context, request):
    """Leave a project."""
    user = request.user
    if not user:
        return HTTPFound(location=request.application_url + "/@@login")

    session = DBSession()

    # Check if member
    role = context.get_member_role(user.id, session)
    if not role:
        request.session.flash("You are not a member of this project.", "error")
        return HTTPFound(location=request.resource_url(context))

    # Owner cannot leave
    if role == "owner":
        request.session.flash("Project owner cannot leave. Transfer ownership first.", "error")
        return HTTPFound(location=request.resource_url(context))

    # Remove member
    context.remove_member(user.id, session)

    request.session.flash("You have left the project.", "info")
    return HTTPFound(location=request.resource_url(context))


# ============================================================================
# API Endpoints
# ============================================================================
@view_config(
    name="api-project-members",
    context=Project,
    renderer="json",
    permission="view",
)
def api_project_members(context, request):
    """Get project members."""
    session = DBSession()
    from kotti.security import Principal

    members = (
        session.query(ProjectMember, Principal)
        .join(Principal, ProjectMember.user_id == Principal.id)
        .filter(ProjectMember.project_id == context.id)
        .filter(ProjectMember.is_active == 1)
        .all()
    )

    return {
        "success": True,
        "members": [
            {
                "user_id": m.user_id,
                "username": p.name,
                "display_name": p.title,
                "role": m.role,
                "role_display": m.get_role_display(),
                "joined_at": m.joined_at,
            }
            for m, p in members
        ],
    }


@view_config(
    name="api-update-member-role",
    context=Project,
    renderer="json",
    permission="edit",
)
def api_update_member_role(context, request):
    """Update a member's role."""
    user = request.user
    if not user:
        return {"success": False, "error": "Not logged in"}

    session = DBSession()

    # Check if user is owner/admin
    role = context.get_member_role(user.id, session)
    if role not in ("owner", "admin") and "role:admin" not in user.groups:
        return {"success": False, "error": "Permission denied"}

    target_user_id = safe_int(request.params.get("user_id"), 0)
    new_role = request.params.get("role", "member")

    if new_role not in MEMBER_ROLES:
        return {"success": False, "error": "Invalid role"}

    # Update role
    member = (
        session.query(ProjectMember)
        .filter(ProjectMember.project_id == context.id)
        .filter(ProjectMember.user_id == target_user_id)
        .filter(ProjectMember.is_active == 1)
        .first()
    )

    if not member:
        return {"success": False, "error": "Member not found"}

    member.role = new_role

    return {"success": True, "role": new_role}


@view_config(
    name="api-project-stats",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_project_stats(context, request):
    """Get project statistics."""
    session = DBSession()

    total = session.query(Project).count()
    by_status = {}
    for status in PROJECT_STATUS:
        count = session.query(Project).filter(Project.status == status).count()
        by_status[status] = count

    return {
        "success": True,
        "total": total,
        "by_status": by_status,
    }
