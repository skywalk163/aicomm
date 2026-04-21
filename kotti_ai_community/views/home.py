# -*- coding: utf-8 -*-
"""
Home page view
"""

from pyramid.view import view_config

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.views.util import template_api

from kotti_ai_community.resources import Idea
from kotti_ai_community.resources import ResourceItem
from kotti_ai_community.resources import Project


@view_config(
    name="home",
    context=IContent,
    renderer="kotti_ai_community:templates/home.pt",
    permission="view",
)
def home(context, request):
    """Home page view"""
    session = DBSession()

    # Get latest ideas
    latest_ideas = (
        session.query(Idea)
        .filter(Idea.status != "draft")
        .order_by(Idea.creation_date.desc())
        .limit(5)
        .all()
    )

    # Get latest resources
    latest_resources = (
        session.query(ResourceItem)
        .order_by(ResourceItem.creation_date.desc())
        .limit(5)
        .all()
    )

    # Get latest projects
    latest_projects = (
        session.query(Project)
        .filter(Project.visibility == "public")
        .order_by(Project.creation_date.desc())
        .limit(5)
        .all()
    )

    # Stats
    total_ideas = session.query(Idea).count()
    total_resources = session.query(ResourceItem).count()
    total_projects = session.query(Project).count()

    return {
        "api": template_api(context, request),
        "latest_ideas": latest_ideas,
        "latest_resources": latest_resources,
        "latest_projects": latest_projects,
        "stats": {
            "total_ideas": total_ideas,
            "total_resources": total_resources,
            "total_projects": total_projects,
        },
    }
