"""Personalization service for content adaptation.

Source: US2 - Personalized Chapter Content
Tasks: T036-T039

Delivers chapter content adapted to user's profile:
- Experience level variants (beginner/intermediate/advanced)
- Code language selection (Python/C++/etc.)
- Hardware-specific exercises (simulation/real hardware)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from src.models.user_profile import UserProfile
from src.models.enums import ExperienceLevel, SoftwareBackground, HardwareAccess


class ContentVariant(str, Enum):
    """Content difficulty/depth variants."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CodeLanguage(str, Enum):
    """Supported code example languages."""

    PYTHON = "python"
    CPP = "cpp"
    BOTH = "both"  # Show both languages


class HardwareVariant(str, Enum):
    """Hardware exercise variants."""

    SIMULATION = "simulation"
    RASPBERRY_PI = "raspberry_pi"
    JETSON = "jetson"
    ROBOT_ARM = "robot_arm"
    HUMANOID = "humanoid"


@dataclass
class PersonalizationSettings:
    """User's personalization settings derived from profile."""

    content_variant: ContentVariant
    preferred_language: CodeLanguage
    available_languages: list[CodeLanguage]
    hardware_variant: HardwareVariant
    available_hardware: list[HardwareVariant]
    show_advanced_topics: bool
    show_hardware_exercises: bool


@dataclass
class ChapterContent:
    """Personalized chapter content."""

    chapter_id: str
    title: str
    variant: ContentVariant
    content_html: str
    code_examples: list[dict]
    exercises: list[dict]
    metadata: dict


@dataclass
class CodeExample:
    """Code example with multiple language variants."""

    example_id: str
    title: str
    description: str
    languages: dict[str, str]  # language -> code
    preferred_language: str
    output: Optional[str] = None


@dataclass
class Exercise:
    """Exercise with hardware variants."""

    exercise_id: str
    title: str
    description: str
    difficulty: str
    hardware_variant: HardwareVariant
    instructions: str
    hints: list[str]
    solution: Optional[str] = None


