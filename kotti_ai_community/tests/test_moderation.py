# -*- coding: utf-8 -*-
"""
Tests for content moderation system
"""

import unittest
from unittest.mock import Mock, patch

from kotti_ai_community.moderation import (
    FLAG_REASONS,
    FLAG_STATUS,
    FLAG_ACTIONS,
    ContentFlag,
    is_moderator,
)


class TestFlagReasons(unittest.TestCase):
    """Tests for flag reason constants."""

    def test_reasons_exist(self):
        """Test that all expected reasons are defined."""
        expected_reasons = [
            "spam",
            "inappropriate",
            "harassment",
            "misinformation",
            "copyright",
            "duplicate",
            "other",
        ]
        for reason in expected_reasons:
            self.assertIn(reason, FLAG_REASONS)

    def test_reasons_have_descriptions(self):
        """Test that all reasons have descriptions."""
        for reason, description in FLAG_REASONS.items():
            self.assertIsInstance(description, str)
            self.assertTrue(len(description) > 0)


class TestFlagStatus(unittest.TestCase):
    """Tests for flag status constants."""

    def test_status_values(self):
        """Test that all expected statuses are defined."""
        expected_statuses = ["pending", "reviewed", "resolved", "dismissed"]
        for status in expected_statuses:
            self.assertIn(status, FLAG_STATUS)


class TestFlagActions(unittest.TestCase):
    """Tests for flag action constants."""

    def test_actions_exist(self):
        """Test that all expected actions are defined."""
        expected_actions = ["none", "warning", "content_removed", "user_banned", "content_edited"]
        for action in expected_actions:
            self.assertIn(action, FLAG_ACTIONS)


class TestContentFlagModel(unittest.TestCase):
    """Tests for ContentFlag model."""

    def test_init(self):
        """Test ContentFlag initialization."""
        flag = ContentFlag(
            content_type="idea",
            content_id=1,
            reporter_id=2,
            reason="spam",
            details="This is spam content",
        )

        self.assertEqual(flag.content_type, "idea")
        self.assertEqual(flag.content_id, 1)
        self.assertEqual(flag.reporter_id, 2)
        self.assertEqual(flag.reason, "spam")
        self.assertEqual(flag.details, "This is spam content")
        # Note: status default is set by SQLAlchemy when persisted

    def test_get_reason_display(self):
        """Test get_reason_display method."""
        flag = ContentFlag(
            content_type="idea",
            content_id=1,
            reporter_id=2,
            reason="spam",
        )

        self.assertEqual(flag.get_reason_display(), "Spam or advertising")

    def test_get_status_display(self):
        """Test get_status_display method."""
        flag = ContentFlag(
            content_type="idea",
            content_id=1,
            reporter_id=2,
            reason="spam",
        )
        flag.status = "pending"

        self.assertEqual(flag.get_status_display(), "Pending Review")

    def test_get_action_display(self):
        """Test get_action_display method."""
        flag = ContentFlag(
            content_type="idea",
            content_id=1,
            reporter_id=2,
            reason="spam",
        )
        flag.action_taken = "content_removed"

        self.assertEqual(flag.get_action_display(), "Content removed")


class TestIsModerator(unittest.TestCase):
    """Tests for is_moderator function."""

    def test_not_logged_in(self):
        """Test that non-logged-in users are not moderators."""
        request = Mock()
        request.user = None

        self.assertFalse(is_moderator(request))

    def test_regular_user(self):
        """Test that regular users are not moderators."""
        request = Mock()
        request.user = Mock()
        request.user.groups = ["role:member"]

        self.assertFalse(is_moderator(request))

    def test_admin_is_moderator(self):
        """Test that admins are moderators."""
        request = Mock()
        request.user = Mock()
        request.user.groups = ["role:admin"]

        self.assertTrue(is_moderator(request))

    def test_moderator_role(self):
        """Test that users with moderator role are moderators."""
        request = Mock()
        request.user = Mock()
        request.user.groups = ["role:moderator"]

        self.assertTrue(is_moderator(request))


if __name__ == "__main__":
    unittest.main()
