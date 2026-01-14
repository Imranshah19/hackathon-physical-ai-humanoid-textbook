"""
VLA Safety Filter for Humanoid Robotics

Implements multi-layer safety constraints for VLA-generated actions:
- Joint limit enforcement
- Workspace boundary checking
- Velocity and acceleration limiting
- Confidence-based filtering
- Emergency stop detection

Reference: Chapter 7 - Safety Constraints
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
import numpy as np
import time


class SafetyViolation(Enum):
    """Types of safety violations."""
    NONE = "none"
    JOINT_LIMIT = "joint_limit"
    VELOCITY_LIMIT = "velocity_limit"
    ACCELERATION_LIMIT = "acceleration_limit"
    WORKSPACE_BOUNDARY = "workspace_boundary"
    LOW_CONFIDENCE = "low_confidence"
    COLLISION_RISK = "collision_risk"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class JointLimits:
    """Joint position limits in radians."""
    lower: np.ndarray
    upper: np.ndarray
    velocity_max: np.ndarray
    acceleration_max: np.ndarray

    @classmethod
    def humanoid_default(cls, num_joints: int = 22) -> 'JointLimits':
        """Create default limits for humanoid robot."""
        return cls(
            lower=np.full(num_joints, -2.0),
            upper=np.full(num_joints, 2.0),
            velocity_max=np.full(num_joints, 2.0),  # rad/s
            acceleration_max=np.full(num_joints, 10.0),  # rad/s^2
        )

    @classmethod
    def from_urdf(cls, urdf_path: str) -> 'JointLimits':
        """Parse limits from URDF file."""
        # Placeholder - actual implementation would parse URDF
        return cls.humanoid_default()


@dataclass
class WorkspaceBounds:
    """3D workspace boundaries for end-effector."""
    x_range: Tuple[float, float] = (-1.0, 1.0)
    y_range: Tuple[float, float] = (-1.0, 1.0)
    z_range: Tuple[float, float] = (0.0, 2.0)
    exclude_zones: List[Dict[str, Any]] = field(default_factory=list)

    def contains(self, position: np.ndarray) -> bool:
        """Check if position is within workspace."""
        if len(position) < 3:
            return True

        x, y, z = position[:3]
        if not (self.x_range[0] <= x <= self.x_range[1]):
            return False
        if not (self.y_range[0] <= y <= self.y_range[1]):
            return False
        if not (self.z_range[0] <= z <= self.z_range[1]):
            return False

        # Check exclusion zones
        for zone in self.exclude_zones:
            if self._in_zone(position, zone):
                return False

        return True

    def _in_zone(self, position: np.ndarray, zone: Dict) -> bool:
        """Check if position is in an exclusion zone."""
        zone_type = zone.get('type', 'sphere')
        if zone_type == 'sphere':
            center = np.array(zone['center'])
            radius = zone['radius']
            return np.linalg.norm(position[:3] - center) < radius
        elif zone_type == 'box':
            min_pt = np.array(zone['min'])
            max_pt = np.array(zone['max'])
            return np.all(position[:3] >= min_pt) and np.all(position[:3] <= max_pt)
        return False


@dataclass
class SafetyConfig:
    """Safety filter configuration."""
    # Limits
    joint_limits: JointLimits = field(default_factory=JointLimits.humanoid_default)
    workspace_bounds: WorkspaceBounds = field(default_factory=WorkspaceBounds)

    # Thresholds
    confidence_threshold: float = 0.3
    min_confidence_for_motion: float = 0.5

    # Timing
    control_dt: float = 0.02  # 50 Hz control loop
    smoothing_alpha: float = 0.3  # Exponential smoothing factor

    # Margins
    joint_limit_margin: float = 0.1  # rad
    velocity_scale: float = 0.8  # Safety factor

    # Emergency stop
    estop_enabled: bool = True
    estop_deceleration: float = 20.0  # rad/s^2


@dataclass
class SafetyResult:
    """Result of safety filtering."""
    action: np.ndarray
    is_safe: bool
    violations: List[SafetyViolation] = field(default_factory=list)
    modifications: Dict[str, Any] = field(default_factory=dict)
    original_action: Optional[np.ndarray] = None


class SafetyFilter:
    """
    Multi-layer safety filter for VLA actions.

    Example:
        >>> config = SafetyConfig()
        >>> safety = SafetyFilter(config)
        >>> result = safety.filter(action, current_pos, confidence=0.8)
        >>> if result.is_safe:
        ...     robot.execute(result.action)
    """

    def __init__(self, config: SafetyConfig):
        self.config = config
        self._prev_action: Optional[np.ndarray] = None
        self._prev_velocity: Optional[np.ndarray] = None
        self._prev_time: Optional[float] = None
        self._estop_active: bool = False

    def filter(
        self,
        action: np.ndarray,
        current_position: np.ndarray,
        confidence: float = 1.0,
        ee_position: Optional[np.ndarray] = None,
    ) -> SafetyResult:
        """
        Apply safety filters to action.

        Args:
            action: Commanded action (position delta or absolute)
            current_position: Current joint positions
            confidence: VLA prediction confidence [0, 1]
            ee_position: Optional end-effector position for workspace check

        Returns:
            SafetyResult with filtered action and violation info
        """
        violations = []
        modifications = {}
        original_action = action.copy()
        safe_action = action.copy()

        # 1. Emergency stop check
        if self._estop_active:
            return SafetyResult(
                action=np.zeros_like(action),
                is_safe=False,
                violations=[SafetyViolation.EMERGENCY_STOP],
                original_action=original_action,
            )

        # 2. Confidence filter
        if confidence < self.config.confidence_threshold:
            violations.append(SafetyViolation.LOW_CONFIDENCE)
            # Scale action by confidence
            scale = confidence / self.config.min_confidence_for_motion
            scale = np.clip(scale, 0.0, 1.0)
            safe_action = safe_action * scale
            modifications['confidence_scale'] = scale

        # 3. Joint limit enforcement
        safe_action, joint_violations = self._apply_joint_limits(
            safe_action, current_position
        )
        if joint_violations:
            violations.append(SafetyViolation.JOINT_LIMIT)
            modifications['joint_clipped'] = joint_violations

        # 4. Velocity limiting
        safe_action, vel_limited = self._apply_velocity_limits(safe_action)
        if vel_limited:
            violations.append(SafetyViolation.VELOCITY_LIMIT)
            modifications['velocity_scaled'] = True

        # 5. Acceleration limiting
        safe_action, accel_limited = self._apply_acceleration_limits(safe_action)
        if accel_limited:
            violations.append(SafetyViolation.ACCELERATION_LIMIT)
            modifications['acceleration_limited'] = True

        # 6. Workspace boundary check
        if ee_position is not None:
            if not self.config.workspace_bounds.contains(ee_position):
                violations.append(SafetyViolation.WORKSPACE_BOUNDARY)
                # Project back to boundary
                safe_action = self._project_to_workspace(
                    safe_action, current_position, ee_position
                )
                modifications['workspace_projected'] = True

        # 7. Smoothing
        safe_action = self._apply_smoothing(safe_action)

        # Update history
        self._update_history(safe_action)

        is_safe = len(violations) == 0
        return SafetyResult(
            action=safe_action,
            is_safe=is_safe,
            violations=violations,
            modifications=modifications,
            original_action=original_action,
        )

    def _apply_joint_limits(
        self,
        action: np.ndarray,
        current_position: np.ndarray,
    ) -> Tuple[np.ndarray, List[int]]:
        """Enforce joint position limits with margin."""
        limits = self.config.joint_limits
        margin = self.config.joint_limit_margin

        # Compute target position
        target = current_position + action

        # Clip to limits with margin
        lower = limits.lower + margin
        upper = limits.upper - margin

        clipped_target = np.clip(target, lower, upper)
        clipped_action = clipped_target - current_position

        # Track which joints were clipped
        clipped_joints = []
        for i in range(len(action)):
            if abs(clipped_action[i] - action[i]) > 1e-6:
                clipped_joints.append(i)

        return clipped_action, clipped_joints

    def _apply_velocity_limits(
        self,
        action: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        """Limit velocity magnitude."""
        limits = self.config.joint_limits
        dt = self.config.control_dt
        scale = self.config.velocity_scale

        # Compute implied velocity
        velocity = action / dt

        # Check against limits
        max_vel = limits.velocity_max * scale
        velocity_ratio = np.abs(velocity) / max_vel

        if np.any(velocity_ratio > 1.0):
            # Scale down uniformly to respect all limits
            scale_factor = 1.0 / np.max(velocity_ratio)
            return action * scale_factor, True

        return action, False

    def _apply_acceleration_limits(
        self,
        action: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        """Limit acceleration magnitude."""
        if self._prev_action is None:
            return action, False

        limits = self.config.joint_limits
        dt = self.config.control_dt

        # Compute velocities
        current_vel = action / dt
        prev_vel = self._prev_action / dt

        # Compute acceleration
        acceleration = (current_vel - prev_vel) / dt

        # Check against limits
        accel_ratio = np.abs(acceleration) / limits.acceleration_max

        if np.any(accel_ratio > 1.0):
            # Limit acceleration
            scale_factor = 1.0 / np.max(accel_ratio)
            limited_accel = acceleration * scale_factor
            limited_vel = prev_vel + limited_accel * dt
            return limited_vel * dt, True

        return action, False

    def _project_to_workspace(
        self,
        action: np.ndarray,
        current_position: np.ndarray,
        ee_position: np.ndarray,
    ) -> np.ndarray:
        """Project action to stay within workspace bounds."""
        bounds = self.config.workspace_bounds

        # Simple clamping approach
        # In practice, would use inverse kinematics
        target_ee = ee_position.copy()

        target_ee[0] = np.clip(target_ee[0], bounds.x_range[0], bounds.x_range[1])
        target_ee[1] = np.clip(target_ee[1], bounds.y_range[0], bounds.y_range[1])
        target_ee[2] = np.clip(target_ee[2], bounds.z_range[0], bounds.z_range[1])

        # Scale action based on how far we are from boundary
        scale = 0.5  # Conservative scaling when at boundary
        return action * scale

    def _apply_smoothing(self, action: np.ndarray) -> np.ndarray:
        """Apply exponential smoothing to reduce jitter."""
        if self._prev_action is None:
            return action

        alpha = self.config.smoothing_alpha
        return alpha * action + (1 - alpha) * self._prev_action

    def _update_history(self, action: np.ndarray) -> None:
        """Update action history for derivative calculations."""
        current_time = time.time()

        if self._prev_action is not None and self._prev_time is not None:
            dt = current_time - self._prev_time
            if dt > 0:
                self._prev_velocity = (action - self._prev_action) / dt

        self._prev_action = action.copy()
        self._prev_time = current_time

    def trigger_estop(self) -> None:
        """Activate emergency stop."""
        self._estop_active = True

    def release_estop(self) -> None:
        """Release emergency stop (requires confirmation)."""
        self._estop_active = False
        self._prev_action = None
        self._prev_velocity = None

    def reset(self) -> None:
        """Reset filter state."""
        self._prev_action = None
        self._prev_velocity = None
        self._prev_time = None
        self._estop_active = False


class CollisionChecker:
    """
    Simple collision checking for safety filter.

    Uses geometric primitives for fast checking.
    """

    def __init__(self, obstacles: List[Dict[str, Any]] = None):
        self.obstacles = obstacles or []

    def check_collision(
        self,
        positions: List[np.ndarray],
        margin: float = 0.05,
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if any positions collide with obstacles.

        Args:
            positions: List of 3D positions (e.g., link positions)
            margin: Safety margin around obstacles

        Returns:
            Tuple of (collision_detected, obstacle_index)
        """
        for pos in positions:
            for i, obs in enumerate(self.obstacles):
                if self._check_point_obstacle(pos, obs, margin):
                    return True, i
        return False, None

    def _check_point_obstacle(
        self,
        point: np.ndarray,
        obstacle: Dict,
        margin: float,
    ) -> bool:
        """Check if point is inside obstacle + margin."""
        obs_type = obstacle.get('type', 'sphere')

        if obs_type == 'sphere':
            center = np.array(obstacle['center'])
            radius = obstacle['radius'] + margin
            return np.linalg.norm(point[:3] - center) < radius

        elif obs_type == 'box':
            min_pt = np.array(obstacle['min']) - margin
            max_pt = np.array(obstacle['max']) + margin
            return np.all(point[:3] >= min_pt) and np.all(point[:3] <= max_pt)

        elif obs_type == 'cylinder':
            center = np.array(obstacle['center'])
            radius = obstacle['radius'] + margin
            height = obstacle['height'] + 2 * margin
            # Check XY distance
            xy_dist = np.linalg.norm(point[:2] - center[:2])
            # Check Z range
            z_in_range = (center[2] - height/2) <= point[2] <= (center[2] + height/2)
            return xy_dist < radius and z_in_range

        return False

    def add_obstacle(self, obstacle: Dict) -> None:
        """Add obstacle to the checker."""
        self.obstacles.append(obstacle)

    def remove_obstacle(self, index: int) -> None:
        """Remove obstacle by index."""
        if 0 <= index < len(self.obstacles):
            self.obstacles.pop(index)


