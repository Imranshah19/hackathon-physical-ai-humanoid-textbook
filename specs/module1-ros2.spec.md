# Module 1 Specification: The Robotic Nervous System (ROS 2)

**Parent**: `specs/book.spec.md`
**Created**: 2026-01-07
**Status**: Draft
**Constitution**: `specs/constitution.md` (v1.0.0)
**Duration**: Weeks 1-2

---

## Overview

The Robotic Nervous System module teaches ROS 2 as the communication infrastructure that connects all parts of a humanoid robot. Like the human nervous system carries signals between brain, sensors, and muscles, ROS 2 carries messages between perception, planning, and actuation components.

Students build foundational skills required for all subsequent modules.

---

## Learning Objectives

By completing this module, students will be able to:

| ID | Objective | Assessment |
|----|-----------|------------|
| LO-1.1 | Explain ROS 2 architecture and the DDS communication model | Quiz + diagram exercise |
| LO-1.2 | Create and build ROS 2 packages using colcon | Working package builds |
| LO-1.3 | Implement publisher and subscriber nodes in Python | Running pub/sub demo |
| LO-1.4 | Design and use custom message types | Custom message compiles |
| LO-1.5 | Implement services for synchronous request/response | Service call succeeds |
| LO-1.6 | Implement actions for long-running tasks with feedback | Action completes with feedback |
| LO-1.7 | Create robot descriptions using URDF and XACRO | Valid URDF visualizes |
| LO-1.8 | Write launch files to start multi-node systems | Launch file runs all nodes |
| LO-1.9 | Use lifecycle nodes for safe robot state management | Lifecycle transitions work |
| LO-1.10 | Debug ROS 2 systems using CLI tools | Student finds injected bug |

---

## Concepts

### Core Concepts

| Concept | Definition | Why It Matters |
|---------|------------|----------------|
| **Node** | Independent executable that performs computation | Modular design allows replacing components |
| **Topic** | Named bus for asynchronous message passing | Decouples producers from consumers |
| **Message** | Typed data structure sent over topics | Standardized interfaces enable interoperability |
| **Service** | Synchronous request/response communication | Required for configuration and queries |
| **Action** | Asynchronous goal with feedback and result | Essential for long-running robot tasks |
| **Parameter** | Runtime-configurable node settings | Tuning without recompilation |
| **QoS** | Quality of Service policies for reliability | Critical for real-time robot control |

### Robot Description Concepts

| Concept | Definition | Why It Matters |
|---------|------------|----------------|
| **URDF** | Unified Robot Description Format (XML) | Standard way to describe robot geometry |
| **XACRO** | XML macro language for URDF | Reduces repetition, enables parameterization |
| **Link** | Rigid body with visual, collision, inertial properties | Physical structure of robot |
| **Joint** | Connection between links with motion constraints | Defines how parts move relative to each other |
| **TF2** | Transform library for coordinate frames | Tracks spatial relationships over time |

### Safety Concepts

| Concept | Definition | Why It Matters |
|---------|------------|----------------|
| **Lifecycle Node** | Node with managed state transitions | Safe startup/shutdown sequences |
| **Watchdog** | Timer that triggers on communication loss | Detects failures, triggers safe stop |
| **E-Stop Integration** | Emergency stop message handling | Human safety is non-negotiable |

---

## System Architecture

### ROS 2 Communication Model

```
┌─────────────────────────────────────────────────────────────┐
│                     DDS (Data Distribution Service)          │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │ Domain  │    │ Domain  │    │ Domain  │    │ Domain  │ │
│   │Particip.│    │Particip.│    │Particip.│    │Particip.│ │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘ │
└────────┼──────────────┼──────────────┼──────────────┼──────┘
         │              │              │              │
    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
    │  Node   │    │  Node   │    │  Node   │    │  Node   │
    │ Sensor  │    │Planning │    │ Control │    │ Actuator│
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

### Humanoid Robot Node Graph (Target Architecture)

```
                    ┌──────────────┐
                    │   /camera    │
                    │  (sensor)    │
                    └──────┬───────┘
                           │ /image_raw
                           ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    /imu      │───▶│  /perception │───▶│  /planning   │