class PersonalizationService:
    """Service for personalizing content based on user profile.

    T036: Core service creation
    T037: Experience level variant selection
    T038: Code language selection
    T039: Hardware variant selection
    """

    # Mapping from software background to preferred code language
    LANGUAGE_PREFERENCE_MAP = {
        SoftwareBackground.PYTHON.value: CodeLanguage.PYTHON,
        SoftwareBackground.CPP.value: CodeLanguage.CPP,
        SoftwareBackground.JAVASCRIPT_TYPESCRIPT.value: CodeLanguage.PYTHON,  # Default to Python
        SoftwareBackground.ROS_ROS2.value: CodeLanguage.BOTH,  # ROS uses both
        SoftwareBackground.MATLAB.value: CodeLanguage.PYTHON,  # Similar syntax
        SoftwareBackground.NONE_LEARNING.value: CodeLanguage.PYTHON,  # Beginner-friendly
    }

    # Mapping from hardware access to exercise variant
    HARDWARE_VARIANT_MAP = {
        HardwareAccess.SIMULATION_ONLY.value: HardwareVariant.SIMULATION,
        HardwareAccess.ARDUINO_MICROCONTROLLERS.value: HardwareVariant.SIMULATION,
        HardwareAccess.RASPBERRY_PI.value: HardwareVariant.RASPBERRY_PI,
        HardwareAccess.NVIDIA_JETSON.value: HardwareVariant.JETSON,
        HardwareAccess.ROBOT_ARM.value: HardwareVariant.ROBOT_ARM,
        HardwareAccess.HUMANOID_ROBOT.value: HardwareVariant.HUMANOID,
        HardwareAccess.DRONE_UAV.value: HardwareVariant.SIMULATION,
        HardwareAccess.CUSTOM_OTHER.value: HardwareVariant.SIMULATION,
    }

    def __init__(self, profile: Optional[UserProfile] = None):
        """Initialize with optional user profile.

        Args:
            profile: User's profile for personalization. If None, uses defaults.
        """
        self.profile = profile

    def get_settings(self) -> PersonalizationSettings:
        """Get personalization settings based on user profile.

        Returns:
            PersonalizationSettings with all derived preferences
        """
        if not self.profile or not self.profile.profile_completed:
            return self._get_default_settings()

        return PersonalizationSettings(
            content_variant=self._get_content_variant(),
            preferred_language=self._get_preferred_language(),
            available_languages=self._get_available_languages(),
            hardware_variant=self._get_hardware_variant(),
            available_hardware=self._get_available_hardware(),
            show_advanced_topics=self._should_show_advanced(),
            show_hardware_exercises=self._has_hardware_access(),
        )

    def _get_default_settings(self) -> PersonalizationSettings:
        """Get default settings for anonymous or incomplete profiles."""
        return PersonalizationSettings(
            content_variant=ContentVariant.BEGINNER,
            preferred_language=CodeLanguage.PYTHON,
            available_languages=[CodeLanguage.PYTHON, CodeLanguage.CPP],
            hardware_variant=HardwareVariant.SIMULATION,
            available_hardware=[HardwareVariant.SIMULATION],
            show_advanced_topics=False,
            show_hardware_exercises=False,
        )

    def _get_content_variant(self) -> ContentVariant:
        """Select content variant based on experience level (T037).

        Maps experience level to content depth:
        - beginner: Foundational concepts, step-by-step explanations
        - intermediate: Standard content with practical examples
        - advanced: Deep dives, research references, optimizations
        """
        if not self.profile or not self.profile.experience_level:
            return ContentVariant.BEGINNER

        level = self.profile.experience_level
        if level == ExperienceLevel.BEGINNER.value:
            return ContentVariant.BEGINNER
        elif level == ExperienceLevel.INTERMEDIATE.value:
            return ContentVariant.INTERMEDIATE
        elif level == ExperienceLevel.ADVANCED.value:
            return ContentVariant.ADVANCED

        return ContentVariant.BEGINNER

    def _get_preferred_language(self) -> CodeLanguage:
        """Select preferred code language based on software background (T038).

        Priority order:
        1. C++ if user has C++ experience
        2. Python if user has Python experience
        3. Both if user has ROS experience
        4. Default to Python for beginners
        """
        if not self.profile or not self.profile.software_background:
            return CodeLanguage.PYTHON

        backgrounds = self.profile.software_background

        # ROS users typically work with both languages
        if SoftwareBackground.ROS_ROS2.value in backgrounds:
            return CodeLanguage.BOTH

        # Prefer C++ if user knows it
        if SoftwareBackground.CPP.value in backgrounds:
            return CodeLanguage.CPP

        # Default to Python (most common for robotics learning)
        return CodeLanguage.PYTHON

    def _get_available_languages(self) -> list[CodeLanguage]:
        """Get list of languages the user is comfortable with."""
        if not self.profile or not self.profile.software_background:
            return [CodeLanguage.PYTHON]

        languages = []
        backgrounds = self.profile.software_background

        if SoftwareBackground.PYTHON.value in backgrounds:
            languages.append(CodeLanguage.PYTHON)
        if SoftwareBackground.CPP.value in backgrounds:
            languages.append(CodeLanguage.CPP)

        # Always include Python as fallback
        if CodeLanguage.PYTHON not in languages:
            languages.append(CodeLanguage.PYTHON)

        return languages

    def _get_hardware_variant(self) -> HardwareVariant:
        """Select hardware variant based on hardware access (T039).

        Priority order (most capable first):
        1. Humanoid robot
        2. Robot arm
        3. Jetson (GPU compute)
        4. Raspberry Pi
        5. Simulation (default)
        """
        if not self.profile or not self.profile.hardware_access:
            return HardwareVariant.SIMULATION

        hardware = self.profile.hardware_access

        # Priority order from most to least capable
        if HardwareAccess.HUMANOID_ROBOT.value in hardware:
            return HardwareVariant.HUMANOID
        if HardwareAccess.ROBOT_ARM.value in hardware:
            return HardwareVariant.ROBOT_ARM
        if HardwareAccess.NVIDIA_JETSON.value in hardware:
            return HardwareVariant.JETSON
        if HardwareAccess.RASPBERRY_PI.value in hardware:
            return HardwareVariant.RASPBERRY_PI

        return HardwareVariant.SIMULATION

    def _get_available_hardware(self) -> list[HardwareVariant]:
        """Get list of hardware variants available to user."""
        if not self.profile or not self.profile.hardware_access:
            return [HardwareVariant.SIMULATION]

        variants = [HardwareVariant.SIMULATION]  # Always available
        hardware = self.profile.hardware_access

        for hw in hardware:
            if hw in self.HARDWARE_VARIANT_MAP:
                variant = self.HARDWARE_VARIANT_MAP[hw]
                if variant not in variants:
                    variants.append(variant)

        return variants

    def _should_show_advanced(self) -> bool:
        """Determine if advanced topics should be shown."""
        if not self.profile:
            return False
        return self.profile.experience_level == ExperienceLevel.ADVANCED.value

    def _has_hardware_access(self) -> bool:
        """Check if user has any real hardware access."""
        if not self.profile or not self.profile.hardware_access:
            return False

        # Check for any hardware beyond simulation
        return any(
            hw != HardwareAccess.SIMULATION_ONLY.value
            for hw in self.profile.hardware_access
        )

    def personalize_chapter(
        self,
        chapter_id: str,
        chapter_data: dict,
    ) -> ChapterContent:
        """Personalize chapter content for the user.

        Args:
            chapter_id: Chapter identifier
            chapter_data: Raw chapter data with all variants

        Returns:
            ChapterContent with appropriate variant selected
        """
        settings = self.get_settings()

        # Select content variant
        variant_key = settings.content_variant.value
        content = chapter_data.get("variants", {}).get(
            variant_key, chapter_data.get("content", "")
        )

        # Filter code examples to preferred language
        code_examples = self._filter_code_examples(
            chapter_data.get("code_examples", []),
            settings.preferred_language,
        )

        # Filter exercises to available hardware
        exercises = self._filter_exercises(
            chapter_data.get("exercises", []),
            settings.available_hardware,
        )

        return ChapterContent(
            chapter_id=chapter_id,
            title=chapter_data.get("title", ""),
            variant=settings.content_variant,
            content_html=content,
            code_examples=code_examples,
            exercises=exercises,
            metadata={
                "preferred_language": settings.preferred_language.value,
                "hardware_variant": settings.hardware_variant.value,
                "show_advanced": settings.show_advanced_topics,
            },
        )

    def _filter_code_examples(
        self,
        examples: list[dict],
        preferred: CodeLanguage,
    ) -> list[dict]:
        """Filter and order code examples by preferred language."""
        result = []
        for example in examples:
            languages = example.get("languages", {})
            if preferred == CodeLanguage.BOTH:
                # Show all available languages
                result.append({
                    **example,
                    "preferred": "python" if "python" in languages else list(languages.keys())[0],
                })
            elif preferred.value in languages:
                result.append({
                    **example,
                    "preferred": preferred.value,
                })
            elif languages:
                # Fallback to first available
                result.append({
                    **example,
                    "preferred": list(languages.keys())[0],
                })
        return result

    def _filter_exercises(
        self,
        exercises: list[dict],
        available_hardware: list[HardwareVariant],
    ) -> list[dict]:
        """Filter exercises to available hardware platforms."""
        available_values = [h.value for h in available_hardware]
        return [
            ex for ex in exercises
            if ex.get("hardware_variant", "simulation") in available_values
        ]

    def get_code_example(
        self,
        example_id: str,
        example_data: dict,
    ) -> CodeExample:
        """Get personalized code example.

        Args:
            example_id: Example identifier
            example_data: Raw example data with all language variants

        Returns:
            CodeExample with preferred language highlighted
        """
        settings = self.get_settings()

        languages = example_data.get("languages", {})
        preferred = settings.preferred_language.value

        # Ensure preferred language exists, fallback to python
        if preferred not in languages and preferred != "both":
            preferred = "python" if "python" in languages else list(languages.keys())[0]

        return CodeExample(
            example_id=example_id,
            title=example_data.get("title", ""),
            description=example_data.get("description", ""),
            languages=languages,
            preferred_language=preferred,
            output=example_data.get("output"),
        )

    def get_exercise(
        self,
        exercise_id: str,
        exercise_data: dict,
    ) -> Exercise:
        """Get exercise with appropriate hardware variant.

        Args:
            exercise_id: Exercise identifier
            exercise_data: Raw exercise data

        Returns:
            Exercise with hardware variant info
        """
        settings = self.get_settings()

        # Determine hardware variant for this exercise
        exercise_hw = exercise_data.get("hardware_variant", "simulation")
        variant = HardwareVariant(exercise_hw) if exercise_hw in [h.value for h in HardwareVariant] else HardwareVariant.SIMULATION

        return Exercise(
            exercise_id=exercise_id,
            title=exercise_data.get("title", ""),
            description=exercise_data.get("description", ""),
            difficulty=exercise_data.get("difficulty", "beginner"),
            hardware_variant=variant,
            instructions=exercise_data.get("instructions", ""),
            hints=exercise_data.get("hints", []),
            solution=exercise_data.get("solution") if settings.show_advanced_topics else None,
        )
