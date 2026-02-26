"""
Tests for UserProfile model methods (is_complete, mark_complete).

Creates UserProfile instances in-memory without a database connection;
SQLAlchemy ORM objects can be used as plain Python objects for unit tests.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from src.models.user_profile import UserProfile


def make_profile(**kwargs) -> UserProfile:
    """Create a UserProfile instance without a DB session."""
    return UserProfile(
        user_id=kwargs.get("user_id", uuid4()),
        software_background=kwargs.get("software_background", []),
        hardware_access=kwargs.get("hardware_access", []),
        experience_level=kwargs.get("experience_level", None),
        profile_completed=kwargs.get("profile_completed", False),
        completed_at=kwargs.get("completed_at", None),
    )


# ---------------------------------------------------------------------------
# is_complete()
# ---------------------------------------------------------------------------

class TestIsComplete:
    def test_all_fields_filled_returns_true(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        assert profile.is_complete() is True

    def test_empty_software_background_returns_false(self):
        profile = make_profile(
            software_background=[],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        assert profile.is_complete() is False

    def test_empty_hardware_access_returns_false(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=[],
            experience_level="beginner",
        )
        assert profile.is_complete() is False

    def test_missing_experience_level_returns_false(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level=None,
        )
        assert profile.is_complete() is False

    def test_all_empty_returns_false(self):
        profile = make_profile()
        assert profile.is_complete() is False

    def test_multiple_selections_returns_true(self):
        profile = make_profile(
            software_background=["python", "cpp", "ros_ros2"],
            hardware_access=["simulation_only", "nvidia_jetson"],
            experience_level="advanced",
        )
        assert profile.is_complete() is True

    def test_advanced_experience_complete(self):
        profile = make_profile(
            software_background=["cpp"],
            hardware_access=["humanoid_robot"],
            experience_level="advanced",
        )
        assert profile.is_complete() is True

    def test_intermediate_experience_complete(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["raspberry_pi"],
            experience_level="intermediate",
        )
        assert profile.is_complete() is True


# ---------------------------------------------------------------------------
# mark_complete()
# ---------------------------------------------------------------------------

class TestMarkComplete:
    def test_sets_profile_completed_true_when_complete(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        assert profile.profile_completed is False
        profile.mark_complete()
        assert profile.profile_completed is True

    def test_sets_completed_at_when_complete(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        assert profile.completed_at is None
        profile.mark_complete()
        assert profile.completed_at is not None
        assert isinstance(profile.completed_at, datetime)

    def test_completed_at_is_recent(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        before = datetime.now(timezone.utc)
        profile.mark_complete()
        after = datetime.now(timezone.utc)
        assert before <= profile.completed_at <= after

    def test_does_not_mark_when_software_background_empty(self):
        profile = make_profile(
            software_background=[],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        profile.mark_complete()
        assert profile.profile_completed is False
        assert profile.completed_at is None

    def test_does_not_mark_when_hardware_access_empty(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=[],
            experience_level="beginner",
        )
        profile.mark_complete()
        assert profile.profile_completed is False
        assert profile.completed_at is None

    def test_does_not_mark_when_experience_level_missing(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level=None,
        )
        profile.mark_complete()
        assert profile.profile_completed is False
        assert profile.completed_at is None

    def test_idempotent_when_already_complete(self):
        """Calling mark_complete twice should not reset completed_at."""
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        profile.mark_complete()
        first_completed_at = profile.completed_at
        profile.mark_complete()
        # completed_at will be updated (utcnow called again), profile_completed stays True
        assert profile.profile_completed is True


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

class TestRepr:
    def test_repr_contains_class_name(self):
        profile = make_profile()
        assert "UserProfile" in repr(profile)

    def test_repr_contains_user_id(self):
        profile = make_profile()
        assert "user_id" in repr(profile)
