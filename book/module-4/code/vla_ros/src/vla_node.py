"""
VLA ROS 2 Node for Humanoid Robot Control

This module implements the ROS 2 node that bridges the VLA model
with the robot control system.

Reference: Chapter 6 - ROS 2 Integration
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from std_msgs.msg import String, Bool, Float32MultiArray
from sensor_msgs.msg import Image, JointState
from geometry_msgs.msg import PoseStamped

from cv_bridge import CvBridge
import numpy as np
from PIL import Image as PILImage
from dataclasses import dataclass
from typing import Optional, Dict, Any
import threading
import time

# Import VLA components (would be installed as package)
# from vla_core.models.openvla_wrapper import OpenVLAWrapper, VLAConfig
# from vla_core.safety.safety_filter import SafetyFilter, SafetyConfig


@dataclass
class VLANodeConfig:
    """Configuration for VLA node."""
    # Model settings
    model_name: str = "openvla/openvla-7b"
    action_dim: int = 22  # Full humanoid
    use_quantization: bool = True

    # Control settings
    control_rate: float = 20.0  # Hz
    action_horizon: int = 1

    # Topics
    camera_topic: str = "/camera/color/image_raw"
    joint_state_topic: str = "/joint_states"
    action_topic: str = "/vla/action"
    command_topic: str = "/vla/command"
    status_topic: str = "/vla/status"

    # Safety
    safety_enabled: bool = True
    confidence_threshold: float = 0.5


class VLANode(Node):
    """
    ROS 2 node for Vision-Language-Action inference.

    Subscribes to:
        - /camera/color/image_raw: RGB camera images
        - /joint_states: Current robot joint states
        - /vla/command: Text commands for the robot

    Publishes:
        - /vla/action: Generated action commands
        - /vla/status: Node status and diagnostics
    """

    def __init__(self, config: VLANodeConfig = None):
        super().__init__('vla_node')

        self.config = config or VLANodeConfig()

        # Declare and load parameters
        self._declare_parameters()
        self._load_parameters()

        # Initialize state
        self.cv_bridge = CvBridge()
        self.current_image: Optional[np.ndarray] = None
        self.current_joint_state: Optional[np.ndarray] = None
        self.current_instruction: str = ""
        self.is_active: bool = False
        self._lock = threading.Lock()

        # Initialize VLA model
        self.get_logger().info("Loading VLA model...")
        self._init_vla_model()

        # Initialize safety filter
        if self.config.safety_enabled:
            self._init_safety_filter()

        # Setup QoS profiles
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Create callback groups
        self.sensor_cb_group = ReentrantCallbackGroup()
        self.control_cb_group = MutuallyExclusiveCallbackGroup()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image,
            self.config.camera_topic,
            self.image_callback,
            sensor_qos,
            callback_group=self.sensor_cb_group,
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            self.config.joint_state_topic,
            self.joint_state_callback,
            sensor_qos,
            callback_group=self.sensor_cb_group,
        )

        self.command_sub = self.create_subscription(
            String,
            self.config.command_topic,
            self.command_callback,
            reliable_qos,
            callback_group=self.control_cb_group,
        )

        # Publishers
        self.action_pub = self.create_publisher(
            Float32MultiArray,
            self.config.action_topic,
            reliable_qos,
        )

        self.status_pub = self.create_publisher(
            String,
            self.config.status_topic,
            reliable_qos,
        )

        # Control timer
        control_period = 1.0 / self.config.control_rate
        self.control_timer = self.create_timer(
            control_period,
            self.control_callback,
            callback_group=self.control_cb_group,
        )

        # Status timer
        self.status_timer = self.create_timer(
            1.0,  # 1 Hz status updates
            self.status_callback,
            callback_group=self.sensor_cb_group,
        )

        self.get_logger().info("VLA node initialized")

    def _declare_parameters(self) -> None:
        """Declare ROS 2 parameters."""
        self.declare_parameter('model_name', self.config.model_name)
        self.declare_parameter('action_dim', self.config.action_dim)
        self.declare_parameter('use_quantization', self.config.use_quantization)
        self.declare_parameter('control_rate', self.config.control_rate)
        self.declare_parameter('safety_enabled', self.config.safety_enabled)
        self.declare_parameter('confidence_threshold', self.config.confidence_threshold)

    def _load_parameters(self) -> None:
        """Load parameters from ROS 2 parameter server."""
        self.config.model_name = self.get_parameter('model_name').value
        self.config.action_dim = self.get_parameter('action_dim').value
        self.config.use_quantization = self.get_parameter('use_quantization').value
        self.config.control_rate = self.get_parameter('control_rate').value
        self.config.safety_enabled = self.get_parameter('safety_enabled').value
        self.config.confidence_threshold = self.get_parameter('confidence_threshold').value

    def _init_vla_model(self) -> None:
        """Initialize the VLA model."""
        # Placeholder - actual implementation would load the model
        self.vla_model = None
        self.get_logger().info(f"VLA model placeholder initialized")

        # In actual implementation:
        # from vla_core.models.openvla_wrapper import OpenVLAWrapper, VLAConfig
        # vla_config = VLAConfig(
        #     model_name=self.config.model_name,
        #     action_dim=self.config.action_dim,
        #     use_quantization=self.config.use_quantization,
        # )
        # self.vla_model = OpenVLAWrapper(vla_config)

    def _init_safety_filter(self) -> None:
        """Initialize the safety filter."""
        # Placeholder - actual implementation would create safety filter
        self.safety_filter = None
        self.get_logger().info("Safety filter placeholder initialized")

        # In actual implementation:
        # from vla_core.safety.safety_filter import SafetyFilter, SafetyConfig
        # safety_config = SafetyConfig(...)
        # self.safety_filter = SafetyFilter(safety_config)

    def image_callback(self, msg: Image) -> None:
        """Handle incoming camera images."""
        try:
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, "rgb8")
            with self._lock:
                self.current_image = cv_image
        except Exception as e:
            self.get_logger().error(f"Image conversion error: {e}")

    def joint_state_callback(self, msg: JointState) -> None:
        """Handle incoming joint states."""
        with self._lock:
            self.current_joint_state = np.array(msg.position)

    def command_callback(self, msg: String) -> None:
        """Handle incoming text commands."""
        command = msg.data.strip()

        if command.lower() == "stop":
            self.is_active = False
            self.get_logger().info("VLA control stopped")
        elif command.lower() == "start":
            self.is_active = True
            self.get_logger().info("VLA control started")
        elif command.startswith("task:"):
            self.current_instruction = command[5:].strip()
            self.is_active = True
            self.get_logger().info(f"New task: {self.current_instruction}")
        else:
            self.current_instruction = command
            self.is_active = True
            self.get_logger().info(f"Instruction: {self.current_instruction}")

    def control_callback(self) -> None:
        """Main control loop - generate and publish actions."""
        if not self.is_active:
            return

        with self._lock:
            image = self.current_image
            joint_state = self.current_joint_state
            instruction = self.current_instruction

        if image is None or instruction == "":
            return

        try:
            # Generate action from VLA model
            action, confidence = self._predict_action(image, instruction, joint_state)

            if action is None:
                return

            # Apply safety filter
            if self.config.safety_enabled and self.safety_filter is not None:
                result = self.safety_filter.filter(
                    action,
                    joint_state if joint_state is not None else np.zeros(self.config.action_dim),
                    confidence=confidence,
                )
                action = result.action
                if not result.is_safe:
                    self.get_logger().warn(f"Safety violations: {result.violations}")

            # Publish action
            action_msg = Float32MultiArray()
            action_msg.data = action.tolist()
            self.action_pub.publish(action_msg)

        except Exception as e:
            self.get_logger().error(f"Control error: {e}")

    def _predict_action(
        self,
        image: np.ndarray,
        instruction: str,
        joint_state: Optional[np.ndarray],
    ) -> tuple:
        """Generate action prediction from VLA model."""
        if self.vla_model is None:
            # Placeholder - return zero action
            return np.zeros(self.config.action_dim), 1.0

        # Convert to PIL Image
        pil_image = PILImage.fromarray(image)

        # Run inference
        # output = self.vla_model.predict(pil_image, instruction, joint_state)
        # return output.actions, output.confidence

        # Placeholder return
        return np.zeros(self.config.action_dim), 1.0

    def status_callback(self) -> None:
        """Publish node status."""
        status = {
            'active': self.is_active,
            'has_image': self.current_image is not None,
            'has_joint_state': self.current_joint_state is not None,
            'instruction': self.current_instruction,
            'safety_enabled': self.config.safety_enabled,
        }

        status_msg = String()
        status_msg.data = str(status)
        self.status_pub.publish(status_msg)


def main(args=None):
    """Main entry point."""
    rclpy.init(args=args)

    config = VLANodeConfig()
    node = VLANode(config)

    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
