#!/usr/bin/env python3
"""
Joint command publisher for humanoid robot.

This node publishes joint position commands using custom messages.
Demonstrates publisher creation, timers, and parameters.
"""

import math

import rclpy
from rclpy.node import Node
from humanoid_msgs.msg import JointCommand


class JointPublisher(Node):
    """Publishes sinusoidal joint commands for testing."""

    def __init__(self) -> None:
        super().__init__('joint_publisher')

        # Declare parameters
        self.declare_parameter('joint_name', 'head_pan')
        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('amplitude', 0.5)
        self.declare_parameter('frequency', 0.5)

        # Get parameters
        self.joint_name = self.get_parameter('joint_name').value
        rate = self.get_parameter('publish_rate').value
        self.amplitude = self.get_parameter('amplitude').value
        self.frequency = self.get_parameter('frequency').value

        # Create publisher
        self.publisher = self.create_publisher(
            JointCommand,
            '/joint_commands',
            10
        )

        # Create timer
        timer_period = 1.0 / rate
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # State
        self.start_time = self.get_clock().now()

        self.get_logger().info(
            f'Joint publisher started: {self.joint_name} at {rate} Hz'
        )

    def timer_callback(self) -> None:
        """Publish joint command at each timer tick."""
        # Calculate elapsed time
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        # Calculate sinusoidal position
        position = self.amplitude * math.sin(
            2 * math.pi * self.frequency * elapsed
        )

        # Create message
        msg = JointCommand()
        msg.joint_name = self.joint_name
        msg.position = position
        msg.velocity = 0.0
        msg.effort = 0.0
        msg.stamp = self.get_clock().now().to_msg()

        # Publish
        self.publisher.publish(msg)

        # Log periodically
        if int(elapsed) % 5 == 0 and elapsed - int(elapsed) < 0.1:
            self.get_logger().info(
                f'{self.joint_name}: {position:.3f} rad'
            )


def main(args=None) -> None:
    """Entry point."""
    rclpy.init(args=args)

    node = JointPublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
