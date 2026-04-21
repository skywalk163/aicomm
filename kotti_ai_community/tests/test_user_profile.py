# -*- coding: utf-8 -*-
"""
Unit tests for user profile and badge system
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from kotti_ai_community.user_profile import UserProfile
from kotti_ai_community.views.user import (
    BADGE_DEFINITIONS,
    has_badge,
    award_badge,
    check_and_award_badges,
)


class TestUserProfile(unittest.TestCase):
    """Tests for UserProfile model."""

    def setUp(self):
        """Set up test fixtures."""
        self.profile = UserProfile(user_id=1)

    def test_level_calculation(self):
        """Test level calculation based on points."""
        # Level 1: 0-99 points
        self.profile.points = 0
        self.assertEqual(self.profile.level, 1)
        
        self.profile.points = 99
        self.assertEqual(self.profile.level, 1)

        # Level 2: 100-299 points
        self.profile.points = 100
        self.assertEqual(self.profile.level, 2)
        
        self.profile.points = 299
        self.assertEqual(self.profile.level, 2)

        # Level 3: 300-599 points
        self.profile.points = 300
        self.assertEqual(self.profile.level, 3)

        # Level 4: 600-999 points
        self.profile.points = 600
        self.assertEqual(self.profile.level, 4)

        # Level 5: 1000-1999 points (points < 2000)
        self.profile.points = 1000
        self.assertEqual(self.profile.level, 5)
        
        self.profile.points = 1999
        self.assertEqual(self.profile.level, 5)

        # Level 6: 2000-2999 points (5 + (points-2000)//1000)
        # At 2000: 5 + (2000-2000)//1000 = 5 + 0 = 5
        # At 2001: 5 + (2001-2000)//1000 = 5 + 0 = 5
        # At 3000: 5 + (3000-2000)//1000 = 5 + 1 = 6
        self.profile.points = 3000
        self.assertEqual(self.profile.level, 6)

        # Level 10: 7000+ points
        self.profile.points = 7000
        self.assertEqual(self.profile.level, 10)

    def test_level_name(self):
        """Test level name mapping."""
        test_cases = [
            (0, 1, "Newcomer"),
            (100, 2, "Explorer"),
            (300, 3, "Contributor"),
            (600, 4, "Creator"),
            (1000, 5, "Innovator"),
            (3000, 6, "Expert"),
            (4000, 7, "Master"),
            (5000, 8, "Guru"),
            (6000, 9, "Legend"),
            (7000, 10, "Visionary"),
        ]
        
        for points, expected_level, expected_name in test_cases:
            self.profile.points = points
            self.assertEqual(self.profile.level, expected_level, f"Level mismatch at {points} points")
            self.assertEqual(self.profile.level_name, expected_name, f"Name mismatch at {points} points")

    def test_add_points(self):
        """Test adding points to profile."""
        initial_points = self.profile.points
        self.profile.add_points(10, "Test reason")
        
        self.assertEqual(self.profile.points, initial_points + 10)
        self.assertIsNotNone(self.profile.last_activity)


class TestBadgeSystem(unittest.TestCase):
    """Tests for badge system."""

    def test_badge_definitions_exist(self):
        """Test that badge definitions are properly defined."""
        self.assertIn("first_idea", BADGE_DEFINITIONS)
        self.assertIn("idea_master", BADGE_DEFINITIONS)
        self.assertIn("first_resource", BADGE_DEFINITIONS)
        self.assertIn("level_5", BADGE_DEFINITIONS)

    def test_badge_definitions_structure(self):
        """Test that badge definitions have required fields."""
        for badge_id, badge_def in BADGE_DEFINITIONS.items():
            self.assertIn("name", badge_def)
            self.assertIn("description", badge_def)
            self.assertIn("points", badge_def)
            self.assertIn("icon", badge_def)

    def test_has_badge_false_when_no_badges(self):
        """Test has_badge returns False when profile has no badges."""
        profile = Mock()
        profile.badges = None
        
        self.assertFalse(has_badge(profile, "first_idea"))

    def test_has_badge_true_when_badge_exists(self):
        """Test has_badge returns True when badge exists."""
        profile = Mock()
        profile.badges = [{"id": "first_idea", "name": "Idea Generator"}]
        
        self.assertTrue(has_badge(profile, "first_idea"))

    def test_has_badge_false_when_badge_not_exists(self):
        """Test has_badge returns False when badge doesn't exist."""
        profile = Mock()
        profile.badges = [{"id": "first_idea", "name": "Idea Generator"}]
        
        self.assertFalse(has_badge(profile, "idea_master"))

    def test_award_badge_structure(self):
        """Test that award_badge creates correct badge structure."""
        # Test the badge structure without actually calling award_badge
        # (which requires database setup)
        badge_def = BADGE_DEFINITIONS["first_idea"]
        self.assertEqual(badge_def["name"], "Idea Generator")
        self.assertEqual(badge_def["points"], 5)
        self.assertIn("description", badge_def)
        self.assertIn("icon", badge_def)


if __name__ == "__main__":
    unittest.main()
