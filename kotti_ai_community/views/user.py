# -*- coding: utf-8 -*-
"""
User profile views for AI Community
"""

from datetime import datetime

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.security import get_principals
from kotti.views.util import template_api

from kotti_ai_community.user_profile import UserProfile
from kotti_ai_community.user_profile import get_profile
from kotti_ai_community.user_profile import get_profile_by_name
from kotti_ai_community.user_profile import update_stats
from kotti_ai_community.user_profile import SKILL_CATEGORIES
from kotti_ai_community.resources import Idea
from kotti_ai_community.resources import ResourceItem
from kotti_ai_community.utils import safe_url, sanitize_social_link, safe_int, is_admin


# ============================================================================
# User Profile View
# ============================================================================
@view_config(
    name="profile",
    context=IContent,
    renderer="kotti_ai_community:templates/user_profile.pt",
    permission="view",
)
def user_profile(context, request):
    """User profile page.

    Access via /@@profile?username=xxx or /@@profile (current user)
    """
    username = request.params.get("username")

    if username:
        # View other user's profile
        principals = get_principals()
        try:
            principal = principals[username]
        except KeyError:
            raise HTTPNotFound()
        profile = get_profile(principal.id)
        is_owner = False
    else:
        # View own profile
        user = request.user
        if user is None:
            # Redirect to login
            return HTTPFound(location=request.application_url + "/@@login")

        principal = user
        profile = get_profile(user.id)
        is_owner = True

    session = DBSession()

    # Get user's ideas
    ideas = session.query(Idea).filter(
        Idea.owner_id == principal.id
    ).order_by(Idea.creation_date.desc()).limit(10).all()

    # Get user's resources
    resources = session.query(ResourceItem).filter(
        ResourceItem.owner_id == principal.id
    ).order_by(ResourceItem.creation_date.desc()).limit(10).all()

    # Sanitize URLs for security
    safe_website = safe_url(profile.website) if profile.website else ''
    safe_avatar_url = safe_url(profile.avatar_url) if profile.avatar_url else ''
    
    # Sanitize social links
    social_links = profile.social_links or {}
    safe_social_links = {
        'github': sanitize_social_link('github', social_links.get('github', '')),
        'twitter': sanitize_social_link('twitter', social_links.get('twitter', '')),
        'linkedin': sanitize_social_link('linkedin', social_links.get('linkedin', '')),
        'wechat': social_links.get('wechat', ''),  # WeChat ID is not a URL
    }

    return {
        "api": template_api(context, request),
        "principal": principal,
        "profile": profile,
        "ideas": ideas,
        "resources": resources,
        "is_owner": is_owner,
        "skill_categories": SKILL_CATEGORIES,
        "safe_website": safe_website,
        "safe_avatar_url": safe_avatar_url,
        "safe_social_links": safe_social_links,
    }


# ============================================================================
# Edit Profile View
# ============================================================================
@view_config(
    name="edit-profile",
    context=IContent,
    renderer="kotti_ai_community:templates/user_profile_edit.pt",
    permission="edit",
)
def edit_profile(context, request):
    """Edit user profile page."""
    user = request.user
    if user is None:
        return HTTPFound(location=request.application_url + "/@@login")

    profile = get_profile(user.id)
    message = ""
    message_type = "info"

    if request.method == "POST":
        # Update profile
        profile.display_name = request.params.get("display_name", "")
        profile.bio = request.params.get("bio", "")
        profile.location = request.params.get("location", "")
        profile.website = request.params.get("website", "")
        profile.avatar_url = request.params.get("avatar_url", "")

        # Parse skills (comma-separated)
        skills_str = request.params.get("skills", "")
        profile.skills = [s.strip() for s in skills_str.split(",") if s.strip()]

        # Parse interests (comma-separated)
        interests_str = request.params.get("interests", "")
        profile.interests = [i.strip() for i in interests_str.split(",") if i.strip()]

        # Parse social links
        profile.social_links = {
            "github": request.params.get("github", ""),
            "twitter": request.params.get("twitter", ""),
            "linkedin": request.params.get("linkedin", ""),
            "wechat": request.params.get("wechat", ""),
        }

        # Update principal title if display_name is set
        if profile.display_name:
            user.title = profile.display_name

        message = "Profile updated successfully!"
        message_type = "success"

    return {
        "api": template_api(context, request),
        "profile": profile,
        "message": message,
        "message_type": message_type,
        "skill_categories": SKILL_CATEGORIES,
    }


