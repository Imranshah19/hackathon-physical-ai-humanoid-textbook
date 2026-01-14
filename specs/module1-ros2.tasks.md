# Tasks: Module 1 - The Robotic Nervous System (ROS 2)

**Input**: `specs/module1-ros2.spec.md`
**Constitution**: `specs/constitution.md` (v1.0.0)
**Prerequisites**: Module 1 specification complete

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = First ROS 2 Node, US2 = Custom Messages, US3 = Robot Visualization
- Paths use `src/` within ROS 2 workspace

## Path Conventions

```
humanoid_ros2_ws/
├── src/
│   ├── humanoid_msgs/
│   ├── humanoid_description/
│   ├── humanoid_control/
│   └── humanoid_bringup/
├── install/
├── build/
└── log/
```

---

## Phase 1: Setup (Workspace & Environment)

**Purpose**: ROS 2 workspace initialization and tooling

- [ ] T001 Document ROS 2 Humble installation steps for Ubuntu 22.04 in `docs/ch01-setup.md`
- [ ] T002 Create workspace structure `humanoid_ros2_ws/src/`
- [ ] T003 [P] Create `.vscode/settings.json` with ROS 2 Python paths and linting
- [ ] T004 [P] Create `README.md` with workspace build instructions

**Checkpoint**: Workspace ready, `colcon build` succeeds with empty src/

---

## Phase 2: Foundational (ROS 2 Package Structure)

**Purpose**: Base packages that all components depend on

**CRITICAL**: No implementation tasks can begin until these packages exist

- [ ] T005 Create `humanoid_msgs` package with `ros2 pkg create --build-type ament_cmake humanoid_msgs`
- [ ] T006 [P] Create `humanoid_description` package with `ros2 pkg create --build-type ament_cmake humanoid_description`
- [ ] T007 [P] Create `humanoid_control` package with `ros2 pkg create --build-type ament_python humanoid_control`
- [ ] T008 [P] Create `humanoid_bringup` package with `ros2 pkg create --build-type ament_python humanoid_bringup`
- [ ] T009 Configure `humanoid_msgs/package.xml` with message generation dependencies
- [ ] T010 Configure `humanoid_msgs/CMakeLists.txt` for message/service/action generation
- [ ] T011 Verify all packages build: `colcon build --packages-select humanoid_msgs humanoid_description humanoid_control humanoid_bringup`

**Checkpoint**: Four empty packages build successfully

---

## Phase 3: User Story 1 - First ROS 2 Node (Priority: P1)

**Goal**: Student creates and runs their first ROS 2 Python node

**Independent Test**: Node runs and publishes to a topic

### Implementation for User Story 1

#### T012-T015: Basic Node Creation

- [ ] T012 [US1] Create `humanoid_control/humanoid_control/__init__.py`
- [ ] T013 [US1] Create minimal publisher node `humanoid_control/humanoid_control/minimal_publisher.py`:
  ```python
  # Node that publishes "Hello Humanoid" to /chatter topic
  # Uses rclpy.create_node(), create_publisher(), timer callback
  ```
- [ ] T014 [US1] Create minimal subscriber node `humanoid_control/humanoid_control/minimal_subscriber.py`:
  ```python
  # Node that subscribes to /chatter and logs messages
  # Uses create_subscription() with callback
  ```
- [ ] T015 [US1] Register entry points in `humanoid_control/setup.py`:
  ```python
  entry_points={
      'console_scripts': [
          'minimal_publisher = humanoid_control.minimal_publisher:main',
          'minimal_subscriber = humanoid_control.minimal_subscriber:main',
      ],
  }
  ```

#### T016-T018: Node Documentation

- [ ] T016 [P] [US1] Write Chapter 1 content `docs/chapters/ch01-ros2-foundations.md`
- [ ] T017 [P] [US1] Write Chapter 2 content `docs/chapters/ch02-nodes-topics.md`
- [ ] T018 [US1] Add docstrings and type hints to all node files

