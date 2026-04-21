# -*- coding: utf-8 -*-
"""
Content moderation views for AI Community
"""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.views.util import template_api
from kotti.security import Principal

from kotti_ai_community.moderation import (
    ContentFlag,
    FLAG_REASONS,
    FLAG_STATUS,
    FLAG_ACTIONS,
    create_flag,
    get_pending_flags,
    get_flags_for_content,
    resolve_flag,
    dismiss_flag,
    get_flag_stats,
    is_moderator,
)
from kotti_ai_community.utils import safe_int, validate_csrf_token


# ============================================================================
# Report Content View
# ============================================================================
@view_config(
    name="report",
    context=IContent,
    renderer="kotti_ai_community:templates/report_content.pt",
    permission="view",
)
def report_content(context, request):
    """Report/flag content for moderation."""
    user = request.user
    if user is None:
        return HTTPFound(location=request.application_url + "/@@login")

    # Determine content type and ID
    content_type = context.__class__.__name__.lower()
    content_id = context.id

    message = ""
    message_type = "info"

    if request.method == "POST":
        # Validate CSRF
        if not validate_csrf_token(request):
            raise HTTPForbidden("Invalid CSRF token")

        reason = request.params.get("reason", "")
        details = request.params.get("details", "")

        if reason not in FLAG_REASONS:
            message = "Invalid reason selected"
            message_type = "error"
        else:
            flag = create_flag(
                content_type=content_type,
                content_id=content_id,
                reporter_id=user.id,
                reason=reason,
                details=details,
            )

            if flag:
                message = "Content has been reported. Thank you for helping keep our community safe."
                message_type = "success"
            else:
                message = "You have already reported this content"
                message_type = "warning"

    # Check if already reported by this user
    session = DBSession()
    existing = session.query(ContentFlag).filter(
        ContentFlag.content_type == content_type,
        ContentFlag.content_id == content_id,
        ContentFlag.reporter_id == user.id,
        ContentFlag.status == "pending",
    ).first()

    return {
        "api": template_api(context, request),
        "content": context,
        "reasons": FLAG_REASONS,
        "message": message,
        "message_type": message_type,
        "already_reported": existing is not None,
    }


# ============================================================================
# Moderator Dashboard
# ============================================================================
@view_config(
    name="moderation",
    context=IContent,
    renderer="kotti_ai_community:templates/moderation_dashboard.pt",
    permission="admin",
)
def moderation_dashboard(context, request):
    """Moderator dashboard showing pending flags."""
    if not is_moderator(request):
        raise HTTPForbidden()

    session = DBSession()

    # Get pending flags with content info
    flags = get_pending_flags(limit=50)

    # Enrich with content and reporter info
    enriched_flags = []
    for flag in flags:
        # Get reporter
        reporter = session.query(Principal).filter(
            Principal.id == flag.reporter_id
        ).first()

        # Get content
        content = None
        if flag.content_type == "idea":
            from kotti_ai_community.resources import Idea
            content = session.query(Idea).filter(Idea.id == flag.content_id).first()
        elif flag.content_type == "resourceitem":
            from kotti_ai_community.resources import ResourceItem
            content = session.query(ResourceItem).filter(ResourceItem.id == flag.content_id).first()
        elif flag.content_type == "project":
            from kotti_ai_community.resources import Project
            content = session.query(Project).filter(Project.id == flag.content_id).first()

        enriched_flags.append({
            "flag": flag,
            "reporter": reporter,
            "content": content,
        })

    # Get stats
    stats = get_flag_stats()

    return {
        "api": template_api(context, request),
        "flags": enriched_flags,
        "stats": stats,
        "reasons": FLAG_REASONS,
        "statuses": FLAG_STATUS,
        "actions": FLAG_ACTIONS,
    }


