# -*- coding: utf-8 -*-
"""
Content moderation system for AI Community

Provides flagging/reporting functionality for content moderation.
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import func

from kotti import Base
from kotti import DBSession


# ============================================================================
# Flag Reasons
# ============================================================================
FLAG_REASONS = {
    "spam": "Spam or advertising",
    "inappropriate": "Inappropriate content",
    "harassment": "Harassment or bullying",
    "misinformation": "Misinformation",
    "copyright": "Copyright violation",
    "duplicate": "Duplicate content",
    "other": "Other",
}

FLAG_STATUS = {
    "pending": "Pending Review",
    "reviewed": "Reviewed",
    "resolved": "Resolved",
    "dismissed": "Dismissed",
}

FLAG_ACTIONS = {
    "none": "No action needed",
    "warning": "Warning issued",
    "content_removed": "Content removed",
    "user_banned": "User banned",
    "content_edited": "Content edited",
}


# ============================================================================
# ContentFlag Model
# ============================================================================
class ContentFlag(Base):
    """Content flag/report for moderation."""

    __tablename__ = "content_flags"

    #: Primary key
    id = Column(Integer, primary_key=True)

    #: Content type (idea, resource, project, etc.)
    content_type = Column(String(50), nullable=False)

    #: Content ID
    content_id = Column(Integer, nullable=False, index=True)

    #: User who flagged the content
    reporter_id = Column(Integer, ForeignKey("principals.id"), nullable=False, index=True)

    #: Reason for flagging
    reason = Column(String(50), nullable=False)

    #: Additional details
    details = Column(UnicodeText())

    #: Status
    status = Column(String(50), default="pending", index=True)

    #: Action taken
    action_taken = Column(String(50), default="none")

    #: Moderator notes
    moderator_notes = Column(UnicodeText())

    #: Moderator who handled the flag
    moderator_id = Column(Integer, ForeignKey("principals.id"))

    #: Creation timestamp
    created = Column(DateTime(), server_default=func.now(), index=True)

    #: Resolution timestamp
    resolved_at = Column(DateTime())

    def __init__(self, content_type, content_id, reporter_id, reason, **kwargs):
        self.content_type = content_type
        self.content_id = content_id
        self.reporter_id = reporter_id
        self.reason = reason
        self.details = kwargs.get("details", "")

    def get_reason_display(self):
        """Get display text for reason."""
        return FLAG_REASONS.get(self.reason, self.reason)

    def get_status_display(self):
        """Get display text for status."""
        return FLAG_STATUS.get(self.status, self.status)

    def get_action_display(self):
        """Get display text for action taken."""
        return FLAG_ACTIONS.get(self.action_taken, self.action_taken)


# ============================================================================
# Helper Functions
# ============================================================================
def create_flag(content_type, content_id, reporter_id, reason, **kwargs):
    """Create a new content flag.

    Args:
        content_type: Type of content (idea, resource, project)
        content_id: ID of the content
        reporter_id: User ID of the reporter
        reason: Reason for flagging

    Returns:
        ContentFlag instance
    """
    if reason not in FLAG_REASONS:
        return None

    session = DBSession()

    # Check if already flagged by this user
    existing = session.query(ContentFlag).filter(
        ContentFlag.content_type == content_type,
        ContentFlag.content_id == content_id,
        ContentFlag.reporter_id == reporter_id,
        ContentFlag.status == "pending",
    ).first()

    if existing:
        return None  # Already flagged

    flag = ContentFlag(
        content_type=content_type,
        content_id=content_id,
        reporter_id=reporter_id,
        reason=reason,
        details=kwargs.get("details", ""),
    )

    session.add(flag)
    session.flush()

    return flag


def get_pending_flags(limit=50):
    """Get all pending flags.

    Args:
        limit: Maximum number of flags to return

    Returns:
        List of ContentFlag instances
    """
    session = DBSession()
    return session.query(ContentFlag).filter(
        ContentFlag.status == "pending"
    ).order_by(ContentFlag.created.desc()).limit(limit).all()


def get_flags_for_content(content_type, content_id):
    """Get all flags for specific content.

    Args:
        content_type: Type of content
        content_id: ID of the content

    Returns:
        List of ContentFlag instances
    """
    session = DBSession()
    return session.query(ContentFlag).filter(
        ContentFlag.content_type == content_type,
        ContentFlag.content_id == content_id,
    ).order_by(ContentFlag.created.desc()).all()


def resolve_flag(flag_id, moderator_id, action, notes=""):
    """Resolve a content flag.

    Args:
        flag_id: ID of the flag
        moderator_id: User ID of the moderator
        action: Action taken
        notes: Moderator notes

    Returns:
        Updated ContentFlag instance or None
    """
    if action not in FLAG_ACTIONS:
        return None

    session = DBSession()
    from datetime import datetime

    flag = session.query(ContentFlag).filter(
        ContentFlag.id == flag_id
    ).first()

    if not flag:
        return None

    flag.status = "resolved"
    flag.action_taken = action
    flag.moderator_id = moderator_id
    flag.moderator_notes = notes
    flag.resolved_at = datetime.now()

    session.flush()

    return flag


def dismiss_flag(flag_id, moderator_id, notes=""):
    """Dismiss a content flag (no action needed).

    Args:
        flag_id: ID of the flag
        moderator_id: User ID of the moderator
        notes: Moderator notes

    Returns:
        Updated ContentFlag instance or None
    """
    session = DBSession()
    from datetime import datetime

    flag = session.query(ContentFlag).filter(
        ContentFlag.id == flag_id
    ).first()

    if not flag:
        return None

    flag.status = "dismissed"
    flag.action_taken = "none"
    flag.moderator_id = moderator_id
    flag.moderator_notes = notes
    flag.resolved_at = datetime.now()

    session.flush()

    return flag


def get_flag_stats():
    """Get flag statistics.

    Returns:
        Dict with counts by status
    """
    session = DBSession()

    stats = {
        "total": session.query(ContentFlag).count(),
        "pending": session.query(ContentFlag).filter(
            ContentFlag.status == "pending"
        ).count(),
        "resolved": session.query(ContentFlag).filter(
            ContentFlag.status == "resolved"
        ).count(),
        "dismissed": session.query(ContentFlag).filter(
            ContentFlag.status == "dismissed"
        ).count(),
    }

    # By reason
    by_reason = {}
    for reason in FLAG_REASONS:
        by_reason[reason] = session.query(ContentFlag).filter(
            ContentFlag.reason == reason
        ).count()
    stats["by_reason"] = by_reason

    return stats


def is_moderator(request):
    """Check if user is a moderator.

    Args:
        request: The current request

    Returns:
        True if user is moderator or admin
    """
    user = request.user
    if user is None:
        return False

    # Admin is always a moderator
    if "role:admin" in user.groups:
        return True

    # Check for moderator role
    if "role:moderator" in user.groups:
        return True

    return False
