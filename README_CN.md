# Kotti AI Community

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

基于 [Kotti CMS](https://github.com/Kotti/Kotti) 的 AI 共创社区插件 —— 实现 AI 资源共享、协作交流和项目孵化。

## 目录

- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用教程](#使用教程)
- [API 接口](#api-接口)
- [游戏化系统](#游戏化系统)
- [安全机制](#安全机制)
- [开发指南](#开发指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 功能特性

### 核心功能

| 功能 | 描述 |
|------|------|
| **创意广场** | 分享 AI 创意，描述所需资源，寻找志同道合的伙伴 |
| **资源库** | 分享 AI 资源（模型、数据集、工具、API），支持访问控制 |
| **项目孵化** | 从创意创建项目，基于角色的团队管理 |
| **实践日志** | 追踪项目进度、里程碑和投入时间 |
| **用户档案** | 扩展个人资料，展示技能、兴趣和社交链接 |
| **排行榜** | 基于贡献积分的游戏化排名系统 |
| **通知系统** | 实时站内通知 |
| **AI 助手** | 基于 g4f 的浏览器端 AI 助手 |

### 技术亮点

- **SQLAlchemy 模型**：清晰、结构化的数据模型
- **Pyramid 视图**：RESTful API 端点和页面视图
- **Chameleon 模板**：响应式 UI 模板
- **Alembic 迁移**：数据库版本控制
- **安全优先**：XSS 防护、CSRF 保护、输入验证

## 环境要求

- Python 3.10 或更高版本
- Kotti CMS 3.0+
- SQLAlchemy 1.4+ 或 2.0+
- PostgreSQL 或 SQLite

## 安装指南

### 1. 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-org/kotti_ai_community.git
cd kotti_ai_community

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

### 2. 配置 Kotti

编辑 `development.ini`：

```ini
[app:main]
pyramid.includes =
    kotti
    kotti_ai_community

kotti.available_types =
    kotti.resources.Document
    kotti.resources.File
    kotti_ai_community.resources.Idea
    kotti_ai_community.resources.ResourceItem
    kotti_ai_community.resources.Project
    kotti_ai_community.resources.PracticeLog
```

### 3. 初始化数据库

```bash
# 运行数据库迁移
alembic upgrade head

# 或从头初始化
kotti-populate development.ini
```

### 4. 启动服务器

```bash
pserve development.ini
```

访问 `http://localhost:6542/@@home` 查看社区首页。

## 配置说明

### 必要配置

```ini
[app:main]
# 数据库连接
sqlalchemy.url = sqlite:///%(here)s/kotti.db

# 会话密钥
kotti.secret = your-secret-key-here

# 邮件设置（用于通知）
kotti.email.from = noreply@example.com
```

### 可选配置

```ini
[app:main]
# 每页显示数量
kotti_ai_community.items_per_page = 20

# 项目最大成员数
kotti_ai_community.max_project_members = 50

# 启用 AI 助手
kotti_ai_community.ai_assistant_enabled = true
```

## 使用教程

### 页面和视图

| URL | 描述 | 权限 |
|-----|------|------|
| `/@@home` | 社区首页 | 查看 |
| `/@@ideas` | 浏览创意 | 查看 |
| `/@@add_idea` | 创建创意 | 编辑 |
| `/@@resources` | 浏览资源 | 查看 |
| `/@@add_resource_item` | 分享资源 | 编辑 |
| `/@@projects` | 浏览项目 | 查看 |
| `/@@add_project` | 创建项目 | 编辑 |
| `/@@members` | 社区成员 | 查看 |
| `/@@leaderboard` | 排行榜 | 查看 |
| `/@@profile` | 个人档案 | 查看 |
| `/@@edit-profile` | 编辑档案 | 编辑 |
| `/@@notifications` | 通知中心 | 查看 |
| `/@@ai-assistant` | AI 助手 | 查看 |

### 创建内容

#### 创意

```python
# 通过 Python 代码创建
from kotti_ai_community.resources import Idea

idea = Idea(
    title="AI 代码审查工具",
    description="构建一个 AI 助手来审查 Pull Request...",
    category="tool",
    difficulty="intermediate",
    tags=["AI", "代码审查", "自动化"],
    needed_resources="GPU 算力、训练数据",
    expected_outcome="审查时间减少 50%",
)
idea.owner_id = user.id
session.add(idea)
```

#### 项目

```python
from kotti_ai_community.resources import Project

project = Project(
    title="代码审查 AI",
    description="自动化代码审查的 AI 助手",
    status="recruiting",
    visibility="public",
    required_roles=["ML 工程师", "后端开发"],
)
project.owner_id = user.id
session.add(project)
project.add_member(user.id, "owner", session)
```

## API 接口

### 用户 API

#### 获取用户统计

```
GET /@@api-user-stats?username=john
```

响应：
```json
{
  "success": true,
  "username": "john",
  "points": 150,
  "level": 2,
  "level_name": "Explorer",
  "ideas_count": 5,
  "resources_count": 3,
  "badges": [
    {"id": "first_idea", "name": "Idea Generator"}
  ]
}
```

#### 检查并授予徽章

```
GET /@@api-check-badges
```

响应：
```json
{
  "success": true,
  "awarded": ["first_idea"],
  "badges": [...],
  "points": 105
}
```

### 项目 API

#### 获取项目成员

```
GET /@@api-project-members
```

响应：
```json
{
  "success": true,
  "members": [
    {
      "user_id": 1,
      "username": "john",
      "display_name": "John Doe",
      "role": "owner",
      "joined_at": 1640000000
    }
  ]
}
```

#### 更新成员角色

```
POST /@@api-update-member-role?user_id=2&role=admin
```

响应：
```json
{
  "success": true,
  "role": "admin"
}
```

### 通知 API

#### 获取通知列表

```
GET /@@api-notifications
```

响应：
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "badge_earned",
      "title": "获得徽章！",
      "message": "您获得了「创意发起者」徽章",
      "link": "/@@profile",
      "is_read": false,
      "created": "2024-01-15T10:30:00"
    }
  ],
  "unread_count": 3
}
```

#### 标记已读

```
POST /@@api-mark-notification-read?id=1
```

响应：
```json
{
  "success": true,
  "unread_count": 2
}
```

## 游戏化系统

### 积分规则

| 行为 | 积分 |
|------|------|
| 创建创意 | 10 |
| 分享资源 | 15 |
| 创建项目 | 20 |
| 加入项目 | 5 |
| 添加实践日志 | 5 |
| 获得徽章 | 5-30（不等） |

### 等级体系

| 等级 | 名称 | 所需积分 |
|------|------|----------|
| 1 | 新手 | 0 |
| 2 | 探索者 | 100 |
| 3 | 贡献者 | 300 |
| 4 | 创作者 | 600 |
| 5 | 创新者 | 1,000 |
| 6 | 专家 | 2,000+ |
| 7 | 大师 | 3,000+ |
| 8 | 大神 | 4,000+ |
| 9 | 传奇 | 5,000+ |
| 10 | 远见者 | 6,000+ |

### 徽章系统

| 徽章 ID | 名称 | 描述 | 额外积分 |
|---------|------|------|----------|
| `first_idea` | 创意发起者 | 创建第一个创意 | 5 |
| `idea_master` | 创意大师 | 创建 10 个创意 | 20 |
| `first_resource` | 资源分享者 | 分享第一个资源 | 5 |
| `resource_master` | 资源大师 | 分享 10 个资源 | 20 |
| `first_project` | 项目发起者 | 创建第一个项目 | 10 |
| `project_leader` | 项目领袖 | 创建 5 个项目 | 30 |
| `team_player` | 团队协作者 | 加入 3 个项目 | 15 |
| `level_5` | 创新者 | 达到 5 级 | 0 |
| `level_10` | 远见者 | 达到 10 级 | 0 |

## 安全机制

### URL 验证

所有用户提交的 URL 都经过验证，防止 XSS 攻击：

```python
from kotti_ai_community.utils import safe_url

# 只允许 http:// 和 https:// 协议
url = safe_url(user_input)  # javascript: URL 返回空字符串
```

### CSRF 保护

所有 POST 表单必须包含 CSRF token：

```html
<input type="hidden" name="csrf_token" value="${request.session.get('csrf_token', '')}"/>
```

在视图中验证：

```python
from kotti_ai_community.utils import validate_csrf_token

if request.method == "POST":
    if not validate_csrf_token(request):
        raise HTTPForbidden("无效的 CSRF token")
```

### 输入验证

```python
from kotti_ai_community.utils import safe_int, truncate_string

# 安全的整数转换
page = safe_int(request.params.get("page"), 1)

# 限制字符串长度
title = truncate_string(request.params.get("title", ""), 200)
```

### 权限辅助函数

```python
from kotti_ai_community.utils import can_edit, is_admin

# 检查编辑权限
if can_edit(context, request):
    # 允许编辑

# 检查管理员身份
if is_admin(request):
    # 仅管理员可执行的操作
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
python -m unittest discover -s kotti_ai_community/tests -v

# 运行特定测试文件
python -m unittest kotti_ai_community.tests.test_utils -v

# 带覆盖率报告
coverage run -m unittest discover
coverage report
```

### 代码规范

- 遵循 [PEP 8](https://pep8.org/) 编码规范
- 函数签名使用类型注解
- 为所有公开函数和类编写文档字符串
- 最大行长度：100 字符

### 项目结构

```
kotti_ai_community/
├── __init__.py              # 插件入口
├── resources.py             # SQLAlchemy 模型
├── user_profile.py          # 用户档案模型
├── notification.py          # 通知系统
├── utils.py                 # 工具函数
├── views/
│   ├── __init__.py
│   ├── home.py              # 首页视图
│   ├── idea.py              # 创意视图
│   ├── resource.py          # 资源视图
│   ├── project.py           # 项目视图
│   ├── user.py              # 用户视图、徽章
│   ├── notification.py      # 通知视图
│   └── practice_log.py      # 实践日志视图
├── templates/
│   ├── home.pt
│   ├── idea_*.pt
│   ├── resource_*.pt
│   ├── project_*.pt
│   ├── user_*.pt
│   └── ...
├── alembic/
│   └── versions/            # 数据库迁移
└── tests/
    ├── test_utils.py
    ├── test_user_profile.py
    └── test_csrf.py
```

### 创建数据库迁移

```bash
# 创建新迁移
alembic revision -m "add_new_table"

# 应用迁移
alembic upgrade head

# 回滚一个版本
alembic downgrade -1
```

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行修改
4. 运行测试 (`python -m unittest discover -s kotti_ai_community/tests`)
5. 提交更改 (`git commit -m 'Add amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

### 贡献准则

- 为新功能编写测试
- 更新相关文档
- 遵循现有代码风格
- 保持提交原子化且描述清晰

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 致谢

- [Kotti CMS](https://github.com/Kotti/Kotti) - 基础 CMS 框架
- [Pyramid Framework](https://trypyramid.com/) - Web 框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [g4f](https://github.com/xtekky/gpt4free) - AI 助手集成

## 支持

- **文档**：[Wiki](https://github.com/your-org/kotti_ai_community/wiki)
- **问题反馈**：[GitHub Issues](https://github.com/your-org/kotti_ai_community/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/your-org/kotti_ai_community/discussions)

---

English | **中文文档**
