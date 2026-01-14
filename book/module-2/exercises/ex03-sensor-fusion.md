# Exercise 3: Sensor Fusion for Balance

**Objective**: Combine IMU and force/torque sensor data to detect balance state.

## Prerequisites
- Exercise 2 completed
- Robot with IMU and F/T sensors configured

## Instructions

### Part 1: Add Sensors to URDF (30 minutes)

1. Add IMU sensor to torso:
   ```xml
   <xacro:imu_sensor name="torso_imu" parent="torso" rate="100">
     <origin xyz="0 0 0" rpy="0 0 0"/>
   </xacro:imu_sensor>
   ```

2. Add F/T sensors to ankles:
   ```xml
   <xacro:ft_sensor name="left_foot_ft" joint="left_ankle_pitch"/>
   <xacro:ft_sensor name="right_foot_ft" joint="right_ankle_pitch"/>
   ```

3. Update bridge to include sensor topics

4. Verify sensors publish data:
   ```bash
   ros2 topic echo /torso_imu/data --once
   ros2 topic echo /left_foot_ft/wrench --once
   ```

### Part 2: IMU Processing (30 minutes)

1. Create `imu_processor.py`:
   ```python
   class IMUProcessor(Node):
       def __init__(self):
           # Subscribe to IMU
           # Compute roll/pitch from accelerometer
           # Apply complementary filter with gyroscope
           # Publish orientation
   ```

2. Implement complementary filter:
   - α = 0.98 (trust gyro more short-term)
   - angle = α * (angle + gyro * dt) + (1-α) * accel_angle

3. Test by tilting robot in simulation

### Part 3: Force Distribution (30 minutes)

1. Create `force_monitor.py`:
   ```python
   class ForceMonitor(Node):
       def __init__(self):
           # Subscribe to both foot F/T sensors
           # Compute total vertical force
           # Compute weight distribution (left/right)
           # Detect single vs double support
   ```

2. Implement support phase detection:
   - Double support: both feet > threshold
   - Left support: only left > threshold
   - Right support: only right > threshold
   - Flight: neither > threshold

3. Test by having robot shift weight

### Part 4: Balance State Machine (30 minutes)

1. Create `balance_detector.py`:
   ```python
   class BalanceDetector(Node):
       # Combine IMU orientation and force data
       # Publish balance state message:
       #   - STABLE: small tilt, good foot contact
       #   - UNSTABLE: large tilt or losing contact
       #   - FALLING: critical tilt or no contact
   ```

2. Define thresholds:
   - Stable tilt: < 10 degrees
   - Unstable tilt: 10-30 degrees
   - Falling tilt: > 30 degrees

3. Test by pushing robot (apply force in sim)

## Deliverables

1. Updated URDF with sensors
2. `imu_processor.py`
3. `force_monitor.py`
4. `balance_detector.py`
5. Custom message definition for balance state

## Evaluation Criteria

- [ ] Sensors publish at correct rates
- [ ] IMU orientation is reasonably accurate
- [ ] Support phase detection works
- [ ] Balance state changes appropriately
- [ ] Code is well-documented
