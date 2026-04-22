# -*- coding: utf-8 -*-
"""
Notification views for AI Community
"""

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from kotti.interfaces import IContent
from kotti.views.util import template_api

from kotti_ai_community.notification import get_unread_count
from kotti_ai_community.notification import get_notifications
from kotti_ai_community.notification import mark_as_read
from kotti_ai_community.notification import mark_all_as_read
from kotti_ai_community.notification import NOTIFICATION_TYPES
from kotti_ai_community.utils import safe_int


# ============================================================================
# Notification List View
# ============================================================================
@view_config(
    name="notifications",
    context=IContent,
    renderer="kotti_ai_community:templates/notifications.pt",
    permission="view",
)
def notification_list(context, request):
    """List user's notifications."""
    user = request.user
    if user is None:
        return HTTPFound(location=request.application_url + "/@@login")

    # Handle mark all as read
    if request.params.get("mark_all_read") == "1":
        mark_all_as_read(user.id)
        return HTTPFound(location=request.application_url + "/@@notifications")

    # Handle mark single as read
    read_id = safe_int(request.params.get("read"), 0)
    if read_id > 0:
        mark_as_read(read_id, user.id)
        return HTTPFound(location=request.application_url + "/@@notifications")

    # Get notifications
    notifications = get_notifications(user.id, limit=50)
    unread_count = get_unread_count(user.id)

    return {
        "api": template_api(context, request),
        "notifications": notifications,
        "unread_count": unread_count,
        "notification_types": NOTIFICATION_TYPES,
    }


# ============================================================================
# API Endpoints
# ============================================================================
@view_config(
    name="api-notifications",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_notifications(context, request):
    """API to get user notifications."""
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    notifications = get_notifications(user.id, limit=20)
    unread_count = get_unread_count(user.id)

    return {
        "success": True,
        "notifications": [
            {
                "id": n.id,
                "type": n.notification_type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "is_read": n.is_read,
                "created": n.created.isoformat() if n.created else None,
            }
            for n in notifications
        ],
        "unread_count": unread_count,
    }


@view_config(
    name="api-notification-count",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_notification_count(context, request):
    """API to get unread notification count."""
    user = request.user
    if user is None:
        return {"success": False, "count": 0}

    count = get_unread_count(user.id)

    return {
        "success": True,
        "count": count,
    }


@view_config(
    name="api-mark-notification-read",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_mark_notification_read(context, request):
    """API to mark a notification as read."""
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    notification_id = safe_int(request.params.get("id"), 0)
    if not notification_id:
        return {"success": False, "error": "Invalid notification ID"}

    success = mark_as_read(notification_id, user.id)

    return {
        "success": success,
        "unread_count": get_unread_count(user.id),
    }


@view_config(
    name="api-mark-all-read",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_mark_all_read(context, request):
    """API to mark all notifications as read."""
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    mark_all_as_read(user.id)

    return {
        "success": True,
        "unread_count": 0,
    }
