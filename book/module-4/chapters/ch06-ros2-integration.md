# Chapter 6: ROS 2 VLA Node Implementation

**Duration**: 5-6 hours
**Prerequisites**: Chapter 5 (VLA Pipeline), ROS 2 basics from Module 1

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Design ROS 2 nodes for VLA inference
- Subscribe to camera and sensor topics
- Publish robot commands from VLA outputs
- Implement real-time control loops
- Create launch files for VLA systems

---

## 6.1 ROS 2 Architecture for VLA

```
┌─────────────────────────────────────────────────────────────────┐
│                   ROS 2 VLA System Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Camera    │  │   Speech    │  │      Joint State        │ │
│  │    Node     │  │    Node     │  │        Node             │ │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │
│         │                │                      │               │
│         ▼                ▼                      ▼               │
│  /camera/image_raw  /vla/instruction     /joint_states         │
│         │                │                      │               │
│         └────────────────┼──────────────────────┘               │
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    VLA Node                              │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │   Camera    │  │  Instruction│  │    State     │    │   │
│  │  │ Subscriber  │  │  Subscriber │  │  Subscriber  │    │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘    │   │
│  │         └────────────────┼────────────────┘            │   │
│  │                          ▼                              │   │
│  │              ┌─────────────────────┐                   │   │
│  │              │    VLA Pipeline     │                   │   │
│  │              └──────────┬──────────┘                   │   │
│  │                         ▼                              │   │
│  │              ┌─────────────────────┐                   │   │
│  │              │   Safety Filter     │                   │   │
│  │              └──────────┬──────────┘                   │   │
│  │                         ▼                              │   │
│  │              ┌─────────────────────┐                   │   │
│  │              │  Action Publisher   │                   │   │
│  │              └──────────┬──────────┘                   │   │
│  └─────────────────────────┼───────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│                    /joint_commands                               │
│                            │                                     │
│                            ▼                                     │
│                    ┌──────────────┐                              │
│                    │  Controller  │                              │
│                    │    Node      │                              │
│                    └──────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6.2 Custom Message Definitions

### VLA Messages

Create custom messages for VLA communication:

```
# msg/VLACommand.msg
# Natural language command for VLA

std_msgs/Header header
string instruction          # Natural language instruction
bool urgent                 # Priority flag
float32 timeout            # Execution timeout in seconds
```

```
# msg/VLAAction.msg
# Action output from VLA model

std_msgs/Header header
float64[7] action          # Action values (x,y,z,rx,ry,rz,gripper)
float32 confidence         # Model confidence
string instruction         # Original instruction
bool is_final              # Whether this is the final action
```

```
# msg/VLAStatus.msg
# VLA node status

std_msgs/Header header
uint8 state                 # 0=IDLE, 1=PROCESSING, 2=EXECUTING, 3=ERROR
string current_instruction  # Current active instruction
float32 progress           # Execution progress 0-1
string error_message       # Error description if any

uint8 IDLE = 0
uint8 PROCESSING = 1
uint8 EXECUTING = 2
uint8 ERROR = 3
```

### Service Definitions

```
# srv/ExecuteTask.srv
# Service to execute a VLA task

string instruction          # Natural language instruction
float32 timeout            # Timeout in seconds
---
bool success               # Whether task completed successfully
string message             # Result message
float32 execution_time     # Time taken in seconds
```

### Package Configuration

```xml
<!-- package.xml -->
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>humanoid_vla_ros</name>
  <version>0.1.0</version>
  <description>ROS 2 interface for VLA models</description>
  <maintainer email="user@example.com">User</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <buildtool_depend>rosidl_default_generators</buildtool_depend>

  <depend>rclpy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>trajectory_msgs</depend>
  <depend>cv_bridge</depend>

  <exec_depend>rosidl_default_runtime</exec_depend>

  <member_of_group>rosidl_interface_packages</member_of_group>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

---

## 6.3 VLA Node Implementation

### Main VLA Node

