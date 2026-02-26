#!/usr/bin/env python3
"""
ROS 2 Humanoid Policy Inference Node.

This node subscribes to robot state and publishes torque commands
based on a trained locomotion policy.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

import numpy as np
import onnxruntime as ort

from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray


class ONNXPolicyInference:
    """ONNX Runtime policy inference."""

    def __init__(self, model_path: str, device: str = "cpu"):
        """
        Initialize ONNX inference session.

        Args:
            model_path: Path to ONNX model file
            device: Inference device ("cpu" or "cuda")
        """
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = (
            ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        )

        if device == "cuda":
            providers = [
                ("CUDAExecutionProvider", {"device_id": 0}),
                "CPUExecutionProvider",
            ]
        else:
            providers = ["CPUExecutionProvider"]

        self.session = ort.InferenceSession(
            model_path, sess_options, providers=providers
        )

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        # Warm up
        dummy = np.zeros((1, 48), dtype=np.float32)
        self.session.run([self.output_name], {self.input_name: dummy})

    def infer(self, observation: np.ndarray) -> np.ndarray:
        """
        Run inference on observation.

        Args:
            observation: (obs_dim,) or (batch, obs_dim) numpy array

        Returns:
            action: (action_dim,) or (batch, action_dim) numpy array
        """
        if observation.ndim == 1:
            observation = observation[np.newaxis, :]

        observation = observation.astype(np.float32)

        outputs = self.session.run(
            [self.output_name], {self.input_name: observation}
        )

        return outputs[0].squeeze()


class HumanoidPolicyNode(Node):
    """
    ROS 2 node for humanoid policy inference.

    Subscribes:
        - /joint_states: Joint positions and velocities
        - /imu: IMU sensor data
        - /cmd_vel: Velocity commands

    Publishes:
        - /joint_commands: Joint torque commands
    """

    def __init__(self):
        super().__init__("humanoid_policy_node")

        # Declare parameters
        self.declare_parameter("model_path", "policy.onnx")
        self.declare_parameter("inference_rate", 100.0)
        self.declare_parameter("action_scale", 0.5)

        # Get parameters
        model_path = self.get_parameter("model_path").value
        self.inference_rate = self.get_parameter("inference_rate").value
        self.action_scale = self.get_parameter("action_scale").value

        # Load ONNX model
        self.policy = ONNXPolicyInference(model_path, device="cpu")
        self.get_logger().info(f"Loaded policy from {model_path}")

        # Robot configuration
        self.num_dofs = 14
        self.obs_dim = 48

        # State buffers
        self.joint_positions = np.zeros(self.num_dofs, dtype=np.float32)
        self.joint_velocities = np.zeros(self.num_dofs, dtype=np.float32)
        self.base_lin_vel = np.zeros(3, dtype=np.float32)
        self.base_ang_vel = np.zeros(3, dtype=np.float32)
        self.gravity_proj = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.commands = np.zeros(3, dtype=np.float32)
        self.last_actions = np.zeros(self.num_dofs, dtype=np.float32)

        # Default joint positions
        self.default_dof_pos = np.array(
            [
                0.0, 0.0, 0.0, 0.3, 0.0,  # Left leg
                0.0, 0.0, 0.0, 0.3, 0.0,  # Right leg
                0.0, 0.0,  # Left arm
                0.0, 0.0,  # Right arm
            ],
            dtype=np.float32,
        )

        # Observation scales
        self.lin_vel_scale = 2.0
        self.ang_vel_scale = 0.25
        self.dof_pos_scale = 1.0
        self.dof_vel_scale = 0.05

        # Torque limits
        self.torque_limits = np.array(
            [100.0] * 10 + [50.0, 30.0, 50.0, 30.0], dtype=np.float32
        )

        # QoS profile
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        # Subscribers
        self.joint_sub = self.create_subscription(
            JointState, "/joint_states", self.joint_callback, qos
        )
        self.imu_sub = self.create_subscription(
            Imu, "/imu", self.imu_callback, qos
        )
        self.cmd_sub = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_callback, qos
        )

        # Publisher
        self.cmd_pub = self.create_publisher(Float64MultiArray, "/joint_commands", 10)

        # Timer for inference
        period = 1.0 / self.inference_rate
        self.timer = self.create_timer(period, self.inference_callback)

        self.get_logger().info(
            f"Policy node started at {self.inference_rate} Hz"
        )

    def joint_callback(self, msg: JointState):
        """Process joint state message."""
        for i, (pos, vel) in enumerate(zip(msg.position, msg.velocity)):
            if i < self.num_dofs:
                self.joint_positions[i] = pos
                self.joint_velocities[i] = vel

    def imu_callback(self, msg: Imu):
        """Process IMU message."""
        self.base_ang_vel[0] = msg.angular_velocity.x
        self.base_ang_vel[1] = msg.angular_velocity.y
        self.base_ang_vel[2] = msg.angular_velocity.z

        # Gravity projection from orientation
        q = msg.orientation
        self.gravity_proj = self._quat_rotate_inverse(
            np.array([q.x, q.y, q.z, q.w]), np.array([0.0, 0.0, -1.0])
        )

    def cmd_callback(self, msg: Twist):
        """Process velocity command."""
        self.commands[0] = msg.linear.x
        self.commands[1] = msg.linear.y
        self.commands[2] = msg.angular.z

    def inference_callback(self):
        """Run policy inference and publish commands."""
        # Build observation vector
        obs = self._build_observation()

        # Run inference
        action = self.policy.infer(obs)

        # Scale action to torques
        torques = action * self.action_scale * self.torque_limits

        # Update last actions
        self.last_actions = action.copy()

        # Publish
        msg = Float64MultiArray()
        msg.data = torques.tolist()
        self.cmd_pub.publish(msg)

    def _build_observation(self) -> np.ndarray:
        """Build observation vector from sensor data."""
        obs = np.concatenate(
            [
                self.base_lin_vel * self.lin_vel_scale,
                self.base_ang_vel * self.ang_vel_scale,
                self.gravity_proj,
                (self.joint_positions - self.default_dof_pos) * self.dof_pos_scale,
                self.joint_velocities * self.dof_vel_scale,
                self.commands,
                self.last_actions,
            ]
        )

        obs = np.clip(obs, -100.0, 100.0)
        return obs.astype(np.float32)

    def _quat_rotate_inverse(self, q, v):
        """Rotate vector by inverse of quaternion."""
        q_w = q[3]
        q_vec = q[:3]
        a = v * (2.0 * q_w**2 - 1.0)
        b = np.cross(q_vec, v) * q_w * 2.0
        c = q_vec * np.dot(q_vec, v) * 2.0
        return a - b + c


def main(args=None):
    rclpy.init(args=args)
    node = HumanoidPolicyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
