"""
Tests for PersonalizationService.

All tests run in-memory with no database or external services.
"""

import pytest
from uuid import uuid4

from src.models.user_profile import UserProfile
from src.models.enums import ExperienceLevel, SoftwareBackground, HardwareAccess
from src.services.personalization import (
    PersonalizationService,
    ContentVariant,
    CodeLanguage,
    HardwareVariant,
    PersonalizationSettings,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_profile(**kwargs) -> UserProfile:
    """Create a test UserProfile without a DB session."""
    return UserProfile(
        user_id=kwargs.get("user_id", uuid4()),
        software_background=kwargs.get("software_background", []),
        hardware_access=kwargs.get("hardware_access", []),
        experience_level=kwargs.get("experience_level", None),
        profile_completed=kwargs.get("profile_completed", True),
        completed_at=None,
    )


def beginner_sim_python() -> UserProfile:
    return make_profile(
        software_background=["python"],
        hardware_access=["simulation_only"],
        experience_level="beginner",
    )


def advanced_jetson_cpp() -> UserProfile:
    return make_profile(
        software_background=["cpp"],
        hardware_access=["nvidia_jetson"],
        experience_level="advanced",
    )


# ---------------------------------------------------------------------------
# Default settings (no profile or incomplete profile)
# ---------------------------------------------------------------------------

class TestDefaultSettings:
    def test_no_profile_content_variant_is_beginner(self):
        s = PersonalizationService(profile=None).get_settings()
        assert s.content_variant == ContentVariant.BEGINNER

    def test_no_profile_preferred_language_is_python(self):
        s = PersonalizationService(profile=None).get_settings()
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_no_profile_hardware_variant_is_simulation(self):
        s = PersonalizationService(profile=None).get_settings()
        assert s.hardware_variant == HardwareVariant.SIMULATION

    def test_no_profile_show_advanced_is_false(self):
        s = PersonalizationService(profile=None).get_settings()
        assert s.show_advanced_topics is False

    def test_no_profile_show_hardware_exercises_is_false(self):
        s = PersonalizationService(profile=None).get_settings()
        assert s.show_hardware_exercises is False

    def test_no_profile_available_languages_includes_python(self):
        s = PersonalizationService(profile=None).get_settings()
        assert CodeLanguage.PYTHON in s.available_languages

    def test_no_profile_available_hardware_includes_simulation(self):
        s = PersonalizationService(profile=None).get_settings()
        assert HardwareVariant.SIMULATION in s.available_hardware

    def test_incomplete_profile_uses_defaults(self):
        profile = make_profile(
            software_background=[],
            hardware_access=[],
            experience_level=None,
            profile_completed=False,
        )
        s = PersonalizationService(profile=profile).get_settings()
        assert s.content_variant == ContentVariant.BEGINNER
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_returns_personalization_settings_instance(self):
        s = PersonalizationService(profile=None).get_settings()
        assert isinstance(s, PersonalizationSettings)


# ---------------------------------------------------------------------------
# Content variant selection (experience level → variant)
# ---------------------------------------------------------------------------

class TestContentVariant:
    def test_beginner_maps_to_beginner_variant(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert s.content_variant == ContentVariant.BEGINNER

    def test_intermediate_maps_to_intermediate_variant(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.content_variant == ContentVariant.INTERMEDIATE

    def test_advanced_maps_to_advanced_variant(self):
        s = PersonalizationService(advanced_jetson_cpp()).get_settings()
        assert s.content_variant == ContentVariant.ADVANCED


# ---------------------------------------------------------------------------
# Preferred language selection (software background → language)
# ---------------------------------------------------------------------------

class TestPreferredLanguage:
    def test_python_background_prefers_python(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_cpp_background_prefers_cpp(self):
        profile = make_profile(
            software_background=["cpp"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.CPP

    def test_ros_background_prefers_both(self):
        profile = make_profile(
            software_background=["ros_ros2"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.BOTH

    def test_ros_overrides_cpp_preference(self):
        """ROS/ROS2 should win over C++ when both are present."""
        profile = make_profile(
            software_background=["cpp", "ros_ros2"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.BOTH

    def test_javascript_defaults_to_python(self):
        profile = make_profile(
            software_background=["javascript_typescript"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_matlab_defaults_to_python(self):
        profile = make_profile(
            software_background=["matlab"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_none_learning_defaults_to_python(self):
        profile = make_profile(
            software_background=["none_learning"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.PYTHON

    def test_python_and_cpp_cpp_preferred_over_python(self):
        """With both Python and C++ (no ROS), C++ should be preferred."""
        profile = make_profile(
            software_background=["python", "cpp"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.preferred_language == CodeLanguage.CPP


# ---------------------------------------------------------------------------
# Hardware variant selection (priority order)
# ---------------------------------------------------------------------------

class TestHardwareVariant:
    def test_humanoid_is_highest_priority(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["humanoid_robot", "nvidia_jetson", "raspberry_pi"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.HUMANOID

    def test_robot_arm_beats_jetson(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["robot_arm", "nvidia_jetson"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.ROBOT_ARM

    def test_jetson_beats_raspberry_pi(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["nvidia_jetson", "raspberry_pi"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.JETSON

    def test_raspberry_pi_variant(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["raspberry_pi"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.RASPBERRY_PI

    def test_simulation_only_gives_simulation(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert s.hardware_variant == HardwareVariant.SIMULATION

    def test_drone_maps_to_simulation(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["drone_uav"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.SIMULATION

    def test_arduino_maps_to_simulation(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["arduino_microcontrollers"],
            experience_level="beginner",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.hardware_variant == HardwareVariant.SIMULATION


# ---------------------------------------------------------------------------
# Advanced topics visibility
# ---------------------------------------------------------------------------

class TestShowAdvancedTopics:
    def test_advanced_user_sees_advanced_topics(self):
        s = PersonalizationService(advanced_jetson_cpp()).get_settings()
        assert s.show_advanced_topics is True

    def test_beginner_does_not_see_advanced_topics(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert s.show_advanced_topics is False

    def test_intermediate_does_not_see_advanced_topics(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.show_advanced_topics is False


# ---------------------------------------------------------------------------
# Hardware exercises visibility
# ---------------------------------------------------------------------------

class TestShowHardwareExercises:
    def test_simulation_only_no_hardware_exercises(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert s.show_hardware_exercises is False

    def test_real_hardware_enables_hardware_exercises(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["raspberry_pi"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.show_hardware_exercises is True

    def test_mixed_sim_and_real_hardware_shows_exercises(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["simulation_only", "nvidia_jetson"],
            experience_level="intermediate",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.show_hardware_exercises is True

    def test_humanoid_shows_hardware_exercises(self):
        profile = make_profile(
            software_background=["python"],
            hardware_access=["humanoid_robot"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert s.show_hardware_exercises is True


# ---------------------------------------------------------------------------
# Available languages list
# ---------------------------------------------------------------------------

class TestAvailableLanguages:
    def test_python_only_background_gives_python(self):
        s = PersonalizationService(beginner_sim_python()).get_settings()
        assert CodeLanguage.PYTHON in s.available_languages

    def test_cpp_only_still_includes_python_as_fallback(self):
        profile = make_profile(
            software_background=["cpp"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert CodeLanguage.PYTHON in s.available_languages
        assert CodeLanguage.CPP in s.available_languages

    def test_python_and_cpp_includes_both(self):
        profile = make_profile(
            software_background=["python", "cpp"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        s = PersonalizationService(profile).get_settings()
        assert CodeLanguage.PYTHON in s.available_languages
        assert CodeLanguage.CPP in s.available_languages


# ---------------------------------------------------------------------------
# personalize_chapter()
# ---------------------------------------------------------------------------

class TestPersonalizeChapter:
    def _make_chapter(self, **kwargs):
        base = {
            "title": "Test Chapter",
            "content": "<p>Default content</p>",
            "code_examples": [],
            "exercises": [],
        }
        base.update(kwargs)
        return base

    def test_selects_beginner_variant_for_beginner(self):
        chapter = self._make_chapter(
            variants={
                "beginner": "<p>Beginner</p>",
                "intermediate": "<p>Intermediate</p>",
                "advanced": "<p>Advanced</p>",
            }
        )
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch1", chapter)
        assert result.content_html == "<p>Beginner</p>"

    def test_selects_advanced_variant_for_advanced(self):
        chapter = self._make_chapter(
            variants={
                "beginner": "<p>Beginner</p>",
                "advanced": "<p>Advanced</p>",
            }
        )
        result = PersonalizationService(advanced_jetson_cpp()).personalize_chapter("ch1", chapter)
        assert result.content_html == "<p>Advanced</p>"

    def test_falls_back_to_content_when_no_variants(self):
        chapter = self._make_chapter(content="<p>Default</p>")
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch1", chapter)
        assert result.content_html == "<p>Default</p>"

    def test_preserves_chapter_id_and_title(self):
        chapter = self._make_chapter(title="ROS 2 Basics")
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch-ros2-01", chapter)
        assert result.chapter_id == "ch-ros2-01"
        assert result.title == "ROS 2 Basics"

    def test_includes_variant_in_result(self):
        chapter = self._make_chapter()
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch1", chapter)
        assert result.variant == ContentVariant.BEGINNER

    def test_filters_exercises_by_hardware(self):
        chapter = self._make_chapter(
            exercises=[
                {"id": "ex1", "hardware_variant": "simulation"},
                {"id": "ex2", "hardware_variant": "jetson"},
                {"id": "ex3", "hardware_variant": "simulation"},
            ]
        )
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch1", chapter)
        assert len(result.exercises) == 2
        assert all(ex["hardware_variant"] == "simulation" for ex in result.exercises)

    def test_metadata_includes_expected_keys(self):
        chapter = self._make_chapter()
        result = PersonalizationService(beginner_sim_python()).personalize_chapter("ch1", chapter)
        assert "preferred_language" in result.metadata
        assert "hardware_variant" in result.metadata
        assert "show_advanced" in result.metadata


# ---------------------------------------------------------------------------
# _filter_code_examples()
# ---------------------------------------------------------------------------

class TestFilterCodeExamples:
    def _service(self, **profile_kwargs):
        return PersonalizationService(make_profile(**profile_kwargs))

    def test_filters_to_python_examples(self):
        service = self._service(
            software_background=["python"],
            hardware_access=["simulation_only"],
            experience_level="beginner",
        )
        examples = [
            {"id": "ex1", "languages": {"python": "print()", "cpp": "cout;"}},
            {"id": "ex2", "languages": {"python": "x = 1"}},
        ]
        result = service._filter_code_examples(examples, CodeLanguage.PYTHON)
        assert len(result) == 2
        assert all(e["preferred"] == "python" for e in result)

    def test_filters_to_cpp_examples(self):
        service = self._service(
            software_background=["cpp"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        examples = [
            {"id": "ex1", "languages": {"python": "print()", "cpp": "cout;"}},
        ]
        result = service._filter_code_examples(examples, CodeLanguage.CPP)
        assert result[0]["preferred"] == "cpp"

    def test_fallback_to_first_language_if_preferred_not_found(self):
        service = self._service(
            software_background=["cpp"],
            hardware_access=["simulation_only"],
            experience_level="advanced",
        )
        examples = [
            {"id": "ex1", "languages": {"python": "print()"}},  # no cpp
        ]
        result = service._filter_code_examples(examples, CodeLanguage.CPP)
        assert result[0]["preferred"] == "python"

    def test_both_language_shows_all_examples(self):
        service = self._service(
            software_background=["ros_ros2"],
            hardware_access=["simulation_only"],
            experience_level="intermediate",
        )
        examples = [
            {"id": "ex1", "languages": {"python": "print()", "cpp": "cout;"}},
        ]
        result = service._filter_code_examples(examples, CodeLanguage.BOTH)
        assert len(result) == 1
        assert result[0]["preferred"] == "python"  # default for BOTH

    def test_empty_examples_returns_empty(self):
        service = PersonalizationService(profile=None)
        result = service._filter_code_examples([], CodeLanguage.PYTHON)
        assert result == []


# ---------------------------------------------------------------------------
# get_code_example()
# ---------------------------------------------------------------------------

class TestGetCodeExample:
    def test_returns_code_example_with_preferred_language(self):
        service = PersonalizationService(beginner_sim_python())
        example_data = {
            "title": "Hello World",
            "description": "Basic output",
            "languages": {"python": "print('Hello')", "cpp": "cout << 'Hello';"},
            "output": "Hello",
        }
        result = service.get_code_example("ex1", example_data)
        assert result.example_id == "ex1"
        assert result.title == "Hello World"
        assert result.preferred_language == "python"
        assert result.output == "Hello"

    def test_falls_back_when_preferred_language_unavailable(self):
        service = PersonalizationService(
            make_profile(
                software_background=["cpp"],
                hardware_access=["simulation_only"],
                experience_level="advanced",
            )
        )
        example_data = {
            "title": "Python Only",
            "description": "No C++",
            "languages": {"python": "print()"},
        }
        result = service.get_code_example("ex1", example_data)
        assert result.preferred_language == "python"

    def test_output_is_none_when_not_provided(self):
        service = PersonalizationService(beginner_sim_python())
        example_data = {
            "title": "No output",
            "description": "An example",
            "languages": {"python": "x = 1"},
        }
        result = service.get_code_example("ex1", example_data)
        assert result.output is None


# ---------------------------------------------------------------------------
# get_exercise()
# ---------------------------------------------------------------------------

class TestGetExercise:
    def test_advanced_user_sees_solution(self):
        service = PersonalizationService(advanced_jetson_cpp())
        exercise_data = {
            "title": "Hard Exercise",
            "description": "Difficult",
            "difficulty": "advanced",
            "hardware_variant": "simulation",
            "instructions": "Do this",
            "hints": ["Hint 1"],
            "solution": "The answer",
        }
        result = service.get_exercise("ex1", exercise_data)
        assert result.solution == "The answer"

    def test_beginner_does_not_see_solution(self):
        service = PersonalizationService(beginner_sim_python())
        exercise_data = {
            "title": "Basic Exercise",
            "description": "Simple",
            "difficulty": "beginner",
            "hardware_variant": "simulation",
            "instructions": "Follow these steps",
            "hints": [],
            "solution": "The answer",
        }
        result = service.get_exercise("ex1", exercise_data)
        assert result.solution is None

    def test_exercise_fields_populated(self):
        service = PersonalizationService(beginner_sim_python())
        exercise_data = {
            "title": "My Exercise",
            "description": "Do the thing",
            "difficulty": "beginner",
            "hardware_variant": "simulation",
            "instructions": "Step by step",
            "hints": ["Check the docs", "Try again"],
        }
        result = service.get_exercise("ex42", exercise_data)
        assert result.exercise_id == "ex42"
        assert result.title == "My Exercise"
        assert result.difficulty == "beginner"
        assert len(result.hints) == 2
        assert result.hardware_variant == HardwareVariant.SIMULATION

    def test_hardware_variant_mapped_correctly(self):
        service = PersonalizationService(advanced_jetson_cpp())
        exercise_data = {
            "title": "Jetson Exercise",
            "description": "GPU stuff",
            "difficulty": "advanced",
            "hardware_variant": "jetson",
            "instructions": "Run on Jetson",
            "hints": [],
        }
        result = service.get_exercise("ex1", exercise_data)
        assert result.hardware_variant == HardwareVariant.JETSON

    def test_unknown_hardware_variant_falls_back_to_simulation(self):
        service = PersonalizationService(beginner_sim_python())
        exercise_data = {
            "title": "Exercise",
            "description": "Desc",
            "difficulty": "beginner",
            "hardware_variant": "alien_robot",  # unknown
            "instructions": "Do it",
            "hints": [],
        }
        result = service.get_exercise("ex1", exercise_data)
        assert result.hardware_variant == HardwareVariant.SIMULATION
