# Exercise 5: Full Digital Twin Integration

**Objective**: Create a complete digital twin pipeline with Gazebo physics and Unity rendering.

## Prerequisites
- All previous exercises completed
- Both Gazebo and Unity environments ready

## Instructions

### Part 1: Combined Launch (30 minutes)

1. Create `full_simulation.launch.py`:
   ```python
   # Launch in order:
   # 1. Gazebo simulation
   # 2. Robot spawn
   # 3. Sensor bridges
   # 4. Unity TCP endpoint
   # 5. Simulation monitor
   ```

2. Add launch arguments:
   - `use_gazebo` (default: true)
   - `use_unity` (default: true)
   - `headless` (default: false)

3. Test combined launch:
   ```bash
   ros2 launch humanoid_gazebo full_simulation.launch.py
   # Then start Unity
   ```

### Part 2: State Synchronization (40 minutes)

1. Verify joint states flow:
   - Gazebo → ros_gz_bridge → ROS 2
   - ROS 2 → ros_tcp_endpoint → Unity

2. Create `state_sync_monitor.py`:
   ```python
   # Subscribe to both Gazebo and Unity joint states
   # Compare positions
   # Report synchronization error
   # Warn if error exceeds threshold
   ```

3. Test synchronization:
   - Send joint commands
   - Verify both simulators respond
   - Measure sync latency

### Part 3: Sensor Fusion Pipeline (40 minutes)

1. Create unified sensor processing:
   ```
   Gazebo IMU ──┐
   Gazebo F/T ──┼──> ROS 2 Processing ──> State Estimation
   Unity Camera ┘
   ```

2. Implement state estimator:
   - Orientation from IMU
   - Position from visual odometry (optional)
   - Contact state from F/T

3. Publish estimated pose as TF

### Part 4: Diagnostic Dashboard (30 minutes)

1. Create `simulation_dashboard.py`:
   ```python
   # Monitor and display:
   # - RTF (real-time factor)
   # - Topic rates
   # - Sync errors
   # - Sensor health
   ```

2. Add warning thresholds:
   - RTF < 0.8: Yellow
   - RTF < 0.5: Red
   - Topic rate < expected/2: Yellow

3. Log to file for analysis

### Part 5: Validation Suite (30 minutes)

1. Create automated tests:
   ```python
   # test_digital_twin.py
   def test_joint_count():
       # Verify 14 joints

   def test_sensor_rates():
       # Verify IMU at 100Hz, Camera at 30Hz

   def test_physics_gravity():
       # Verify robot responds to gravity

   def test_sync_latency():
       # Verify < 100ms sync delay
   ```

2. Run full test suite

3. Generate validation report

### Part 6: Documentation (20 minutes)

1. Document system architecture

2. Create troubleshooting guide:
   - Common issues and solutions
   - Diagnostic commands

3. Write quick-start instructions

## Deliverables

1. `full_simulation.launch.py`
2. `state_sync_monitor.py`
3. `simulation_dashboard.py`
4. `test_digital_twin.py`
5. Architecture diagram
6. Troubleshooting guide

## Evaluation Criteria

- [ ] Combined system launches successfully
- [ ] Joint states synchronized < 100ms
- [ ] All sensors publishing
- [ ] Dashboard shows system health
- [ ] Validation tests pass
- [ ] Documentation is complete

## Bonus Challenges

1. Add walking controller and verify in both simulators
2. Implement visual servoing using Unity camera
3. Create synthetic dataset for ML training
4. Add support for hardware-in-the-loop testing