```python
#!/usr/bin/env python3
"""
VLA ROS 2 Node

Integrates VLA model with ROS 2 for robot control.
"""

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

import numpy as np
from PIL import Image
import torch
from threading import Lock
from typing import Optional
import time

# ROS 2 messages
from sensor_msgs.msg import Image as ImageMsg, JointState
from std_msgs.msg import String
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from cv_bridge import CvBridge

# Custom messages (would be generated from .msg files)
# from humanoid_vla_ros.msg import VLACommand, VLAAction, VLAStatus
# from humanoid_vla_ros.srv import ExecuteTask


class VLANode(Node):
    """ROS 2 Node for VLA inference and control."""

    def __init__(self):
        super().__init__('vla_node')

        # Declare parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('model_path', 'openvla/openvla-7b'),
                ('use_quantization', True),
                ('quantization_bits', 4),
                ('control_rate', 10.0),  # Hz
                ('safety_enabled', True),
                ('confidence_threshold', 0.5),
            ]
        )

        # Get parameters
        self.model_path = self.get_parameter('model_path').value
        self.use_quantization = self.get_parameter('use_quantization').value
        self.quantization_bits = self.get_parameter('quantization_bits').value
        self.control_rate = self.get_parameter('control_rate').value
        self.safety_enabled = self.get_parameter('safety_enabled').value
        self.confidence_threshold = self.get_parameter('confidence_threshold').value

        # Initialize components
        self.cv_bridge = CvBridge()
        self.lock = Lock()

        # State variables
        self.latest_image: Optional[np.ndarray] = None
        self.latest_instruction: Optional[str] = None
        self.latest_joint_state: Optional[np.ndarray] = None
        self.is_executing = False

        # Callback groups for threading
        self.sensor_callback_group = ReentrantCallbackGroup()
        self.inference_callback_group = MutuallyExclusiveCallbackGroup()

        # Initialize VLA pipeline
        self._init_vla_pipeline()

        # Initialize safety filter
        self._init_safety_filter()

        # Create subscribers
        self._create_subscribers()

        # Create publishers
        self._create_publishers()

        # Create services
        self._create_services()

        # Create control timer
        self.control_timer = self.create_timer(
            1.0 / self.control_rate,
            self.control_callback,
            callback_group=self.inference_callback_group
        )

        self.get_logger().info(f"VLA Node initialized")
        self.get_logger().info(f"  Model: {self.model_path}")
        self.get_logger().info(f"  Control rate: {self.control_rate} Hz")

    def _init_vla_pipeline(self):
        """Initialize VLA inference pipeline."""
        from vla_pipeline import VLAPipeline, VLAConfig

        self.get_logger().info("Loading VLA model...")

        config = VLAConfig(
            model_path=self.model_path,
            use_quantization=self.use_quantization,
            quantization_bits=self.quantization_bits,
        )

        self.vla_pipeline = VLAPipeline(config)
        self.get_logger().info("VLA model loaded successfully")

    def _init_safety_filter(self):
        """Initialize safety filter."""
        from safety_filter import SafetyFilter, SafetyConfig

        config = SafetyConfig(
            joint_limits={
                'left_hip_yaw': (-0.5, 0.5),
                'left_hip_roll': (-0.3, 0.5),
                # ... other joints
            },
            max_velocity=1.0,
            max_acceleration=2.0,
            workspace_bounds={
                'x': (-0.5, 0.5),
                'y': (-0.5, 0.5),
                'z': (0.0, 0.8),
            }
        )

        self.safety_filter = SafetyFilter(config)

    def _create_subscribers(self):
        """Create ROS 2 subscribers."""
        # Camera subscriber
        qos_sensor = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.image_sub = self.create_subscription(
            ImageMsg,
            '/camera/image_raw',
            self.image_callback,
            qos_sensor,
            callback_group=self.sensor_callback_group
        )

        # Instruction subscriber
        self.instruction_sub = self.create_subscription(
            String,
            '/vla/instruction',
            self.instruction_callback,
            10,
            callback_group=self.sensor_callback_group
        )

        # Joint state subscriber
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            qos_sensor,
            callback_group=self.sensor_callback_group
        )

    def _create_publishers(self):
        """Create ROS 2 publishers."""
        # Joint trajectory publisher
        self.joint_cmd_pub = self.create_publisher(
            JointTrajectory,
            '/joint_commands',
            10
        )

        # Status publisher
        self.status_pub = self.create_publisher(
            String,  # Would be VLAStatus
            '/vla/status',
            10
        )

    def _create_services(self):
        """Create ROS 2 services."""
        # Execute task service
        # self.execute_srv = self.create_service(
        #     ExecuteTask,
        #     '/vla/execute_task',
        #     self.execute_task_callback
        # )
        pass

    def image_callback(self, msg: ImageMsg):
        """Handle incoming camera images."""
        try:
            # Convert ROS image to numpy
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'rgb8')

            with self.lock:
                self.latest_image = cv_image

        except Exception as e:
            self.get_logger().error(f"Image callback error: {e}")

    def instruction_callback(self, msg: String):
        """Handle incoming instructions."""
        instruction = msg.data.strip()

        if instruction:
            with self.lock:
                self.latest_instruction = instruction
                self.is_executing = True

            self.get_logger().info(f"Received instruction: {instruction}")

    def joint_state_callback(self, msg: JointState):
        """Handle incoming joint states."""
        with self.lock:
            self.latest_joint_state = np.array(msg.position)

    def control_callback(self):
        """Main control loop callback."""
        # Check if we have all required data
        with self.lock:
            image = self.latest_image
            instruction = self.latest_instruction
            joint_state = self.latest_joint_state
            is_executing = self.is_executing

        if not is_executing:
            return

        if image is None:
            self.get_logger().warn("No image available")
            return

        if instruction is None:
            return

        try:
            # Convert numpy to PIL
            pil_image = Image.fromarray(image)

            # Run VLA inference
            start_time = time.perf_counter()

            output = self.vla_pipeline.predict(
                pil_image,
                instruction,
                joint_state
            )

            inference_time = (time.perf_counter() - start_time) * 1000

            # Check confidence
            if output.confidence < self.confidence_threshold:
                self.get_logger().warn(
                    f"Low confidence ({output.confidence:.2f}), skipping action"
                )
                return

            # Apply safety filter
            if self.safety_enabled:
                safe_action, is_safe = self.safety_filter.filter(
                    output.actions[0],
                    joint_state
                )
                if not is_safe:
                    self.get_logger().warn("Action filtered by safety system")
            else:
                safe_action = output.actions[0]

            # Publish action
            self.publish_action(safe_action)

            self.get_logger().debug(
                f"Action: {safe_action[:3]} | "
                f"Conf: {output.confidence:.2f} | "
                f"Time: {inference_time:.0f}ms"
            )

        except Exception as e:
            self.get_logger().error(f"Control loop error: {e}")

    def publish_action(self, action: np.ndarray):
        """Publish action to robot controller."""
        msg = JointTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()

        # Joint names (customize for your robot)
        msg.joint_names = [
            'joint_1', 'joint_2', 'joint_3', 'joint_4',
            'joint_5', 'joint_6', 'gripper'
        ]

        # Create trajectory point
        point = JointTrajectoryPoint()
        point.positions = action.tolist()
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = int(0.1 * 1e9)  # 100ms

        msg.points = [point]

        self.joint_cmd_pub.publish(msg)

    def stop_execution(self):
        """Stop current execution."""
        with self.lock:
            self.is_executing = False
            self.latest_instruction = None

        self.get_logger().info("Execution stopped")


def main(args=None):
    rclpy.init(args=args)

    node = VLANode()

    # Use multi-threaded executor
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
```

