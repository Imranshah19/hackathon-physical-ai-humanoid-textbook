# Module 1 Diagrams

All diagrams use Mermaid syntax for rendering in GitHub/GitLab/documentation tools.

## Architecture Diagrams

### ROS 2 Communication Model

```mermaid
graph TB
    subgraph "DDS Layer"
        DDS[Data Distribution Service]
    end

    subgraph "ROS 2 Nodes"
        N1[Camera Node]
        N2[Perception Node]
        N3[Planning Node]
        N4[Control Node]
    end

    N1 -->|/image_raw| DDS
    DDS -->|/image_raw| N2
    N2 -->|/detections| DDS
    DDS -->|/detections| N3
    N3 -->|/cmd_vel| DDS
    DDS -->|/cmd_vel| N4
```

### Humanoid Robot Node Graph

```mermaid
graph TB
    subgraph "Sensors"
        CAM[camera_node]
        IMU[imu_node]
        FT[force_torque_node]
    end

    subgraph "Perception"
        SE[state_estimator]
    end

    subgraph "Planning"
        LP[locomotion_planner]
        MP[manipulation_planner]
    end

    subgraph "Control"
        JC[joint_controller]
        BC[balance_controller]
    end

    CAM -->|/image| SE
    IMU -->|/imu/data| SE
    FT -->|/ft_sensor| SE
    SE -->|/robot_state| LP
    SE -->|/robot_state| MP
    LP -->|/gait_commands| BC
    MP -->|/arm_commands| JC
    BC -->|/joint_commands| JC
```

## Communication Pattern Diagrams

### Topic (Publish/Subscribe)

```mermaid
sequenceDiagram
    participant P as Publisher
    participant DDS as DDS Middleware
    participant S1 as Subscriber 1
    participant S2 as Subscriber 2

    P->>DDS: publish(msg)
    DDS->>S1: deliver(msg)
    DDS->>S2: deliver(msg)
```

### Service (Request/Response)

```mermaid
sequenceDiagram
    participant C as Client
    participant DDS as DDS
    participant S as Server

    C->>DDS: request
    DDS->>S: deliver request
    S->>S: process
    S->>DDS: response
    DDS->>C: deliver response
```

### Action (Long-Running Task)

```mermaid
sequenceDiagram
    participant C as Action Client
    participant S as Action Server

    C->>S: Send Goal
    S->>C: Goal Accepted

    loop Execution
        S->>C: Feedback
    end

    S->>C: Result
```

## Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> Unconfigured: Create

    Unconfigured --> Inactive: configure()
    Inactive --> Unconfigured: cleanup()

    Inactive --> Active: activate()
    Active --> Inactive: deactivate()

    Active --> Finalized: shutdown()
    Inactive --> Finalized: shutdown()
    Unconfigured --> Finalized: shutdown()

    Finalized --> [*]: Destroy
```

## URDF Structure

### Link and Joint Hierarchy

```mermaid
graph TB
    B[base_link]
    B --> HP[head_pan joint]
    HP --> H[head]

    B --> LSP[left_shoulder_pitch]
    LSP --> LUA[left_upper_arm]
    LUA --> LE[left_elbow]
    LE --> LF[left_forearm]

    B --> RSP[right_shoulder_pitch]
    RSP --> RUA[right_upper_arm]
    RUA --> RE[right_elbow]
    RE --> RF[right_forearm]

    B --> LHP[left_hip_pitch]
    LHP --> LUL[left_upper_leg]
    LUL --> LK[left_knee]
    LK --> LLL[left_lower_leg]
    LLL --> LA[left_ankle]
    LA --> LFT[left_foot]

    B --> RHP[right_hip_pitch]
    RHP --> RUL[right_upper_leg]
    RUL --> RK[right_knee]
    RK --> RLL[right_lower_leg]
    RLL --> RA[right_ankle]
    RA --> RFT[right_foot]
```

### Joint Types

```mermaid
graph LR
    subgraph "Revolute"
        R[Rotation with limits]
    end
    subgraph "Continuous"
        C[Unlimited rotation]
    end
    subgraph "Prismatic"
        P[Linear motion]
    end
    subgraph "Fixed"
        F[No motion]
    end
```

## Debugging Flowchart

```mermaid
flowchart TD
    A[Problem] --> B{Node running?}
    B -->|No| C[Start node]
    B -->|Yes| D{Topic exists?}

    D -->|No| E[Check topic name]
    D -->|Yes| F{Messages flowing?}

    F -->|No| G[Check publisher]
    F -->|Yes| H{Correct type?}

    H -->|No| I[Fix message type]
    H -->|Yes| J{QoS match?}

    J -->|No| K[Align QoS]
    J -->|Yes| L[Check logic]
```

## Package Structure

```mermaid
graph TB
    subgraph "humanoid_ros2_ws/src"
        M[humanoid_msgs]
        D[humanoid_description]
        C[humanoid_control]
        B[humanoid_bringup]
    end

    M -->|messages| C
    M -->|messages| B
    D -->|URDF| B
    C -->|nodes| B
```

## Rendering

These diagrams render automatically in:
- GitHub README files
- GitLab documentation
- Notion pages
- MkDocs with mermaid plugin
- Docusaurus

For PDF export, use:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i diagram.mmd -o diagram.png
```
