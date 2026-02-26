# Tasks: Module 2 - Digital Twin (Gazebo & Unity)

**Input**: `specs/module2-digital-twin.spec.md`
**Constitution**: `specs/constitution.md` (v1.0.0)
**Prerequisites**: Module 1 completed

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = Simulate Before Build, US2 = Sensor Data, US3 = Photorealistic, US4 = Stable Walking
- Paths use `src/` within simulation workspace

## Path Conventions

```
humanoid_simulation_ws/
├── src/
│   ├── humanoid_gazebo/        # Gazebo integration
│   ├── humanoid_sensors/       # Sensor configurations
│   └── humanoid_unity/         # Unity bridge
└── unity_project/              # Unity project (separate)
```

---

## Phase 1: Setup (Simulation Environment)

**Purpose**: Install simulation tools and create workspace

- [ ] T001 Document Gazebo Harmonic installation steps in `docs/ch01-digital-twin-fundamentals.md`
- [ ] T002 Create simulation workspace `humanoid_simulation_ws/src/`
- [ ] T003 [P] Install ros_gz packages: `sudo apt install ros-humble-ros-gz`
- [ ] T004 [P] Verify Gazebo installation: `gz sim --version`
- [ ] T005 Create workspace README with build instructions

**Checkpoint**: Gazebo runs, ros_gz packages installed

---

## Phase 2: Foundational (Package Structure)

**Purpose**: Create ROS 2 packages for simulation

- [ ] T006 Create `humanoid_gazebo` package: `ros2 pkg create --build-type ament_cmake humanoid_gazebo`
- [ ] T007 [P] Create `humanoid_sensors` package: `ros2 pkg create --build-type ament_cmake humanoid_sensors`
- [ ] T008 [P] Create `humanoid_unity` package: `ros2 pkg create --build-type ament_python humanoid_unity`
- [ ] T009 Configure `humanoid_gazebo/package.xml` with gz-sim dependencies
- [ ] T010 Configure `humanoid_gazebo/CMakeLists.txt` to install worlds, models, launch
- [ ] T011 Verify all packages build: `colcon build`

**Checkpoint**: Three packages build successfully

---

## Phase 3: User Story 1 - Gazebo World Setup (Priority: P1)

**Goal**: Create Gazebo world with proper physics for humanoid simulation

**Independent Test**: World loads with ground plane and lighting

### T012-T018: World Creation

- [ ] T012 [US1] Create `humanoid_gazebo/worlds/empty.sdf`:
  ```xml
  <!-- Minimal world with physics settings -->
  <!-- Ground plane, sun light, physics config -->
  ```
- [ ] T013 [US1] Create `humanoid_gazebo/worlds/humanoid_world.sdf`:
  ```xml
  <!-- Full world with:
       - Ground plane (10x10m)
       - Friction coefficients (mu=1.0, mu2=1.0)
       - Physics: ODE, 1ms timestep
       - Gravity: 0 0 -9.81
       - Ambient + directional lighting
  -->
  ```
- [ ] T014 [P] [US1] Create `humanoid_gazebo/config/physics.yaml`:
  ```yaml
  physics:
    engine: ode
    max_step_size: 0.001
    real_time_factor: 1.0
    real_time_update_rate: 1000
  ```
- [ ] T015 [US1] Create `humanoid_gazebo/launch/gazebo.launch.py`:
  ```python
  # Launch Gazebo with humanoid_world.sdf
  # Configure physics parameters
  ```
- [ ] T016 [US1] Test world loads: `ros2 launch humanoid_gazebo gazebo.launch.py`
- [ ] T017 [US1] Verify physics: drop test object, check fall rate
- [ ] T018 [US1] Write Chapter 2 content `docs/chapters/ch02-gazebo-world-setup.md`

**Verification**:
```bash
ros2 launch humanoid_gazebo gazebo.launch.py
# Gazebo opens with ground plane and lighting
```

**Checkpoint**: World loads with stable physics

---

