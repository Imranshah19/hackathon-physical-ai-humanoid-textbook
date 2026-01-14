#!/usr/bin/env python3
"""
Move to position action server for humanoid robot.

Moves a joint to a target position with feedback.
Demonstrates action server implementation with goal handling.
"""

import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from humanoid_msgs.action import MoveToPosition


class MoveActionServer(Node):
    """Action server for moving joints to target positions."""

    def __init__(self) -> None:
        super().__init__('move_action_server')

        # Simulated joint positions
        self.joint_positions: dict[str, float] = {
            'head_pan': 0.0,
            'left_shoulder_pitch': 0.0,
            'left_elbow': 0.0,
            'right_shoulder_pitch': 0.0,
            'right_elbow': 0.0,
            'left_hip_pitch': 0.0,
            'left_knee': 0.0,
            'left_ankle': 0.0,
            'right_hip_pitch': 0.0,
            'right_knee': 0.0,
            'right_ankle': 0.0,
        }

        # Create action server
        self._action_server = ActionServer(
            self,
            MoveToPosition,
            '/move_to_position',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )

        self.get_logger().info('Move action server ready')

    def goal_callback(self, goal_request) -> GoalResponse:
        """Accept or reject incoming goal requests."""
        joint_name = goal_request.joint_name

        if joint_name not in self.joint_positions:
            self.get_logger().warn(f'Rejecting goal: unknown joint {joint_name}')
            return GoalResponse.REJECT

        self.get_logger().info(
            f'Accepting goal: {joint_name} -> {goal_request.target_position:.3f} rad'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle) -> CancelResponse:
        """Accept cancel requests."""
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        """Execute the motion to target position."""
        self.get_logger().info('Executing goal...')

        # Extract goal parameters
        joint_name = goal_handle.request.joint_name
        target = goal_handle.request.target_position
        max_vel = goal_handle.request.max_velocity

        # Get current position
        current = self.joint_positions[joint_name]
        start_time = time.time()

        # Feedback message
        feedback_msg = MoveToPosition.Feedback()

        # Control loop rate
        rate = 0.02  # 50 Hz

        # Simulate motion until target reached
        while abs(target - current) > 0.001:
            # Check for cancellation
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal cancelled')

                result = MoveToPosition.Result()
                result.final_position = current
                result.error = abs(target - current)
                result.success = False
                result.message = 'Motion cancelled'
                return result

            # Calculate motion step
            direction = 1.0 if target > current else -1.0
            step = min(max_vel * rate, abs(target - current))
            current += direction * step

            # Update simulated position
            self.joint_positions[joint_name] = current

            # Publish feedback
            feedback_msg.current_position = current
            feedback_msg.remaining_distance = abs(target - current)
            feedback_msg.elapsed_time = time.time() - start_time
            goal_handle.publish_feedback(feedback_msg)

            # Wait for next iteration
            time.sleep(rate)

        # Motion complete - success
        goal_handle.succeed()

        result = MoveToPosition.Result()
        result.final_position = current
        result.error = abs(target - current)
        result.success = True
        result.message = 'Motion complete'

        self.get_logger().info(
            f'Goal succeeded: {joint_name} at {current:.3f} rad '
            f'(elapsed: {time.time() - start_time:.2f}s)'
        )

        return result


def main(args=None) -> None:
    """Entry point."""
    rclpy.init(args=args)

    node = MoveActionServer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
