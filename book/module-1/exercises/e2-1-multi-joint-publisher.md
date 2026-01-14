# Exercise 2.1: Multi-Joint Publisher

**Chapter**: 2 - Nodes, Topics, and Messages
**Difficulty**: Intermediate
**Time**: 45 minutes

---

## Objective

Create a publisher node that sends commands to multiple humanoid joints simultaneously, each moving with a different motion pattern.

## Requirements

1. Publish to 3 joints: `head_pan`, `left_shoulder_pitch`, `right_shoulder_pitch`
2. Each joint moves with a different frequency:
   - `head_pan`: 0.5 Hz (slow)
   - `left_shoulder_pitch`: 1.0 Hz (medium)
   - `right_shoulder_pitch`: 1.5 Hz (fast)
3. Use sinusoidal motion with amplitude 0.5 radians
4. Publish rate: 50 Hz
5. Use `humanoid_msgs/msg/JointCommand` message type

## Starter Code

```python
#!/usr/bin/env python3
"""
Multi-joint publisher exercise.

TODO: Complete this node to publish commands to multiple joints.
"""

import rclpy
from rclpy.node import Node
from humanoid_msgs.msg import JointCommand
import math


class MultiJointPublisher(Node):
    def __init__(self):
        super().__init__('multi_joint_publisher')

        # TODO: Define joint configurations
        # Each joint should have: name, frequency, current_phase

        # TODO: Create publisher

        # TODO: Create timer for 50 Hz publishing

        self.get_logger().info('Multi-joint publisher started')

    def publish_commands(self):
        """Publish commands for all joints."""
        # TODO: For each joint:
        # 1. Calculate position using sin(2*pi*frequency*time + phase)
        # 2. Create JointCommand message
        # 3. Publish message
        pass


def main(args=None):
    rclpy.init(args=args)
    node = MultiJointPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Expected Output

When running:
```bash
ros2 run humanoid_control multi_joint_publisher
```

And echoing the topic:
```bash
ros2 topic echo /joint_commands
```

You should see messages like:
```
joint_name: head_pan
position: 0.354
velocity: 0.0
effort: 0.0
stamp:
  sec: 1234567890
  nanosec: 123456789
---
joint_name: left_shoulder_pitch
position: -0.212
...
```

## Verification

```bash
# Check publish rate
ros2 topic hz /joint_commands
# Expected: ~150 Hz (50 Hz × 3 joints)

# Plot positions (if using separate topics)
ros2 run rqt_plot rqt_plot /head_pan/position /left_shoulder_pitch/position
```

## Hints

<details>
<summary>Hint 1: Joint Configuration</summary>

Use a list of dictionaries:
```python
self.joints = [
    {'name': 'head_pan', 'frequency': 0.5, 'phase': 0.0},
    {'name': 'left_shoulder_pitch', 'frequency': 1.0, 'phase': 0.0},
    {'name': 'right_shoulder_pitch', 'frequency': 1.5, 'phase': 0.0},
]
```
</details>

<details>
<summary>Hint 2: Time Tracking</summary>

Track elapsed time:
```python
self.start_time = self.get_clock().now()

# In callback:
elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
```
</details>

<details>
<summary>Hint 3: Position Calculation</summary>

```python
position = amplitude * math.sin(2 * math.pi * frequency * elapsed)
```
</details>

## Solution

See `solutions/e2-1-solution.py` after attempting the exercise.

---

## Bonus Challenges

1. **Phase Offset**: Add configurable phase offset to each joint
2. **Parameters**: Make frequencies configurable via ROS parameters
3. **Visualization**: Create a separate subscriber that logs all received commands
4. **Different Waveforms**: Add support for square, triangle, and sawtooth waves
