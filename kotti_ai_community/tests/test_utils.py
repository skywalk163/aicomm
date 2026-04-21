# -*- coding: utf-8 -*-
"""
Unit tests for utility functions
"""

import unittest
from kotti_ai_community.utils import (
    safe_url,
    sanitize_social_link,
    safe_int,
    truncate_string,
    Pagination,
)


class TestSafeUrl(unittest.TestCase):
    """Tests for safe_url function."""

    def test_valid_http_url(self):
        """Test that valid HTTP URLs are accepted."""
        self.assertEqual(
            safe_url("http://example.com"),
            "http://example.com"
        )

    def test_valid_https_url(self):
        """Test that valid HTTPS URLs are accepted."""
        self.assertEqual(
            safe_url("https://example.com"),
            "https://example.com"
        )

    def test_javascript_url_blocked(self):
        """Test that javascript: URLs are blocked."""
        self.assertEqual(
            safe_url("javascript:alert('xss')"),
            ""
        )

    def test_javascript_url_case_insensitive(self):
        """Test that JavaScript: URLs are blocked (case insensitive)."""
        self.assertEqual(
            safe_url("JavaScript:alert('xss')"),
            ""
        )

    def test_data_url_blocked(self):
        """Test that data: URLs are blocked."""
        self.assertEqual(
            safe_url("data:text/html,<script>alert('xss')</script>"),
            ""
        )

    def test_empty_url(self):
        """Test that empty URLs return empty string."""
        self.assertEqual(safe_url(""), "")
        self.assertEqual(safe_url(None), "")

    def test_url_with_whitespace(self):
        """Test that URLs with whitespace are trimmed."""
        self.assertEqual(
            safe_url("  https://example.com  "),
            "https://example.com"
        )


class TestSanitizeSocialLink(unittest.TestCase):
    """Tests for sanitize_social_link function."""

    def test_github_link(self):
        """Test GitHub link generation."""
        self.assertEqual(
            sanitize_social_link("github", "testuser"),
            "https://github.com/testuser"
        )

    def test_twitter_link(self):
        """Test Twitter link generation."""
        self.assertEqual(
            sanitize_social_link("twitter", "testuser"),
            "https://twitter.com/testuser"
        )

    def test_linkedin_link(self):
        """Test LinkedIn link generation."""
        self.assertEqual(
            sanitize_social_link("linkedin", "testuser"),
            "https://linkedin.com/in/testuser"
        )

    def test_at_prefix_removed(self):
        """Test that @ prefix is removed."""
        self.assertEqual(
            sanitize_social_link("twitter", "@testuser"),
            "https://twitter.com/testuser"
        )

    def test_invalid_characters_blocked(self):
        """Test that invalid characters are blocked."""
        self.assertEqual(
            sanitize_social_link("github", "test<script>"),
            ""
        )

    def test_empty_value(self):
        """Test that empty values return empty string."""
        self.assertEqual(sanitize_social_link("github", ""), "")
        self.assertEqual(sanitize_social_link("github", None), "")

    def test_unknown_platform(self):
        """Test that unknown platforms return empty string."""
        self.assertEqual(
            sanitize_social_link("unknown", "testuser"),
            ""
        )


class TestSafeInt(unittest.TestCase):
    """Tests for safe_int function."""

    def test_valid_integer(self):
        """Test that valid integers are converted correctly."""
        self.assertEqual(safe_int("123"), 123)
        self.assertEqual(safe_int(456), 456)

    def test_invalid_string(self):
        """Test that invalid strings return default."""
        self.assertEqual(safe_int("abc"), 0)
        self.assertEqual(safe_int("abc", default=10), 10)

    def test_none_value(self):
        """Test that None returns default."""
        self.assertEqual(safe_int(None), 0)
        self.assertEqual(safe_int(None, default=5), 5)

    def test_float_value(self):
        """Test that floats are truncated."""
        self.assertEqual(safe_int(3.14), 3)

    def test_negative_value(self):
        """Test that negative values work correctly."""
        self.assertEqual(safe_int("-5"), -5)


class TestTruncateString(unittest.TestCase):
    """Tests for truncate_string function."""

    def test_short_string(self):
        """Test that short strings are not modified."""
        self.assertEqual(
            truncate_string("short", 100),
            "short"
        )

    def test_long_string(self):
        """Test that long strings are truncated."""
        long_string = "a" * 1000
        result = truncate_string(long_string, 100)
        self.assertEqual(len(result), 100)

    def test_empty_string(self):
        """Test that empty strings return empty."""
        self.assertEqual(truncate_string(""), "")
        self.assertEqual(truncate_string(None), "")

    def test_default_max_length(self):
        """Test default max length."""
        long_string = "a" * 1000
        result = truncate_string(long_string)
        self.assertEqual(len(result), 500)


class TestPagination(unittest.TestCase):
    """Tests for Pagination class."""

    def test_basic_pagination(self):
        """Test basic pagination calculation."""
        pagination = Pagination(total=100, page=1, per_page=20)
        self.assertEqual(pagination.pages, 5)
        self.assertEqual(pagination.offset, 0)
        self.assertTrue(pagination.has_next)
        self.assertFalse(pagination.has_prev)

    def test_second_page(self):
        """Test second page calculation."""
        pagination = Pagination(total=100, page=2, per_page=20)
        self.assertEqual(pagination.offset, 20)
        self.assertTrue(pagination.has_next)
        self.assertTrue(pagination.has_prev)

    def test_last_page(self):
        """Test last page calculation."""
        pagination = Pagination(total=100, page=5, per_page=20)
        self.assertEqual(pagination.pages, 5)
        self.assertFalse(pagination.has_next)
        self.assertTrue(pagination.has_prev)

    def test_empty_result(self):
        """Test pagination with no results."""
        pagination = Pagination(total=0, page=1, per_page=20)
        self.assertEqual(pagination.pages, 1)
        self.assertEqual(pagination.offset, 0)
        self.assertFalse(pagination.has_next)
        self.assertFalse(pagination.has_prev)

    def test_page_bounds(self):
        """Test that page is bounded to minimum 1."""
        pagination = Pagination(total=100, page=0, per_page=20)
        self.assertEqual(pagination.page, 1)

    def test_per_page_bounds(self):
        """Test that per_page is bounded to max 100."""
        pagination = Pagination(total=1000, page=1, per_page=200)
        self.assertEqual(pagination.per_page, 100)

    def test_range_pages(self):
        """Test range_pages method."""
        pagination = Pagination(total=100, page=3, per_page=20)
        pages = pagination.range_pages(window=1)
        self.assertEqual(pages, [2, 3, 4])


if __name__ == "__main__":
    unittest.main()
