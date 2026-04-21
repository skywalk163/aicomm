# -*- coding: utf-8 -*-
"""
Notification system for AI Community

Provides in-app notifications for users.
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import func

from kotti import Base
from kotti import DBSession


# ============================================================================
# Notification Types
# ============================================================================
NOTIFICATION_TYPES = {
    "project_member_joined": {
        "title": "New Team Member",
        "icon": "users",
    },
    "project_update": {
        "title": "Project Update",
        "icon": "refresh",
    },
    "project_completed": {
        "title": "Project Completed",
        "icon": "check-circle",
    },
    "idea_liked": {
        "title": "Idea Liked",
        "icon": "heart",
    },
    "resource_downloaded": {
        "title": "Resource Downloaded",
        "icon": "download",
    },
    "badge_earned": {
        "title": "Badge Earned",
        "icon": "award",
    },
    "level_up": {
        "title": "Level Up!",
        "icon": "star",
    },
    "mention": {
        "title": "Mentioned",
        "icon": "at-sign",
    },
    "system": {
        "title": "System",
        "icon": "bell",
    },
}


# ============================================================================
# Notification Model
# ============================================================================
class Notification(Base):
    """User notification."""

    __tablename__ = "notifications"

    #: Primary key
    id = Column(Integer, primary_key=True)

    #: User who receives the notification
    user_id = Column(Integer, ForeignKey("principals.id"), nullable=False, index=True)

    #: Notification type
    notification_type = Column(String(50), nullable=False)

    #: Title
    title = Column(Unicode(200))

    #: Message content
    message = Column(UnicodeText())

    #: Link to related content (optional)
    link = Column(Unicode(500))

    #: Related object type (idea, project, etc.)
    related_type = Column(String(50))

    #: Related object ID
    related_id = Column(Integer)

    #: Whether notification has been read
    is_read = Column(Boolean, default=False)

    #: Creation timestamp
    created = Column(DateTime(), server_default=func.now(), index=True)

    def __init__(self, user_id, notification_type, **kwargs):
        self.user_id = user_id
        self.notification_type = notification_type
        self.title = kwargs.get("title", "")
        self.message = kwargs.get("message", "")
        self.link = kwargs.get("link", "")
        self.related_type = kwargs.get("related_type", "")
        self.related_id = kwargs.get("related_id")


# ============================================================================
# Helper Functions
# ============================================================================
def create_notification(user_id, notification_type, **kwargs):
    """Create a new notification for a user."""
    if notification_type not in NOTIFICATION_TYPES:
        return None

    type_info = NOTIFICATION_TYPES[notification_type]

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=kwargs.get("title", type_info["title"]),
        message=kwargs.get("message", ""),
        link=kwargs.get("link", ""),
        related_type=kwargs.get("related_type"),
        related_id=kwargs.get("related_id"),
    )

    session = DBSession()
    session.add(notification)
    session.flush()

    return notification


def get_unread_count(user_id):
    """Get count of unread notifications for a user."""
    session = DBSession()
    return session.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).count()


def get_notifications(user_id, limit=20, unread_only=False):
    """Get notifications for a user."""
    session = DBSession()
    query = session.query(Notification).filter(
        Notification.user_id == user_id
    )

    if unread_only:
        query = query.filter(Notification.is_read == False)

    query = query.order_by(Notification.created.desc())
    return query.limit(limit).all()


def mark_as_read(notification_id, user_id):
    """Mark a notification as read."""
    session = DBSession()
    notification = session.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

    if notification:
        notification.is_read = True
        return True
    return False


def mark_all_as_read(user_id):
    """Mark all notifications as read for a user."""
    session = DBSession()
    session.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    return True


def notify_project_members(project_id, notification_type, exclude_user_id=None, **kwargs):
    """Send notification to all project members."""
    from kotti_ai_community.resources import ProjectMember

    session = DBSession()
    members = session.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.is_active == True
    ).all()

    for member in members:
        if exclude_user_id and member.user_id == exclude_user_id:
            continue
        create_notification(member.user_id, notification_type, **kwargs)