---

## 6.4 Camera Processing Node

Handle image preprocessing:

```python
#!/usr/bin/env python3
"""
Camera processing node for VLA.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
import cv2
import numpy as np


class CameraProcessorNode(Node):
    """Process camera images for VLA input."""

    def __init__(self):
        super().__init__('camera_processor')

        # Parameters
        self.declare_parameter('input_topic', '/camera/image_raw')
        self.declare_parameter('output_topic', '/vla/image')
        self.declare_parameter('target_width', 640)
        self.declare_parameter('target_height', 480)
        self.declare_parameter('use_compression', False)

        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.target_width = self.get_parameter('target_width').value
        self.target_height = self.get_parameter('target_height').value
        self.use_compression = self.get_parameter('use_compression').value

        self.cv_bridge = CvBridge()

        # Create subscriber and publisher
        self.image_sub = self.create_subscription(
            Image,
            self.input_topic,
            self.image_callback,
            10
        )

        self.image_pub = self.create_publisher(
            Image,
            self.output_topic,
            10
        )

        self.get_logger().info(f"Camera processor: {self.input_topic} -> {self.output_topic}")

    def image_callback(self, msg: Image):
        """Process incoming image."""
        try:
            # Convert to OpenCV
            cv_image = self.cv_bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Resize if needed
            h, w = cv_image.shape[:2]
            if w != self.target_width or h != self.target_height:
                cv_image = cv2.resize(
                    cv_image,
                    (self.target_width, self.target_height),
                    interpolation=cv2.INTER_LINEAR
                )

            # Convert BGR to RGB
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

            # Convert back to ROS message
            out_msg = self.cv_bridge.cv2_to_imgmsg(cv_image, 'rgb8')
            out_msg.header = msg.header

            self.image_pub.publish(out_msg)

        except Exception as e:
            self.get_logger().error(f"Image processing error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = CameraProcessorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## 6.5 Command Interface Node

Handle text command input:

```python
#!/usr/bin/env python3
"""
Command interface for VLA.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import threading


class CommandInterfaceNode(Node):
    """Terminal interface for VLA commands."""

    def __init__(self):
        super().__init__('command_interface')

        # Publisher
        self.cmd_pub = self.create_publisher(
            String,
            '/vla/instruction',
            10
        )

        # Status subscriber
        self.status_sub = self.create_subscription(
            String,
            '/vla/status',
            self.status_callback,
            10
        )

        self.current_status = "IDLE"

        # Start input thread
        self.input_thread = threading.Thread(target=self.input_loop, daemon=True)
        self.input_thread.start()

        self.get_logger().info("Command interface ready. Type 'help' for commands.")

    def status_callback(self, msg: String):
        """Handle status updates."""
        self.current_status = msg.data

    def input_loop(self):
        """Handle terminal input."""
        print("\n" + "=" * 50)
        print("VLA Command Interface")
        print("=" * 50)
        print("Commands:")
        print("  <instruction>  - Send instruction to VLA")
        print("  status         - Show current status")
        print("  stop           - Stop execution")
        print("  quit           - Exit interface")
        print("=" * 50 + "\n")

        while rclpy.ok():
            try:
                user_input = input("VLA> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    rclpy.shutdown()
                    break

                if user_input.lower() == 'status':
                    print(f"Status: {self.current_status}")
                    continue

                if user_input.lower() == 'stop':
                    msg = String()
                    msg.data = "__STOP__"
                    self.cmd_pub.publish(msg)
                    print("Stop command sent")
                    continue

                if user_input.lower() == 'help':
                    print("Enter a natural language instruction, e.g.:")
                    print("  'pick up the red block'")
                    print("  'put the cup on the tray'")
                    print("  'move to the left'")
                    continue

                # Send instruction
                msg = String()
                msg.data = user_input
                self.cmd_pub.publish(msg)
                print(f"Sent: {user_input}")

            except EOFError:
                break
            except KeyboardInterrupt:
                break


def main(args=None):
    rclpy.init(args=args)
    node = CommandInterfaceNode()

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

---

## 6.6 Launch Files

### Main VLA Launch

```python
# launch/vla_demo.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare arguments
    model_path_arg = DeclareLaunchArgument(
        'model_path',
        default_value='openvla/openvla-7b',
        description='Path to VLA model'
    )

    use_sim_arg = DeclareLaunchArgument(
        'use_sim',
        default_value='true',
        description='Use simulation'
    )

    # VLA node
    vla_node = Node(
        package='humanoid_vla_ros',
        executable='vla_node',
        name='vla_node',
        parameters=[{
            'model_path': LaunchConfiguration('model_path'),
            'use_quantization': True,
            'quantization_bits': 4,
            'control_rate': 10.0,
            'safety_enabled': True,
            'confidence_threshold': 0.5,
        }],
        output='screen'
    )

    # Camera processor
    camera_processor = Node(
        package='humanoid_vla_ros',
        executable='camera_processor',
        name='camera_processor',
        parameters=[{
            'input_topic': '/camera/image_raw',
            'output_topic': '/vla/image',
            'target_width': 640,
            'target_height': 480,
        }],
        output='screen'
    )

    # Command interface
    command_interface = Node(
        package='humanoid_vla_ros',
        executable='command_interface',
        name='command_interface',
        output='screen',
        prefix='xterm -e'  # Open in new terminal
    )

    return LaunchDescription([
        model_path_arg,
        use_sim_arg,
        vla_node,
        camera_processor,
        command_interface,
    ])
```

### Simulation Launch

```python
# launch/vla_simulation.launch.py

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Paths
    pkg_humanoid_vla = get_package_share_directory('humanoid_vla_ros')
    pkg_humanoid_sim = get_package_share_directory('humanoid_vla_sim')

    # Gazebo simulation
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_humanoid_sim, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': os.path.join(pkg_humanoid_sim, 'worlds', 'manipulation_scene.world'),
        }.items()
    )

    # Spawn robot
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'humanoid',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '0.5'
        ],
        output='screen'
    )

    # VLA demo launch
    vla_demo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_humanoid_vla, 'launch', 'vla_demo.launch.py')
        ),
        launch_arguments={
            'use_sim': 'true',
        }.items()
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        vla_demo,
    ])
```

---

## 6.7 Real-Time Considerations

### Rate Limiting and Timing

```python
class RealTimeVLANode(Node):
    """VLA node with real-time guarantees."""

    def __init__(self):
        super().__init__('realtime_vla_node')

        # Timing parameters
        self.target_rate = 10.0  # Hz
        self.target_period = 1.0 / self.target_rate

        # Monitoring
        self.last_callback_time = None
        self.callback_durations = []
        self.deadline_misses = 0

        # Control timer with high priority
        self.control_timer = self.create_timer(
            self.target_period,
            self.control_callback_timed
        )

    def control_callback_timed(self):
        """Control callback with timing monitoring."""
        start_time = time.perf_counter()

        # Check for deadline miss
        if self.last_callback_time is not None:
            actual_period = start_time - self.last_callback_time
            if actual_period > self.target_period * 1.5:
                self.deadline_misses += 1
                self.get_logger().warn(
                    f"Deadline miss: {actual_period*1000:.1f}ms > "
                    f"{self.target_period*1000:.1f}ms"
                )

        self.last_callback_time = start_time

        # Run control logic
        try:
            self._run_control()
        except Exception as e:
            self.get_logger().error(f"Control error: {e}")

        # Record duration
        duration = time.perf_counter() - start_time
        self.callback_durations.append(duration)

        # Warn if close to deadline
        if duration > self.target_period * 0.8:
            self.get_logger().warn(
                f"Control loop taking {duration*1000:.1f}ms "
                f"(target: {self.target_period*1000:.1f}ms)"
            )

    def get_timing_stats(self):
        """Get timing statistics."""
        if not self.callback_durations:
            return {}

        durations_ms = np.array(self.callback_durations) * 1000

        return {
            'mean_ms': np.mean(durations_ms),
            'max_ms': np.max(durations_ms),
            'p95_ms': np.percentile(durations_ms, 95),
            'deadline_misses': self.deadline_misses,
            'miss_rate': self.deadline_misses / len(self.callback_durations)
        }
```

---

## 6.8 Summary

In this chapter, you learned:

1. **ROS 2 Architecture**: Node design for VLA systems
2. **Custom Messages**: VLACommand, VLAAction, VLAStatus
3. **VLA Node**: Main inference node implementation
4. **Camera Processing**: Image preprocessing for VLA
5. **Command Interface**: Terminal-based instruction input
6. **Launch Files**: System orchestration
7. **Real-Time**: Timing considerations and monitoring

---

## 6.9 Exercises

### Exercise 6.1: Message Definition
Create and build the custom VLA messages in a ROS 2 package.

### Exercise 6.2: VLA Node
Implement the VLA node and test with recorded bag files.

### Exercise 6.3: Launch System
Create a complete launch file that starts all VLA components.

### Exercise 6.4: Real-Time Analysis
Measure and plot control loop timing for 1000 iterations.

---

## Quick Reference

### Launch VLA System
```bash
ros2 launch humanoid_vla_ros vla_demo.launch.py
```

### Send Instruction
```bash
ros2 topic pub /vla/instruction std_msgs/String "data: 'pick up the red block'"
```

### Monitor Status
```bash
ros2 topic echo /vla/status
```

---

**Next Chapter**: [Chapter 7 - Safety Constraints and Action Filtering](ch07-safety-constraints.md)
