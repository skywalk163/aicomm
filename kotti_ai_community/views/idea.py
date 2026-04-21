# -*- coding: utf-8 -*-
"""
Ideas views
"""

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.views.util import template_api

from kotti_ai_community.resources import Idea
from kotti_ai_community.resources import IDEA_CATEGORIES
from kotti_ai_community.resources import IDEA_STATUS
from kotti_ai_community.resources import DIFFICULTY_LEVELS
from kotti_ai_community.user_profile import get_profile
from kotti_ai_community.user_profile import update_stats
from kotti_ai_community.views.user import check_and_award_badges
from kotti_ai_community.utils import safe_int, truncate_string, can_edit, validate_csrf_token, Pagination


# ============================================================================
# Idea Views
# ============================================================================
@view_defaults(context=Idea, permission="view")
class IdeaViews:
    """Idea views"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name="view", renderer="kotti_ai_community:templates/idea_view.pt")
    def view(self):
        """Idea detail view"""
        self.context.views_count += 1
        return {
            "api": template_api(self.context, self.request),
            "can_edit": can_edit(self.context, self.request),
        }

    @view_config(name="edit", renderer="kotti_ai_community:templates/idea_edit.pt", permission="edit")
    def edit(self):
        """Idea edit view"""
        if not can_edit(self.context, self.request):
            raise HTTPForbidden()

        if self.request.method == "POST":
            # Update idea
            self.context.title = self.request.params.get("title", self.context.title)
            self.context.description = self.request.params.get("description", self.context.description)
            self.context.category = self.request.params.get("category", self.context.category)
            self.context.difficulty = self.request.params.get("difficulty", self.context.difficulty)
            self.context.status = self.request.params.get("status", self.context.status)
            self.context.needed_resources = self.request.params.get("needed_resources", "")
            self.context.expected_outcome = self.request.params.get("expected_outcome", "")

            # Parse tags
            tags_str = self.request.params.get("tags", "")
            self.context.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            return HTTPFound(location=self.request.resource_url(self.context))

        return {
            "api": template_api(self.context, self.request),
            "categories": IDEA_CATEGORIES,
            "statuses": IDEA_STATUS,
            "difficulties": DIFFICULTY_LEVELS,
        }


# ============================================================================
# Idea List View
# ============================================================================
@view_config(
    name="ideas",
    context=IContent,
    renderer="kotti_ai_community:templates/idea_list.pt",
    permission="view",
)
def idea_list(context, request):
    """Idea list view"""
    session = DBSession()

    category = request.params.get("category", "")
    status = request.params.get("status", "")
    difficulty = request.params.get("difficulty", "")
    search = request.params.get("search", "")

    query = session.query(Idea)

    if category:
        query = query.filter(Idea.category == category)
    if status:
        query = query.filter(Idea.status == status)
    if difficulty:
        query = query.filter(Idea.difficulty == difficulty)
    if search:
        query = query.filter(
            Idea.title.contains(search) | Idea.description.contains(search)
        )

    # Get total count for pagination
    total = query.count()

    # Pagination
    page = safe_int(request.params.get("page"), 1)
    per_page = 20
    pagination = Pagination(total, page, per_page)

    sort = request.params.get("sort", "created")
    if sort == "created":
        query = query.order_by(Idea.creation_date.desc())
    elif sort == "likes":
        query = query.order_by(Idea.likes_count.desc())
    elif sort == "views":
        query = query.order_by(Idea.views_count.desc())

    ideas = query.offset(pagination.offset).limit(pagination.per_page).all()

    return {
        "api": template_api(context, request),
        "ideas": ideas,
        "categories": IDEA_CATEGORIES,
        "statuses": IDEA_STATUS,
        "difficulties": DIFFICULTY_LEVELS,
        "filters": {
            "category": category,
            "status": status,
            "difficulty": difficulty,
            "search": search,
            "sort": sort,
        },
        "pagination": pagination,
    }


@view_config(
    name="add_idea",
    context=IContent,
    renderer="kotti_ai_community:templates/idea_add.pt",
    permission="edit",
)
def add_idea(context, request):
    """Add idea view"""
    user = request.user

    if request.method == "POST":
        # Validate CSRF token
        if not validate_csrf_token(request):
            from pyramid.httpexceptions import HTTPForbidden
            raise HTTPForbidden("Invalid CSRF token")
        
        # Create new idea
        idea = Idea(
            title=truncate_string(request.params.get("title", ""), 200),
            description=request.params.get("description", ""),
            category=request.params.get("category", "other"),
            difficulty=request.params.get("difficulty", "beginner"),
            status=request.params.get("status", "draft"),
            needed_resources=request.params.get("needed_resources", ""),
            expected_outcome=request.params.get("expected_outcome", ""),
        )

        # Parse tags
        tags_str = request.params.get("tags", "")
        idea.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Set owner
        if user:
            idea.owner_id = user.id

        session = DBSession()
        session.add(idea)
        session.flush()

        # Update user profile
        if user:
            profile = get_profile(user.id)
            profile.add_points(10, "Created an idea")
            update_stats(user.id)
            check_and_award_badges(user.id)

        return HTTPFound(location=request.resource_url(idea))

    return {
        "api": template_api(context, request),
        "categories": IDEA_CATEGORIES,
        "statuses": IDEA_STATUS,
        "difficulties": DIFFICULTY_LEVELS,
    }