# ============================================================================
# Resolve Flag View
# ============================================================================
@view_config(
    name="resolve-flag",
    context=IContent,
    permission="admin",
)
def resolve_flag_view(context, request):
    """Resolve a content flag."""
    if not is_moderator(request):
        raise HTTPForbidden()

    user = request.user
    if user is None:
        return HTTPFound(location=request.application_url + "/@@login")

    # Validate CSRF
    if not validate_csrf_token(request):
        raise HTTPForbidden("Invalid CSRF token")

    flag_id = safe_int(request.params.get("flag_id"), 0)
    action = request.params.get("action", "")
    notes = request.params.get("notes", "")

    if flag_id <= 0:
        request.session.flash("Invalid flag ID", "error")
        return HTTPFound(location=request.application_url + "/@@moderation")

    if action == "dismiss":
        result = dismiss_flag(flag_id, user.id, notes)
    else:
        result = resolve_flag(flag_id, user.id, action, notes)

    if result:
        request.session.flash("Flag has been resolved", "success")
    else:
        request.session.flash("Failed to resolve flag", "error")

    return HTTPFound(location=request.application_url + "/@@moderation")


# ============================================================================
# Flag History View
# ============================================================================
@view_config(
    name="flag-history",
    context=IContent,
    renderer="kotti_ai_community:templates/flag_history.pt",
    permission="admin",
)
def flag_history(context, request):
    """View flag history for specific content."""
    if not is_moderator(request):
        raise HTTPForbidden()

    content_type = context.__class__.__name__.lower()
    content_id = context.id

    flags = get_flags_for_content(content_type, content_id)

    # Enrich with reporter and moderator info
    session = DBSession()
    enriched_flags = []
    for flag in flags:
        reporter = session.query(Principal).filter(
            Principal.id == flag.reporter_id
        ).first()

        moderator = None
        if flag.moderator_id:
            moderator = session.query(Principal).filter(
                Principal.id == flag.moderator_id
            ).first()

        enriched_flags.append({
            "flag": flag,
            "reporter": reporter,
            "moderator": moderator,
        })

    return {
        "api": template_api(context, request),
        "content": context,
        "flags": enriched_flags,
        "reasons": FLAG_REASONS,
        "statuses": FLAG_STATUS,
        "actions": FLAG_ACTIONS,
    }


# ============================================================================
# API Endpoints
# ============================================================================
@view_config(
    name="api-report-content",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_report_content(context, request):
    """API to report content."""
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    if request.method != "POST":
        return {"success": False, "error": "POST method required"}

    # Validate CSRF
    if not validate_csrf_token(request):
        return {"success": False, "error": "Invalid CSRF token"}

    reason = request.params.get("reason", "")
    details = request.params.get("details", "")

    if reason not in FLAG_REASONS:
        return {"success": False, "error": "Invalid reason"}

    content_type = context.__class__.__name__.lower()
    content_id = context.id

    flag = create_flag(
        content_type=content_type,
        content_id=content_id,
        reporter_id=user.id,
        reason=reason,
        details=details,
    )

    if flag:
        return {"success": True, "flag_id": flag.id}
    else:
        return {"success": False, "error": "Already reported"}


@view_config(
    name="api-flag-stats",
    context=IContent,
    renderer="json",
    permission="admin",
)
def api_flag_stats(context, request):
    """API to get flag statistics."""
    if not is_moderator(request):
        return {"success": False, "error": "Permission denied"}

    stats = get_flag_stats()

    return {
        "success": True,
        "stats": stats,
    }


@view_config(
    name="api-resolve-flag",
    context=IContent,
    renderer="json",
    permission="admin",
)
def api_resolve_flag(context, request):
    """API to resolve a flag."""
    if not is_moderator(request):
        return {"success": False, "error": "Permission denied"}

    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    flag_id = safe_int(request.params.get("flag_id"), 0)
    action = request.params.get("action", "")
    notes = request.params.get("notes", "")

    if flag_id <= 0:
        return {"success": False, "error": "Invalid flag ID"}

    if action == "dismiss":
        result = dismiss_flag(flag_id, user.id, notes)
    else:
        result = resolve_flag(flag_id, user.id, action, notes)

    if result:
        return {"success": True}
    else:
        return {"success": False, "error": "Failed to resolve"}
