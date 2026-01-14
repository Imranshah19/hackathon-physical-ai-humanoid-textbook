# Chapter 7: Safety Constraints and Action Filtering

**Duration**: 4-5 hours
**Prerequisites**: Chapter 6 (ROS 2 Integration)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand why safety constraints are critical for VLA systems
- Implement joint limit enforcement
- Apply workspace boundary checking
- Build velocity and acceleration limiters
- Create confidence-based action filtering
- Implement emergency stop mechanisms

---

## 7.1 Why Safety Matters for VLA

VLA models can generate unsafe actions because:

1. **Hallucination**: Model predicts actions for non-existent objects
2. **Distribution shift**: Real scene differs from training data
3. **Discretization errors**: Action tokenization introduces imprecision
4. **Lack of physics**: Model doesn't understand physical constraints

```
┌─────────────────────────────────────────────────────────────────┐
│                    Safety Filter Pipeline                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  VLA Output (potentially unsafe)                                │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Confidence Filter                           │   │
│  │  • Reject low-confidence predictions                     │   │
│  │  • Threshold: 0.5-0.8 typical                           │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Joint Limit Checker                         │   │
│  │  • Clip to URDF-defined limits                          │   │
│  │  • Soft limits for margin                               │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Workspace Boundary Checker                  │   │
│  │  • End-effector stays in safe workspace                 │   │
│  │  • Forward kinematics check                             │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Velocity Limiter                            │   │
│  │  • Smooth rapid position changes                        │   │
│  │  • Enforce max joint velocities                         │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Collision Checker (optional)                │   │
│  │  • Self-collision detection                             │   │
│  │  • Environment collision (if model available)           │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Action Smoother                             │   │
│  │  • Exponential moving average                           │   │
│  │  • Trajectory interpolation                             │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         ▼                                        │
│  Safe Robot Command                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7.2 Safety Configuration

```python
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional, List
import numpy as np


@dataclass
class SafetyConfig:
    """Configuration for safety filter."""

    # Joint limits (rad)
    joint_limits: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    # Soft limit margin (percentage of range)
    soft_limit_margin: float = 0.05

    # Workspace bounds (meters)
    workspace_bounds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        'x': (-0.6, 0.6),
        'y': (-0.6, 0.6),
        'z': (0.0, 1.0),
    })

    # Velocity limits (rad/s)
    max_joint_velocity: float = 2.0

    # Acceleration limits (rad/s^2)
    max_joint_acceleration: float = 5.0

    # Confidence threshold
    min_confidence: float = 0.5

    # Action smoothing
    smoothing_factor: float = 0.3  # EMA factor (0 = no smoothing, 1 = instant)

    # Emergency stop distance (meters from workspace boundary)
    emergency_stop_margin: float = 0.05


