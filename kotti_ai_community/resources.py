# -*- coding: utf-8 -*-
"""
AI共创社区内容类型定义

包含:
- Idea: 点子内容类型
- ResourceItem: 资源内容类型
"""

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy.orm import relationship

from kotti import Base
from kotti.interfaces import IContent
from kotti.interfaces import IDocument
from kotti.resources import Content
from kotti.resources import File
from kotti.sqla import JsonType
from kotti.util import _
from zope.interface import implementer


# ============================================================================
# 点子状态枚举
# ============================================================================
IDEA_STATUS = {
    "draft": _("草稿"),
    "brainstorming": _("构思中"),
    "recruiting": _("招募中"),
    "in_progress": _("进行中"),
    "completed": _("已完成"),
    "archived": _("已归档"),
}

IDEA_CATEGORIES = {
    "tool": _("工具/应用"),
    "research": _("研究/实验"),
    "startup": _("创业/商业"),
    "learning": _("学习/教育"),
    "creative": _("创意/艺术"),
    "other": _("其他"),
}

DIFFICULTY_LEVELS = {
    "beginner": _("入门级"),
    "intermediate": _("中级"),
    "advanced": _("高级"),
    "expert": _("专家级"),
}


# ============================================================================
# 资源类型枚举
# ============================================================================
RESOURCE_CATEGORIES = {
    "model": _("模型/权重"),
    "dataset": _("数据集"),
    "tool": _("工具/框架"),
    "api": _("API 服务"),
    "compute": _("算力资源"),
    "funding": _("资金支持"),
    "mentor": _("导师/指导"),
    "other": _("其他"),
}

ACCESS_TYPES = {
    "free": _("免费开放"),
    "freemium": _("部分免费"),
    "paid": _("付费"),
    "application": _("申请制"),
    "invite": _("邀请制"),
}


# ============================================================================
# Idea - 点子内容类型
# ============================================================================
@implementer(IContent)
class Idea(Content):
    """点子内容类型

    用于发布 AI 相关的点子、想法和项目构思
    """

    __tablename__ = "ideas"
    __mapper_args__ = dict(polymorphic_identity="idea")

    #: 关联到 Content 的 id
    id = Column(Integer, ForeignKey("contents.id"), primary_key=True)

    #: 点子分类
    category = Column(String(50), default="other")

    #: 难度等级
    difficulty = Column(String(50), default="beginner")

    #: 状态
    status = Column(String(50), default="draft")

    #: 标签 (JSON 数组)
    tags = Column(JsonType, default=list)

    #: 详细描述
    description = Column(UnicodeText())

    #: 需要的资源描述
    needed_resources = Column(UnicodeText())

    #: 预期成果
    expected_outcome = Column(UnicodeText())

    #: 预计时间 (天)
    estimated_days = Column(Integer, default=0)

    #: 关注者数量
    followers_count = Column(Integer, default=0)

    #: 点赞数
    likes_count = Column(Integer, default=0)

    #: 浏览数
    views_count = Column(Integer, default=0)

    #: AI 生成的建议 (可选)
    ai_suggestions = Column(UnicodeText())

    type_info = Content.type_info.copy(
        name="idea",
        title=_("点子"),
        add_view="add_idea",
        addable_to=["Document"],
        edit_links=[],
    )

    def __init__(self, title=None, description=None, **kwargs):
        """初始化点子"""
        super(Idea, self).__init__(title=title, **kwargs)
        self.description = description
        self.tags = kwargs.get("tags", [])
        self.category = kwargs.get("category", "other")
        self.difficulty = kwargs.get("difficulty", "beginner")
        self.status = kwargs.get("status", "draft")
        self.needed_resources = kwargs.get("needed_resources", "")
        self.expected_outcome = kwargs.get("expected_outcome", "")
        self.estimated_days = kwargs.get("estimated_days", 0)

    def get_status_display(self):
        """获取状态的显示文本"""
        return IDEA_STATUS.get(self.status, self.status)

    def get_category_display(self):
        """获取分类的显示文本"""
        return IDEA_CATEGORIES.get(self.category, self.category)

    def get_difficulty_display(self):
        """获取难度的显示文本"""
        return DIFFICULTY_LEVELS.get(self.difficulty, self.difficulty)


