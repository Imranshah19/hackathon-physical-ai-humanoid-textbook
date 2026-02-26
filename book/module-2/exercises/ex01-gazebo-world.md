# Exercise 1: Create Custom Gazebo World

**Objective**: Create a custom Gazebo world with physics tuned for humanoid simulation.

## Prerequisites
- Gazebo Harmonic installed
- ROS 2 Humble workspace configured

## Instructions

### Part 1: Basic World (30 minutes)

1. Create a new SDF file `my_world.sdf`:
   ```xml
   <?xml version="1.0"?>
   <sdf version="1.9">
     <world name="my_world">
       <!-- Add physics configuration here -->
       <!-- Add ground plane here -->
       <!-- Add lighting here -->
     </world>
   </sdf>
   ```

2. Add physics configuration:
   - Timestep: 0.001s
   - Solver iterations: 50
   - Real-time factor: 1.0

3. Add a ground plane with:
   - Size: 50m x 50m
   - Friction mu: 1.0
   - Contact stiffness: 1e6

4. Add directional light (sun)

5. Launch the world:
   ```bash
   gz sim my_world.sdf
   ```

### Part 2: Physics Tuning (30 minutes)

1. Add a box model that can be dropped:
   ```xml
   <model name="test_box">
     <pose>0 0 2 0 0 0</pose>
     <link name="link">
       <collision name="collision">
         <geometry><box><size>0.2 0.2 0.2</size></box></geometry>
       </collision>
       <visual name="visual">
         <geometry><box><size>0.2 0.2 0.2</size></box></geometry>
       </visual>
       <inertial>
         <mass>1.0</mass>
       </inertial>
     </link>
   </model>
   ```

2. Experiment with contact parameters:
   - Test kp values: 1e5, 1e6, 1e7
   - Observe bouncing behavior
   - Document which value gives realistic bounce

3. Experiment with friction:
   - Test mu values: 0.3, 0.6, 1.0, 1.5
   - Tilt ground plane to 30 degrees
   - Find minimum mu where box doesn't slide

### Part 3: Performance Testing (20 minutes)

1. Add 10 boxes to the scene
2. Record RTF (real-time factor)
3. Add 50 boxes
4. Record RTF again
5. How does complexity affect performance?

## Deliverables

1. `my_world.sdf` - Your custom world file
2. A short report (text file) documenting:
   - Optimal kp value found
   - Minimum friction coefficient for 30° incline
   - RTF measurements for 10 vs 50 objects

## Evaluation Criteria

- [ ] World launches without errors
- [ ] Physics timestep is 0.001s
- [ ] Ground plane has proper friction
- [ ] Lighting creates visible shadows
- [ ] Report includes all measurements