**Verification**:
```bash
ros2 run humanoid_control minimal_publisher
ros2 run humanoid_control minimal_subscriber
ros2 topic echo /chatter
```

**Checkpoint**: Student can run publisher/subscriber and see messages

---

## Phase 4: User Story 2 - Custom Messages (Priority: P1)

**Goal**: Student defines and uses custom message types for humanoid control

**Independent Test**: Custom messages compile and can be published/echoed

### Implementation for User Story 2

#### T019-T024: Message Definitions

- [ ] T019 [P] [US2] Create `humanoid_msgs/msg/JointCommand.msg`:
  ```
  string joint_name
  float64 position
  float64 velocity
  float64 effort
  builtin_interfaces/Time stamp
  ```
- [ ] T020 [P] [US2] Create `humanoid_msgs/msg/JointState.msg`:
  ```
  string[] joint_names
  float64[] positions
  float64[] velocities
  float64[] efforts
  builtin_interfaces/Time stamp
  ```
- [ ] T021 [P] [US2] Create `humanoid_msgs/msg/RobotState.msg`:
  ```
  std_msgs/Header header
  humanoid_msgs/JointState joint_state
  geometry_msgs/Pose base_pose
  geometry_msgs/Twist base_twist
  bool emergency_stop
  ```
- [ ] T022 [US2] Update `humanoid_msgs/CMakeLists.txt` to generate messages
- [ ] T023 [US2] Build and verify messages: `ros2 interface show humanoid_msgs/msg/JointCommand`
- [ ] T024 [US2] Write message documentation in `docs/chapters/ch02-nodes-topics.md`

#### T025-T028: Service Definitions

- [ ] T025 [P] [US2] Create `humanoid_msgs/srv/GetJointLimits.srv`:
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
- [ ] T026 [P] [US2] Create `humanoid_msgs/srv/SetJointPosition.srv`:
  ```
  string joint_name
  float64 position
  float64 max_velocity
  ---
  bool success
  string message
  ```
- [ ] T027 [US2] Update `CMakeLists.txt` to generate services
- [ ] T028 [US2] Verify services: `ros2 interface show humanoid_msgs/srv/GetJointLimits`

#### T029-T033: Action Definitions

- [ ] T029 [P] [US2] Create `humanoid_msgs/action/MoveToPosition.action`:
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
  string message
  ---
  # Feedback
  float64 current_position
  float64 remaining_distance
  float64 elapsed_time
  ```
- [ ] T030 [P] [US2] Create `humanoid_msgs/action/ExecuteTrajectory.action`:
  ```
  # Goal
  string[] joint_names
  float64[] positions
  float64 duration
  ---
  # Result
  bool success
  float64[] final_positions
  string message
  ---
  # Feedback
  float64 progress_percentage
  float64[] current_positions
  float64 time_remaining
  ```
- [ ] T031 [US2] Update `CMakeLists.txt` to generate actions
- [ ] T032 [US2] Verify actions: `ros2 interface show humanoid_msgs/action/MoveToPosition`
- [ ] T033 [US2] Write Chapter 3 content `docs/chapters/ch03-services-actions.md`

**Verification**:
```bash
ros2 interface list | grep humanoid_msgs
ros2 interface show humanoid_msgs/msg/JointCommand
ros2 interface show humanoid_msgs/srv/GetJointLimits
ros2 interface show humanoid_msgs/action/MoveToPosition
```

**Checkpoint**: All custom interfaces compile and are visible

---

## Phase 5: User Story 2 (continued) - Python rclpy Bridge

**Goal**: Implement service and action servers/clients using rclpy

**Independent Test**: Service calls return data, actions complete with feedback

### Implementation for Services

- [ ] T034 [US2] Create `humanoid_control/humanoid_control/joint_limits_service.py`:
  ```python
  # Service server that returns joint limits from config
  # Implements GetJointLimits.srv
  ```
- [ ] T035 [US2] Create `humanoid_control/humanoid_control/joint_limits_client.py`:
  ```python
  # Service client that queries joint limits
  # Demonstrates synchronous service call
  ```
- [ ] T036 [US2] Create `humanoid_control/config/joint_limits.yaml`:
  ```yaml
  joints:
    head_pan:
      min_position: -1.57
      max_position: 1.57
      max_velocity: 1.0
      max_effort: 10.0
    # ... other joints
  ```

### Implementation for Actions

- [ ] T037 [US2] Create `humanoid_control/humanoid_control/move_action_server.py`:
  ```python
  # Action server for MoveToPosition
  # Publishes feedback during execution
  # Handles cancellation
  ```
- [ ] T038 [US2] Create `humanoid_control/humanoid_control/move_action_client.py`:
  ```python
  # Action client that sends goal and prints feedback
  # Demonstrates async action pattern
  ```
- [ ] T039 [US2] Register all new entry points in `setup.py`
- [ ] T040 [US2] Add type hints and docstrings to all service/action files

**Verification**:
```bash
# Terminal 1
ros2 run humanoid_control joint_limits_service
# Terminal 2
ros2 run humanoid_control joint_limits_client head_pan

