# -*- coding: utf-8 -*-
"""
AI共创社区插件

基于 Kotti CMS 构建的 AI 资源互助平台
"""

from kotti_ai_community.resources import Idea
from kotti_ai_community.resources import ResourceItem
from kotti_ai_community.resources import Project
from kotti_ai_community.resources import PracticeLog
from kotti_ai_community import user_profile


def kotti_configure(settings):
    """配置插件"""
    # 添加 pyramid includes
    if "pyramid.includes" in settings:
        if "kotti_ai_community" not in settings["pyramid.includes"]:
            settings["pyramid.includes"] += " kotti_ai_community"
    else:
        settings["pyramid.includes"] = "kotti_ai_community"

    # 添加到可用类型
    if "kotti.available_types" in settings:
        types = settings["kotti.available_types"].split()
        if "kotti_ai_community.resources.Idea" not in types:
            settings["kotti.available_types"] += (
                "\n    kotti_ai_community.resources.Idea"
                "\n    kotti_ai_community.resources.ResourceItem"
                "\n    kotti_ai_community.resources.Project"
                "\n    kotti_ai_community.resources.PracticeLog"
            )
    else:
        settings["kotti.available_types"] = (
            "kotti.resources.Document\n"
            "kotti.resources.File\n"
            "kotti_ai_community.resources.Idea\n"
            "kotti_ai_community.resources.ResourceItem\n"
            "kotti_ai_community.resources.Project\n"
            "kotti_ai_community.resources.PracticeLog"
        )


def includeme(config):
    """Pyramid 包含配置"""
    # 扫描整个 kotti_ai_community 包
    config.scan("kotti_ai_community")