# ============================================================================
# User List View
# ============================================================================
@view_config(
    name="members",
    context=IContent,
    renderer="kotti_ai_community:templates/user_list.pt",
    permission="view",
)
def user_list(context, request):
    """List all community members."""
    session = DBSession()

    # Get all users with profiles
    search = request.params.get("search", "")
    skill_filter = request.params.get("skill", "")

    query = session.query(UserProfile).join(
        UserProfile.user_id
    )

    # We need to join with principals to get user info
    from kotti.security import Principal
    query = session.query(UserProfile, Principal).join(
        Principal, UserProfile.user_id == Principal.id
    ).filter(Principal.active == True)

    if search:
        query = query.filter(
            (Principal.name.contains(search)) |
            (Principal.title.contains(search)) |
            (UserProfile.bio.contains(search))
        )

    if skill_filter:
        # JSON search for skills
        query = query.filter(UserProfile.skills.contains(skill_filter))

    # Order by points
    query = query.order_by(UserProfile.points.desc())

    results = query.limit(50).all()

    members = []
    for profile, principal in results:
        members.append({
            "profile": profile,
            "principal": principal,
        })

    return {
        "api": template_api(context, request),
        "members": members,
        "search": search,
        "skill_filter": skill_filter,
        "skill_categories": SKILL_CATEGORIES,
    }


# ============================================================================
# API Endpoints
# ============================================================================
@view_config(
    name="api-add-points",
    context=IContent,
    renderer="json",
    permission="admin",  # Restricted to admin only
)
def api_add_points(context, request):
    """API to add points to a user. Admin only.
    
    This API is restricted to administrators to prevent gaming the points system.
    """
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    # Double-check admin permission
    if not is_admin(request):
        return {"success": False, "error": "Permission denied"}

    target_user_id = safe_int(request.params.get("user_id"), 0)
    if target_user_id == 0:
        target_user_id = user.id
    
    points = safe_int(request.params.get("points"), 0)
    reason = request.params.get("reason", "")

    if points <= 0:
        return {"success": False, "error": "Points must be positive"}

    profile = get_profile(target_user_id)
    profile.add_points(points, reason)

    return {
        "success": True,
        "points": profile.points,
        "level": profile.level,
        "level_name": profile.level_name,
    }


@view_config(
    name="api-user-stats",
    context=IContent,
    renderer="json",
    permission="view",
)
def api_user_stats(context, request):
    """API to get user statistics."""
    username = request.params.get("username")

    if username:
        principals = get_principals()
        try:
            principal = principals[username]
        except KeyError:
            return {"success": False, "error": "User not found"}
    else:
        principal = request.user
        if principal is None:
            return {"success": False, "error": "Not logged in"}

    profile = get_profile(principal.id)

    return {
        "success": True,
        "username": principal.name,
        "points": profile.points,
        "level": profile.level,
        "level_name": profile.level_name,
        "ideas_count": profile.ideas_count,
        "resources_count": profile.resources_count,
        "badges": profile.badges or [],
    }


# ============================================================================
# Leaderboard View
# ============================================================================
@view_config(
    name="leaderboard",
    context=IContent,
    renderer="kotti_ai_community:templates/leaderboard.pt",
    permission="view",
)
def leaderboard(context, request):
    """Leaderboard showing top users by points."""
    session = DBSession()
    from kotti.security import Principal

    # Get time period filter
    period = request.params.get("period", "all")

    # Base query - join UserProfile with Principal
    query = session.query(UserProfile, Principal).join(
        Principal, UserProfile.user_id == Principal.id
    ).filter(Principal.active == True)

    # Filter by time period
    if period == "week":
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        query = query.filter(UserProfile.last_activity >= week_ago)
    elif period == "month":
        from datetime import datetime, timedelta
        month_ago = datetime.now() - timedelta(days=30)
        query = query.filter(UserProfile.last_activity >= month_ago)

    # Order by points
    query = query.order_by(UserProfile.points.desc())

    # Get top 50 users
    results = query.limit(50).all()

    leaderboard_data = []
    for rank, (profile, principal) in enumerate(results, 1):
        leaderboard_data.append({
            "rank": rank,
            "profile": profile,
            "principal": principal,
        })

    # Get current user's rank if logged in
    user_rank = None
    user = request.user
    if user:
        profile = get_profile(user.id)
        # Count users with more points
        user_rank = session.query(UserProfile).filter(
            UserProfile.points > profile.points
        ).count() + 1

    return {
        "api": template_api(context, request),
        "leaderboard": leaderboard_data,
        "period": period,
        "user_rank": user_rank,
    }


