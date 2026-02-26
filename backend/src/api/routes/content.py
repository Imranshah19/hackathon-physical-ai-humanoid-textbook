"""Content API routes for personalized chapter content.

Source: US2 - Personalized Chapter Content
Tasks: T040-T042, T048-T049
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.middleware.auth import get_current_user, get_optional_user
from src.db.postgres import get_db_session
from src.services.profile import ProfileService
from src.services.personalization import (
    PersonalizationService,
    ContentVariant,
    CodeLanguage,
    HardwareVariant,
)

router = APIRouter(prefix="/api/content", tags=["content"])


# Response models
class PersonalizationSettingsResponse(BaseModel):
    """User's personalization settings."""

    content_variant: str
    preferred_language: str
    available_languages: list[str]
    hardware_variant: str
    available_hardware: list[str]
    show_advanced_topics: bool
    show_hardware_exercises: bool


class CodeExampleResponse(BaseModel):
    """Code example with language variants."""

    example_id: str
    title: str
    description: str
    languages: dict[str, str]
    preferred_language: str
    output: Optional[str] = None


class ExerciseResponse(BaseModel):
    """Exercise with hardware variant."""

    exercise_id: str
    title: str
    description: str
    difficulty: str
    hardware_variant: str
    instructions: str
    hints: list[str]
    solution: Optional[str] = None


class ChapterContentResponse(BaseModel):
    """Personalized chapter content."""

    chapter_id: str
    title: str
    variant: str
    content_html: str
    code_examples: list[dict]
    exercises: list[dict]
    metadata: dict


class PreferencesUpdateRequest(BaseModel):
    """Request to update content preferences."""

    content_variant: Optional[str] = None
    preferred_language: Optional[str] = None
    hardware_variant: Optional[str] = None


class PreferencesResponse(BaseModel):
    """User's content preferences."""

    content_variant: str
    preferred_language: str
    hardware_variant: str
    auto_personalize: bool = True


# Sample chapter data (in production, this would come from database or CMS)
SAMPLE_CHAPTERS = {
    "01-introduction": {
        "title": "Introduction to Physical AI",
        "variants": {
            "beginner": """
                <h2>Welcome to Physical AI</h2>
                <p>Physical AI combines artificial intelligence with robotics to create
                intelligent machines that can interact with the real world.</p>
                <p>In this chapter, we'll start with the basics and build up your understanding
                step by step.</p>
                <h3>What You'll Learn</h3>
                <ul>
                    <li>What is Physical AI?</li>
                    <li>Key components of robotic systems</li>
                    <li>Your first simulation environment</li>
                </ul>
            """,
            "intermediate": """
                <h2>Physical AI Fundamentals</h2>
                <p>Physical AI integrates perception, planning, and control systems to enable
                autonomous behavior in robotic platforms.</p>
                <p>This chapter covers the core architecture and design patterns used in
                modern robotic systems.</p>
                <h3>Topics Covered</h3>
                <ul>
                    <li>Sense-Plan-Act architecture</li>
                    <li>Real-time control loops</li>
                    <li>Sensor fusion techniques</li>
                    <li>Setting up development environments</li>
                </ul>
            """,
            "advanced": """
                <h2>Physical AI: Architecture and Implementation</h2>
                <p>This chapter provides a comprehensive overview of physical AI systems,
                including state-of-the-art approaches and research directions.</p>
                <h3>Advanced Topics</h3>
                <ul>
                    <li>Hierarchical control architectures</li>
                    <li>Learning-based control policies</li>
                    <li>Sim-to-real transfer techniques</li>
                    <li>Safety-critical system design</li>
                    <li>Current research frontiers</li>
                </ul>
            """,
        },
        "code_examples": [
            {
                "id": "ex-01-hello-robot",
                "title": "Hello Robot",
                "description": "Your first robot control script",
                "languages": {
                    "python": '''import rclpy
from rclpy.node import Node

class HelloRobot(Node):
    def __init__(self):
        super().__init__('hello_robot')
        self.get_logger().info('Hello, Robot World!')

def main():
    rclpy.init()
    node = HelloRobot()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()''',
                    "cpp": '''#include <rclcpp/rclcpp.hpp>

class HelloRobot : public rclcpp::Node {
public:
    HelloRobot() : Node("hello_robot") {
        RCLCPP_INFO(this->get_logger(), "Hello, Robot World!");
    }
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<HelloRobot>());
    rclcpp::shutdown();
    return 0;
}''',
                },
                "output": "Hello, Robot World!",
            },
        ],
        "exercises": [
            {
                "id": "exercise-01-sim",
                "title": "Launch Your First Simulation",
                "description": "Set up and run a basic robot simulation",
                "difficulty": "beginner",
                "hardware_variant": "simulation",
                "instructions": "1. Install Gazebo\n2. Launch the demo world\n3. Observe the robot",
                "hints": ["Use 'ros2 launch' command", "Check the Gazebo GUI"],
            },
            {
                "id": "exercise-01-pi",
                "title": "Raspberry Pi LED Control",
                "description": "Control an LED using ROS2 on Raspberry Pi",
                "difficulty": "beginner",
                "hardware_variant": "raspberry_pi",
                "instructions": "1. Connect LED to GPIO\n2. Write a ROS2 node\n3. Toggle the LED",
                "hints": ["Use RPi.GPIO library", "Publish to /led_state topic"],
            },
        ],
    },
}


