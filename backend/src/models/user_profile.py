"""UserProfile model for learner personalization.

Source: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db.postgres import Base


class UserProfile(Base):
    """Learner profile for content personalization.

    Stores user preferences for software background, hardware access,
    and experience level to enable personalized chapter content delivery.
    """

    __tablename__ = "user_profile"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Foreign key to better-auth user table
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        unique=True,
        nullable=False,
        index=True,
    )

    # FR-007: Software background (multi-select)
    # Values: python, cpp, javascript_typescript, ros_ros2, matlab, none_learning
    software_background: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        default=list,
        nullable=False,
    )

    # FR-008: Hardware access (multi-select)
    # Values: simulation_only, arduino_microcontrollers, raspberry_pi, nvidia_jetson,
    #         robot_arm, humanoid_robot, drone_uav, custom_other
    hardware_access: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        default=list,
        nullable=False,
    )

    # FR-009: Experience level (single-select)
    # Values: beginner, intermediate, advanced
    experience_level: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    # Profile completion tracking (FR-010)
    profile_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Reminder tracking for skipped profiles
    last_reminded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def is_complete(self) -> bool:
        """Check if profile has all required fields filled."""
        return bool(
            self.software_background
            and self.hardware_access
            and self.experience_level
        )

    def mark_complete(self) -> None:
        """Mark profile as completed with timestamp."""
        if self.is_complete():
            self.profile_completed = True
            self.completed_at = datetime.now()

    def __repr__(self) -> str:
        return (
            f"UserProfile(id={self.id}, user_id={self.user_id}, "
            f"experience_level={self.experience_level}, "
            f"profile_completed={self.profile_completed})"
        )
