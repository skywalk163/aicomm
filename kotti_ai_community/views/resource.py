# -*- coding: utf-8 -*-
"""
Resources views
"""

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.views.util import template_api

from kotti_ai_community.resources import ResourceItem
from kotti_ai_community.resources import RESOURCE_CATEGORIES
from kotti_ai_community.resources import ACCESS_TYPES
from kotti_ai_community.user_profile import get_profile
from kotti_ai_community.user_profile import update_stats
from kotti_ai_community.views.user import check_and_award_badges
from kotti_ai_community.utils import safe_int, truncate_string, can_edit, validate_csrf_token, Pagination


# ============================================================================
# Resource Views
# ============================================================================
@view_defaults(context=ResourceItem, permission="view")
class ResourceItemViews:
    """Resource views"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(
        name="view", renderer="kotti_ai_community:templates/resource_view.pt"
    )
    def view(self):
        """Resource detail view"""
        self.context.views_count += 1
        return {
            "api": template_api(self.context, self.request),
            "can_edit": can_edit(self.context, self.request),
        }

    @view_config(
        name="edit", renderer="kotti_ai_community:templates/resource_edit.pt", permission="edit"
    )
    def edit(self):
        """Resource edit view"""
        if not can_edit(self.context, self.request):
            raise HTTPForbidden()

        if self.request.method == "POST":
            # Update resource
            self.context.title = self.request.params.get("title", self.context.title)
            self.context.description = self.request.params.get("description", self.context.description)
            self.context.category = self.request.params.get("category", self.context.category)
            self.context.access_type = self.request.params.get("access_type", self.context.access_type)
            self.context.url = self.request.params.get("url", self.context.url)
            self.context.usage_guide = self.request.params.get("usage_guide", "")
            self.context.limitations = self.request.params.get("limitations", "")

            # Parse tags
            tags_str = self.request.params.get("tags", "")
            self.context.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

            return HTTPFound(location=self.request.resource_url(self.context))

        return {
            "api": template_api(self.context, self.request),
            "categories": RESOURCE_CATEGORIES,
            "access_types": ACCESS_TYPES,
        }


# ============================================================================
# Resource List View
# ============================================================================
@view_config(
    name="resources",
    context=IContent,
    renderer="kotti_ai_community:templates/resource_list.pt",
    permission="view",
)
def resource_list(context, request):
    """Resource list view"""
    session = DBSession()

    category = request.params.get("category", "")
    access_type = request.params.get("access_type", "")
    search = request.params.get("search", "")

    query = session.query(ResourceItem)

    if category:
        query = query.filter(ResourceItem.category == category)
    if access_type:
        query = query.filter(ResourceItem.access_type == access_type)
    if search:
        query = query.filter(
            ResourceItem.title.contains(search)
            | ResourceItem.description.contains(search)
        )

    # Get total count for pagination
    total = query.count()

    # Pagination
    page = safe_int(request.params.get("page"), 1)
    per_page = 20
    pagination = Pagination(total, page, per_page)

    sort = request.params.get("sort", "created")
    if sort == "created":
        query = query.order_by(ResourceItem.creation_date.desc())
    elif sort == "likes":
        query = query.order_by(ResourceItem.likes_count.desc())
    elif sort == "views":
        query = query.order_by(ResourceItem.views_count.desc())
    elif sort == "references":
        query = query.order_by(ResourceItem.references_count.desc())

    resources = query.offset(pagination.offset).limit(pagination.per_page).all()

    return {
        "api": template_api(context, request),
        "resources": resources,
        "categories": RESOURCE_CATEGORIES,
        "access_types": ACCESS_TYPES,
        "filters": {
            "category": category,
            "access_type": access_type,
            "search": search,
            "sort": sort,
        },
        "pagination": pagination,
    }


@view_config(
    name="add_resource_item",
    context=IContent,
    renderer="kotti_ai_community:templates/resource_add.pt",
    permission="edit",
)
def add_resource_item(context, request):
    """Add resource view"""
    user = request.user

    if request.method == "POST":
        # Validate CSRF token
        if not validate_csrf_token(request):
            raise HTTPForbidden("Invalid CSRF token")
        
        # Create new resource
        resource = ResourceItem(
            title=truncate_string(request.params.get("title", ""), 200),
            description=request.params.get("description", ""),
            category=request.params.get("category", "other"),
            access_type=request.params.get("access_type", "free"),
            url=request.params.get("url", ""),
            usage_guide=request.params.get("usage_guide", ""),
            limitations=request.params.get("limitations", ""),
        )

        # Parse tags
        tags_str = request.params.get("tags", "")
        resource.tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        # Set owner
        if user:
            resource.owner_id = user.id

        session = DBSession()
        session.add(resource)
        session.flush()

        # Update user profile
        if user:
            profile = get_profile(user.id)
            profile.add_points(15, "Shared a resource")
            update_stats(user.id)
            check_and_award_badges(user.id)

        return HTTPFound(location=request.resource_url(resource))

    return {
        "api": template_api(context, request),
        "categories": RESOURCE_CATEGORIES,
        "access_types": ACCESS_TYPES,
    }