## Phase 4: User Story 1 - Robot Spawning (Priority: P1)

**Goal**: Spawn humanoid robot in Gazebo and control via ROS 2

### T019-T026: Model and Spawning

- [ ] T019 [US1] Convert URDF to SDF-compatible format:
  ```bash
  # Copy humanoid URDF from Module 1
  # Add Gazebo-specific tags
  ```
- [ ] T020 [US1] Create `humanoid_gazebo/models/humanoid/model.config`:
  ```xml
  <!-- Model metadata for Gazebo -->
  ```
- [ ] T021 [US1] Create `humanoid_gazebo/models/humanoid/model.sdf`:
  ```xml
  <!-- SDF version of humanoid with:
       - All links and joints
       - Collision geometry
       - Inertial properties
       - Joint plugins
  -->
  ```
- [ ] T022 [US1] Create `humanoid_gazebo/launch/spawn_robot.launch.py`:
  ```python
  # Spawn humanoid in Gazebo
  # Start robot_state_publisher
  # Configure ros_gz_bridge
  ```
- [ ] T023 [US1] Create `humanoid_gazebo/config/ros_gz_bridge.yaml`:
  ```yaml
  # Bridge configuration:
  # - /joint_states: gz -> ros
  # - /joint_commands: ros -> gz
  # - /clock: gz -> ros
  ```
- [ ] T024 [US1] Implement joint position controller plugin
- [ ] T025 [US1] Test joint control via ROS 2 topic
- [ ] T026 [US1] Write Chapter 3 content `docs/chapters/ch03-spawning-robots.md`

**Verification**:
```bash
ros2 launch humanoid_gazebo spawn_robot.launch.py
ros2 topic pub /joint_commands humanoid_msgs/msg/JointCommand \
  "{joint_name: 'head_pan', position: 0.5}"
# Robot head moves in Gazebo
```

**Checkpoint**: Robot spawns and responds to commands

---

## Phase 5: User Story 2 - Camera Sensor (Priority: P1)

**Goal**: Simulate camera and stream images to ROS 2

### T027-T033: Camera Implementation

- [ ] T027 [P] [US2] Create `humanoid_sensors/config/camera.yaml`:
  ```yaml
  camera:
    width: 640
    height: 480
    fps: 30
    fov: 1.047  # 60 degrees
    clip:
      near: 0.1
      far: 100.0
    noise:
      type: gaussian
      mean: 0.0
      stddev: 0.007
  ```
- [ ] T028 [US2] Add camera sensor to humanoid head in SDF:
  ```xml
  <sensor name="head_camera" type="camera">
    <!-- Camera parameters -->
    <!-- Image format: R8G8B8 -->
  </sensor>
  ```
- [ ] T029 [US2] Configure camera bridge in `ros_gz_bridge.yaml`:
  ```yaml
  - topic: /camera/image_raw
    type: sensor_msgs/msg/Image
    direction: gz_to_ros
  - topic: /camera/camera_info
    type: sensor_msgs/msg/CameraInfo
    direction: gz_to_ros
  ```
- [ ] T030 [US2] Test camera image topic:
  ```bash
  ros2 topic echo /camera/image_raw --no-arr
  ```
- [ ] T031 [US2] Verify image in RViz2
- [ ] T032 [US2] Measure frame rate: `ros2 topic hz /camera/image_raw`
- [ ] T033 [US2] Write camera section in `docs/chapters/ch04-sensor-simulation.md`

**Verification**:
```bash
ros2 topic hz /camera/image_raw
# Expected: average rate: 30.0 Hz
```

**Checkpoint**: Camera streams at 30 Hz

---

## Phase 6: User Story 2 - IMU Sensor (Priority: P1)

**Goal**: Simulate IMU and publish to ROS 2

### T034-T039: IMU Implementation

- [ ] T034 [P] [US2] Create `humanoid_sensors/config/imu.yaml`:
  ```yaml
  imu:
    update_rate: 100
    accelerometer:
      noise:
        mean: 0.0
        stddev: 0.01
    gyroscope:
      noise:
        mean: 0.0
        stddev: 0.001
  ```
