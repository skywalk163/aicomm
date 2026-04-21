# -*- coding: utf-8 -*-
"""
Unit tests for CSRF protection
"""

import unittest
from unittest.mock import Mock, MagicMock
import hmac

from kotti_ai_community.utils import (
    get_csrf_token,
    validate_csrf_token,
)


class TestCSRFProtection(unittest.TestCase):
    """Tests for CSRF protection functions."""

    def test_get_csrf_token_generates_new(self):
        """Test that get_csrf_token generates a new token if none exists."""
        request = Mock()
        request.session = {}
        
        token = get_csrf_token(request)
        
        self.assertIsNotNone(token)
        self.assertEqual(len(token), 64)  # 32 bytes hex = 64 chars
        self.assertIn("csrf_token", request.session)

    def test_get_csrf_token_returns_existing(self):
        """Test that get_csrf_token returns existing token."""
        request = Mock()
        request.session = {"csrf_token": "existing_token_123"}
        
        token = get_csrf_token(request)
        
        self.assertEqual(token, "existing_token_123")

    def test_validate_csrf_token_valid(self):
        """Test that validate_csrf_token returns True for valid token."""
        request = Mock()
        request.session = {"csrf_token": "valid_token_123"}
        request.params = {"csrf_token": "valid_token_123"}
        
        result = validate_csrf_token(request)
        
        self.assertTrue(result)

    def test_validate_csrf_token_invalid(self):
        """Test that validate_csrf_token returns False for invalid token."""
        request = Mock()
        request.session = {"csrf_token": "valid_token_123"}
        request.params = {"csrf_token": "invalid_token"}
        
        result = validate_csrf_token(request)
        
        self.assertFalse(result)

    def test_validate_csrf_token_missing_session(self):
        """Test that validate_csrf_token returns False when session token missing."""
        request = Mock()
        request.session = {}
        request.params = {"csrf_token": "some_token"}
        
        result = validate_csrf_token(request)
        
        self.assertFalse(result)

    def test_validate_csrf_token_missing_param(self):
        """Test that validate_csrf_token returns False when param token missing."""
        request = Mock()
        request.session = {"csrf_token": "valid_token_123"}
        request.params = {}
        
        result = validate_csrf_token(request)
        
        self.assertFalse(result)

    def test_validate_csrf_token_explicit_token(self):
        """Test that validate_csrf_token works with explicit token parameter."""
        request = Mock()
        request.session = {"csrf_token": "valid_token_123"}
        
        result = validate_csrf_token(request, token="valid_token_123")
        
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
