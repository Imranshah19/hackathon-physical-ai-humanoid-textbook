#!/usr/bin/env python3
"""
Joint limits service server for humanoid robot.

Provides joint limit information via ROS 2 service.
Demonstrates service server implementation.
"""

import rclpy
from rclpy.node import Node
from humanoid_msgs.srv import GetJointLimits


class JointLimitsServer(Node):
    """Service server that returns joint limits from configuration."""

    # Joint limits configuration (would typically load from YAML)
    JOINT_LIMITS = {
        'head_pan': {
            'min_position': -1.57,
            'max_position': 1.57,
            'max_velocity': 2.0,
            'max_effort': 10.0
        },
        'left_shoulder_pitch': {
            'min_position': -3.14,
            'max_position': 1.57,
            'max_velocity': 1.5,
            'max_effort': 50.0
        },
        'left_elbow': {
            'min_position': 0.0,
            'max_position': 2.5,
            'max_velocity': 2.0,
            'max_effort': 30.0
        },
        'right_shoulder_pitch': {
            'min_position': -3.14,
            'max_position': 1.57,
            'max_velocity': 1.5,
            'max_effort': 50.0
        },
        'right_elbow': {
            'min_position': 0.0,
            'max_position': 2.5,
            'max_velocity': 2.0,
            'max_effort': 30.0
        },
        'left_hip_pitch': {
            'min_position': -1.57,
            'max_position': 1.57,
            'max_velocity': 1.5,
            'max_effort': 100.0
        },
        'left_knee': {
            'min_position': 0.0,
            'max_position': 2.5,
            'max_velocity': 2.0,
            'max_effort': 80.0
        },
        'left_ankle': {
            'min_position': -0.8,
            'max_position': 0.8,
            'max_velocity': 2.0,
            'max_effort': 50.0
        },
        'right_hip_pitch': {
            'min_position': -1.57,
            'max_position': 1.57,
            'max_velocity': 1.5,
            'max_effort': 100.0
        },
        'right_knee': {
            'min_position': 0.0,
            'max_position': 2.5,
            'max_velocity': 2.0,
            'max_effort': 80.0
        },
        'right_ankle': {
            'min_position': -0.8,
            'max_position': 0.8,
            'max_velocity': 2.0,
            'max_effort': 50.0
        },
    }

    def __init__(self) -> None:
        super().__init__('joint_limits_server')

        # Create service
        self.service = self.create_service(
            GetJointLimits,
            '/get_joint_limits',
            self.get_limits_callback
        )

        self.get_logger().info(
            f'Joint limits service ready ({len(self.JOINT_LIMITS)} joints configured)'
        )

    def get_limits_callback(
        self,
        request: GetJointLimits.Request,
        response: GetJointLimits.Response
    ) -> GetJointLimits.Response:
        """Handle service request for joint limits."""
        joint_name = request.joint_name

        self.get_logger().info(f'Received request for: {joint_name}')

        if joint_name in self.JOINT_LIMITS:
            limits = self.JOINT_LIMITS[joint_name]
            response.min_position = limits['min_position']
            response.max_position = limits['max_position']
            response.max_velocity = limits['max_velocity']
            response.max_effort = limits['max_effort']
            response.success = True
            response.message = f'Limits for {joint_name}'
        else:
            response.min_position = 0.0
            response.max_position = 0.0
            response.max_velocity = 0.0
            response.max_effort = 0.0
            response.success = False
            response.message = f'Unknown joint: {joint_name}'
            self.get_logger().warn(f'Unknown joint requested: {joint_name}')

        return response


def main(args=None) -> None:
    """Entry point."""
    rclpy.init(args=args)

    node = JointLimitsServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
