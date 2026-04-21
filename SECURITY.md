# Security Policy

## Security Fixes Applied

This document describes the security vulnerabilities identified and fixed in the code review.

### P0 - Critical Issues (Fixed)

#### 1. XSS Vulnerability in Templates

**Issue**: User content was rendered without escaping using `structure` keyword in Chameleon templates.

**Files affected**: `templates/idea_view.pt`

**Fix**: Removed `structure` keyword to enable automatic HTML escaping.

```html
<!-- Before (vulnerable) -->
<div tal:content="structure context.description"></div>

<!-- After (safe) -->
<div tal:content="context/description | python: ''"></div>
```

#### 2. External Link Vulnerability

**Issue**: User-submitted URLs (website, avatar_url, social links) were not validated, allowing `javascript:` URLs.

**Files affected**: `views/user.py`, `templates/user_profile.pt`

**Fix**: Added URL validation in `utils.py`:

```python
def safe_url(url: Optional[str]) -> str:
    """Only allows http:// and https:// URLs."""
    if not url:
        return ''
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {'http', 'https'}:
        return ''
    return url
```

#### 3. Incorrect Badge Timestamp

**Issue**: `func.now()` (SQL function) was used in Python code, returning SQL expression instead of datetime.

**Files affected**: `user_profile.py`

**Fix**: Changed to `datetime.now().isoformat()`.

### P1 - High Priority Issues (Fixed)

#### 4. Missing Exception Handling

**Issue**: `int()` conversions without exception handling caused 500 errors on invalid input.

**Files affected**: All view files

**Fix**: Created `safe_int()` utility function:

```python
def safe_int(value: any, default: int = 0) -> int:
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default
```

#### 5. Points API Vulnerability

**Issue**: Any user with `edit` permission could add arbitrary points to themselves.

**Files affected**: `views/user.py`

**Fix**: Changed permission from `edit` to `admin` and added validation:

```python
@view_config(
    name="api-add-points",
    permission="admin",  # Restricted to admin only
)
def api_add_points(context, request):
    if not is_admin(request):
        return {"success": False, "error": "Permission denied"}
    ...
```

### P2 - Medium Priority Issues (Fixed)

#### 6. Missing CSRF Protection

**Issue**: POST forms lacked CSRF token validation.

**Files affected**: All form templates and views

**Fix**: Added CSRF token to forms and validation in views:

```html
<input type="hidden" name="csrf_token" value="${request.session.get('csrf_token', '')}"/>
```

```python
if not validate_csrf_token(request):
    raise HTTPForbidden("Invalid CSRF token")
```

#### 7. Missing Pagination

**Issue**: List views returned all records without pagination, risking memory issues.

**Files affected**: `views/idea.py`, `views/resource.py`, `views/project.py`

**Fix**: Added `Pagination` class and applied to all list views.

## Security Best Practices

### For Developers

1. **Always escape user content**: Never use `structure` in templates unless content has been sanitized.

2. **Validate URLs**: Use `safe_url()` for any user-submitted URLs.

3. **Validate integers**: Use `safe_int()` instead of `int()`.

4. **Limit input length**: Use `truncate_string()` for text inputs.

5. **Protect POST forms**: Always include CSRF token.

6. **Check permissions**: Use `can_edit()` and `is_admin()` helpers.

### For Administrators

1. Review user-submitted content regularly
2. Monitor the notification system for abuse
3. Keep the plugin updated for security patches

## Reporting Security Issues

If you discover a security vulnerability, please report it privately to the maintainers. Do not create a public issue.

## Security Test Coverage

The test suite includes:

- URL validation tests (XSS prevention)
- CSRF token validation tests
- Input validation tests
- Permission check tests

Run tests with:

```bash
python -m unittest discover -s kotti_ai_community/tests -v
```