# Default humanoid joint limits
HUMANOID_JOINT_LIMITS = {
    'left_hip_yaw': (-0.5, 0.5),
    'left_hip_roll': (-0.3, 0.5),
    'left_hip_pitch': (-1.5, 0.5),
    'left_knee': (0.0, 2.0),
    'left_ankle_pitch': (-0.5, 0.5),
    'left_ankle_roll': (-0.3, 0.3),
    'right_hip_yaw': (-0.5, 0.5),
    'right_hip_roll': (-0.5, 0.3),
    'right_hip_pitch': (-1.5, 0.5),
    'right_knee': (0.0, 2.0),
    'right_ankle_pitch': (-0.5, 0.5),
    'right_ankle_roll': (-0.3, 0.3),
    'torso_yaw': (-0.5, 0.5),
    'torso_pitch': (-0.3, 0.3),
}
```

---

## 7.3 Joint Limit Checker

```python
class JointLimitChecker:
    """Enforce joint position limits."""

    def __init__(self, joint_limits: Dict[str, Tuple[float, float]], soft_margin: float = 0.05):
        self.joint_limits = joint_limits
        self.soft_margin = soft_margin
        self.joint_names = list(joint_limits.keys())

        # Compute soft limits
        self.soft_limits = {}
        for name, (low, high) in joint_limits.items():
            range_size = high - low
            margin = range_size * soft_margin
            self.soft_limits[name] = (low + margin, high - margin)

    def check(self, positions: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Check if positions are within limits.

        Args:
            positions: Joint positions array

        Returns:
            (is_valid, list of violations)
        """
        violations = []

        for i, name in enumerate(self.joint_names):
            if i >= len(positions):
                break

            pos = positions[i]
            low, high = self.joint_limits[name]

            if pos < low:
                violations.append(f"{name}: {pos:.3f} < {low:.3f}")
            elif pos > high:
                violations.append(f"{name}: {pos:.3f} > {high:.3f}")

        return len(violations) == 0, violations

    def clip(self, positions: np.ndarray, use_soft: bool = True) -> np.ndarray:
        """
        Clip positions to limits.

        Args:
            positions: Joint positions array
            use_soft: Whether to use soft limits

        Returns:
            Clipped positions
        """
        clipped = positions.copy()
        limits = self.soft_limits if use_soft else self.joint_limits

        for i, name in enumerate(self.joint_names):
            if i >= len(clipped):
                break

            low, high = limits[name]
            clipped[i] = np.clip(clipped[i], low, high)

        return clipped

    def get_limit_distance(self, positions: np.ndarray) -> np.ndarray:
        """
        Get distance to nearest limit for each joint.

        Returns:
            Array of distances (positive = inside, negative = outside)
        """
        distances = []

        for i, name in enumerate(self.joint_names):
            if i >= len(positions):
                break

            pos = positions[i]
            low, high = self.joint_limits[name]

            dist_low = pos - low
            dist_high = high - pos
            distances.append(min(dist_low, dist_high))

        return np.array(distances)


# Usage
limit_checker = JointLimitChecker(HUMANOID_JOINT_LIMITS)

# Check positions
positions = np.array([0.3, 0.2, -0.5, 1.0, 0.0, 0.0, -0.3, 0.2, -0.5, 1.0, 0.0, 0.0, 0.1, 0.0])
is_valid, violations = limit_checker.check(positions)

print(f"Valid: {is_valid}")
if violations:
    print(f"Violations: {violations}")

# Clip to limits
clipped = limit_checker.clip(positions)
print(f"Clipped: {clipped}")
```

---

## 7.4 Workspace Boundary Checker

```python
class WorkspaceBoundaryChecker:
    """Check end-effector workspace boundaries."""

    def __init__(
        self,
        bounds: Dict[str, Tuple[float, float]],
        margin: float = 0.05
    ):
        self.bounds = bounds
        self.margin = margin

        # Compute bounds with margin
        self.safe_bounds = {}
        for axis, (low, high) in bounds.items():
            self.safe_bounds[axis] = (low + margin, high - margin)

    def check_position(self, position: np.ndarray) -> Tuple[bool, List[str]]:
        """
        Check if 3D position is within workspace.

        Args:
            position: [x, y, z] position

        Returns:
            (is_valid, list of violations)
        """
        violations = []
        axes = ['x', 'y', 'z']

        for i, axis in enumerate(axes):
            if i >= len(position):
                break

            pos = position[i]
            low, high = self.bounds[axis]

            if pos < low:
                violations.append(f"{axis}: {pos:.3f} < {low:.3f}")
            elif pos > high:
                violations.append(f"{axis}: {pos:.3f} > {high:.3f}")

        return len(violations) == 0, violations

    def project_to_workspace(self, position: np.ndarray) -> np.ndarray:
        """
        Project position to nearest point inside workspace.

        Args:
            position: [x, y, z] position

        Returns:
            Projected position
        """
        projected = position.copy()
        axes = ['x', 'y', 'z']

        for i, axis in enumerate(axes):
            if i >= len(projected):
                break

            low, high = self.safe_bounds[axis]
            projected[i] = np.clip(projected[i], low, high)

        return projected

    def get_boundary_distance(self, position: np.ndarray) -> float:
        """
        Get minimum distance to workspace boundary.

        Returns:
            Distance (positive = inside, negative = outside)
        """
        min_dist = float('inf')
        axes = ['x', 'y', 'z']

        for i, axis in enumerate(axes):
            if i >= len(position):
                break

            pos = position[i]
            low, high = self.bounds[axis]

            dist_low = pos - low
            dist_high = high - pos
            min_dist = min(min_dist, dist_low, dist_high)

        return min_dist


# Usage
workspace_checker = WorkspaceBoundaryChecker({
    'x': (-0.5, 0.5),
    'y': (-0.5, 0.5),
    'z': (0.0, 0.8),
})

position = np.array([0.6, 0.0, 0.5])  # Outside x bounds
is_valid, violations = workspace_checker.check_position(position)
print(f"Valid: {is_valid}, Violations: {violations}")

# Project back
projected = workspace_checker.project_to_workspace(position)
print(f"Projected: {projected}")
```

---

## 7.5 Velocity and Acceleration Limiters

```python
class VelocityLimiter:
    """Limit joint velocities."""

    def __init__(
        self,
        max_velocity: float = 2.0,  # rad/s
        dt: float = 0.1  # Control timestep
    ):
        self.max_velocity = max_velocity
        self.dt = dt
        self.max_delta = max_velocity * dt

    def limit(
        self,
        current_position: np.ndarray,
        target_position: np.ndarray
    ) -> np.ndarray:
        """
        Limit velocity by capping position delta.

        Args:
            current_position: Current joint positions
            target_position: Target joint positions

        Returns:
            Velocity-limited target positions
        """
        delta = target_position - current_position

        # Compute velocity
        velocity = delta / self.dt

        # Check for violations
        max_abs_velocity = np.abs(velocity).max()

        if max_abs_velocity > self.max_velocity:
            # Scale down delta to respect velocity limit
            scale = self.max_velocity / max_abs_velocity
            delta = delta * scale

        return current_position + delta

    def get_velocity(
        self,
        current_position: np.ndarray,
        target_position: np.ndarray
    ) -> np.ndarray:
        """Compute velocity from position change."""
        return (target_position - current_position) / self.dt


class AccelerationLimiter:
    """Limit joint accelerations."""

    def __init__(
        self,
        max_acceleration: float = 5.0,  # rad/s^2
        dt: float = 0.1
    ):
        self.max_acceleration = max_acceleration
        self.dt = dt
        self.last_velocity = None

    def limit(
        self,
        current_velocity: np.ndarray,
        target_velocity: np.ndarray
    ) -> np.ndarray:
        """
        Limit acceleration by capping velocity change.

        Args:
            current_velocity: Current joint velocities
            target_velocity: Target joint velocities

        Returns:
            Acceleration-limited velocities
        """
        delta_v = target_velocity - current_velocity
        acceleration = delta_v / self.dt

        max_abs_accel = np.abs(acceleration).max()

        if max_abs_accel > self.max_acceleration:
            scale = self.max_acceleration / max_abs_accel
            delta_v = delta_v * scale

        return current_velocity + delta_v

    def update(self, velocity: np.ndarray):
        """Update velocity history."""
        self.last_velocity = velocity.copy()


# Combined velocity and acceleration limiter
class KinematicLimiter:
    """Combined velocity and acceleration limiting."""

    def __init__(
        self,
        max_velocity: float = 2.0,
        max_acceleration: float = 5.0,
        dt: float = 0.1
    ):
        self.vel_limiter = VelocityLimiter(max_velocity, dt)
        self.acc_limiter = AccelerationLimiter(max_acceleration, dt)
        self.dt = dt

        self.last_position = None
        self.last_velocity = None

    def limit(
        self,
        current_position: np.ndarray,
        target_position: np.ndarray
    ) -> np.ndarray:
        """
        Apply both velocity and acceleration limits.

        Returns:
            Safe target position
        """
        # Compute target velocity
        if self.last_position is None:
            self.last_position = current_position.copy()
            self.last_velocity = np.zeros_like(current_position)

        current_velocity = (current_position - self.last_position) / self.dt
        target_velocity = (target_position - current_position) / self.dt

        # Limit acceleration
        limited_velocity = self.acc_limiter.limit(current_velocity, target_velocity)

        # Limit velocity magnitude
        max_vel = np.abs(limited_velocity).max()
        if max_vel > self.vel_limiter.max_velocity:
            limited_velocity *= self.vel_limiter.max_velocity / max_vel

        # Compute limited position
        limited_position = current_position + limited_velocity * self.dt

        # Update state
        self.last_position = current_position.copy()
        self.last_velocity = limited_velocity.copy()

        return limited_position


# Usage
kinematic_limiter = KinematicLimiter(max_velocity=2.0, max_acceleration=5.0, dt=0.1)

current = np.array([0.0, 0.0, 0.0])
target = np.array([1.0, 0.5, -0.5])  # Large jump

limited = kinematic_limiter.limit(current, target)
print(f"Original target: {target}")
print(f"Limited target: {limited}")
```

---

## 7.6 Confidence-Based Filtering

```python
class ConfidenceFilter:
    """Filter actions based on model confidence."""

    def __init__(
        self,
        min_confidence: float = 0.5,
        fallback_action: str = "hold"  # "hold", "stop", "previous"
    ):
        self.min_confidence = min_confidence
        self.fallback_action = fallback_action
        self.previous_action = None

    def filter(
        self,
        action: np.ndarray,
        confidence: float,
        current_position: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, bool, str]:
        """
        Filter action based on confidence.

        Args:
            action: Predicted action
            confidence: Model confidence score
            current_position: Current joint positions (for hold fallback)

        Returns:
            (filtered_action, was_accepted, rejection_reason)
        """
        if confidence >= self.min_confidence:
            self.previous_action = action.copy()
            return action, True, ""

        # Low confidence - apply fallback
        reason = f"Confidence {confidence:.2f} < threshold {self.min_confidence}"

        if self.fallback_action == "hold":
            if current_position is not None:
                return current_position, False, reason
            else:
                return np.zeros_like(action), False, reason

        elif self.fallback_action == "stop":
            return np.zeros_like(action), False, reason

        elif self.fallback_action == "previous":
            if self.previous_action is not None:
                return self.previous_action, False, reason
            else:
                return np.zeros_like(action), False, reason

        return action, False, reason

    def get_adaptive_threshold(
        self,
        recent_confidences: List[float],
        percentile: float = 25
    ) -> float:
        """
        Compute adaptive threshold based on recent history.

        Returns threshold at given percentile of recent confidences.
        """
        if not recent_confidences:
            return self.min_confidence

        return max(self.min_confidence, np.percentile(recent_confidences, percentile))


# Usage
conf_filter = ConfidenceFilter(min_confidence=0.6, fallback_action="hold")

# High confidence - accepted
action1 = np.array([0.1, 0.2, 0.3])
filtered1, accepted1, reason1 = conf_filter.filter(action1, confidence=0.8)
print(f"High conf: accepted={accepted1}")

# Low confidence - rejected
action2 = np.array([0.5, 0.6, 0.7])
current_pos = np.array([0.0, 0.0, 0.0])
filtered2, accepted2, reason2 = conf_filter.filter(action2, confidence=0.3, current_position=current_pos)
print(f"Low conf: accepted={accepted2}, reason='{reason2}'")
print(f"Fallback action: {filtered2}")
```

---

## 7.7 Action Smoother

```python
class ActionSmoother:
    """Smooth action sequences for stability."""

    def __init__(
        self,
        smoothing_factor: float = 0.3,
        method: str = "ema"  # "ema" or "moving_average"
    ):
        self.smoothing_factor = smoothing_factor
        self.method = method

        self.history = []
        self.ema_value = None

    def smooth(self, action: np.ndarray) -> np.ndarray:
        """
        Apply smoothing to action.

        Args:
            action: Raw action from VLA

        Returns:
            Smoothed action
        """
        if self.method == "ema":
            return self._smooth_ema(action)
        elif self.method == "moving_average":
            return self._smooth_ma(action)
        else:
            return action

    def _smooth_ema(self, action: np.ndarray) -> np.ndarray:
        """Exponential moving average smoothing."""
        if self.ema_value is None:
            self.ema_value = action.copy()
            return action

        # EMA update: new_ema = alpha * action + (1 - alpha) * old_ema
        alpha = self.smoothing_factor
        self.ema_value = alpha * action + (1 - alpha) * self.ema_value

        return self.ema_value.copy()

    def _smooth_ma(self, action: np.ndarray, window: int = 5) -> np.ndarray:
        """Moving average smoothing."""
        self.history.append(action)

        if len(self.history) > window:
            self.history.pop(0)

        return np.mean(self.history, axis=0)

    def reset(self):
        """Reset smoother state."""
        self.history = []
        self.ema_value = None


# Usage
smoother = ActionSmoother(smoothing_factor=0.3, method="ema")

# Simulate noisy action sequence
np.random.seed(42)
base_action = np.array([0.5, 0.3, 0.2])

print("Raw vs Smoothed actions:")
for i in range(10):
    noise = np.random.randn(3) * 0.1
    raw_action = base_action + noise
    smoothed = smoother.smooth(raw_action)
    print(f"  {i}: raw={raw_action.round(3)}, smoothed={smoothed.round(3)}")
```

---

## 7.8 Complete Safety Filter

```python
@dataclass
class SafetyResult:
    """Result from safety filter."""
    action: np.ndarray
    is_safe: bool
    was_modified: bool
    modifications: List[str]
    confidence_accepted: bool


class SafetyFilter:
    """Complete safety filter combining all components."""

    def __init__(self, config: SafetyConfig):
        self.config = config

        # Initialize components
        self.joint_limiter = JointLimitChecker(
            config.joint_limits,
            config.soft_limit_margin
        )

        self.workspace_checker = WorkspaceBoundaryChecker(
            config.workspace_bounds,
            config.emergency_stop_margin
        )

        self.kinematic_limiter = KinematicLimiter(
            config.max_joint_velocity,
            config.max_joint_acceleration,
            dt=0.1  # Assuming 10Hz control
        )

        self.confidence_filter = ConfidenceFilter(
            config.min_confidence,
            fallback_action="hold"
        )

        self.smoother = ActionSmoother(
            config.smoothing_factor,
            method="ema"
        )

        # Emergency stop state
        self.emergency_stopped = False

    def filter(
        self,
        action: np.ndarray,
        current_position: np.ndarray,
        confidence: float = 1.0,
        ee_position: Optional[np.ndarray] = None
    ) -> SafetyResult:
        """
        Apply all safety filters to action.

        Args:
            action: Raw VLA action
            current_position: Current joint positions
            confidence: Model confidence
            ee_position: End-effector position (optional)

        Returns:
            SafetyResult with filtered action and metadata
        """
        if self.emergency_stopped:
            return SafetyResult(
                action=current_position,
                is_safe=False,
                was_modified=True,
                modifications=["Emergency stop active"],
                confidence_accepted=False
            )

        modifications = []
        was_modified = False
        safe_action = action.copy()

        # 1. Confidence filter
        safe_action, conf_accepted, conf_reason = self.confidence_filter.filter(
            safe_action, confidence, current_position
        )
        if not conf_accepted:
            modifications.append(f"Confidence: {conf_reason}")
            was_modified = True

        # 2. Joint limits
        is_valid, violations = self.joint_limiter.check(safe_action)
        if not is_valid:
            safe_action = self.joint_limiter.clip(safe_action)
            modifications.append(f"Joint limits: {violations}")
            was_modified = True

        # 3. Kinematic limits (velocity/acceleration)
        safe_action = self.kinematic_limiter.limit(current_position, safe_action)
        if not np.allclose(safe_action, action):
            if "Kinematic limits" not in str(modifications):
                modifications.append("Kinematic limits applied")
            was_modified = True

        # 4. Workspace check (if ee_position available)
        if ee_position is not None:
            ws_valid, ws_violations = self.workspace_checker.check_position(ee_position)
            if not ws_valid:
                modifications.append(f"Workspace: {ws_violations}")
                # Project to safe workspace
                # (In practice, would need IK to map back to joints)
                was_modified = True

        # 5. Smoothing
        safe_action = self.smoother.smooth(safe_action)

        return SafetyResult(
            action=safe_action,
            is_safe=not was_modified or len(modifications) <= 1,  # Allow minor mods
            was_modified=was_modified,
            modifications=modifications,
            confidence_accepted=conf_accepted
        )

    def emergency_stop(self):
        """Trigger emergency stop."""
        self.emergency_stopped = True

    def reset_emergency(self):
        """Reset emergency stop."""
        self.emergency_stopped = False

    def reset(self):
        """Reset all filter states."""
        self.smoother.reset()
        self.kinematic_limiter.last_position = None
        self.kinematic_limiter.last_velocity = None
        self.confidence_filter.previous_action = None
        self.emergency_stopped = False


# Usage example
config = SafetyConfig(
    joint_limits=HUMANOID_JOINT_LIMITS,
    max_joint_velocity=2.0,
    max_joint_acceleration=5.0,
    min_confidence=0.5,
    smoothing_factor=0.3
)

safety_filter = SafetyFilter(config)

# Simulate filtering
current_pos = np.zeros(14)
action = np.random.randn(14) * 0.5  # Random action

result = safety_filter.filter(action, current_pos, confidence=0.7)

print(f"Safe: {result.is_safe}")
print(f"Modified: {result.was_modified}")
print(f"Modifications: {result.modifications}")
print(f"Original: {action[:4].round(3)}")
print(f"Filtered: {result.action[:4].round(3)}")
```

---

## 7.9 Emergency Stop Implementation

```python
import threading
from typing import Callable

class EmergencyStopManager:
    """Manage emergency stop functionality."""

    def __init__(self):
        self.is_stopped = False
        self.stop_reason = ""
        self.callbacks: List[Callable] = []
        self.lock = threading.Lock()

    def register_callback(self, callback: Callable):
        """Register callback to be called on emergency stop."""
        self.callbacks.append(callback)

    def trigger(self, reason: str = "Manual trigger"):
        """Trigger emergency stop."""
        with self.lock:
            if not self.is_stopped:
                self.is_stopped = True
                self.stop_reason = reason

                print(f"\n{'='*50}")
                print("EMERGENCY STOP TRIGGERED")
                print(f"Reason: {reason}")
                print('='*50 + "\n")

                # Call all registered callbacks
                for callback in self.callbacks:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Callback error: {e}")

    def reset(self, confirm: bool = False):
        """Reset emergency stop (requires confirmation)."""
        if not confirm:
            print("Emergency reset requires confirmation. Call reset(confirm=True)")
            return False

        with self.lock:
            self.is_stopped = False
            self.stop_reason = ""
            print("Emergency stop reset")
            return True

    def check(self) -> bool:
        """Check if emergency stop is active."""
        return self.is_stopped


# Integration with ROS 2
class EmergencyStopNode:
    """ROS 2 node for emergency stop."""

    def __init__(self, node, safety_filter: SafetyFilter):
        self.node = node
        self.safety_filter = safety_filter
        self.estop_manager = EmergencyStopManager()

        # Register safety filter callback
        self.estop_manager.register_callback(self.safety_filter.emergency_stop)

        # Create service for emergency stop
        # self.estop_srv = node.create_service(
        #     Trigger,
        #     '/vla/emergency_stop',
        #     self.estop_callback
        # )

        # Create service for reset
        # self.reset_srv = node.create_service(
        #     Trigger,
        #     '/vla/reset_emergency',
        #     self.reset_callback
        # )

    def estop_callback(self, request, response):
        """Handle emergency stop service call."""
        self.estop_manager.trigger("Service call")
        response.success = True
        response.message = "Emergency stop activated"
        return response

    def reset_callback(self, request, response):
        """Handle emergency reset service call."""
        success = self.estop_manager.reset(confirm=True)
        self.safety_filter.reset_emergency()
        response.success = success
        response.message = "Emergency stop reset" if success else "Reset failed"
        return response
```

---

## 7.10 Summary

In this chapter, you learned:

1. **Why Safety Matters**: VLA models can generate unsafe actions
2. **Joint Limits**: Clipping actions to URDF-defined ranges
3. **Workspace Bounds**: Keeping end-effector in safe region
4. **Kinematic Limits**: Velocity and acceleration constraints
5. **Confidence Filtering**: Rejecting low-confidence predictions
6. **Action Smoothing**: EMA for stable trajectories
7. **Complete Safety Filter**: Combining all components
8. **Emergency Stop**: Hardware and software kill switches

---

## 7.11 Exercises

### Exercise 7.1: Joint Limiter
Implement and test joint limit checker with soft margins.

### Exercise 7.2: Workspace Boundary
Create workspace visualization showing safe and unsafe regions.

### Exercise 7.3: Safety Pipeline
Build complete safety filter and test with adversarial inputs.

### Exercise 7.4: Emergency Stop
Implement ROS 2 emergency stop service with hardware integration.

---

## Quick Reference

### Safety Filter Usage
```python
config = SafetyConfig(joint_limits=JOINT_LIMITS)
filter = SafetyFilter(config)
result = filter.filter(action, current_pos, confidence=0.8)
```

### Emergency Stop
```python
filter.emergency_stop()  # Activate
filter.reset_emergency()  # Deactivate
```

---

**Next Chapter**: [Chapter 8 - Fine-tuning VLA on Custom Data](ch08-finetuning.md)
