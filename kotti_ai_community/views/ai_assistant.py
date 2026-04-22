# -*- coding: utf-8 -*-
"""
AI Assistant views
"""

from pyramid.view import view_config

from kotti.interfaces import IContent
from kotti.views.util import template_api


@view_config(
    name="ai-assistant",
    context=IContent,
    renderer="kotti_ai_community:templates/ai_assistant.pt",
    permission="view",
)
def ai_assistant(context, request):
    """AI Assistant chat interface"""
    return {
        "api": template_api(context, request),
    }


@view_config(
    name="api/ai/optimize-idea",
    context=IContent,
    renderer="json",
    permission="edit",
    request_method="POST",
)
def api_optimize_idea(context, request):
    """API: 优化点子描述（返回前端处理的提示词）"""
    try:
        data = request.json_body
        idea_data = {
            "title": data.get("title", ""),
            "category": data.get("category", ""),
            "description": data.get("description", ""),
            "neededResources": data.get("needed_resources", ""),
            "expectedOutcome": data.get("expected_outcome", ""),
        }
        
        # 返回提示词，由前端调用 g4f
        prompt = f"""请帮我优化以下 AI 点子的描述，使其更加清晰、专业、有吸引力：

标题：{idea_data['title']}
分类：{idea_data['category']}
当前描述：{idea_data['description']}
需要的资源：{idea_data['neededResources'] or '未填写'}
预期成果：{idea_data['expectedOutcome'] or '未填写'}

请从以下几个方面进行优化：
1. 点子背景和动机
2. 核心创新点
3. 技术可行性分析
4. 预期价值和影响
5. 实施建议

请用中文回复，格式清晰。"""

        return {
            "success": True,
            "prompt": prompt,
            "system_prompt": "你是一位 AI 产品专家和技术顾问，擅长帮助用户完善和优化 AI 项目点子。"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@view_config(
    name="api/ai/suggest-tags",
    context=IContent,
    renderer="json",
    permission="view",
    request_method="POST",
)
def api_suggest_tags(context, request):
    """API: 生成标签建议"""
    try:
        data = request.json_body
        content = data.get("content", "")
        content_type = data.get("type", "idea")
        
        prompt = f"""请根据以下内容，生成 5-10 个合适的标签：

类型：{'点子' if content_type == 'idea' else '资源'}
内容：{content}

要求：
1. 标签要准确反映内容主题
2. 包含技术领域标签（如：NLP、CV、LLM等）
3. 包含应用场景标签（如：智能客服、图像生成等）
4. 标签简洁，每个 2-8 个字
5. 只输出标签，用逗号分隔"""

        return {
            "success": True,
            "prompt": prompt,
            "system_prompt": "你是一位标签分类专家，擅长为内容生成准确的分类标签。"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@view_config(
    name="api/ai/match",
    context=IContent,
    renderer="json",
    permission="view",
    request_method="POST",
)
def api_match(context, request):
    """API: 匹配点子和资源"""
    try:
        data = request.json_body
        idea = data.get("idea", {})
        resource = data.get("resource", {})
        
        prompt = f"""分析以下点子和资源的匹配度：

点子：
- 标题：{idea.get('title', '')}
- 描述：{idea.get('description', '')}
- 需要的资源：{idea.get('needed_resources', '')}

资源：
- 标题：{resource.get('title', '')}
- 描述：{resource.get('description', '')}
- 分类：{resource.get('category', '')}

请分析：
1. 匹配度评分（0-100分）
2. 匹配理由
3. 使用建议"""

        return {
            "success": True,
            "prompt": prompt,
            "system_prompt": "你是一位项目匹配专家，擅长分析点子和资源的契合度。"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
