#!/usr/bin/env python3
"""
Joint command subscriber for humanoid robot.

Subscribes to joint commands and logs received messages.
Demonstrates subscription creation and callback handling.
"""

import rclpy
from rclpy.node import Node
from humanoid_msgs.msg import JointCommand


class JointSubscriber(Node):
    """Subscribes to joint commands and tracks statistics."""

    def __init__(self) -> None:
        super().__init__('joint_subscriber')

        # Create subscription
        self.subscription = self.create_subscription(
            JointCommand,
            '/joint_commands',
            self.command_callback,
            10
        )

        # Statistics
        self.message_count = 0
        self.joints_seen: dict[str, int] = {}

        self.get_logger().info('Joint subscriber started')

    def command_callback(self, msg: JointCommand) -> None:
        """Process incoming joint commands."""
        self.message_count += 1

        # Track per-joint statistics
        if msg.joint_name not in self.joints_seen:
            self.joints_seen[msg.joint_name] = 0
        self.joints_seen[msg.joint_name] += 1

        # Log every 10th message
        if self.message_count % 10 == 0:
            self.get_logger().info(
                f'[{self.message_count}] {msg.joint_name}: '
                f'pos={msg.position:.3f} rad, '
                f'vel={msg.velocity:.3f} rad/s'
            )

    def log_statistics(self) -> None:
        """Log accumulated statistics."""
        self.get_logger().info(f'Total messages: {self.message_count}')
        for joint, count in self.joints_seen.items():
            self.get_logger().info(f'  {joint}: {count} messages')


def main(args=None) -> None:
    """Entry point."""
    rclpy.init(args=args)

    node = JointSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.log_statistics()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
