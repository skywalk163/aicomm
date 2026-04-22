# -*- coding: utf-8 -*-
"""Full-text search view for ideas, resources, and projects."""

import math
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy import or_
from sqlalchemy.sql import func

from kotti import DBSession
from kotti_ai_community.resources import Idea, ResourceItem, Project
from kotti_ai_community.utils import Pagination, safe_int


@view_config(name="search", renderer="kotti_ai_community:templates/search.pt")
def search_view(context, request):
    """Full-text search across ideas, resources, and projects."""
    query = request.params.get("q", "").strip()
    content_type = request.params.get("type", "all")  # all, ideas, resources, projects
    page = safe_int(request.params.get("page", 1), 1)
    per_page = 20
    
    results = []
    total_count = 0
    pagination = None
    
    if query and len(query) >= 2:
        # Build search pattern
        search_pattern = f"%{query}%"
        
        # Search Ideas
        if content_type in ("all", "ideas"):
            ideas = (
                DBSession.query(Idea)
                .filter(Idea.title.ilike(search_pattern))
                .filter(or_(
                    Idea.description.ilike(search_pattern),
                    Idea.title.ilike(search_pattern),
                ))
                .order_by(Idea.creation_date.desc())
                .all()
            )
            for idea in ideas:
                results.append({
                    "type": "idea",
                    "item": idea,
                    "title": idea.title,
                    "description": idea.description or "",
                    "tags": idea.tags or [],
                    "url": request.resource_url(idea),
                    "created": idea.creation_date,
                })
        
        # Search Resources
        if content_type in ("all", "resources"):
            resources = (
                DBSession.query(ResourceItem)
                .filter(or_(
                    ResourceItem.title.ilike(search_pattern),
                    ResourceItem.description.ilike(search_pattern),
                ))
                .order_by(ResourceItem.creation_date.desc())
                .all()
            )
            for resource in resources:
                results.append({
                    "type": "resource",
                    "item": resource,
                    "title": resource.title,
                    "description": resource.description or "",
                    "tags": resource.tags or [],
                    "url": request.resource_url(resource),
                    "created": resource.creation_date,
                })
        
        # Search Projects
        if content_type in ("all", "projects"):
            projects = (
                DBSession.query(Project)
                .filter(Project.visibility == "public")
                .filter(or_(
                    Project.title.ilike(search_pattern),
                    Project.description.ilike(search_pattern),
                ))
                .order_by(Project.creation_date.desc())
                .all()
            )
            for project in projects:
                results.append({
                    "type": "project",
                    "item": project,
                    "title": project.title,
                    "description": project.description or "",
                    "tags": project.tags or [],
                    "url": request.resource_url(project),
                    "created": project.creation_date,
                })
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.get("created", 0) or 0, reverse=True)
        
        # Paginate results
        total_count = len(results)
        start = (page - 1) * per_page
        end = start + per_page
        results = results[start:end]
        
        # Create pagination
        pagination = Pagination(total=total_count, page=page, per_page=per_page)
    
    return {
        "query": query,
        "content_type": content_type,
        "results": results,
        "total_count": total_count,
        "pagination": pagination,
    }


@view_config(name="search_api", renderer="json")
def search_api(context, request):
    """JSON API for search (for autocomplete/suggestions)."""
    query = request.params.get("q", "").strip()
    limit = safe_int(request.params.get("limit", 10), 10)
    
    if not query or len(query) < 2:
        return {"results": []}
    
    search_pattern = f"%{query}%"
    results = []
    
    # Search Ideas
    ideas = (
        DBSession.query(Idea)
        .filter(or_(
            Idea.title.ilike(search_pattern),
            Idea.description.ilike(search_pattern),
        ))
        .limit(limit)
        .all()
    )
    for idea in ideas:
        results.append({
            "type": "idea",
            "title": idea.title,
            "url": request.resource_url(idea),
        })
    
    # Search Resources
    resources = (
        DBSession.query(ResourceItem)
        .filter(or_(
            ResourceItem.title.ilike(search_pattern),
            ResourceItem.description.ilike(search_pattern),
        ))
        .limit(limit)
        .all()
    )
    for resource in resources:
        results.append({
            "type": "resource",
            "title": resource.title,
            "url": request.resource_url(resource),
        })
    
    # Search Projects
    projects = (
        DBSession.query(Project)
        .filter(Project.visibility == "public")
        .filter(or_(
            Project.title.ilike(search_pattern),
            Project.description.ilike(search_pattern),
        ))
        .limit(limit)
        .all()
    )
    for project in projects:
        results.append({
            "type": "project",
            "title": project.title,
            "url": request.resource_url(project),
        })
    
    return {"results": results[:limit]}
