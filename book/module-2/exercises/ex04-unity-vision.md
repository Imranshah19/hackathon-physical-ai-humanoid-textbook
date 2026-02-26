# Exercise 4: Unity Vision Pipeline

**Objective**: Set up Unity camera streaming to ROS 2 with domain randomization.

## Prerequisites
- Unity 2022.3 LTS installed
- ROS-TCP-Connector package installed
- Exercise 3 completed (robot simulation running)

## Instructions

### Part 1: Unity Project Setup (30 minutes)

1. Create new Unity HDRP project

2. Install packages:
   - ROS-TCP-Connector
   - URDF Importer

3. Import humanoid robot from URDF

4. Configure ROSConnection:
   - IP: 127.0.0.1
   - Port: 10000

5. Test connection:
   ```bash
   ros2 run ros_tcp_endpoint default_server_endpoint
   ```

### Part 2: Camera Streaming (40 minutes)

1. Add camera to robot head

2. Create `RGBCameraPublisher.cs`:
   - Resolution: 640x480
   - Rate: 30 Hz
   - Topic: /unity/camera/image_raw

3. Attach script to camera

4. Verify in ROS 2:
   ```bash
   ros2 topic hz /unity/camera/image_raw
   ros2 run rqt_image_view rqt_image_view
   ```

5. Add depth camera:
   - Topic: /unity/camera/depth
   - Format: 16UC1 (mm)

### Part 3: Environment Setup (40 minutes)

1. Create indoor lab environment:
   - Floor: 10m x 10m
   - Walls: 3m height
   - Ceiling with lights

2. Apply PBR materials:
   - Concrete floor (low metallic, rough)
   - White walls (diffuse)
   - Metal objects (high metallic)

3. Add various objects:
   - Tables
   - Chairs
   - Boxes
   - Cylinders

4. Configure HDRP lighting:
   - Area lights on ceiling
   - Ambient occlusion
   - Post-processing

### Part 4: Domain Randomization (40 minutes)

1. Create `DomainRandomizer.cs`:
   ```csharp
   // Randomize:
   // - Floor/wall textures
   // - Lighting intensity/color
   // - Object positions
   // - Object colors
   ```

2. Expose as ROS service:
   - Service: /randomize_domain
   - Type: std_srvs/Trigger

3. Test from ROS 2:
   ```bash
   ros2 service call /randomize_domain std_srvs/srv/Trigger
   ```

4. Create dataset recording:
   - Save RGB images
   - Save depth images
   - Record metadata (poses)

### Part 5: Validation (20 minutes)

1. Record 100 frames with randomization

2. Verify images saved correctly

3. Check depth alignment with RGB

4. Visualize samples

## Deliverables

1. Unity project (zipped)
2. `RGBCameraPublisher.cs`
3. `DomainRandomizer.cs`
4. 100-frame dataset
5. Sample images (5 randomized scenes)

## Evaluation Criteria

- [ ] Unity connects to ROS TCP endpoint
- [ ] Camera publishes at 30 Hz
- [ ] Depth images are valid
- [ ] Environment looks realistic
- [ ] Randomization produces variety
- [ ] Dataset is correctly structured
