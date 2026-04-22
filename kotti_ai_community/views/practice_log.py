# -*- coding: utf-8 -*-
"""
Practice log views for AI Community
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
from kotti_ai_community.resources import PracticeLog
from kotti_ai_community.resources import Milestone
from kotti_ai_community.resources import LOG_TYPES
from kotti_ai_community.resources import LOG_VISIBILITY
from kotti_ai_community.resources import MILESTONE_STATUS
from kotti_ai_community.user_profile import get_profile
from kotti_ai_community.utils import safe_int, truncate_string, can_edit, is_admin


# ============================================================================
# Practice Log Views
# ============================================================================
@view_defaults(context=PracticeLog, permission="view")
class PracticeLogViews:
    """Practice log views."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name="view", renderer="kotti_ai_community:templates/practice_log_view.pt")
    def view(self):
        """Practice log detail view."""
        session = DBSession()

        # Get project
        project = session.query(Project).filter(
            Project.id == self.context.project_id
        ).first()

        return {
            "api": template_api(self.context, self.request),
            "project": project,
            "log_types": LOG_TYPES,
        }

    @view_config(name="edit", renderer="kotti_ai_community:templates/practice_log_edit.pt", permission="edit")
    def edit(self):
        """Edit practice log."""
        user = self.request.user
        session = DBSession()

        # Check permission
        if not user or (user.id != self.context.owner_id and "role:admin" not in user.groups):
            raise HTTPForbidden()

        if self.request.method == "POST":
            # Validate CSRF token
            if not validate_csrf_token(self.request):
                raise HTTPForbidden("Invalid CSRF token")

            self.context.title = truncate_string(self.request.params.get("title", ""), 200)
            self.context.content = self.request.params.get("content", "")
            self.context.log_type = self.request.params.get("log_type", "progress")
            self.context.visibility = self.request.params.get("visibility", "public")
            self.context.time_spent = safe_int(self.request.params.get("time_spent"), 0)

            # Parse tags (limit to 10 tags, each max 50 chars)
            tags_str = self.request.params.get("tags", "")
            self.context.tags = [t.strip()[:50] for t in tags_str.split(",") if t.strip()][:10]

            return HTTPFound(location=self.request.resource_url(self.context))

        return {
            "api": template_api(self.context, self.request),
            "log_types": LOG_TYPES,
            "log_visibility": LOG_VISIBILITY,
        }


# ============================================================================
# Project Logs View
# ============================================================================
@view_config(
    name="logs",
    context=Project,
    renderer="kotti_ai_community:templates/practice_log_list.pt",
    permission="view",
)
def project_logs(context, request):
    """List practice logs for a project."""
    session = DBSession()
    user = request.user

    # Check if user can view logs
    if context.visibility == "private":
        if not user:
            raise HTTPForbidden()
        if not context.is_member(user.id, session) and "role:admin" not in user.groups:
            raise HTTPForbidden()

    # Get logs
    log_type = request.params.get("log_type", "")
    query = session.query(PracticeLog).filter(
        PracticeLog.project_id == context.id
    )

    # Filter by visibility
    if user:
        if not context.is_member(user.id, session):
            query = query.filter(PracticeLog.visibility == "public")
    else:
        query = query.filter(PracticeLog.visibility == "public")

    if log_type:
        query = query.filter(PracticeLog.log_type == log_type)

    logs = query.order_by(PracticeLog.log_date.desc()).limit(50).all()

    # Get milestones
    milestones = context.get_milestones(session)

    return {
        "api": template_api(context, request),
        "logs": logs,
        "milestones": milestones,
        "log_types": LOG_TYPES,
        "log_type_filter": log_type,
    }


