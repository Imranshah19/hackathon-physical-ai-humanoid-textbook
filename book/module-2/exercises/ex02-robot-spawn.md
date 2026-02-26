# Exercise 2: Spawn and Control Robot in Gazebo

**Objective**: Spawn a robot from URDF and send joint commands via ROS 2.

## Prerequisites
- Exercise 1 completed
- humanoid_description package from Module 1

## Instructions

### Part 1: Robot Spawning (30 minutes)

1. Create a launch file `spawn_robot.launch.py`:
   ```python
   # Your code here
   # - Include Gazebo world
   # - Publish robot_description
   # - Spawn robot at z=1.0
   ```

2. Add required nodes:
   - `robot_state_publisher`
   - `ros_gz_sim create`
   - `ros_gz_bridge` (for clock)

3. Test the launch:
   ```bash
   ros2 launch humanoid_gazebo spawn_robot.launch.py
   ```

4. Verify robot appears in Gazebo

### Part 2: Bridge Configuration (30 minutes)

1. Create a bridge configuration for:
   - Clock synchronization (GZ → ROS)
   - Joint states (GZ → ROS)
   - Joint commands (ROS → GZ)

2. Add bridge arguments to launch file:
   ```python
   bridge = Node(
       package='ros_gz_bridge',
       executable='parameter_bridge',
       arguments=[
           # Add your bridge arguments here
       ],
   )
   ```

3. Verify topics are visible:
   ```bash
   ros2 topic list
   # Should see /clock, /joint_states, etc.
   ```

### Part 3: Joint Control (30 minutes)

1. Create a Python node `joint_commander.py`:
   ```python
   # Subscribe to /joint_states
   # Publish to individual joint command topics
   # Implement a simple motion (e.g., knee bend)
   ```

2. Test the controller:
   ```bash
   ros2 run humanoid_gazebo joint_commander
   ```

3. Verify robot moves in simulation

### Part 4: Closed-Loop Control (30 minutes)

1. Modify your node to implement position control:
   - Read current joint position
   - Calculate error from target
   - Apply proportional control

2. Test by commanding different target positions

3. Tune proportional gain for smooth motion

## Deliverables

1. `spawn_robot.launch.py` - Launch file
2. `joint_commander.py` - Control node
3. Video or screenshot of robot moving

## Evaluation Criteria

- [ ] Robot spawns at correct height
- [ ] Bridge connects all required topics
- [ ] Joint commands cause robot motion
- [ ] Closed-loop control reaches targets
- [ ] No physics explosions or instabilities
