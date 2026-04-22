# -*- coding: utf-8 -*-
"""
Home page view
"""

from sqlalchemy import func

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

    # Use subqueries for efficient counting (single query instead of 3)
    stats_subquery = session.query(
        func.count(Idea.id).label('ideas'),
    ).subquery()
    
    stats = session.query(
        func.count(Idea.id).label('total_ideas'),
        func.count(ResourceItem.id).label('total_resources'),
        func.count(Project.id).label('total_projects'),
    ).one()
    
    # Or use a more efficient approach with separate count queries
    # that can be cached later
    from sqlalchemy import literal_column
    
    # Get counts in a single round-trip using UNION ALL
    counts = session.execute("""
        SELECT 'ideas' as type, COUNT(*) as count FROM ideas
        UNION ALL
        SELECT 'resources', COUNT(*) FROM resource_items
        UNION ALL
        SELECT 'projects', COUNT(*) FROM projects
    """).fetchall()
    
    stats_dict = {row[0]: row[1] for row in counts}

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

    return {
        "api": template_api(context, request),
        "latest_ideas": latest_ideas,
        "latest_resources": latest_resources,
        "latest_projects": latest_projects,
        "stats": {
            "total_ideas": stats_dict.get('ideas', 0),
            "total_resources": stats_dict.get('resources', 0),
            "total_projects": stats_dict.get('projects', 0),
        },
    }
