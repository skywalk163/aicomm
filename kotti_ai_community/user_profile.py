# -*- coding: utf-8 -*-
"""
User profile extension for AI Community

Extends Kotti's Principal with additional profile fields.
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import func

from kotti import Base
from kotti import DBSession
from kotti.sqla import JsonType


# ============================================================================
# User Profile Constants
# ============================================================================

USER_ROLES = {
    "member": "Community Member",
    "contributor": "Contributor",
    "moderator": "Moderator",
}

SKILL_CATEGORIES = {
    "ml": "Machine Learning",
    "nlp": "Natural Language Processing",
    "cv": "Computer Vision",
    "data": "Data Science",
    "engineering": "Engineering",
    "design": "Design",
    "business": "Business",
    "research": "Research",
    "other": "Other",
}


# ============================================================================
# UserProfile - Extended user information
# ============================================================================
class UserProfile(Base):
    """Extended user profile information.

    Links to Kotti's Principal via user_id.
    """

    __tablename__ = "user_profiles"

    #: Primary key
    id = Column(Integer, primary_key=True)

    #: Link to Principal.id
    user_id = Column(Integer, ForeignKey("principals.id"), unique=True, nullable=False)

    #: Display name (can be different from login name)
    display_name = Column(Unicode(100))

    #: Bio/description
    bio = Column(UnicodeText())

    #: Skills/tags (JSON array)
    skills = Column(JsonType, default=list)

    #: Interests (JSON array)
    interests = Column(JsonType, default=list)

    #: Avatar URL
    avatar_url = Column(Unicode(500))

    #: Social links (JSON object: {"github": "...", "twitter": "..."})
    social_links = Column(JsonType, default=dict)

    #: Location
    location = Column(Unicode(100))

    #: Website
    website = Column(Unicode(500))

    #: Points for gamification
    points = Column(Integer, default=0)

    #: Badges earned (JSON array)
    badges = Column(JsonType, default=list)

    #: Ideas created count (cached)
    ideas_count = Column(Integer, default=0)

    #: Resources shared count (cached)
    resources_count = Column(Integer, default=0)

    #: Projects joined count (cached)
    projects_count = Column(Integer, default=0)

    #: Last activity timestamp
    last_activity = Column(DateTime())

    #: Creation timestamp
    created = Column(DateTime(), server_default=func.now())

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        self.display_name = kwargs.get("display_name", "")
        self.bio = kwargs.get("bio", "")
        self.skills = kwargs.get("skills", [])
        self.interests = kwargs.get("interests", [])
        self.avatar_url = kwargs.get("avatar_url", "")
        self.social_links = kwargs.get("social_links", {})
        self.location = kwargs.get("location", "")
        self.website = kwargs.get("website", "")
        self.points = kwargs.get("points", 0)
        self.badges = kwargs.get("badges", [])

    @property
    def level(self):
        """Calculate user level based on points."""
        if self.points < 100:
            return 1
        elif self.points < 300:
            return 2
        elif self.points < 600:
            return 3
        elif self.points < 1000:
            return 4
        elif self.points < 2000:
            return 5
        else:
            return min(10, 5 + (self.points - 2000) // 1000)

    @property
    def level_name(self):
        """Get level name."""
        level_names = {
            1: "Newcomer",
            2: "Explorer",
            3: "Contributor",
            4: "Creator",
            5: "Innovator",
            6: "Expert",
            7: "Master",
            8: "Guru",
            9: "Legend",
            10: "Visionary",
        }
        return level_names.get(self.level, "Unknown")

    def add_points(self, points, reason=""):
        """Add points to user profile."""
        self.points += points
        from datetime import datetime
        self.last_activity = datetime.now()

    def add_badge(self, badge_id, badge_name):
        """Add a badge to user profile."""
        from datetime import datetime
        if not self.badges:
            self.badges = []
        if badge_id not in [b.get("id") for b in self.badges]:
            self.badges.append({
                "id": badge_id,
                "name": badge_name,
                "earned_at": datetime.now().isoformat(),
            })


# ============================================================================
# Helper functions
# ============================================================================

def get_profile(user_id):
    """Get or create user profile by user_id."""
    session = DBSession()
    profile = session.query(UserProfile).filter(
        UserProfile.user_id == user_id
    ).first()

    if profile is None:
        profile = UserProfile(user_id=user_id)
        session.add(profile)
        session.flush()

    return profile


def get_profile_by_name(username):
    """Get user profile by username."""
    from kotti.security import get_principals

    principals = get_principals()
    try:
        principal = principals[username]
        return get_profile(principal.id)
    except KeyError:
        return None


def update_stats(user_id):
    """Update cached statistics for a user."""
    session = DBSession()
    profile = get_profile(user_id)

    from kotti_ai_community.resources import Idea, ResourceItem

    # Count ideas
    profile.ideas_count = session.query(Idea).filter(
        Idea.owner_id == user_id
    ).count()

    # Count resources
    profile.resources_count = session.query(ResourceItem).filter(
        ResourceItem.owner_id == user_id
    ).count()

    from datetime import datetime
    profile.last_activity = datetime.now()