# ============================================================================
# ResourceItem - 资源内容类型
# ============================================================================
@implementer(IContent)
class ResourceItem(Content):
    """资源内容类型

    用于分享 AI 相关的资源，如模型、数据集、工具等
    """

    __tablename__ = "resource_items"
    __mapper_args__ = dict(polymorphic_identity="resource_item")

    #: 关联到 Content 的 id
    id = Column(Integer, ForeignKey("contents.id"), primary_key=True)

    #: 资源分类
    category = Column(String(50), default="other")

    #: 访问方式
    access_type = Column(String(50), default="free")

    #: 标签 (JSON 数组)
    tags = Column(JsonType, default=list)

    #: 详细描述
    description = Column(UnicodeText())

    #: 资源链接
    url = Column(Unicode(500))

    #: 使用说明
    usage_guide = Column(UnicodeText())

    #: 限制条件
    limitations = Column(UnicodeText())

    #: 可用性状态
    availability = Column(String(50), default="available")

    #: 被引用次数
    references_count = Column(Integer, default=0)

    #: 点赞数
    likes_count = Column(Integer, default=0)

    #: 浏览数
    views_count = Column(Integer, default=0)

    type_info = Content.type_info.copy(
        name="resource_item",
        title=_("资源"),
        add_view="add_resource_item",
        addable_to=["Document"],
        edit_links=[],
    )

    def __init__(self, title=None, description=None, **kwargs):
        """初始化资源"""
        super(ResourceItem, self).__init__(title=title, **kwargs)
        self.description = description
        self.tags = kwargs.get("tags", [])
        self.category = kwargs.get("category", "other")
        self.access_type = kwargs.get("access_type", "free")
        self.url = kwargs.get("url", "")
        self.usage_guide = kwargs.get("usage_guide", "")
        self.limitations = kwargs.get("limitations", "")

    def get_category_display(self):
        """获取分类的显示文本"""
        return RESOURCE_CATEGORIES.get(self.category, self.category)

    def get_access_type_display(self):
        """获取访问方式的显示文本"""
        return ACCESS_TYPES.get(self.access_type, self.access_type)


# ============================================================================
# Project Status and Role Enums
# ============================================================================
PROJECT_STATUS = {
    "planning": _("Planning"),
    "recruiting": _("Recruiting"),
    "in_progress": _("In Progress"),
    "on_hold": _("On Hold"),
    "completed": _("Completed"),
    "cancelled": _("Cancelled"),
}

PROJECT_VISIBILITY = {
    "public": _("Public"),
    "private": _("Private"),
    "invite_only": _("Invite Only"),
}

MEMBER_ROLES = {
    "owner": _("Owner"),
    "admin": _("Admin"),
    "member": _("Member"),
    "contributor": _("Contributor"),
    "observer": _("Observer"),
}


# ============================================================================
# ProjectMember - Team member association
# ============================================================================
class ProjectMember(Base):
    """Project team member association."""

    __tablename__ = "project_members"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("principals.id"), nullable=False)
    role = Column(String(50), default="member")
    joined_at = Column(Integer, default=0)  # timestamp
    contribution_summary = Column(UnicodeText())
    is_active = Column(Integer, default=1)  # 1 = active, 0 = left

    def __init__(self, project_id, user_id, role="member", **kwargs):
        self.project_id = project_id
        self.user_id = user_id
        self.role = role
        self.contribution_summary = kwargs.get("contribution_summary", "")

    def get_role_display(self):
        return MEMBER_ROLES.get(self.role, self.role)


