# Exercise 7.1: Debug Challenge

**Chapter**: 7 - Debugging and Tools
**Difficulty**: Intermediate
**Time**: 45 minutes

---

## Objective

Find and fix bugs in a provided ROS 2 system using debugging tools.

## Scenario

A fellow developer created a joint control system but it's not working. Your task is to:
1. Identify what's wrong using ROS 2 debugging tools
2. Document each bug found
3. Fix the issues

## The Buggy System

**File: buggy_publisher.py**
```python
#!/usr/bin/env python3
"""Buggy publisher - find the bugs!"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class BuggyPublisher(Node):
    def __init__(self):
        super().__init__('buggy_publisher')

        # Bug 1: Topic name typo
        self.publisher = self.create_publisher(
            Float64,
            '/joitn_commands',  # Intentional typo
            10
        )

        # Bug 2: Timer period is 0 (infinite rate)
        self.timer = self.create_timer(0, self.callback)

        self.count = 0

    def callback(self):
        msg = Float64()
        msg.data = float(self.count)
        self.publisher.publish(msg)
        self.count += 1


def main():
    rclpy.init()
    node = BuggyPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

**File: buggy_subscriber.py**
```python
#!/usr/bin/env python3
"""Buggy subscriber - find the bugs!"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32  # Bug 3: Wrong message type


class BuggySubscriber(Node):
    def __init__(self):
        super().__init__('buggy_subscriber')

        # Bug 4: Different topic name
        self.subscription = self.create_subscription(
            Float32,
            '/joint_commands',  # Correct spelling but wrong
            self.callback,
            10
        )

    # Bug 5: Callback signature wrong
    def callback(self):
        self.get_logger().info('Received message')


def main():
    rclpy.init()
    node = BuggySubscriber()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Debugging Tasks

### Task 1: Identify Communication Issues

Use these commands to investigate:

```bash
# List topics
ros2 topic list

# Check topic info
ros2 topic info /joint_commands
ros2 topic info /joitn_commands

# Check message rate
ros2 topic hz /joitn_commands

# Echo messages
ros2 topic echo /joitn_commands
```

**Questions to answer:**
1. Why isn't the subscriber receiving messages?
2. What topics exist in the system?
3. What's the actual publish rate?

### Task 2: Identify Type Mismatches

```bash
# Check message types
ros2 topic info /joitn_commands --verbose
ros2 interface show std_msgs/msg/Float64
ros2 interface show std_msgs/msg/Float32
```

**Questions to answer:**
1. What type is the publisher using?
2. What type is the subscriber expecting?
3. Would they be compatible even with same topic name?

### Task 3: Check Node Health

```bash
# List nodes
ros2 node list

# Node info
ros2 node info /buggy_publisher
ros2 node info /buggy_subscriber

# System diagnostics
ros2 doctor --report
```

### Task 4: Fix the Bugs

Create corrected versions:

**fixed_publisher.py** - Fix bugs 1 and 2
**fixed_subscriber.py** - Fix bugs 3, 4, and 5

## Bug Report Template

Document each bug:

```markdown
## Bug Report

### Bug 1: [Title]
- **Location**: file.py, line X
- **Symptom**: What was observed
- **Root cause**: Why it happened
- **Fix**: How to correct it

### Bug 2: ...
```

## Expected Bugs Summary

| # | File | Line | Issue |
|---|------|------|-------|
| 1 | buggy_publisher.py | 13 | Topic name typo |
| 2 | buggy_publisher.py | 18 | Timer period 0 |
| 3 | buggy_subscriber.py | 7 | Wrong message type import |
| 4 | buggy_subscriber.py | 15 | Topic name mismatch |
| 5 | buggy_subscriber.py | 21 | Callback missing `msg` parameter |

## Verification

After fixing:

```bash
# Run fixed nodes
ros2 run humanoid_control fixed_publisher &
ros2 run humanoid_control fixed_subscriber

# Verify communication
ros2 topic hz /joint_commands
# Expected: ~10 Hz

ros2 topic echo /joint_commands
# Expected: incrementing values
```

---

## Bonus Challenge

Add these additional bugs and find them:
1. QoS mismatch between publisher and subscriber
2. Node name collision (two nodes with same name)
3. Parameter that causes crash when invalid