# Convenience functions
def create_safety_filter(
    num_joints: int = 22,
    confidence_threshold: float = 0.3,
) -> SafetyFilter:
    """Create safety filter with default configuration."""
    config = SafetyConfig(
        joint_limits=JointLimits.humanoid_default(num_joints),
        confidence_threshold=confidence_threshold,
    )
    return SafetyFilter(config)


if __name__ == "__main__":
    # Example usage
    print("VLA Safety Filter Module")
    print("=" * 50)

    # Create filter
    safety = create_safety_filter(num_joints=7)

    # Test action filtering
    current_pos = np.zeros(7)
    action = np.array([0.5, -0.3, 0.1, 0.0, 0.2, -0.1, 0.3])

    result = safety.filter(action, current_pos, confidence=0.9)
    print(f"\nHigh confidence action:")
    print(f"  Original: {action}")
    print(f"  Filtered: {result.action}")
    print(f"  Is safe:  {result.is_safe}")
    print(f"  Violations: {result.violations}")

    # Test low confidence
    result = safety.filter(action, current_pos, confidence=0.2)
    print(f"\nLow confidence action:")
    print(f"  Original: {action}")
    print(f"  Filtered: {result.action}")
    print(f"  Violations: {result.violations}")

    # Test joint limit violation
    extreme_action = np.array([3.0, -3.0, 2.5, 0.0, 2.0, -2.0, 1.5])
    result = safety.filter(extreme_action, current_pos, confidence=0.9)
    print(f"\nJoint limit violation:")
    print(f"  Original: {extreme_action}")
    print(f"  Filtered: {result.action}")
    print(f"  Violations: {result.violations}")
