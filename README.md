# Kotti AI Community

[![Tests](https://github.com/skywalk163/kotti_ai_community/actions/workflows/test.yml/badge.svg)](https://github.com/skywalk163/kotti_ai_community/actions/workflows/test.yml)
[![Lint](https://github.com/skywalk163/kotti_ai_community/actions/workflows/lint.yml/badge.svg)](https://github.com/skywalk163/kotti_ai_community/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive AI community plugin for [Kotti CMS](https://github.com/Kotti/Kotti) - enabling AI resource sharing, collaboration, and project incubation.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Gamification System](#gamification-system)
- [Security](#security)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| **Ideas Square** | Share AI ideas, describe needed resources, find collaborators |
| **Resource Library** | Share AI resources (models, datasets, tools, APIs) with access control |
| **Project Incubation** | Create projects from ideas, manage teams with role-based permissions |
| **Practice Logs** | Track project progress, milestones, and time spent |
| **User Profiles** | Extended profiles with skills, interests, and social links |
| **Leaderboard** | Gamified ranking system based on contribution points |
| **Notifications** | Real-time in-app notification system |
| **AI Assistant** | Browser-based AI helper powered by g4f |
| **Full-text Search** | Search ideas, resources, and projects by keywords |

### Technical Highlights

- **SQLAlchemy Models**: Clean, well-structured data models
- **Pyramid Views**: RESTful API endpoints and page views
- **Chameleon Templates**: Responsive UI templates
- **Alembic Migrations**: Database version control
- **Security First**: XSS prevention, CSRF protection, input validation

## Requirements

- Python 3.10 or higher
- Kotti CMS 3.0+
- SQLAlchemy 1.4+ or 2.0+
- PostgreSQL or SQLite

## Installation

### 1. Install from Source

```bash
# Clone the repository
git clone https://github.com/your-org/kotti_ai_community.git
cd kotti_ai_community

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### 2. Add to Kotti Configuration

Edit your `development.ini`:

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

### 3. Initialize Database

```bash
# Run database migrations
alembic upgrade head

# Or initialize from scratch
kotti-populate development.ini
```

### 4. Start the Server

```bash
pserve development.ini
```

Visit `http://localhost:6542/@@home` to see the community homepage.

## Configuration

### Required Settings

```ini
[app:main]
# Database URL
sqlalchemy.url = sqlite:///%(here)s/kotti.db

# Secret key for sessions
kotti.secret = your-secret-key-here

# Email settings (for notifications)
kotti.email.from = noreply@example.com
```

### Optional Settings

```ini
[app:main]
# Items per page
kotti_ai_community.items_per_page = 20

# Maximum project members
kotti_ai_community.max_project_members = 50

# Enable AI assistant
kotti_ai_community.ai_assistant_enabled = true
```

## Usage

### Pages and Views

| URL | Description | Permission |
|-----|-------------|------------|
| `/@@home` | Community homepage | View |
| `/@@ideas` | Browse all ideas | View |
| `/@@add_idea` | Create new idea | Edit |
| `/@@resources` | Browse resources | View |
| `/@@add_resource_item` | Share resource | Edit |
| `/@@projects` | Browse projects | View |
| `/@@add_project` | Create project | Edit |
| `/@@members` | Community members | View |
| `/@@leaderboard` | Top contributors | View |
| `/@@profile` | User profile | View |
| `/@@edit-profile` | Edit profile | Edit |
| `/@@notifications` | Notifications | View |
| `/@@ai-assistant` | AI assistant | View |
| `/@@search` | Full-text search | View |

### Creating Content

#### Ideas

```python
# Via Python
from kotti_ai_community.resources import Idea

idea = Idea(
    title="AI-Powered Code Review Tool",
    description="Build an AI assistant that reviews pull requests...",
    category="tool",
    difficulty="intermediate",
    tags=["AI", "code-review", "automation"],
    needed_resources="GPU compute, training data",
    expected_outcome="Reduced review time by 50%",
)
idea.owner_id = user.id
session.add(idea)
```

#### Projects

```python
from kotti_ai_community.resources import Project

project = Project(
    title="Code Review AI",
    description="AI assistant for automated code review",
    status="recruiting",
    visibility="public",
    required_roles=["ML Engineer", "Backend Developer"],
)
project.owner_id = user.id
session.add(project)
project.add_member(user.id, "owner", session)
```

## API Reference

### User API

#### Get User Statistics

```
GET /@@api-user-stats?username=john
```

Response:
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

#### Check and Award Badges

```
GET /@@api-check-badges
```

Response:
```json
{
  "success": true,
  "awarded": ["first_idea"],
  "badges": [...],
  "points": 105
}
```

### Project API

#### Get Project Members

```
GET /@@api-project-members
```

Response:
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

#### Update Member Role

```
POST /@@api-update-member-role?user_id=2&role=admin
```

Response:
```json
{
  "success": true,
  "role": "admin"
}
```

### Notification API

#### Get Notifications

```
GET /@@api-notifications
```

Response:
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "badge_earned",
      "title": "Badge Earned!",
      "message": "You earned the 'Idea Generator' badge",
      "link": "/@@profile",
      "is_read": false,
      "created": "2024-01-15T10:30:00"
    }
  ],
  "unread_count": 3
}
```

#### Mark as Read

```
POST /@@api-mark-notification-read?id=1
```

Response:
```json
{
  "success": true,
  "unread_count": 2
}
```

### Search API

#### Search Content

```
GET /@@search?q=ai&type=all&page=1
```

Parameters:
- `q` (required): Search query (minimum 2 characters)
- `type` (optional): Content type filter (`all`, `ideas`, `resources`, `projects`)
- `page` (optional): Page number (default: 1)

Response:
```json
{
  "query": "ai",
  "content_type": "all",
  "results": [
    {
      "type": "idea",
      "title": "AI-Powered Code Review",
      "description": "Build an AI assistant...",
      "tags": ["AI", "automation"],
      "url": "/ideas/1"
    }
  ],
  "total_count": 15,
  "pagination": {
    "page": 1,
    "pages": 1
  }
}
```

#### Search API (JSON)

```
GET /@@search_api?q=ai&limit=10
```

Response:
```json
{
  "results": [
    {
      "type": "idea",
      "title": "AI-Powered Code Review",
      "url": "/ideas/1"
    }
  ]
}
```

## Gamification System

### Points

| Action | Points |
|--------|--------|
| Create an idea | 10 |
| Share a resource | 15 |
| Create a project | 20 |
| Join a project | 5 |
| Add a practice log | 5 |
| Earn a badge | 5-30 (varies) |

### Levels

| Level | Name | Points Required |
|-------|------|-----------------|
| 1 | Newcomer | 0 |
| 2 | Explorer | 100 |
| 3 | Contributor | 300 |
| 4 | Creator | 600 |
| 5 | Innovator | 1,000 |
| 6 | Expert | 2,000+ |
| 7 | Master | 3,000+ |
| 8 | Guru | 4,000+ |
| 9 | Legend | 5,000+ |
| 10 | Visionary | 6,000+ |

### Badges

| Badge ID | Name | Description | Bonus Points |
|----------|------|-------------|--------------|
| `first_idea` | Idea Generator | Created your first idea | 5 |
| `idea_master` | Idea Master | Created 10 ideas | 20 |
| `first_resource` | Resource Sharer | Shared your first resource | 5 |
| `resource_master` | Resource Master | Shared 10 resources | 20 |
| `first_project` | Project Starter | Created your first project | 10 |
| `project_leader` | Project Leader | Created 5 projects | 30 |
| `team_player` | Team Player | Joined 3 projects | 15 |
| `level_5` | Innovator | Reached level 5 | 0 |
| `level_10` | Visionary | Reached level 10 | 0 |

## Security

### URL Validation

All user-submitted URLs are validated to prevent XSS attacks:

```python
from kotti_ai_community.utils import safe_url

# Only http:// and https:// URLs are allowed
url = safe_url(user_input)  # Returns '' for javascript: URLs
```

### CSRF Protection

All POST forms must include CSRF token:

```html
<input type="hidden" name="csrf_token" value="${request.session.get('csrf_token', '')}"/>
```

In views:

```python
from kotti_ai_community.utils import validate_csrf_token

if request.method == "POST":
    if not validate_csrf_token(request):
        raise HTTPForbidden("Invalid CSRF token")
```

### Input Validation

```python
from kotti_ai_community.utils import safe_int, truncate_string

# Safe integer conversion
page = safe_int(request.params.get("page"), 1)

# Limit string length
title = truncate_string(request.params.get("title", ""), 200)
```

### Permission Helpers

```python
from kotti_ai_community.utils import can_edit, is_admin

# Check edit permission
if can_edit(context, request):
    # Allow editing

# Check admin status
if is_admin(request):
    # Admin-only operations
```

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover -s kotti_ai_community/tests -v

# Run specific test file
python -m unittest kotti_ai_community.tests.test_utils -v

# Run with coverage
coverage run -m unittest discover
coverage report
```

### Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Maximum line length: 100 characters

### Project Structure

```
kotti_ai_community/
├── __init__.py              # Plugin entry point
├── resources.py             # SQLAlchemy models
├── user_profile.py          # User profile model
├── notification.py          # Notification system
├── moderation.py            # Content moderation
├── utils.py                 # Utility functions
├── views/
│   ├── __init__.py
│   ├── home.py              # Homepage view
│   ├── idea.py              # Idea views
│   ├── resource.py          # Resource views
│   ├── project.py           # Project views
│   ├── user.py              # User views, badges
│   ├── notification.py      # Notification views
│   ├── practice_log.py      # Practice log views
│   ├── moderation.py        # Moderation views
│   ├── search.py            # Full-text search
│   ├── ai_assistant.py      # AI assistant
│   └── match.py             # Tag matching
├── templates/
│   ├── home.pt
│   ├── idea_*.pt
│   ├── resource_*.pt
│   ├── project_*.pt
│   ├── user_*.pt
│   ├── search.pt
│   └── ...
├── alembic/
│   └── versions/            # Database migrations
└── tests/
    ├── test_utils.py
    ├── test_user_profile.py
    ├── test_csrf.py
    ├── test_moderation.py
    └── test_search.py
```

### Creating a Migration

```bash
# Create new migration
alembic revision -m "add_new_table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m unittest discover -s kotti_ai_community/tests`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Guidelines

- Write tests for new features
- Update documentation
- Follow the existing code style
- Keep commits atomic and well-described

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Kotti CMS](https://github.com/Kotti/Kotti) - The foundation CMS
- [Pyramid Framework](https://trypyramid.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [g4f](https://github.com/xtekky/gpt4free) - AI assistant integration

## Support

- **Documentation**: [Wiki](https://github.com/your-org/kotti_ai_community/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/kotti_ai_community/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/kotti_ai_community/discussions)

---

**[中文文档](README_CN.md)** | English
