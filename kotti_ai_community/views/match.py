# -*- coding: utf-8 -*-
"""
Tag matching and search functionality
"""

from pyramid.view import view_config
from pyramid.response import Response

from kotti import DBSession
from kotti.interfaces import IContent
from kotti.views.util import template_api

from kotti_ai_community.resources import Idea
from kotti_ai_community.resources import ResourceItem


@view_config(
    name="api/match/by-tags",
    context=IContent,
    renderer="json",
    permission="view",
    request_method="POST",
)
def api_match_by_tags(context, request):
    """API: 根据标签匹配点子和资源"""
    try:
        data = request.json_body
        tags = data.get("tags", [])
        content_type = data.get("type", "idea")  # idea 或 resource
        
        session = DBSession()
        results = []
        
        if content_type == "idea":
            # 查找匹配的点子
            ideas = session.query(Idea).filter(Idea.status != "draft").all()
            for idea in ideas:
                if idea.tags:
                    # 计算标签重叠度
                    common_tags = set(tags) & set(idea.tags)
                    if common_tags:
                        match_score = len(common_tags) / max(len(tags), len(idea.tags)) * 100
                        results.append({
                            "id": idea.id,
                            "title": idea.title,
                            "description": idea.description[:200] if idea.description else "",
                            "tags": idea.tags,
                            "category": idea.category,
                            "status": idea.status,
                            "match_score": round(match_score, 1),
                            "common_tags": list(common_tags),
                            "url": f"/idea/{idea.id}",
                        })
            
            # 按匹配度排序
            results.sort(key=lambda x: x["match_score"], reverse=True)
            
        else:
            # 查找匹配的资源
            resources = session.query(ResourceItem).all()
            for resource in resources:
                if resource.tags:
                    common_tags = set(tags) & set(resource.tags)
                    if common_tags:
                        match_score = len(common_tags) / max(len(tags), len(resource.tags)) * 100
                        results.append({
                            "id": resource.id,
                            "title": resource.title,
                            "description": resource.description[:200] if resource.description else "",
                            "tags": resource.tags,
                            "category": resource.category,
                            "access_type": resource.access_type,
                            "match_score": round(match_score, 1),
                            "common_tags": list(common_tags),
                            "url": f"/resource/{resource.id}",
                        })
            
            results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "success": True,
            "results": results[:20],  # 返回前 20 个结果
            "total": len(results),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@view_config(
    name="api/search",
    context=IContent,
    renderer="json",
    permission="view",
    request_method="GET",
)
def api_search(context, request):
    """API: 全局搜索"""
    try:
        query = request.params.get("q", "").strip()
        content_type = request.params.get("type", "all")  # all, idea, resource
        
        if not query:
            return {"success": False, "error": "搜索关键词不能为空"}
        
        session = DBSession()
        results = {"ideas": [], "resources": []}
        
        # 搜索点子
        if content_type in ["all", "idea"]:
            ideas = (
                session.query(Idea)
                .filter(
                    (Idea.title.contains(query) | Idea.description.contains(query))
                    & (Idea.status != "draft")
                )
                .limit(10)
                .all()
            )
            for idea in ideas:
                results["ideas"].append({
                    "id": idea.id,
                    "title": idea.title,
                    "description": idea.description[:150] if idea.description else "",
                    "category": idea.category,
                    "status": idea.status,
                    "url": f"/idea/{idea.id}",
                })
        
        # 搜索资源
        if content_type in ["all", "resource"]:
            resources = (
                session.query(ResourceItem)
                .filter(
                    ResourceItem.title.contains(query)
                    | ResourceItem.description.contains(query)
                )
                .limit(10)
                .all()
            )
            for resource in resources:
                results["resources"].append({
                    "id": resource.id,
                    "title": resource.title,
                    "description": resource.description[:150] if resource.description else "",
                    "category": resource.category,
                    "access_type": resource.access_type,
                    "url": f"/resource/{resource.id}",
                })
        
        return {
            "success": True,
            "query": query,
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@view_config(
    name="api/tags/popular",
    context=IContent,
    renderer="json",
    permission="view",
    request_method="GET",
)
def api_popular_tags(context, request):
    """API: 获取热门标签"""
    try:
        limit = int(request.params.get("limit", 20))
        session = DBSession()
        
        # 收集所有标签
        tag_counts = {}
        
        # 从点子收集
        ideas = session.query(Idea).filter(Idea.tags != None).all()
        for idea in ideas:
            if idea.tags:
                for tag in idea.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 从资源收集
        resources = session.query(ResourceItem).filter(ResourceItem.tags != None).all()
        for resource in resources:
            if resource.tags:
                for tag in resource.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 排序并返回
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            "success": True,
            "tags": [{"name": tag, "count": count} for tag, count in sorted_tags],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@view_config(
    name="match",
    context=IContent,
    renderer="kotti_ai_community:templates/match.pt",
    permission="view",
)
def match_page(context, request):
    """标签匹配页面"""
    session = DBSession()
    
    # 获取热门标签
    tag_counts = {}
    ideas = session.query(Idea).filter(Idea.tags != None).all()
    for idea in ideas:
        if idea.tags:
            for tag in idea.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    resources = session.query(ResourceItem).filter(ResourceItem.tags != None).all()
    for resource in resources:
        if resource.tags:
            for tag in resource.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    
    return {
        "api": template_api(context, request),
        "popular_tags": popular_tags,
    }
