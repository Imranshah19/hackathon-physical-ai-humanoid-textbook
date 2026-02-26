#!/usr/bin/env python3
"""
Lifecycle-managed joint controller for humanoid robot.

Demonstrates lifecycle node implementation with safe state transitions.
Only publishes commands when in the active state.
"""

import math

import rclpy
from rclpy.lifecycle import Node as LifecycleNode
from rclpy.lifecycle import State, TransitionCallbackReturn
from std_msgs.msg import Float64
from humanoid_msgs.msg import JointCommand


class LifecycleJointController(LifecycleNode):
    """Lifecycle-managed joint controller with safe state transitions."""

    def __init__(self) -> None:
        super().__init__('lifecycle_joint_controller')

        # Declare parameters (available in all states)
        self.declare_parameter('joint_name', 'head_pan')
        self.declare_parameter('control_rate', 50.0)
        self.declare_parameter('amplitude', 0.5)
        self.declare_parameter('frequency', 0.5)

        # Initialize attributes (set properly in on_configure)
        self.publisher = None
        self.timer = None
        self.start_time = None

        self.get_logger().info('Lifecycle controller created (unconfigured)')

    # ==================== Lifecycle Callbacks ====================

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        """
        Configure the node.

        Load parameters and create publisher (but don't start publishing).
        """
        self.get_logger().info('Configuring...')

        try:
            # Get parameters
            self.joint_name = self.get_parameter('joint_name').value
            self.control_rate = self.get_parameter('control_rate').value
            self.amplitude = self.get_parameter('amplitude').value
            self.frequency = self.get_parameter('frequency').value

            # Validate parameters
            if self.control_rate <= 0:
                self.get_logger().error('Invalid control_rate')
                return TransitionCallbackReturn.FAILURE

            # Create lifecycle publisher (inactive until activated)
            self.publisher = self.create_lifecycle_publisher(
                Float64,
                f'/{self.joint_name}/command',
                10
            )

            self.get_logger().info(
                f'Configured: {self.joint_name} at {self.control_rate} Hz'
            )
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'Configuration failed: {e}')
            return TransitionCallbackReturn.FAILURE

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        """
        Activate the node.

        Start the control loop timer.
        """
        self.get_logger().info('Activating...')

        try:
            # Record start time for motion calculation
            self.start_time = self.get_clock().now()

            # Create control timer
            period = 1.0 / self.control_rate
            self.timer = self.create_timer(period, self.control_callback)

            self.get_logger().info('Controller ACTIVE - publishing commands')
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'Activation failed: {e}')
            return TransitionCallbackReturn.FAILURE

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        """
        Deactivate the node.

        Stop publishing and hold position.
        """
        self.get_logger().info('Deactivating...')

        try:
            # Stop timer
            if self.timer is not None:
                self.timer.cancel()
                self.timer = None

            self.get_logger().info('Controller INACTIVE - holding position')
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'Deactivation failed: {e}')
            return TransitionCallbackReturn.FAILURE

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        """
        Clean up the node.

        Release all resources.
        """
        self.get_logger().info('Cleaning up...')

        try:
            # Destroy publisher
            if self.publisher is not None:
                self.destroy_publisher(self.publisher)
                self.publisher = None

            self.get_logger().info('Cleanup complete')
            return TransitionCallbackReturn.SUCCESS

        except Exception as e:
            self.get_logger().error(f'Cleanup failed: {e}')
            return TransitionCallbackReturn.FAILURE

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        """
        Shutdown the node.

        Final cleanup before destruction.
        """
        self.get_logger().info('Shutting down...')

        # Ensure cleanup
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

        return TransitionCallbackReturn.SUCCESS

    # ==================== Control Callback ====================

    def control_callback(self) -> None:
        """
        Control loop callback.

        Only called when node is active.
        """
        if self.start_time is None:
            return

        # Calculate elapsed time
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9

        # Calculate sinusoidal position
        position = self.amplitude * math.sin(
            2 * math.pi * self.frequency * elapsed
        )

        # Publish command
        msg = Float64()
        msg.data = position
        self.publisher.publish(msg)


def main(args=None) -> None:
    """Entry point."""
    rclpy.init(args=args)

    node = LifecycleJointController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