- [ ] T035 [US2] Add IMU sensor to humanoid torso in SDF:
  ```xml
  <sensor name="torso_imu" type="imu">
    <!-- IMU configuration -->
    <!-- Update rate: 100 Hz -->
  </sensor>
  ```
- [ ] T036 [US2] Configure IMU bridge:
  ```yaml
  - topic: /imu/data
    type: sensor_msgs/msg/Imu
    direction: gz_to_ros
  ```
- [ ] T037 [US2] Test IMU topic: `ros2 topic echo /imu/data`
- [ ] T038 [US2] Verify orientation changes when robot moves
- [ ] T039 [US2] Write IMU section in `docs/chapters/ch04-sensor-simulation.md`

**Verification**:
```bash
ros2 topic hz /imu/data
# Expected: average rate: 100.0 Hz
```

**Checkpoint**: IMU publishes at 100 Hz

---

## Phase 7: User Story 2 - Force/Torque Sensors (Priority: P2)

**Goal**: Simulate foot force/torque sensors

### T040-T045: F/T Sensor Implementation

- [ ] T040 [P] [US2] Create `humanoid_sensors/config/force_torque.yaml`:
  ```yaml
  force_torque:
    update_rate: 100
    noise:
      force:
        stddev: 0.1
      torque:
        stddev: 0.01
  ```
- [ ] T041 [US2] Add F/T sensor to left foot in SDF:
  ```xml
  <sensor name="left_foot_ft" type="force_torque">
    <joint>left_ankle</joint>
    <!-- F/T configuration -->
  </sensor>
  ```
- [ ] T042 [P] [US2] Add F/T sensor to right foot in SDF
- [ ] T043 [US2] Configure F/T bridge:
  ```yaml
  - topic: /left_foot/ft_sensor
    type: geometry_msgs/msg/WrenchStamped
    direction: gz_to_ros
  - topic: /right_foot/ft_sensor
    type: geometry_msgs/msg/WrenchStamped
    direction: gz_to_ros
  ```
- [ ] T044 [US2] Test F/T topics when robot stands
- [ ] T045 [US2] Write F/T section in `docs/chapters/ch04-sensor-simulation.md`

**Verification**:
```bash
ros2 topic echo /left_foot/ft_sensor
# Should show force ~= mass * gravity when standing
```

**Checkpoint**: F/T sensors report contact forces

---

## Phase 8: User Story 4 - Physics Tuning (Priority: P2)

**Goal**: Tune physics for stable humanoid motion

### T046-T052: Physics Optimization

- [ ] T046 [US4] Document baseline physics parameters
- [ ] T047 [US4] Tune ground contact parameters:
  ```xml
  <collision>
    <surface>
      <friction>
        <ode>
          <mu>1.0</mu>
          <mu2>1.0</mu2>
        </ode>
      </friction>
      <contact>
        <ode>
          <kp>1e6</kp>
          <kd>100</kd>
        </ode>
      </contact>
    </surface>
  </collision>
  ```
- [ ] T048 [US4] Tune joint damping for smooth motion
- [ ] T049 [US4] Verify inertia values match URDF
- [ ] T050 [US4] Test standing stability: robot holds pose for 10 seconds
- [ ] T051 [US4] Test basic motion: move joints without physics explosion
- [ ] T052 [US4] Write Chapter 5 content `docs/chapters/ch05-physics-tuning.md`

**Verification**:
```bash
# Robot should stand without falling for 10+ seconds
# Joints should move smoothly when commanded
```

**Checkpoint**: Physics stable for standing and basic motion

---

## Phase 9: User Story 3 - Unity Setup (Priority: P2)

**Goal**: Set up Unity project with ROS 2 bridge

### T053-T060: Unity Project Setup