# Terminal 1
ros2 run humanoid_control move_action_server
# Terminal 2
ros2 run humanoid_control move_action_client head_pan 0.5
```

**Checkpoint**: Services return data, actions provide feedback

---

## Phase 6: User Story 3 - Robot Visualization (Priority: P1)

**Goal**: Student creates URDF and visualizes humanoid in RViz2

**Independent Test**: Humanoid model displays and joints move in RViz2

### Implementation for URDF

#### T041-T045: URDF Structure

- [ ] T041 [US3] Create `humanoid_description/urdf/humanoid.urdf.xacro` (main file):
  ```xml
  <!-- Root XACRO that includes all components -->
  <!-- Defines base_link as root -->
  ```
- [ ] T042 [P] [US3] Create `humanoid_description/urdf/materials.xacro`:
  ```xml
  <!-- Color definitions for robot visualization -->
  <!-- silver, black, blue for different parts -->
  ```
- [ ] T043 [P] [US3] Create `humanoid_description/urdf/properties.xacro`:
  ```xml
  <!-- Dimension parameters for humanoid -->
  <!-- torso_height, arm_length, leg_length, etc. -->
  ```

#### T046-T049: Body Links

- [ ] T046 [US3] Create `humanoid_description/urdf/links/torso.urdf.xacro`:
  ```xml
  <!-- base_link (torso) with visual, collision, inertial -->
  <!-- Box geometry approximately 0.3 x 0.2 x 0.5 m -->
  ```
- [ ] T047 [P] [US3] Create `humanoid_description/urdf/links/head.urdf.xacro`:
  ```xml
  <!-- head_link connected to torso via head_pan joint -->
  <!-- Sphere geometry for head -->
  ```

#### T050-T053: Arm XACRO Macro

- [ ] T050 [US3] Create `humanoid_description/urdf/macros/arm.xacro`:
  ```xml
  <!-- Parameterized arm macro with prefix (left/right) -->
  <!-- Joints: shoulder_pitch, shoulder_roll, elbow -->
  <!-- 3 DOF per arm -->
  ```
- [ ] T051 [US3] Create `humanoid_description/urdf/links/left_arm.urdf.xacro`:
  ```xml
  <!-- Instantiate arm macro with prefix="left" -->
  ```
- [ ] T052 [P] [US3] Create `humanoid_description/urdf/links/right_arm.urdf.xacro`:
  ```xml
  <!-- Instantiate arm macro with prefix="right" -->
  ```

#### T054-T057: Leg XACRO Macro

- [ ] T053 [US3] Create `humanoid_description/urdf/macros/leg.xacro`:
  ```xml
  <!-- Parameterized leg macro with prefix (left/right) -->
  <!-- Joints: hip_pitch, knee, ankle -->
  <!-- 3 DOF per leg -->
  ```
- [ ] T054 [US3] Create `humanoid_description/urdf/links/left_leg.urdf.xacro`:
  ```xml
  <!-- Instantiate leg macro with prefix="left" -->
  ```
- [ ] T055 [P] [US3] Create `humanoid_description/urdf/links/right_leg.urdf.xacro`:
  ```xml
  <!-- Instantiate leg macro with prefix="right" -->
  ```

#### T056-T058: URDF Validation

- [ ] T056 [US3] Generate URDF from XACRO: `xacro humanoid.urdf.xacro > humanoid.urdf`
- [ ] T057 [US3] Validate URDF: `check_urdf humanoid.urdf`
- [ ] T058 [US3] Verify joint count: 14 joints total (1 head + 6 arms + 6 legs + 1 fixed base)

**Verification**:
```bash
cd humanoid_description/urdf
xacro humanoid.urdf.xacro > humanoid.urdf
check_urdf humanoid.urdf
# Expected: robot name, 15 links, 14 joints
```

### Implementation for Visualization

#### T059-T063: Launch and Config

- [ ] T059 [US3] Create `humanoid_description/launch/display.launch.py`:
  ```python
  # Launch robot_state_publisher with URDF
  # Launch joint_state_publisher_gui
  # Launch RViz2 with config
  ```
- [ ] T060 [P] [US3] Create `humanoid_description/rviz/humanoid.rviz`:
  ```yaml
  # RViz2 config with RobotModel, TF, Grid displays
  # Fixed frame: base_link
  ```
- [ ] T061 [US3] Create `humanoid_description/config/joint_names.yaml`:
  ```yaml
  joint_names:
    - head_pan
    - left_shoulder_pitch
    - left_shoulder_roll
    - left_elbow
    # ... all 14 joints
  ```
- [ ] T062 [US3] Update `humanoid_description/CMakeLists.txt` to install launch, rviz, config, urdf
- [ ] T063 [US3] Write Chapter 4 content `docs/chapters/ch04-urdf-xacro.md`

**Verification**:
```bash
ros2 launch humanoid_description display.launch.py
# RViz2 opens with humanoid model
# Sliders move joints
```

**Checkpoint**: Humanoid visualizes in RViz2 with working joint sliders

---

## Phase 7: Launch Files and Parameters

**Goal**: Create system launch files for multi-node startup

### Implementation

- [ ] T064 [US3] Create `humanoid_bringup/launch/simulation.launch.py`:
  ```python
  # Launch full simulation stack:
  # - robot_state_publisher
  # - joint_state_publisher
  # - All control nodes
  # - RViz2
  ```
- [ ] T065 [P] [US3] Create `humanoid_bringup/config/simulation_params.yaml`:
  ```yaml
  # Parameters for simulation mode
  # Update rates, QoS settings
  ```
- [ ] T066 [US3] Create `humanoid_bringup/launch/control.launch.py`:
  ```python
  # Launch control nodes only
  # Include argument for simulation vs hardware
  ```
- [ ] T067 [US3] Write Chapter 5 content `docs/chapters/ch05-launch-parameters.md`

**Verification**:
```bash
ros2 launch humanoid_bringup simulation.launch.py
# All nodes start from single command
```

---

## Phase 8: Lifecycle Nodes and Safety

**Goal**: Implement safe state management for robot control

### Implementation

- [ ] T068 Create `humanoid_control/humanoid_control/lifecycle_controller.py`:
  ```python
  # Lifecycle node with:
  # - on_configure: load params, validate
  # - on_activate: start control loop
  # - on_deactivate: stop, hold position
  # - on_cleanup: release resources
  ```
- [ ] T069 Create `humanoid_control/humanoid_control/watchdog_node.py`:
  ```python
  # Monitors communication, triggers e-stop on timeout
  # Publishes to /emergency_stop topic
  ```
- [ ] T070 Update `humanoid_bringup/launch/control.launch.py` to use lifecycle nodes
- [ ] T071 Write Chapter 6 content `docs/chapters/ch06-lifecycle-safety.md`

**Verification**:
```bash
ros2 lifecycle set /lifecycle_controller configure
ros2 lifecycle set /lifecycle_controller activate
ros2 lifecycle get /lifecycle_controller
# Shows "active"
```

---

## Phase 9: Debugging and Tools

**Goal**: Document debugging workflows and tools

### Implementation

- [ ] T072 [P] Create `docs/chapters/ch07-debugging-tools.md` covering:
  - `ros2 topic`, `ros2 node`, `ros2 service` CLI
  - `ros2 doctor` diagnostics
  - `ros2 bag` recording
  - `rqt_graph`, `rqt_plot`, `rqt_console`
- [ ] T073 [P] Create `humanoid_bringup/scripts/record_demo.sh`:
  ```bash
  # Record bag file of joint states and commands
  ```
- [ ] T074 Create debugging exercise with intentional bug in `humanoid_control/humanoid_control/buggy_node.py`
- [ ] T075 Create solution guide `docs/exercises/debug-solution.md`

---

## Phase 10: Polish & Integration

**Purpose**: Final integration and documentation

- [ ] T076 [P] Create module summary `docs/module1-summary.md`
- [ ] T077 [P] Create exercises index `docs/exercises/README.md`
- [ ] T078 Verify all packages build: `colcon build`
- [ ] T079 Run full launch test: `ros2 launch humanoid_bringup simulation.launch.py`
- [ ] T080 Verify all 14 joints move correctly in RViz2
- [ ] T081 Document known issues in `docs/troubleshooting.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ──── BLOCKS ALL ────┐
    │                                       │
    ▼                                       ▼