# ============================================================================
# Badge Definitions and Awarding
# ============================================================================
BADGE_DEFINITIONS = {
    # Activity badges
    "first_idea": {"name": "Idea Generator", "description": "Created your first idea", "points": 5, "icon": "lightbulb"},
    "idea_master": {"name": "Idea Master", "description": "Created 10 ideas", "points": 20, "icon": "lightbulb"},
    "first_resource": {"name": "Resource Sharer", "description": "Shared your first resource", "points": 5, "icon": "folder"},
    "resource_master": {"name": "Resource Master", "description": "Shared 10 resources", "points": 20, "icon": "folder"},
    "first_project": {"name": "Project Starter", "description": "Created your first project", "points": 10, "icon": "rocket"},
    "project_leader": {"name": "Project Leader", "description": "Created 5 projects", "points": 30, "icon": "rocket"},
    "team_player": {"name": "Team Player", "description": "Joined 3 projects", "points": 15, "icon": "users"},

    # Level badges
    "level_5": {"name": "Innovator", "description": "Reached level 5", "points": 0, "icon": "star"},
    "level_10": {"name": "Visionary", "description": "Reached level 10", "points": 0, "icon": "crown"},

    # Engagement badges
    "popular_idea": {"name": "Popular Idea", "description": "Idea received 10+ likes", "points": 15, "icon": "heart"},
    "helpful": {"name": "Helpful", "description": "Resource downloaded 50+ times", "points": 20, "icon": "download"},
    "collaborator": {"name": "Collaborator", "description": "Participated in a completed project", "points": 25, "icon": "check-circle"},
}


def check_and_award_badges(user_id):
    """Check and award badges based on user activity."""
    session = DBSession()
    profile = get_profile(user_id)

    awarded = []

    # Check idea badges
    from kotti_ai_community.resources import Idea, ResourceItem, Project, ProjectMember

    ideas_count = session.query(Idea).filter(Idea.owner_id == user_id).count()
    resources_count = session.query(ResourceItem).filter(ResourceItem.owner_id == user_id).count()
    projects_created = session.query(Project).filter(Project.owner_id == user_id).count()
    projects_joined = session.query(ProjectMember).filter(
        ProjectMember.user_id == user_id,
        ProjectMember.is_active == True
    ).count()

    # First idea
    if ideas_count >= 1 and not has_badge(profile, "first_idea"):
        award_badge(profile, "first_idea")
        awarded.append("first_idea")

    # Idea master
    if ideas_count >= 10 and not has_badge(profile, "idea_master"):
        award_badge(profile, "idea_master")
        awarded.append("idea_master")

    # First resource
    if resources_count >= 1 and not has_badge(profile, "first_resource"):
        award_badge(profile, "first_resource")
        awarded.append("first_resource")

    # Resource master
    if resources_count >= 10 and not has_badge(profile, "resource_master"):
        award_badge(profile, "resource_master")
        awarded.append("resource_master")

    # First project
    if projects_created >= 1 and not has_badge(profile, "first_project"):
        award_badge(profile, "first_project")
        awarded.append("first_project")

    # Project leader
    if projects_created >= 5 and not has_badge(profile, "project_leader"):
        award_badge(profile, "project_leader")
        awarded.append("project_leader")

    # Team player
    if projects_joined >= 3 and not has_badge(profile, "team_player"):
        award_badge(profile, "team_player")
        awarded.append("team_player")

    # Level badges
    if profile.level >= 5 and not has_badge(profile, "level_5"):
        award_badge(profile, "level_5")
        awarded.append("level_5")

    if profile.level >= 10 and not has_badge(profile, "level_10"):
        award_badge(profile, "level_10")
        awarded.append("level_10")

    return awarded


def has_badge(profile, badge_id):
    """Check if user has a specific badge."""
    if not profile.badges:
        return False
    return any(b.get("id") == badge_id for b in profile.badges)


def award_badge(profile, badge_id):
    """Award a badge to user."""
    from datetime import datetime

    badge_def = BADGE_DEFINITIONS.get(badge_id)
    if not badge_def:
        return False

    if not profile.badges:
        profile.badges = []

    profile.badges.append({
        "id": badge_id,
        "name": badge_def["name"],
        "description": badge_def["description"],
        "icon": badge_def["icon"],
        "earned_at": datetime.now().isoformat(),
    })

    # Add bonus points if any
    if badge_def["points"] > 0:
        profile.add_points(badge_def["points"], f"Earned badge: {badge_def['name']}")

    # Create notification for badge earned
    from kotti_ai_community.notification import create_notification
    create_notification(
        profile.user_id,
        "badge_earned",
        title="Badge Earned!",
        message=f"You earned the '{badge_def['name']}' badge: {badge_def['description']}",
    )

    return True


@view_config(
    name="api-check-badges",
    context=IContent,
    renderer="json",
    permission="edit",
)
def api_check_badges(context, request):
    """API to check and award badges for current user."""
    user = request.user
    if user is None:
        return {"success": False, "error": "Not logged in"}

    awarded = check_and_award_badges(user.id)
    profile = get_profile(user.id)

    return {
        "success": True,
        "awarded": awarded,
        "badges": profile.badges or [],
        "points": profile.points,
    }