- [ ] T053 [US3] Document Unity 2022.3 LTS installation
- [ ] T054 [US3] Create Unity project with HDRP template
- [ ] T055 [US3] Install ROS-TCP-Connector package:
  ```
  https://github.com/Unity-Technologies/ROS-TCP-Connector.git
  ```
- [ ] T056 [US3] Create `humanoid_unity/launch/ros_tcp_endpoint.launch.py`:
  ```python
  # Launch ROS-TCP-Endpoint node
  # Configure IP and port
  ```
- [ ] T057 [US3] Configure Unity ROSConnection settings:
  - ROS IP Address: localhost
  - ROS Port: 10000
- [ ] T058 [US3] Test connection with simple publisher/subscriber
- [ ] T059 [US3] Import humanoid robot model into Unity
- [ ] T060 [US3] Write Chapter 6 content `docs/chapters/ch06-unity-setup.md`

**Verification**:
```bash
ros2 launch humanoid_unity ros_tcp_endpoint.launch.py
# Unity connects and messages flow
```

**Checkpoint**: Unity-ROS 2 bridge established

---

## Phase 10: User Story 3 - Photorealistic Environment (Priority: P2)

**Goal**: Create photorealistic room in Unity

### T061-T067: Environment Creation

- [ ] T061 [P] [US3] Create room geometry:
  - Floor: 10x10m
  - Walls: 3m height
  - Ceiling with lights
- [ ] T062 [P] [US3] Apply PBR materials:
  - Floor: wood texture
  - Walls: painted drywall
- [ ] T063 [US3] Set up HDRP lighting:
  - Area lights for ambient
  - Spot lights for accents
  - Reflection probes
- [ ] T064 [P] [US3] Add furniture objects:
  - Table
  - Chair
  - Objects for manipulation
- [ ] T065 [US3] Position humanoid robot in scene
- [ ] T066 [US3] Configure main camera view
- [ ] T067 [US3] Write Chapter 7 content `docs/chapters/ch07-photorealistic-environments.md`

**Verification**:
- Scene renders with realistic lighting
- Robot visible in environment

**Checkpoint**: Photorealistic room complete

---

## Phase 11: User Story 3 - Unity Camera Streaming (Priority: P2)

**Goal**: Stream synthetic camera images from Unity to ROS 2

### T068-T074: Camera Streaming

- [ ] T068 [US3] Create Unity camera publisher script:
  ```csharp
  // CameraPublisher.cs
  // Captures render texture
  // Publishes sensor_msgs/Image
  ```
- [ ] T069 [US3] Configure camera parameters:
  - Resolution: 640x480
  - FPS: 30
  - Format: RGB8
- [ ] T070 [US3] Implement depth camera:
  ```csharp
  // DepthCameraPublisher.cs
  // Publishes depth image
  ```
- [ ] T071 [US3] Optimize streaming performance:
  - Async GPU readback
  - Image compression
- [ ] T072 [US3] Test image reception in ROS 2:
  ```bash
  ros2 topic echo /unity/camera/image_raw --no-arr
  ```
- [ ] T073 [US3] Verify in RViz2
- [ ] T074 [US3] Write Chapter 8 content `docs/chapters/ch08-synthetic-sensor-data.md`

**Verification**:
```bash
ros2 topic hz /unity/camera/image_raw
# Expected: ~30 Hz
```

**Checkpoint**: Unity camera streams to ROS 2

---

## Phase 12: Domain Randomization (Priority: P3)

**Goal**: Implement domain randomization for training robustness

### T075-T081: Randomization System

- [ ] T075 [US3] Create texture randomization script:
  ```csharp
  // TextureRandomizer.cs
  // Randomizes floor and wall textures
  ```
- [ ] T076 [P] [US3] Create lighting randomization script:
  ```csharp
  // LightingRandomizer.cs
  // Randomizes light positions, intensities, colors
  ```
- [ ] T077 [P] [US3] Create object placement randomizer:
  ```csharp
  // ObjectRandomizer.cs
  // Randomizes furniture positions
  ```