│  (sensor)    │    │   (fusion)   │    │  (decision)  │
└──────────────┘    └──────────────┘    └──────┬───────┘
       │                                       │
       │ /imu/data                             │ /cmd_vel
       ▼                                       ▼
┌──────────────┐                        ┌──────────────┐
│ /joint_states│◀───────────────────────│  /control    │
│  (feedback)  │                        │ (execution)  │
└──────────────┘                        └──────┬───────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │  /actuators  │
                                        │  (hardware)  │
                                        └──────────────┘
```

### Package Structure

```
humanoid_ros2_ws/
├── src/
│   ├── humanoid_description/      # URDF/XACRO files
│   │   ├── urdf/
│   │   │   ├── humanoid.urdf.xacro
│   │   │   ├── links/
│   │   │   └── joints/
│   │   ├── meshes/
│   │   ├── launch/
│   │   └── package.xml
│   │
│   ├── humanoid_msgs/             # Custom messages
│   │   ├── msg/
│   │   │   ├── JointCommand.msg
│   │   │   └── RobotState.msg
│   │   ├── srv/
│   │   │   └── GetJointLimits.srv
│   │   ├── action/
│   │   │   └── MoveToPosition.action
│   │   └── package.xml
│   │
│   ├── humanoid_control/          # Control nodes
│   │   ├── humanoid_control/
│   │   │   ├── __init__.py
│   │   │   ├── joint_controller.py
│   │   │   └── lifecycle_controller.py
│   │   ├── launch/
│   │   ├── config/
│   │   └── package.xml
│   │
│   └── humanoid_bringup/          # System launch
│       ├── launch/
│       │   ├── simulation.launch.py
│       │   └── robot.launch.py
│       ├── config/
│       └── package.xml
│
├── install/
├── build/
└── log/
```

---

## Chapter Breakdown

### Chapter 1: ROS 2 Foundations

**Duration**: 3-4 hours

**Topics**:
- What is ROS 2 and why it exists
- ROS 2 vs ROS 1 differences
- DDS and the publish-subscribe model
- Installing ROS 2 Humble on Ubuntu 22.04
- Workspace setup and colcon basics
- ROS 2 CLI tools overview

**Hands-On**:
- Install ROS 2 Humble
- Create first workspace
- Run `turtlesim` demo
- Use `ros2 topic`, `ros2 node`, `ros2 service` commands

**Required Output**:
- Screenshot: `ros2 topic list` showing turtlesim topics
- Screenshot: `ros2 node info /turtlesim` output

---

### Chapter 2: Nodes, Topics, and Messages

**Duration**: 4-5 hours

**Topics**:
- Node architecture and lifecycle
- Creating a ROS 2 Python package
- Publishers and subscribers
- Message types and `std_msgs`
- Custom message definitions
- QoS profiles for reliability

**Hands-On**:
- Create `humanoid_msgs` package
- Define `JointCommand.msg` with fields:
  ```
  string joint_name
  float64 position
  float64 velocity
  float64 effort
  builtin_interfaces/Time stamp
  ```
- Write publisher node for joint commands
- Write subscriber node that logs received commands

**Required Output**:
- File: `humanoid_msgs/msg/JointCommand.msg`
- File: `humanoid_control/joint_publisher.py`
- File: `humanoid_control/joint_subscriber.py`
- Terminal: `ros2 topic echo /joint_commands` showing messages

---

### Chapter 3: Services and Actions

**Duration**: 4-5 hours

**Topics**:
- When to use services vs topics
- Service definition and implementation
- Service clients and synchronous calls
- Action concept: goal, feedback, result
- Action servers and clients
- Cancellation and preemption

**Hands-On**:
- Define `GetJointLimits.srv`:
  ```
  string joint_name
  ---
  float64 min_position
  float64 max_position
  float64 max_velocity
  float64 max_effort
  bool success
  string message
  ```
- Define `MoveToPosition.action`:
  ```
  # Goal
  string joint_name
  float64 target_position
  float64 max_velocity
  ---
  # Result
  float64 final_position
  float64 error
  bool success
  ---
  # Feedback
  float64 current_position
  float64 remaining_distance
  float64 elapsed_time
  ```
- Implement service server and client
- Implement action server with feedback

**Required Output**:
- File: `humanoid_msgs/srv/GetJointLimits.srv`
- File: `humanoid_msgs/action/MoveToPosition.action`
- File: `humanoid_control/joint_limits_service.py`
- File: `humanoid_control/move_action_server.py`
- Terminal: Action feedback showing progress

---

### Chapter 4: Robot Description with URDF/XACRO

**Duration**: 5-6 hours

**Topics**:
- URDF structure: links and joints
- Visual, collision, and inertial properties
- Joint types: revolute, prismatic, continuous, fixed
- XACRO macros and parameters
- Including and composing XACRO files
- Visualizing in RViz2

**Hands-On**:
- Create simplified humanoid URDF with:
  - Torso (base link)
  - Head (1 DOF: pan)
  - Left/Right arms (3 DOF each: shoulder_pitch, shoulder_roll, elbow)
  - Left/Right legs (3 DOF each: hip_pitch, knee, ankle)
- Total: 14 joints (simplified humanoid)
- Use XACRO macros for symmetric limbs

**Required Output**:
- File: `humanoid_description/urdf/humanoid.urdf.xacro`
- File: `humanoid_description/urdf/macros/arm.xacro`
- File: `humanoid_description/urdf/macros/leg.xacro`
- Screenshot: Humanoid visualized in RViz2
- Verification: `check_urdf humanoid.urdf` passes

---

### Chapter 5: Launch Files and Parameters

**Duration**: 3-4 hours

**Topics**:
- Python launch file syntax
- Launching multiple nodes
- Node namespacing and remapping
- Parameter files (YAML)
- Loading parameters at launch
- Conditional logic in launch files

**Hands-On**:
- Create launch file that starts:
  - Robot state publisher
  - Joint state publisher GUI
  - RViz2 with humanoid config
- Create parameter file for joint limits
- Add launch arguments for simulation vs hardware mode

**Required Output**:
- File: `humanoid_bringup/launch/display.launch.py`
- File: `humanoid_bringup/config/joint_limits.yaml`
- Terminal: All nodes running from single launch command

---

### Chapter 6: Lifecycle Nodes and Safety

**Duration**: 3-4 hours

**Topics**:
- Why lifecycle management matters for robots
- Lifecycle node states: unconfigured, inactive, active, finalized
- Transition callbacks
- Managed startup sequences
- Emergency stop integration
- Watchdog timers

**Hands-On**:
- Convert joint controller to lifecycle node
- Implement safe state transitions:
  - `on_configure`: Load parameters, validate
  - `on_activate`: Start publishing commands
  - `on_deactivate`: Stop commands, hold position
  - `on_cleanup`: Release resources
- Add watchdog that triggers deactivation on communication loss

**Required Output**:
- File: `humanoid_control/lifecycle_controller.py`
- Terminal: Lifecycle transitions via `ros2 lifecycle` CLI
- Demonstration: Watchdog triggers safe stop

---

### Chapter 7: Debugging and Tools

**Duration**: 2-3 hours

**Topics**:
- ROS 2 CLI tools deep dive
- `ros2 doctor` for system diagnostics
- `ros2 bag` for recording and playback
- RQT tools: graph, console, plot
- Logging best practices
- Common debugging patterns

**Hands-On**:
- Record bag file of humanoid joint states
- Visualize node graph with `rqt_graph`
- Plot joint positions with `rqt_plot`
- Find and fix intentionally broken node

**Required Output**:
- File: Recorded bag file with joint data
- Screenshot: `rqt_graph` showing node connections
- Written: Bug report describing found issue and fix

---

## Required Outputs Summary

### Code Deliverables

| Chapter | Deliverable | Verification |
|---------|-------------|--------------|
| Ch 1 | ROS 2 workspace setup | `colcon build` succeeds |
| Ch 2 | `humanoid_msgs` package | Messages compile |
| Ch 2 | Publisher/subscriber nodes | Topics echo correctly |
| Ch 3 | Service definition and server | Service call returns data |
| Ch 3 | Action definition and server | Action completes with feedback |
| Ch 4 | Humanoid URDF/XACRO | `check_urdf` passes |
| Ch 5 | Launch files | Single command starts system |
| Ch 6 | Lifecycle controller | State transitions work |
| Ch 7 | Recorded bag file | Playback shows data |

### Package Deliverables

At module completion, student workspace contains:

```
humanoid_ros2_ws/src/
├── humanoid_msgs/          # Custom interfaces
├── humanoid_description/   # Robot URDF
├── humanoid_control/       # Control nodes
└── humanoid_bringup/       # Launch system
```

### Verification Checklist

- [ ] All packages build without errors
- [ ] `ros2 pkg list` shows all four packages
- [ ] URDF visualizes correctly in RViz2
- [ ] Joint commands flow through system
- [ ] Lifecycle transitions work correctly
- [ ] Launch file starts complete system

---

## User Scenarios & Testing

### User Story 1 - First ROS 2 Node (Priority: P1)

Student with Python experience creates their first ROS 2 node.

**Acceptance Scenarios**:

1. **Given** fresh Ubuntu 22.04, **When** following Chapter 1 instructions, **Then** ROS 2 Humble installs and sources correctly
2. **Given** ROS 2 installed, **When** student runs `ros2 run turtlesim turtlesim_node`, **Then** turtle window appears
3. **Given** workspace created, **When** `colcon build` runs, **Then** build succeeds with no errors

---

### User Story 2 - Custom Messages (Priority: P1)

Student defines and uses custom message types.

**Acceptance Scenarios**:

1. **Given** `humanoid_msgs` package, **When** student defines `JointCommand.msg`, **Then** message compiles
2. **Given** compiled message, **When** imported in Python node, **Then** no import errors
3. **Given** publisher running, **When** `ros2 topic echo` used, **Then** message fields display correctly

---

### User Story 3 - Robot Visualization (Priority: P1)

Student creates URDF and visualizes humanoid robot.

**Acceptance Scenarios**:

1. **Given** URDF file, **When** `check_urdf` runs, **Then** validation passes
2. **Given** valid URDF, **When** RViz2 launches with config, **Then** robot model displays
3. **Given** joint state publisher GUI, **When** sliders moved, **Then** robot model updates in RViz2

---

### Edge Cases

- What if student has ROS 1 installed? (Sourcing conflict warning provided)
- What if colcon build fails? (Troubleshooting section per chapter)
- What if URDF has broken joints? (Validation error messages explained)

---

## Requirements

### Functional Requirements

- **FR-M1-001**: All code MUST use ROS 2 Humble APIs
- **FR-M1-002**: All packages MUST follow ROS 2 naming conventions
- **FR-M1-003**: All Python code MUST include type hints
- **FR-M1-004**: All nodes MUST implement graceful shutdown
- **FR-M1-005**: URDF MUST pass `check_urdf` validation
- **FR-M1-006**: Launch files MUST use Python syntax (not XML)
- **FR-M1-007**: Parameters MUST be loaded from YAML files
- **FR-M1-008**: Lifecycle nodes MUST handle all state transitions

### Non-Functional Requirements

- **NFR-M1-001**: Build time < 60 seconds on standard hardware
- **NFR-M1-002**: Node startup time < 2 seconds
- **NFR-M1-003**: Topic latency < 10ms for control messages

---

## Success Criteria

- **SC-M1-001**: Student completes ROS 2 installation in < 30 minutes
- **SC-M1-002**: All four packages build successfully
- **SC-M1-003**: Humanoid displays correctly in RViz2
- **SC-M1-004**: Joint commands publish at 100 Hz
- **SC-M1-005**: Lifecycle transitions complete without errors
- **SC-M1-006**: Student can debug a broken node using CLI tools

---

## Dependencies

### Prerequisites

- Ubuntu 22.04 LTS (or WSL2 on Windows)
- Python 3.10+
- Basic Linux command line knowledge
- Basic Python programming

### Software Dependencies

- ROS 2 Humble Hawksbill
- colcon build tools
- Python packages: `rclpy`, `std_msgs`, `geometry_msgs`
- Visualization: RViz2, rqt

### Next Module

This module is prerequisite for **Module 2: Digital Twin (Gazebo & Unity)**.

---

## Related Files

- `specs/module1-ros2.spec.md` - This specification
- `specs/ros2-nervous-system/plan.md` - Architecture decisions (to create)
- `specs/ros2-nervous-system/tasks.md` - Implementation tasks (to create)

---

**Governed by**: `specs/constitution.md` v1.0.0
