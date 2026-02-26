# Exercise 3.1: Trajectory Action

**Chapter**: 3 - Services and Actions
**Difficulty**: Intermediate
**Time**: 60 minutes

---

## Objective

Create an action server that executes multi-point trajectories for a humanoid joint, with feedback showing progress through waypoints.

## Requirements

1. Define `ExecuteTrajectory.action` with:
   - Goal: list of positions (waypoints) and total duration
   - Result: success status and final positions
   - Feedback: current waypoint index and progress percentage

2. Implement action server that:
   - Interpolates linearly between waypoints
   - Publishes feedback at 20 Hz
   - Supports cancellation mid-trajectory

3. Implement action client that:
   - Sends a 5-waypoint trajectory
   - Displays feedback as progress bar
   - Handles completion and cancellation

## Action Definition

Create `humanoid_msgs/action/ExecuteTrajectory.action`:

```
# Goal
string joint_name
float64[] positions      # Waypoint positions in radians
float64 duration         # Total duration in seconds
---
# Result
bool success
float64[] final_positions
string message
---
# Feedback
uint32 current_waypoint  # 0-indexed
float64 progress         # 0.0 to 1.0
float64 current_position
float64 time_remaining
```

## Starter Code

```python
#!/usr/bin/env python3
"""
Trajectory action server - Exercise 3.1

TODO: Implement execute_callback with:
1. Linear interpolation between waypoints
2. Feedback publishing
3. Cancellation handling
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from humanoid_msgs.action import ExecuteTrajectory


class TrajectoryServer(Node):
    def __init__(self):
        super().__init__('trajectory_server')

        self._action_server = ActionServer(
            self,
            ExecuteTrajectory,
            '/execute_trajectory',
            execute_callback=self.execute_callback
        )

    async def execute_callback(self, goal_handle):
        """Execute trajectory through waypoints."""
        # TODO: Implement trajectory execution
        pass


def main():
    rclpy.init()
    node = TrajectoryServer()
    rclpy.spin(node)
    rclpy.shutdown()
```

## Expected Behavior

```bash
# Terminal 1: Start server
ros2 run humanoid_control trajectory_server

# Terminal 2: Send goal
ros2 action send_goal /execute_trajectory humanoid_msgs/action/ExecuteTrajectory \
  "{joint_name: 'head_pan', positions: [0.0, 0.5, 0.0, -0.5, 0.0], duration: 5.0}" \
  --feedback

# Expected feedback output:
# Feedback: waypoint=0, progress=0.10, pos=0.05
# Feedback: waypoint=0, progress=0.20, pos=0.10
# ...
# Feedback: waypoint=1, progress=0.25, pos=0.50
# ...
# Result: success=True
```

## Hints

<details>
<summary>Hint 1: Time-based interpolation</summary>

```python
# Calculate which segment we're in
segment_duration = total_duration / (len(positions) - 1)
current_segment = int(elapsed / segment_duration)
segment_progress = (elapsed % segment_duration) / segment_duration

# Interpolate within segment
start_pos = positions[current_segment]
end_pos = positions[current_segment + 1]
current_pos = start_pos + (end_pos - start_pos) * segment_progress
```
</details>

<details>
<summary>Hint 2: Progress calculation</summary>

```python
overall_progress = elapsed / total_duration
```
</details>

## Verification Checklist

- [ ] Action definition compiles
- [ ] Server accepts goals
- [ ] Feedback shows correct waypoint index
- [ ] Progress increases monotonically
- [ ] Cancellation stops motion
- [ ] Result reports success/failure accurately

---

## Bonus Challenges

1. **Cubic interpolation**: Use cubic splines for smoother motion
2. **Velocity limits**: Enforce maximum velocity between waypoints
3. **Pause/Resume**: Add ability to pause and resume trajectory
