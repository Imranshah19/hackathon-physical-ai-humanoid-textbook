"""Enums and constants for user profile personalization.

Source: FR-007, FR-008, FR-009 from spec.md
"""

from enum import Enum
from typing import NamedTuple


class ProfileOption(NamedTuple):
    """Profile option with value, label, and description."""

    value: str
    label: str
    description: str


class SoftwareBackground(str, Enum):
    """Software/programming background options (FR-007).

    Multi-select field for user profile.
    """

    PYTHON = "python"
    CPP = "cpp"
    JAVASCRIPT_TYPESCRIPT = "javascript_typescript"
    ROS_ROS2 = "ros_ros2"
    MATLAB = "matlab"
    NONE_LEARNING = "none_learning"


class HardwareAccess(str, Enum):
    """Hardware access options (FR-008).

    Multi-select field for user profile.
    """

    SIMULATION_ONLY = "simulation_only"
    ARDUINO_MICROCONTROLLERS = "arduino_microcontrollers"
    RASPBERRY_PI = "raspberry_pi"
    NVIDIA_JETSON = "nvidia_jetson"
    ROBOT_ARM = "robot_arm"
    HUMANOID_ROBOT = "humanoid_robot"
    DRONE_UAV = "drone_uav"
    CUSTOM_OTHER = "custom_other"


class ExperienceLevel(str, Enum):
    """Experience level options (FR-009).

    Single-select field for user profile.
    """

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# Profile options with labels and descriptions for UI
SOFTWARE_OPTIONS: list[ProfileOption] = [
    ProfileOption(
        value=SoftwareBackground.PYTHON.value,
        label="Python",
        description="General-purpose programming with robotics libraries (NumPy, OpenCV, etc.)",
    ),
    ProfileOption(
        value=SoftwareBackground.CPP.value,
        label="C++",
        description="High-performance robotics and embedded systems programming",
    ),
    ProfileOption(
        value=SoftwareBackground.JAVASCRIPT_TYPESCRIPT.value,
        label="JavaScript/TypeScript",
        description="Web development and visualization tools",
    ),
    ProfileOption(
        value=SoftwareBackground.ROS_ROS2.value,
        label="ROS/ROS2",
        description="Robot Operating System experience",
    ),
    ProfileOption(
        value=SoftwareBackground.MATLAB.value,
        label="MATLAB",
        description="Mathematical modeling and simulation",
    ),
    ProfileOption(
        value=SoftwareBackground.NONE_LEARNING.value,
        label="None/Learning",
        description="New to programming - learning fundamentals",
    ),
]

HARDWARE_OPTIONS: list[ProfileOption] = [
    ProfileOption(
        value=HardwareAccess.SIMULATION_ONLY.value,
        label="Simulation Only",
        description="Learning with virtual robots and simulators (Gazebo, Isaac Sim)",
    ),
    ProfileOption(
        value=HardwareAccess.ARDUINO_MICROCONTROLLERS.value,
        label="Arduino/Microcontrollers",
        description="Basic embedded development boards",
    ),
    ProfileOption(
        value=HardwareAccess.RASPBERRY_PI.value,
        label="Raspberry Pi",
        description="Single-board computer for robotics projects",
    ),
    ProfileOption(
        value=HardwareAccess.NVIDIA_JETSON.value,
        label="NVIDIA Jetson",
        description="GPU-accelerated edge computing for AI",
    ),
    ProfileOption(
        value=HardwareAccess.ROBOT_ARM.value,
        label="Physical Robot Arm",
        description="Industrial or educational manipulators",
    ),
    ProfileOption(
        value=HardwareAccess.HUMANOID_ROBOT.value,
        label="Humanoid Robot",
        description="Full humanoid robot platforms",
    ),
    ProfileOption(
        value=HardwareAccess.DRONE_UAV.value,
        label="Drone/UAV",
        description="Unmanned aerial vehicles",
    ),
    ProfileOption(
        value=HardwareAccess.CUSTOM_OTHER.value,
        label="Custom/Other",
        description="Other robotics hardware not listed",
    ),
]

EXPERIENCE_OPTIONS: list[ProfileOption] = [
    ProfileOption(
        value=ExperienceLevel.BEGINNER.value,
        label="Beginner",
        description="New to robotics - learning fundamentals and core concepts",
    ),
    ProfileOption(
        value=ExperienceLevel.INTERMEDIATE.value,
        label="Intermediate",
        description="Some projects completed - building practical skills",
    ),
    ProfileOption(
        value=ExperienceLevel.ADVANCED.value,
        label="Advanced",
        description="Professional or research experience in robotics",
    ),
]


def get_all_profile_options() -> dict:
    """Get all profile options formatted for API response."""
    return {
        "softwareBackground": [
            {"value": opt.value, "label": opt.label, "description": opt.description}
            for opt in SOFTWARE_OPTIONS
        ],
        "hardwareAccess": [
            {"value": opt.value, "label": opt.label, "description": opt.description}
            for opt in HARDWARE_OPTIONS
        ],
        "experienceLevel": [
            {"value": opt.value, "label": opt.label, "description": opt.description}
            for opt in EXPERIENCE_OPTIONS
        ],
    }


def validate_software_background(values: list[str]) -> bool:
    """Validate software background values."""
    valid_values = {e.value for e in SoftwareBackground}
    return all(v in valid_values for v in values)


def validate_hardware_access(values: list[str]) -> bool:
    """Validate hardware access values."""
    valid_values = {e.value for e in HardwareAccess}
    return all(v in valid_values for v in values)


def validate_experience_level(value: str) -> bool:
    """Validate experience level value."""
    return value in {e.value for e in ExperienceLevel}