- [ ] T078 [US3] Create ROS 2 service to trigger randomization:
  ```
  std_srvs/srv/Trigger → randomize scene
  ```
- [ ] T079 [US3] Test randomization varies environment
- [ ] T080 [US3] Capture randomized images for verification
- [ ] T081 [US3] Write Chapter 9 content `docs/chapters/ch09-domain-randomization.md`

**Verification**:
```bash
ros2 service call /randomize_scene std_srvs/srv/Trigger
# Scene changes visually
```

**Checkpoint**: Domain randomization working

---

## Phase 13: Integration and Debugging

**Goal**: Verify full system and document debugging

### T082-T088: Final Integration

- [ ] T082 Create integrated launch file:
  ```python
  # full_simulation.launch.py
  # Launches Gazebo + ros_gz_bridge + all sensors
  ```
- [ ] T083 [P] Create Unity launch integration
- [ ] T084 Test full sensor pipeline:
  - Gazebo: physics + camera + IMU + F/T
  - Unity: camera + randomization
- [ ] T085 Profile performance:
  - Gazebo real-time factor
  - Topic latencies
  - CPU/GPU usage
- [ ] T086 Create debugging guide with common issues
- [ ] T087 Write Chapter 10 content `docs/chapters/ch10-integration-debugging.md`
- [ ] T088 Create module summary `docs/module2-summary.md`

**Verification**:
```bash
ros2 launch humanoid_gazebo full_simulation.launch.py
# All topics publishing, robot controllable
```

**Checkpoint**: Full simulation operational

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1-2 (Setup)
    │
    ▼
Phase 3-4 (Gazebo World + Spawn) ─────┐
    │                                  │
    ▼                                  │
Phase 5-7 (Sensors)                    │
    │                                  │
    ▼                                  │
Phase 8 (Physics Tuning)               │
    │                                  │
    └──────────┬───────────────────────┘
               │
               ▼
    Phase 9-11 (Unity) ── Can start after Phase 2
               │
               ▼
    Phase 12 (Randomization)
               │
               ▼
    Phase 13 (Integration)
```

### Parallel Opportunities

**Within Phase 5-7** (sensors):
```
T027 camera.yaml       [P]
T034 imu.yaml          [P]
T040 force_torque.yaml [P]
```

**Within Phase 10** (Unity environment):
```
T061 room geometry     [P]
T062 PBR materials     [P]
T064 furniture         [P]
```

**Within Phase 12** (randomization):
```
T075 texture randomizer
T076 lighting randomizer [P]
T077 object randomizer   [P]
```

---

## Task Summary

| Phase | Tasks | Purpose |
|-------|-------|---------|
| 1 | T001-T005 | Setup and installation |
| 2 | T006-T011 | Package creation |
| 3 | T012-T018 | Gazebo world (US1) |
| 4 | T019-T026 | Robot spawning (US1) |
| 5 | T027-T033 | Camera sensor (US2) |
| 6 | T034-T039 | IMU sensor (US2) |
| 7 | T040-T045 | F/T sensors (US2) |
| 8 | T046-T052 | Physics tuning (US4) |
| 9 | T053-T060 | Unity setup (US3) |
| 10 | T061-T067 | Photorealistic env (US3) |
| 11 | T068-T074 | Unity camera (US3) |
| 12 | T075-T081 | Domain randomization |
| 13 | T082-T088 | Integration |

**Total**: 88 tasks

---

## Verification Checklist

- [ ] Gazebo world loads with stable physics
- [ ] Humanoid spawns and responds to commands
- [ ] Camera streams at 30 Hz
- [ ] IMU publishes at 100 Hz
- [ ] F/T sensors report contact forces
- [ ] Physics stable for 10+ seconds standing
- [ ] Unity-ROS bridge connected
- [ ] Unity camera streams to ROS 2
- [ ] Domain randomization changes scene
- [ ] Full simulation runs integrated

---

**Governed by**: `specs/constitution.md` v1.0.0