async def get_personalization_service(
    user_id: Optional[UUID],
    db: AsyncSession,
) -> PersonalizationService:
    """Get personalization service with user profile if authenticated."""
    if not user_id:
        return PersonalizationService(profile=None)

    profile_service = ProfileService(db)
    profile = await profile_service.get_profile(user_id)
    return PersonalizationService(profile=profile)


@router.get("/chapter/{chapter_id}", response_model=ChapterContentResponse)
async def get_chapter_content(
    chapter_id: str,
    variant: Optional[str] = Query(None, description="Override content variant"),
    user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get personalized chapter content (T040).

    Returns chapter content adapted to user's profile:
    - Experience level determines content depth
    - Software background determines code language
    - Hardware access determines exercise variants

    Anonymous users get beginner-level content with Python examples.
    """
    # Get chapter data
    chapter_data = SAMPLE_CHAPTERS.get(chapter_id)
    if not chapter_data:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_id}' not found")

    # Get personalization service
    user_id = UUID(user["id"]) if user else None
    service = await get_personalization_service(user_id, db)

    # Personalize content
    content = service.personalize_chapter(chapter_id, chapter_data)

    # Override variant if specified
    if variant and variant in ["beginner", "intermediate", "advanced"]:
        variant_content = chapter_data.get("variants", {}).get(variant, content.content_html)
        return ChapterContentResponse(
            chapter_id=content.chapter_id,
            title=content.title,
            variant=variant,
            content_html=variant_content,
            code_examples=content.code_examples,
            exercises=content.exercises,
            metadata={**content.metadata, "variant_override": True},
        )

    return ChapterContentResponse(
        chapter_id=content.chapter_id,
        title=content.title,
        variant=content.variant.value,
        content_html=content.content_html,
        code_examples=content.code_examples,
        exercises=content.exercises,
        metadata=content.metadata,
    )


@router.get("/code-example/{example_id}", response_model=CodeExampleResponse)
async def get_code_example(
    example_id: str,
    language: Optional[str] = Query(None, description="Override language"),
    user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get code example with preferred language (T041).

    Returns code example with language variants.
    Preferred language is based on user's software background.
    """
    # Find example in all chapters (in production, use proper indexing)
    example_data = None
    for chapter in SAMPLE_CHAPTERS.values():
        for ex in chapter.get("code_examples", []):
            if ex.get("id") == example_id:
                example_data = ex
                break
        if example_data:
            break

    if not example_data:
        raise HTTPException(status_code=404, detail=f"Code example '{example_id}' not found")

    # Get personalization
    user_id = UUID(user["id"]) if user else None
    service = await get_personalization_service(user_id, db)
    example = service.get_code_example(example_id, example_data)

    # Override language if specified
    preferred = language if language and language in example.languages else example.preferred_language

    return CodeExampleResponse(
        example_id=example.example_id,
        title=example.title,
        description=example.description,
        languages=example.languages,
        preferred_language=preferred,
        output=example.output,
    )


@router.get("/exercise/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get exercise with hardware variant (T042).

    Returns exercise appropriate for user's hardware access.
    """
    # Find exercise in all chapters
    exercise_data = None
    for chapter in SAMPLE_CHAPTERS.values():
        for ex in chapter.get("exercises", []):
            if ex.get("id") == exercise_id:
                exercise_data = ex
                break
        if exercise_data:
            break

    if not exercise_data:
        raise HTTPException(status_code=404, detail=f"Exercise '{exercise_id}' not found")

    # Get personalization
    user_id = UUID(user["id"]) if user else None
    service = await get_personalization_service(user_id, db)
    exercise = service.get_exercise(exercise_id, exercise_data)

    return ExerciseResponse(
        exercise_id=exercise.exercise_id,
        title=exercise.title,
        description=exercise.description,
        difficulty=exercise.difficulty,
        hardware_variant=exercise.hardware_variant.value,
        instructions=exercise.instructions,
        hints=exercise.hints,
        solution=exercise.solution,
    )


@router.get("/preferences", response_model=PreferencesResponse)
async def get_preferences(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get user's content preferences (T048).

    Returns current personalization settings derived from profile.
    """
    user_id = UUID(user["id"])
    service = await get_personalization_service(user_id, db)
    settings = service.get_settings()

    return PreferencesResponse(
        content_variant=settings.content_variant.value,
        preferred_language=settings.preferred_language.value,
        hardware_variant=settings.hardware_variant.value,
        auto_personalize=True,
    )


@router.patch("/preferences", response_model=PreferencesResponse)
async def update_preferences(
    request: PreferencesUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update user's content preferences (T049).

    Allows manual override of personalization settings.
    These are session-level overrides (not persisted to profile).
    """
    # Validate inputs
    if request.content_variant and request.content_variant not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(status_code=400, detail="Invalid content variant")

    if request.preferred_language and request.preferred_language not in ["python", "cpp", "both"]:
        raise HTTPException(status_code=400, detail="Invalid language preference")

    if request.hardware_variant and request.hardware_variant not in [h.value for h in HardwareVariant]:
        raise HTTPException(status_code=400, detail="Invalid hardware variant")

    # Get current settings
    user_id = UUID(user["id"])
    service = await get_personalization_service(user_id, db)
    settings = service.get_settings()

    # Apply overrides
    return PreferencesResponse(
        content_variant=request.content_variant or settings.content_variant.value,
        preferred_language=request.preferred_language or settings.preferred_language.value,
        hardware_variant=request.hardware_variant or settings.hardware_variant.value,
        auto_personalize=False,  # Manual override active
    )


@router.get("/settings", response_model=PersonalizationSettingsResponse)
async def get_personalization_settings(
    user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get full personalization settings.

    Returns all personalization settings including available options.
    Useful for building UI toggles and preferences panels.
    """
    user_id = UUID(user["id"]) if user else None
    service = await get_personalization_service(user_id, db)
    settings = service.get_settings()

    return PersonalizationSettingsResponse(
        content_variant=settings.content_variant.value,
        preferred_language=settings.preferred_language.value,
        available_languages=[lang.value for lang in settings.available_languages],
        hardware_variant=settings.hardware_variant.value,
        available_hardware=[hw.value for hw in settings.available_hardware],
        show_advanced_topics=settings.show_advanced_topics,
        show_hardware_exercises=settings.show_hardware_exercises,
    )
