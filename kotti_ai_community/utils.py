# -*- coding: utf-8 -*-
"""
Utility functions for AI Community

Contains security helpers, permission checks, and common utilities.
"""

import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


# ============================================================================
# Security: URL Validation
# ============================================================================
ALLOWED_URL_SCHEMES = {'http', 'https'}


def safe_url(url: Optional[str]) -> str:
    """Validate and sanitize URL to prevent XSS and phishing.
    
    Only allows http:// and https:// URLs.
    Returns empty string for invalid/unsafe URLs.
    
    Args:
        url: The URL to validate
        
    Returns:
        Safe URL string or empty string if invalid
    """
    if not url:
        return ''
    
    url = url.strip()
    
    # Check for javascript: and other dangerous protocols
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
            return ''
        return url
    except Exception:
        return ''


def sanitize_social_link(platform: str, value: Optional[str]) -> str:
    """Sanitize social media links.
    
    Args:
        platform: Platform name (github, twitter, linkedin, wechat)
        value: The username or value
        
    Returns:
        Full URL or empty string
    """
    if not value:
        return ''
    
    value = value.strip()
    
    # Remove any @ prefix for consistency
    if value.startswith('@'):
        value = value[1:]
    
    # Only allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[\w\-]+$', value):
        return ''
    
    platform_urls = {
        'github': f'https://github.com/{value}',
        'twitter': f'https://twitter.com/{value}',
        'linkedin': f'https://linkedin.com/in/{value}',
    }
    
    return platform_urls.get(platform, '')


# ============================================================================
# Security: Input Validation
# ============================================================================
def safe_int(value: any, default: int = 0) -> int:
    """Safely convert value to integer.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def truncate_string(value: Optional[str], max_length: int = 500) -> str:
    """Truncate string to maximum length.
    
    Args:
        value: String to truncate
        max_length: Maximum allowed length
        
    Returns:
        Truncated string
    """
    if not value:
        return ''
    return value[:max_length] if len(value) > max_length else value


# ============================================================================
# Permission Helpers
# ============================================================================
def can_edit(context, request) -> bool:
    """Check if user can edit the content.
    
    Args:
        context: The content object
        request: The current request
        
    Returns:
        True if user can edit, False otherwise
    """
    user = request.user
    if user is None:
        return False

    # Admin can edit anything
    if "role:admin" in user.groups:
        return True

    # Owner can edit their own content
    if hasattr(context, "owner_id") and context.owner_id == user.id:
        return True

    # Editor role can edit
    if "role:editor" in user.groups:
        return True

    return False


def is_admin(request) -> bool:
    """Check if current user is an admin.
    
    Args:
        request: The current request
        
    Returns:
        True if user is admin, False otherwise
    """
    user = request.user
    if user is None:
        return False
    return "role:admin" in user.groups


# ============================================================================
# Pagination Helper
# ============================================================================
class Pagination:
    """Simple pagination helper."""
    
    def __init__(self, total: int, page: int = 1, per_page: int = 20):
        self.total = total
        self.page = max(1, page)
        self.per_page = max(1, min(100, per_page))  # Max 100 per page
        
    @property
    def pages(self) -> int:
        """Total number of pages."""
        return max(1, (self.total + self.per_page - 1) // self.per_page)
    
    @property
    def offset(self) -> int:
        """Offset for database query."""
        return (self.page - 1) * self.per_page
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages
    
    @property
    def prev_page(self) -> Optional[int]:
        """Previous page number."""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_page(self) -> Optional[int]:
        """Next page number."""
        return self.page + 1 if self.has_next else None
    
    def range_pages(self, window: int = 2) -> list:
        """Get list of page numbers to display.
        
        Args:
            window: Number of pages to show on each side
            
        Returns:
            List of page numbers
        """
        start = max(1, self.page - window)
        end = min(self.pages, self.page + window)
        return list(range(start, end + 1))


# ============================================================================
# Date/Time Helpers
# ============================================================================
def now_iso() -> str:
    """Get current datetime in ISO format.
    
    Returns:
        ISO formatted datetime string
    """
    return datetime.now().isoformat()


def timestamp_now() -> int:
    """Get current Unix timestamp.
    
    Returns:
        Unix timestamp in seconds
    """
    import time
    return int(time.time())


# ============================================================================
# CSRF Protection
# ============================================================================
def get_csrf_token(request) -> str:
    """Get CSRF token from session.
    
    Args:
        request: The current request
        
    Returns:
        CSRF token string
    """
    session = request.session
    token = session.get('csrf_token')
    if not token:
        import secrets
        token = secrets.token_hex(32)
        session['csrf_token'] = token
    return token


def validate_csrf_token(request, token: str = None) -> bool:
    """Validate CSRF token.
    
    Args:
        request: The current request
        token: Token to validate (if None, uses request.params)
        
    Returns:
        True if valid, False otherwise
    """
    if token is None:
        token = request.params.get('csrf_token', '')
    
    session_token = request.session.get('csrf_token', '')
    
    # Use constant-time comparison to prevent timing attacks
    import hmac
    if not token or not session_token:
        return False
    
    return hmac.compare_digest(str(token), str(session_token))


def csrf_protected(view_func):
    """Decorator to protect a view with CSRF validation.
    
    Usage:
        @view_config(...)
        @csrf_protected
        def my_view(context, request):
            ...
    """
    def wrapper(context, request):
        if request.method == 'POST':
            if not validate_csrf_token(request):
                from pyramid.httpexceptions import HTTPForbidden
                raise HTTPForbidden('Invalid CSRF token')
        return view_func(context, request)
    return wrapper