# ============================================================================
# Project - Project content type
# ============================================================================
@implementer(IContent)
class Project(Content):
    """Project content type.

    A project is created from an Idea and involves team collaboration.
    """

    __tablename__ = "projects"
    __mapper_args__ = dict(polymorphic_identity="project")

    id = Column(Integer, ForeignKey("contents.id"), primary_key=True)

    #: Source idea (optional)
    idea_id = Column(Integer, ForeignKey("ideas.id"), nullable=True)

    #: Project description
    description = Column(UnicodeText())

    #: Status
    status = Column(String(50), default="planning")

    #: Visibility
    visibility = Column(String(50), default="public")

    #: Tags
    tags = Column(JsonType, default=list)

    #: Goals (JSON array of goal objects)
    goals = Column(JsonType, default=list)

    #: Milestones (JSON array)
    milestones = Column(JsonType, default=list)

    #: Required skills/roles
    required_roles = Column(JsonType, default=list)

    #: Repository URL
    repo_url = Column(Unicode(500))

    #: Demo URL
    demo_url = Column(Unicode(500))

    #: Documentation URL
    doc_url = Column(Unicode(500))

    #: Start date (timestamp)
    start_date = Column(Integer, default=0)

    #: Target end date (timestamp)
    end_date = Column(Integer, default=0)

    #: Actual end date
    actual_end_date = Column(Integer, default=0)

    #: Max team size
    max_members = Column(Integer, default=10)

    #: Current member count (cached)
    members_count = Column(Integer, default=1)

    #: Followers count
    followers_count = Column(Integer, default=0)

    #: Stars count
    stars_count = Column(Integer, default=0)

    #: Views count
    views_count = Column(Integer, default=0)

    #: Progress percentage (0-100)
    progress = Column(Integer, default=0)

    #: Results summary
    results = Column(UnicodeText())

    #: Lessons learned
    lessons = Column(UnicodeText())

    type_info = Content.type_info.copy(
        name="project",
        title=_("Project"),
        add_view="add_project",
        addable_to=["Document"],
        edit_links=[],
    )

    def __init__(self, title=None, description=None, **kwargs):
        super(Project, self).__init__(title=title, **kwargs)
        self.description = description
        self.tags = kwargs.get("tags", [])
        self.status = kwargs.get("status", "planning")
        self.visibility = kwargs.get("visibility", "public")
        self.goals = kwargs.get("goals", [])
        self.milestones = kwargs.get("milestones", [])
        self.required_roles = kwargs.get("required_roles", [])
        self.repo_url = kwargs.get("repo_url", "")
        self.demo_url = kwargs.get("demo_url", "")
        self.doc_url = kwargs.get("doc_url", "")
        self.idea_id = kwargs.get("idea_id")

    def get_status_display(self):
        return PROJECT_STATUS.get(self.status, self.status)

    def get_visibility_display(self):
        return PROJECT_VISIBILITY.get(self.visibility, self.visibility)

    def get_members(self, session):
        """Get all active team members."""
        from kotti.security import Principal
        members = (
            session.query(ProjectMember, Principal)
            .join(Principal, ProjectMember.user_id == Principal.id)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.is_active == 1)
            .all()
        )
        return members

    def get_member_count(self, session):
        """Get current member count."""
        count = (
            session.query(ProjectMember)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.is_active == 1)
            .count()
        )
        return count

    def is_member(self, user_id, session):
        """Check if user is a team member."""
        member = (
            session.query(ProjectMember)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.user_id == user_id)
            .filter(ProjectMember.is_active == 1)
            .first()
        )
        return member is not None

    def get_member_role(self, user_id, session):
        """Get user's role in project."""
        member = (
            session.query(ProjectMember)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.user_id == user_id)
            .filter(ProjectMember.is_active == 1)
            .first()
        )
        return member.role if member else None

    def add_member(self, user_id, role, session):
        """Add a member to the project."""
        # Check if already a member
        existing = (
            session.query(ProjectMember)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.user_id == user_id)
            .first()
        )
        if existing:
            existing.is_active = 1
            existing.role = role
        else:
            import time
            member = ProjectMember(
                project_id=self.id,
                user_id=user_id,
                role=role,
                joined_at=int(time.time()),
            )
            session.add(member)

        # Update member count
        self.members_count = self.get_member_count(session)

    def remove_member(self, user_id, session):
        """Remove a member from the project."""
        member = (
            session.query(ProjectMember)
            .filter(ProjectMember.project_id == self.id)
            .filter(ProjectMember.user_id == user_id)
            .first()
        )
        if member:
            member.is_active = 0
            self.members_count = self.get_member_count(session)

    def get_logs(self, session, limit=None):
        """Get practice logs for this project."""
        query = (
            session.query(PracticeLog)
            .filter(PracticeLog.project_id == self.id)
            .order_by(PracticeLog.log_date.desc())
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_milestones(self, session):
        """Get all milestones for this project."""
        return (
            session.query(Milestone)
            .filter(Milestone.project_id == self.id)
            .order_by(Milestone.target_date)
            .all()
        )


# ============================================================================
# Practice Log Types
# ============================================================================
LOG_TYPES = {
    "progress": _("Progress Update"),
    "milestone": _("Milestone Reached"),
    "blocker": _("Blocker/Issue"),
    "achievement": _("Achievement"),
    "learning": _("Learning/Discovery"),
    "decision": _("Decision Made"),
    "resource": _("Resource Added"),
    "other": _("Other"),
}

LOG_VISIBILITY = {
    "public": _("Public"),
    "members": _("Team Only"),
    "private": _("Private"),
}


# ============================================================================
# PracticeLog - Practice/Progress Log Entry
# ============================================================================
@implementer(IContent)
class PracticeLog(Content):
    """Practice log entry for tracking project progress."""

    __tablename__ = "practice_logs"
    __mapper_args__ = dict(polymorphic_identity="practice_log")

    id = Column(Integer, ForeignKey("contents.id"), primary_key=True)

    #: Associated project
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    #: Log type
    log_type = Column(String(50), default="progress")

    #: Log date (can be different from creation date)
    log_date = Column(Integer, default=0)  # timestamp

    #: Content
    content = Column(UnicodeText())

    #: Progress change (e.g., +10%)
    progress_change = Column(Integer, default=0)

    #: New progress value after this log
    new_progress = Column(Integer, default=0)

    #: Time spent (hours)
    time_spent = Column(Integer, default=0)

    #: Tags
    tags = Column(JsonType, default=list)

    #: Attachments (JSON array of file URLs)
    attachments = Column(JsonType, default=list)

    #: Visibility
    visibility = Column(String(50), default="public")

    #: Likes count
    likes_count = Column(Integer, default=0)

    #: Comments count
    comments_count = Column(Integer, default=0)

    type_info = Content.type_info.copy(
        name="practice_log",
        title=_("Practice Log"),
        add_view="add_practice_log",
        addable_to=["Document"],
        edit_links=[],
    )

    def __init__(self, title=None, content=None, project_id=None, **kwargs):
        super(PracticeLog, self).__init__(title=title, **kwargs)
        self.content = content
        self.project_id = project_id
        self.log_type = kwargs.get("log_type", "progress")
        self.log_date = kwargs.get("log_date", int(__import__("time").time()))
        self.progress_change = kwargs.get("progress_change", 0)
        self.new_progress = kwargs.get("new_progress", 0)
        self.time_spent = kwargs.get("time_spent", 0)
        self.tags = kwargs.get("tags", [])
        self.visibility = kwargs.get("visibility", "public")

    def get_log_type_display(self):
        return LOG_TYPES.get(self.log_type, self.log_type)

    def get_visibility_display(self):
        return LOG_VISIBILITY.get(self.visibility, self.visibility)


# ============================================================================
# Milestone Status
# ============================================================================
MILESTONE_STATUS = {
    "planned": _("Planned"),
    "in_progress": _("In Progress"),
    "completed": _("Completed"),
    "missed": _("Missed"),
    "cancelled": _("Cancelled"),
}


# ============================================================================
# Milestone - Project Milestone
# ============================================================================
class Milestone(Base):
    """Project milestone for tracking major goals."""

    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    #: Milestone title
    title = Column(Unicode(200), nullable=False)

    #: Description
    description = Column(UnicodeText())

    #: Target date (timestamp)
    target_date = Column(Integer, default=0)

    #: Actual completion date
    completed_date = Column(Integer, default=0)

    #: Status
    status = Column(String(50), default="planned")

    #: Progress percentage for this milestone
    progress = Column(Integer, default=0)

    #: Order/priority
    order_index = Column(Integer, default=0)

    #: Created by
    created_by = Column(Integer, default=0)

    #: Created at
    created_at = Column(Integer, default=0)

    def __init__(self, project_id, title, **kwargs):
        self.project_id = project_id
        self.title = title
        self.description = kwargs.get("description", "")
        self.target_date = kwargs.get("target_date", 0)
        self.status = kwargs.get("status", "planned")
        self.progress = kwargs.get("progress", 0)
        self.order_index = kwargs.get("order_index", 0)
        self.created_by = kwargs.get("created_by", 0)
        self.created_at = int(__import__("time").time())

    def get_status_display(self):
        return MILESTONE_STATUS.get(self.status, self.status)