# ============================================================================
# Add Practice Log View
# ============================================================================
@view_config(
    name="add_log",
    context=Project,
    renderer="kotti_ai_community:templates/practice_log_add.pt",
    permission="edit",
)
def add_practice_log(context, request):
    """Add a practice log to a project."""
    user = request.user
    if not user:
        return HTTPFound(location=request.application_url + "/@@login")

    session = DBSession()

    # Check if user is a project member
    if not context.is_member(user.id, session):
        request.session.flash("You must be a project member to add logs.", "error")
        return HTTPFound(location=request.resource_url(context))

    if request.method == "POST":
        log = PracticeLog(
            title=request.params.get("title", ""),
            content=request.params.get("content", ""),
            project_id=context.id,
            log_type=request.params.get("log_type", "progress"),
            visibility=request.params.get("visibility", "public"),
            time_spent=int(request.params.get("time_spent", 0)),
        )

        # Parse tags
        tags_str = request.params.get("tags", "")
        log.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Set owner
        log.owner_id = user.id

        # Handle progress update
        progress_change = safe_int(request.params.get("progress_change"), 0)
        if progress_change != 0:
            log.progress_change = progress_change
            new_progress = min(100, max(0, context.progress + progress_change))
            log.new_progress = new_progress
            context.progress = new_progress

        session.add(log)
        session.flush()

        # Update user profile
        profile = get_profile(user.id)
        profile.add_points(5, "Added a practice log")

        request.session.flash("Practice log added!", "success")
        return HTTPFound(location=request.resource_url(context) + "/@@logs")

    return {
        "api": template_api(context, request),
        "log_types": LOG_TYPES,
        "log_visibility": LOG_VISIBILITY,
    }


# ============================================================================
# Milestone Views
# ============================================================================
@view_config(
    name="milestones",
    context=Project,
    renderer="kotti_ai_community:templates/milestone_list.pt",
    permission="view",
)
def project_milestones(context, request):
    """List milestones for a project."""
    session = DBSession()
    milestones = context.get_milestones(session)

    return {
        "api": template_api(context, request),
        "milestones": milestones,
        "milestone_status": MILESTONE_STATUS,
    }


@view_config(
    name="add_milestone",
    context=Project,
    renderer="kotti_ai_community:templates/milestone_add.pt",
    permission="edit",
)
def add_milestone(context, request):
    """Add a milestone to a project."""
    user = request.user
    if not user:
        return HTTPFound(location=request.application_url + "/@@login")

    session = DBSession()

    # Check if user is owner/admin
    role = context.get_member_role(user.id, session)
    if role not in ("owner", "admin") and "role:admin" not in user.groups:
        request.session.flash("Only project owners/admins can add milestones.", "error")
        return HTTPFound(location=request.resource_url(context) + "/@@milestones")

    if request.method == "POST":
        milestone = Milestone(
            project_id=context.id,
            title=truncate_string(request.params.get("title", ""), 200),
            description=request.params.get("description", ""),
            target_date=safe_int(request.params.get("target_date"), 0) if request.params.get("target_date") else 0,
            created_by=user.id,
        )

        session.add(milestone)
        request.session.flash("Milestone added!", "success")
        return HTTPFound(location=request.resource_url(context) + "/@@milestones")

    return {
        "api": template_api(context, request),
    }


# ============================================================================
# API Endpoints
# ============================================================================
@view_config(
    name="api-update-milestone",
    context=Project,
    renderer="json",
    permission="edit",
)
def api_update_milestone(context, request):
    """Update milestone status."""
    user = request.user
    if not user:
        return {"success": False, "error": "Not logged in"}

    session = DBSession()

    milestone_id = safe_int(request.params.get("milestone_id"), 0)
    new_status = request.params.get("status", "")

    if new_status not in MILESTONE_STATUS:
        return {"success": False, "error": "Invalid status"}

    milestone = (
        session.query(Milestone)
        .filter(Milestone.id == milestone_id)
        .filter(Milestone.project_id == context.id)
        .first()
    )

    if not milestone:
        return {"success": False, "error": "Milestone not found"}

    milestone.status = new_status

    if new_status == "completed":
        milestone.completed_date = int(time.time())
        milestone.progress = 100

    return {
        "success": True,
        "status": new_status,
        "status_display": milestone.get_status_display(),
    }


@view_config(
    name="api-project-timeline",
    context=Project,
    renderer="json",
    permission="view",
)
def api_project_timeline(context, request):
    """Get project timeline (logs + milestones)."""
    session = DBSession()

    # Get logs
    logs = (
        session.query(PracticeLog)
        .filter(PracticeLog.project_id == context.id)
        .order_by(PracticeLog.log_date.desc())
        .limit(20)
        .all()
    )

    # Get milestones
    milestones = context.get_milestones(session)

    return {
        "success": True,
        "logs": [
            {
                "id": log.id,
                "title": log.title,
                "type": log.log_type,
                "type_display": log.get_log_type_display(),
                "date": log.log_date,
                "progress_change": log.progress_change,
                "time_spent": log.time_spent,
            }
            for log in logs
        ],
        "milestones": [
            {
                "id": m.id,
                "title": m.title,
                "target_date": m.target_date,
                "status": m.status,
                "status_display": m.get_status_display(),
                "progress": m.progress,
            }
            for m in milestones
        ],
    }