Phase 3 (US1: Nodes)              Phase 4-5 (US2: Messages)
    │                                       │
    └───────────────┬───────────────────────┘
                    │
                    ▼
            Phase 6 (US3: URDF)
                    │
                    ▼
            Phase 7 (Launch)
                    │
                    ▼
            Phase 8 (Lifecycle)
                    │
                    ▼
            Phase 9-10 (Polish)
```

### Parallel Opportunities

**Within Phase 2** (all independent packages):
```
T005 humanoid_msgs
T006 humanoid_description  [P]
T007 humanoid_control      [P]
T008 humanoid_bringup      [P]
```

**Within Phase 4** (all message definitions):
```
T019 JointCommand.msg      [P]
T020 JointState.msg        [P]
T021 RobotState.msg        [P]
T025 GetJointLimits.srv    [P]
T026 SetJointPosition.srv  [P]
T029 MoveToPosition.action [P]
T030 ExecuteTrajectory.action [P]
```

**Within Phase 6** (URDF components):
```
T042 materials.xacro       [P]
T043 properties.xacro      [P]
T047 head.urdf.xacro       [P]
T051 left_arm.urdf.xacro
T052 right_arm.urdf.xacro  [P]
T054 left_leg.urdf.xacro
T055 right_leg.urdf.xacro  [P]
```

---

## Task Summary

| Phase | Tasks | Purpose |
|-------|-------|---------|
| 1 | T001-T004 | Workspace setup |
| 2 | T005-T011 | Package creation |
| 3 | T012-T018 | Basic nodes (US1) |
| 4-5 | T019-T040 | Messages, services, actions (US2) |
| 6 | T041-T063 | URDF and visualization (US3) |
| 7 | T064-T067 | Launch files |
| 8 | T068-T071 | Lifecycle and safety |
| 9 | T072-T075 | Debugging |
| 10 | T076-T081 | Polish |

**Total**: 81 tasks

---

## Verification Checklist

- [ ] All 4 packages build without errors
- [ ] 3 message types compile (JointCommand, JointState, RobotState)
- [ ] 2 service types compile (GetJointLimits, SetJointPosition)
- [ ] 2 action types compile (MoveToPosition, ExecuteTrajectory)
- [ ] URDF validates with `check_urdf`
- [ ] 14 joints visible in RViz2
- [ ] Lifecycle transitions work
- [ ] All 7 chapters written

---

**Governed by**: `specs/constitution.md` v1.0.0
