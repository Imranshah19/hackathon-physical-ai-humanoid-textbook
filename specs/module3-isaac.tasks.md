# Module 3 Tasks: AI-Robot Brain – NVIDIA Isaac

**Specification**: `specs/module3-isaac.spec.md`
**Created**: 2026-01-07
**Status**: Draft
**Constitution**: `specs/constitution.md` (v1.0.0)

---

## Task Overview

| Phase | Description | Tasks | Priority |
|-------|-------------|-------|----------|
| 1 | Environment Setup | 8 | P0 |
| 2 | Isaac Sim Configuration | 9 | P0 |
| 3 | Isaac Gym Setup | 8 | P0 |
| 4 | Training Environment | 10 | P0 |
| 5 | Reward System | 9 | P1 |
| 6 | PPO Training | 10 | P1 |
| 7 | Domain Randomization | 8 | P1 |
| 8 | Curriculum Learning | 7 | P2 |
| 9 | Policy Export | 8 | P1 |
| 10 | ROS 2 Deployment | 9 | P1 |
| 11 | Gazebo Integration | 7 | P2 |
| 12 | Sim-to-Real Analysis | 6 | P2 |
| 13 | Documentation & Testing | 7 | P1 |
| **Total** | | **106** | |

---

## Phase 1: Environment Setup

### Task 1.1: System Requirements Verification
**Priority**: P0
**Chapter**: 1

**Description**: Verify system meets Isaac Sim requirements.

**Acceptance Criteria**:
- [ ] NVIDIA GPU with 12GB+ VRAM detected
- [ ] CUDA 11.8+ installed and functional
- [ ] Ubuntu 22.04 or compatible OS
- [ ] 32GB+ RAM available
- [ ] 100GB+ free disk space

**Test Cases**:
```bash
# TC-1.1.1: Check GPU
nvidia-smi
# Expected: GPU with 12GB+ memory shown

# TC-1.1.2: Check CUDA
nvcc --version
# Expected: CUDA 11.8 or higher

# TC-1.1.3: Check memory
free -h
# Expected: 32GB+ total
```

---

### Task 1.2: Install NVIDIA Omniverse Launcher
**Priority**: P0
**Chapter**: 1

**Description**: Download and install Omniverse Launcher.

**Acceptance Criteria**:
- [ ] Omniverse Launcher downloaded
- [ ] Launcher installed and runs
- [ ] NVIDIA account logged in
- [ ] Nucleus server accessible

**Test Cases**:
```bash
# TC-1.2.1: Launch Omniverse
# Expected: Omniverse Launcher opens
# Expected: Can browse Exchange tab
```

---

### Task 1.3: Install Isaac Sim
**Priority**: P0
**Chapter**: 1

**Description**: Install Isaac Sim 2023.1+ via Omniverse.

**Acceptance Criteria**:
- [ ] Isaac Sim 2023.1+ installed
- [ ] All dependencies resolved
- [ ] Isaac Sim launches successfully
- [ ] Sample scene loads

**Test Cases**:
```bash
# TC-1.3.1: Launch Isaac Sim
~/.local/share/ov/pkg/isaac_sim-2023.1.1/isaac-sim.sh

# TC-1.3.2: Load sample
# File > Open > omniverse://localhost/NVIDIA/Assets/Isaac/2023.1.1/Isaac/Robots/Humanoid/humanoid.usd
# Expected: Humanoid robot visible
```

---

### Task 1.4: Configure Python Environment
**Priority**: P0
**Chapter**: 1

**Description**: Set up Isaac Sim Python environment.

**Acceptance Criteria**:
- [ ] Isaac Sim Python accessible
- [ ] PyTorch with CUDA working
- [ ] Required packages installed
- [ ] Environment variables set

**Test Cases**:
```bash
# TC-1.4.1: Isaac Python
~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh -c "import torch; print(torch.cuda.is_available())"
# Expected: True

# TC-1.4.2: Import omni
~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh -c "import omni.isaac.core"
# Expected: No errors
```

---

### Task 1.5: Install Isaac Gym
**Priority**: P0
**Chapter**: 3

**Description**: Install Isaac Gym Preview 4.

**Acceptance Criteria**:
- [ ] Isaac Gym downloaded
- [ ] Package installed in Python env
- [ ] Import succeeds
- [ ] Sample runs

**Test Cases**:
```bash
# TC-1.5.1: Install
pip install isaacgym

# TC-1.5.2: Import
python -c "from isaacgym import gymapi; print('OK')"
# Expected: OK
```

---

### Task 1.6: Clone IsaacGymEnvs
**Priority**: P0
**Chapter**: 3

**Description**: Clone and set up IsaacGymEnvs repository.

**Acceptance Criteria**:
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Sample environment runs
- [ ] Training starts

**Test Cases**:
```bash
# TC-1.6.1: Clone
git clone https://github.com/NVIDIA-Omniverse/IsaacGymEnvs.git
cd IsaacGymEnvs
pip install -e .

# TC-1.6.2: Run Cartpole
python train.py task=Cartpole
# Expected: Training starts, reward increases
```

---

### Task 1.7: Create ROS 2 Workspace
**Priority**: P0
**Chapter**: 9

**Description**: Create workspace for Isaac-ROS integration.

**Acceptance Criteria**:
- [ ] Workspace created
- [ ] Packages initialized
- [ ] Builds successfully
- [ ] Sourced correctly

**Test Cases**:
```bash
# TC-1.7.1: Create workspace
mkdir -p ~/humanoid_isaac_ws/src
cd ~/humanoid_isaac_ws
colcon build
source install/setup.bash
# Expected: No errors
```

---

### Task 1.8: Install Additional Dependencies
**Priority**: P0
**Chapter**: 1

**Description**: Install RL and utility packages.

**Acceptance Criteria**:
- [ ] rl_games installed
- [ ] tensorboard installed
- [ ] onnx and onnxruntime installed
- [ ] All imports work

**Test Cases**:
```bash
# TC-1.8.1: Install packages
pip install rl_games tensorboard onnx onnxruntime-gpu

# TC-1.8.2: Verify
python -c "import rl_games; import onnx; print('OK')"
# Expected: OK
```

---

## Phase 2: Isaac Sim Configuration

### Task 2.1: Create Isaac Sim Stage
**Priority**: P0
**Chapter**: 2

**Description**: Create new USD stage for humanoid training.

**Acceptance Criteria**:
- [ ] New stage created
- [ ] Physics scene added
- [ ] Ground plane added
- [ ] Lighting configured

**Test Cases**:
```python
# TC-2.1.1: Stage creation
from omni.isaac.core import World
world = World(stage_units_in_meters=1.0)
world.scene.add_default_ground_plane()
# Expected: Ground plane visible
```

---

### Task 2.2: Convert URDF to USD
**Priority**: P0
**Chapter**: 2

**Description**: Import humanoid URDF into Isaac Sim as USD.

**Acceptance Criteria**:
- [ ] URDF importer configured
- [ ] Humanoid imported successfully
- [ ] All joints preserved
- [ ] Collision meshes correct

**Test Cases**:
```python
# TC-2.2.1: Import URDF
from omni.isaac.urdf import _urdf
urdf_interface = _urdf.acquire_urdf_interface()
import_config = _urdf.ImportConfig()
result = urdf_interface.parse_urdf("humanoid.urdf", import_config)
# Expected: Valid USD prim created
```

---

### Task 2.3: Configure Articulation
**Priority**: P0
**Chapter**: 2

**Description**: Set up articulation properties for physics.

**Acceptance Criteria**:
- [ ] Articulation root set
- [ ] Joint drives configured
- [ ] Position/velocity limits set
- [ ] Damping values tuned

**Test Cases**:
```python
# TC-2.3.1: Articulation config
from omni.isaac.core.articulations import Articulation
robot = Articulation(prim_path="/World/Humanoid")
robot.initialize()
print(robot.num_dof)
# Expected: 14 (matching URDF)
```

---

### Task 2.4: Configure Joint Properties
**Priority**: P0
**Chapter**: 2

**Description**: Set joint stiffness, damping, and limits.

**Acceptance Criteria**:
- [ ] Joint stiffness set (position control)
- [ ] Joint damping configured
- [ ] Joint limits match URDF
- [ ] Max effort configured

**Test Cases**:
```python
# TC-2.4.1: Joint properties
joint_props = robot.get_articulation_controller()
# Expected: Can set position targets
```

---

### Task 2.5: Configure Physics Scene
**Priority**: P0
**Chapter**: 2

**Description**: Set up GPU physics parameters.

**Acceptance Criteria**:
- [ ] PhysX GPU enabled
- [ ] Timestep set to 1/120s
- [ ] Solver iterations configured
- [ ] Contact parameters tuned

**Test Cases**:
```python
# TC-2.5.1: Physics config
from omni.isaac.core.utils.physics import set_physics_properties
set_physics_properties(
    solver_type=1,  # TGS
    gpu_enabled=True,
    gpu_max_rigid_contact_count=524288
)
# Expected: GPU physics active
```

---

### Task 2.6: Add Camera Sensor
**Priority**: P1
**Chapter**: 2

**Description**: Configure camera for optional visual observations.

**Acceptance Criteria**:
- [ ] Camera attached to robot head
- [ ] Resolution set (84x84 or 224x224)
- [ ] Render products configured
- [ ] Images retrievable

**Test Cases**:
```python
# TC-2.6.1: Camera setup
from omni.isaac.sensor import Camera
camera = Camera(
    prim_path="/World/Humanoid/head/camera",
    resolution=(224, 224)
)
camera.initialize()
# Expected: Camera renders image
```

---

### Task 2.7: Save USD Asset
**Priority**: P0
**Chapter**: 2

**Description**: Export configured humanoid as USD asset.

**Acceptance Criteria**:
- [ ] USD file saved
- [ ] All properties preserved
- [ ] Can reload successfully
- [ ] File size reasonable

**Test Cases**:
```python
# TC-2.7.1: Save USD
omni.usd.get_context().save_as_stage("humanoid_configured.usd")
# Expected: File created < 50MB
```

---

### Task 2.8: Test Physics Simulation
**Priority**: P0
**Chapter**: 2

**Description**: Verify physics works correctly for humanoid.

**Acceptance Criteria**:
- [ ] Robot falls under gravity
- [ ] Contacts with ground work
- [ ] Joints respond to commands
- [ ] No physics explosions

**Test Cases**:
```python
# TC-2.8.1: Physics test
world.reset()
for i in range(100):
    world.step()
    pos = robot.get_world_pose()[0]
# Expected: Robot falls to ground, z ≈ 0
```

---

### Task 2.9: Create Asset Bundle
**Priority**: P1
**Chapter**: 2

**Description**: Package humanoid USD with all dependencies.

**Acceptance Criteria**:
- [ ] All meshes included
- [ ] Materials packaged
- [ ] Can load on fresh install
- [ ] Documentation included

**Test Cases**:
```bash
# TC-2.9.1: Package test
# Load on different machine
# Expected: All visuals correct
```

---

## Phase 3: Isaac Gym Setup

### Task 3.1: Understand Gym Architecture
**Priority**: P0
**Chapter**: 3

**Description**: Study Isaac Gym environment structure.

**Acceptance Criteria**:
- [ ] Understand VecEnv concept
- [ ] Understand tensor-based API
- [ ] Understand actor/env indexing
- [ ] Can explain observation flow

**Test Cases**:
```
# TC-3.1.1: Documentation review
# Complete Isaac Gym documentation
# Expected: Can explain parallel execution
```

---

### Task 3.2: Run Cartpole Example
**Priority**: P0
**Chapter**: 3

**Description**: Successfully train Cartpole baseline.

**Acceptance Criteria**:
- [ ] Cartpole training starts
- [ ] Rewards increase over time
- [ ] Training completes
- [ ] Policy plays successfully

**Test Cases**:
```bash
# TC-3.2.1: Train
cd IsaacGymEnvs
python train.py task=Cartpole num_envs=1024

# TC-3.2.2: Play
python train.py task=Cartpole test=True checkpoint=runs/Cartpole/nn/Cartpole.pth
# Expected: Cartpole balances
```

---

### Task 3.3: Run Humanoid Example
**Priority**: P0
**Chapter**: 3

**Description**: Run existing humanoid example to understand structure.

**Acceptance Criteria**:
- [ ] Humanoid env loads
- [ ] Training starts
- [ ] Can visualize
- [ ] Understand reward structure

**Test Cases**:
```bash
# TC-3.3.1: Train humanoid
python train.py task=Humanoid num_envs=1024
# Expected: Training progresses

# TC-3.3.2: Visualize
python train.py task=Humanoid test=True num_envs=16
# Expected: Humanoids visible
```

---

### Task 3.4: Analyze Environment Code
**Priority**: P0
**Chapter**: 3

**Description**: Study IsaacGymEnvs humanoid implementation.

**Acceptance Criteria**:
- [ ] Understand observation space
- [ ] Understand action space
- [ ] Understand reward calculation
- [ ] Understand reset logic

**Test Cases**:
```python
# TC-3.4.1: Code review
# File: IsaacGymEnvs/isaacgymenvs/tasks/humanoid.py
# Document: observation dims, action dims, reward components
```

---

### Task 3.5: Create Custom Task Template
**Priority**: P0
**Chapter**: 4

**Description**: Create template for custom humanoid task.

**Acceptance Criteria**:
- [ ] Task file created
- [ ] Config file created
- [ ] Registers with IsaacGymEnvs
- [ ] Can instantiate

**Test Cases**:
```python
# TC-3.5.1: Create task
# isaacgymenvs/tasks/humanoid_custom.py
# Expected: Imports without error
```

---

### Task 3.6: Configure Task YAML
**Priority**: P0
**Chapter**: 4

**Description**: Create configuration file for custom task.

**Acceptance Criteria**:
- [ ] YAML file created
- [ ] All parameters documented
- [ ] Inherits from base config
- [ ] Overrides work correctly

**Test Cases**:
```yaml
# TC-3.6.1: Config file
# isaacgymenvs/cfg/task/HumanoidCustom.yaml
name: HumanoidCustom
physics_engine: physx
env:
  numEnvs: 1024
  numObservations: 48
  numActions: 14
```

---

### Task 3.7: Configure Training YAML
**Priority**: P0
**Chapter**: 6

**Description**: Create PPO training configuration.

**Acceptance Criteria**:
- [ ] PPO parameters set
- [ ] Network architecture defined
- [ ] Learning schedule configured
- [ ] Logging enabled

**Test Cases**:
```yaml
# TC-3.7.1: Training config
# isaacgymenvs/cfg/train/HumanoidCustomPPO.yaml
params:
  algo:
    name: ppo
  network:
    mlp:
      units: [256, 256, 256]
```

---

### Task 3.8: Test Custom Task Registration
**Priority**: P0
**Chapter**: 4

**Description**: Verify custom task loads and runs.

**Acceptance Criteria**:
- [ ] Task appears in task list
- [ ] Environment initializes
- [ ] Random actions work
- [ ] No crashes

**Test Cases**:
```bash
# TC-3.8.1: Run custom task
python train.py task=HumanoidCustom num_envs=64 max_iterations=10
# Expected: Training starts
```

---

## Phase 4: Training Environment

### Task 4.1: Define Observation Space
**Priority**: P0
**Chapter**: 4

**Description**: Design observation vector for humanoid.

**Acceptance Criteria**:
- [ ] Joint positions (14 DOF)
- [ ] Joint velocities (14 DOF)
- [ ] Base orientation (4 quat or 6 projected)
- [ ] Base angular velocity (3)
- [ ] Base linear velocity (3)
- [ ] Command (3: vx, vy, yaw_rate)
- [ ] Total: ~48 dimensions

**Test Cases**:
```python
# TC-4.1.1: Observation check
obs = env.get_observations()
assert obs.shape == (num_envs, 48)
```

---

### Task 4.2: Define Action Space
**Priority**: P0
**Chapter**: 4

**Description**: Design action space for joint control.

**Acceptance Criteria**:
- [ ] 14 joint actions
- [ ] Torque or position targets
- [ ] Action scaling defined
- [ ] Clipping configured

**Test Cases**:
```python
# TC-4.2.1: Action check
actions = torch.randn(num_envs, 14)
env.step(actions)
# Expected: No errors
```

---

### Task 4.3: Implement Observation Computation
**Priority**: P0
**Chapter**: 4

**Description**: Code observation gathering from simulation.

**Acceptance Criteria**:
- [ ] `compute_observations()` implemented
- [ ] All components computed
- [ ] Tensor shapes correct
- [ ] GPU tensors used

**Test Cases**:
```python
# TC-4.3.1: Observation function
def compute_observations(self):
    self.obs_buf[:, 0:14] = self.dof_pos
    self.obs_buf[:, 14:28] = self.dof_vel
    # ... etc
# Expected: obs_buf filled correctly
```

---

### Task 4.4: Implement Action Application
**Priority**: P0
**Chapter**: 4

**Description**: Apply actions to simulation joints.

**Acceptance Criteria**:
- [ ] Actions scaled properly
- [ ] Applied as torques or positions
- [ ] Respects joint limits
- [ ] Smooth application

**Test Cases**:
```python
# TC-4.4.1: Action application
def pre_physics_step(self, actions):
    scaled_actions = actions * self.action_scale
    self.gym.set_dof_actuation_force_tensor(
        self.sim,
        gymtorch.unwrap_tensor(scaled_actions)
    )
# Expected: Joints move
```

---

### Task 4.5: Implement Reset Logic
**Priority**: P0
**Chapter**: 4

**Description**: Reset environments when episode ends.

**Acceptance Criteria**:
- [ ] Detect termination conditions
- [ ] Reset robot pose
- [ ] Reset velocities
- [ ] Randomize initial state

**Test Cases**:
```python
# TC-4.5.1: Reset function
def reset_idx(self, env_ids):
    # Reset positions
    self.dof_pos[env_ids] = self.initial_dof_pos
    self.dof_vel[env_ids] = 0.0
    # Reset base pose
    self.root_states[env_ids] = self.initial_root_states
# Expected: Robots reset to standing
```

---

### Task 4.6: Implement Command Generation
**Priority**: P0
**Chapter**: 4

**Description**: Generate velocity commands for locomotion.

**Acceptance Criteria**:
- [ ] Random commands generated
- [ ] Command ranges configurable
- [ ] Commands change periodically
- [ ] Standing command (zero) included

**Test Cases**:
```python
# TC-4.6.1: Command generation
def resample_commands(self, env_ids):
    self.commands[env_ids, 0] = torch.rand(len(env_ids)) * 2.0 - 1.0  # vx
    self.commands[env_ids, 1] = torch.rand(len(env_ids)) * 0.5 - 0.25  # vy
    self.commands[env_ids, 2] = torch.rand(len(env_ids)) * 1.0 - 0.5  # yaw
# Expected: Varied commands
```

---

### Task 4.7: Configure Parallel Environments
**Priority**: P0
**Chapter**: 4

**Description**: Set up 1024+ parallel environments.

**Acceptance Criteria**:
- [ ] Environment spacing correct
- [ ] No collision between envs
- [ ] GPU memory sufficient
- [ ] All envs simulate

**Test Cases**:
```python
# TC-4.7.1: Parallel envs
env = HumanoidEnv(cfg, num_envs=1024)
assert env.num_envs == 1024
# Expected: All envs visible in grid
```

---

### Task 4.8: Add Terrain Generation
**Priority**: P1
**Chapter**: 4

**Description**: Generate varied terrain for training.

**Acceptance Criteria**:
- [ ] Flat terrain (default)
- [ ] Random height field option
- [ ] Slope terrain option
- [ ] Terrain per-env or shared

**Test Cases**:
```python
# TC-4.8.1: Terrain
terrain = Terrain(cfg.terrain)
terrain.create_heightfield()
# Expected: Non-flat ground visible
```

---

### Task 4.9: Implement Contact Detection
**Priority**: P0
**Chapter**: 4

**Description**: Detect foot contacts with ground.

**Acceptance Criteria**:
- [ ] Left foot contact detected
- [ ] Right foot contact detected
- [ ] Contact force measured
- [ ] Binary contact flag computed

**Test Cases**:
```python
# TC-4.9.1: Contact detection
contact_forces = self.gym.acquire_net_contact_force_tensor(self.sim)
left_contact = contact_forces[:, self.left_foot_idx, 2] > 1.0
# Expected: True when foot on ground
```

---

### Task 4.10: Test Full Environment
**Priority**: P0
**Chapter**: 4

**Description**: Verify complete environment works.

**Acceptance Criteria**:
- [ ] Environment creates
- [ ] Random policy runs
- [ ] No crashes over 1000 steps
- [ ] All tensors valid

**Test Cases**:
```python
# TC-4.10.1: Full test
env = HumanoidEnv(cfg)
obs = env.reset()
for i in range(1000):
    actions = torch.randn(num_envs, 14, device='cuda')
    obs, rew, done, info = env.step(actions)
# Expected: No errors
```

---

## Phase 5: Reward System

### Task 5.1: Design Reward Structure
**Priority**: P1
**Chapter**: 5

**Description**: Design modular reward function.

**Acceptance Criteria**:
- [ ] Reward components identified
- [ ] Weights configurable
- [ ] Positive and negative rewards
- [ ] Total reward computed

**Test Cases**:
```python
# TC-5.1.1: Reward structure
reward = (
    w_vel * r_velocity +
    w_alive * r_alive +
    w_energy * r_energy +
    w_orient * r_orientation
)
```

---

### Task 5.2: Implement Velocity Tracking Reward
**Priority**: P1
**Chapter**: 5

**Description**: Reward for matching commanded velocity.

**Acceptance Criteria**:
- [ ] Linear velocity tracking
- [ ] Angular velocity tracking
- [ ] Exponential or quadratic error
- [ ] Properly scaled

**Test Cases**:
```python
# TC-5.2.1: Velocity reward
lin_vel_error = torch.sum((self.commands[:, :2] - self.base_lin_vel[:, :2])**2, dim=1)
r_velocity = torch.exp(-lin_vel_error / 0.25)
# Expected: r in [0, 1]
```

---

### Task 5.3: Implement Alive Reward
**Priority**: P1
**Chapter**: 5

**Description**: Reward for staying upright.

**Acceptance Criteria**:
- [ ] Constant reward per step
- [ ] Encourages longer episodes
- [ ] Balanced with other rewards

**Test Cases**:
```python
# TC-5.3.1: Alive reward
r_alive = torch.ones(self.num_envs, device=self.device)
# Expected: 1.0 per timestep
```

---

### Task 5.4: Implement Energy Penalty
**Priority**: P1
**Chapter**: 5

**Description**: Penalize excessive torque usage.

**Acceptance Criteria**:
- [ ] Torque squared penalty
- [ ] Encourages efficiency
- [ ] Scaled appropriately

**Test Cases**:
```python
# TC-5.4.1: Energy penalty
r_energy = -torch.sum(self.torques**2, dim=1) * 0.0001
# Expected: Negative, small magnitude
```

---

### Task 5.5: Implement Orientation Reward
**Priority**: P1
**Chapter**: 5

**Description**: Reward for upright base orientation.

**Acceptance Criteria**:
- [ ] Penalize tilt from vertical
- [ ] Use projected gravity vector
- [ ] Smooth penalty function

**Test Cases**:
```python
# TC-5.5.1: Orientation reward
projected_gravity = quat_rotate_inverse(self.base_quat, self.gravity_vec)
r_orient = torch.sum(torch.square(projected_gravity[:, :2]), dim=1)
# Expected: 0 when upright
```

---

### Task 5.6: Implement Foot Contact Reward
**Priority**: P1
**Chapter**: 5

**Description**: Reward appropriate foot contact patterns.

**Acceptance Criteria**:
- [ ] Reward alternating contacts
- [ ] Penalize double flight
- [ ] Encourage gait pattern

**Test Cases**:
```python
# TC-5.6.1: Contact reward
desired_contact = (self.phase < 0.5)  # Simplified
r_contact = (self.left_contact == desired_contact).float()
```

---

### Task 5.7: Implement Joint Limit Penalty
**Priority**: P1
**Chapter**: 5

**Description**: Penalize joints near limits.

**Acceptance Criteria**:
- [ ] Soft limit penalty
- [ ] Prevents hitting hard limits
- [ ] Per-joint computation

**Test Cases**:
```python
# TC-5.7.1: Joint limits
out_of_limits = (self.dof_pos - self.dof_pos_limits[:, 0]).clip(max=0.0)
out_of_limits += (self.dof_pos - self.dof_pos_limits[:, 1]).clip(min=0.0)
r_limits = torch.sum(out_of_limits**2, dim=1)
```

---

### Task 5.8: Implement Smoothness Penalty
**Priority**: P1
**Chapter**: 5

**Description**: Penalize jerky actions.

**Acceptance Criteria**:
- [ ] Action difference penalty
- [ ] Encourages smooth motion
- [ ] Hardware-friendly

**Test Cases**:
```python
# TC-5.8.1: Smoothness
r_smooth = -torch.sum((self.actions - self.last_actions)**2, dim=1)
```

---

### Task 5.9: Create Reward Configuration
**Priority**: P1
**Chapter**: 5

**Description**: Make rewards configurable via YAML.

**Acceptance Criteria**:
- [ ] All weights in config
- [ ] Easy to tune
- [ ] Documentation complete

**Test Cases**:
```yaml
# TC-5.9.1: Reward config
rewards:
  velocity_tracking: 1.0
  alive: 0.5
  energy: -0.0001
  orientation: -0.5
  joint_limits: -1.0
  smoothness: -0.01
```

---

## Phase 6: PPO Training

### Task 6.1: Configure PPO Hyperparameters
**Priority**: P1
**Chapter**: 6

**Description**: Set optimal PPO parameters.

**Acceptance Criteria**:
- [ ] Learning rate: 3e-4
- [ ] Batch size: 4096
- [ ] Mini-batches: 4
- [ ] Epochs: 5
- [ ] Clip range: 0.2
- [ ] GAE lambda: 0.95

**Test Cases**:
```yaml
# TC-6.1.1: PPO config
algo:
  name: ppo
  lr: 3e-4
  clip_param: 0.2
  num_mini_batches: 4
  num_epochs: 5
```

---

### Task 6.2: Configure Network Architecture
**Priority**: P1
**Chapter**: 6

**Description**: Design actor-critic network.

**Acceptance Criteria**:
- [ ] MLP architecture: 256-256-256
- [ ] Activation: ELU
- [ ] Separate actor/critic or shared
- [ ] Proper initialization

**Test Cases**:
```yaml
# TC-6.2.1: Network config
network:
  mlp:
    units: [256, 256, 256]
    activation: elu
    initializer: default
```

---

### Task 6.3: Configure Value Function
**Priority**: P1
**Chapter**: 6

**Description**: Set up value function estimation.

**Acceptance Criteria**:
- [ ] Value loss coefficient
- [ ] Value clipping
- [ ] Returns normalization

**Test Cases**:
```yaml
# TC-6.3.1: Value config
value_loss_coef: 1.0
value_clip: 0.2
normalize_value: True
```

---

### Task 6.4: Configure Entropy Bonus
**Priority**: P1
**Chapter**: 6

**Description**: Set entropy for exploration.

**Acceptance Criteria**:
- [ ] Initial entropy coefficient
- [ ] Entropy decay schedule
- [ ] Prevents premature convergence

**Test Cases**:
```yaml
# TC-6.4.1: Entropy config
entropy_coef: 0.01
entropy_decay: 0.999
```

---

### Task 6.5: Set Up TensorBoard Logging
**Priority**: P1
**Chapter**: 6

**Description**: Configure training visualization.

**Acceptance Criteria**:
- [ ] Rewards logged
- [ ] Losses logged
- [ ] Episode lengths logged
- [ ] Policy stats logged

**Test Cases**:
```bash
# TC-6.5.1: TensorBoard
tensorboard --logdir runs/
# Expected: Training curves visible
```

---

### Task 6.6: Implement Training Loop
**Priority**: P1
**Chapter**: 6

**Description**: Create main training script.

**Acceptance Criteria**:
- [ ] Environment creation
- [ ] Agent initialization
- [ ] Training loop
- [ ] Checkpointing

**Test Cases**:
```bash
# TC-6.6.1: Training script
python train.py task=HumanoidCustom num_envs=1024 max_iterations=1000
# Expected: Training runs for 1000 iterations
```

---

### Task 6.7: Implement Checkpointing
**Priority**: P1
**Chapter**: 6

**Description**: Save and load training progress.

**Acceptance Criteria**:
- [ ] Save every N iterations
- [ ] Save on keyboard interrupt
- [ ] Load and resume training
- [ ] Save best model

**Test Cases**:
```bash
# TC-6.7.1: Checkpoint
python train.py task=HumanoidCustom checkpoint=runs/checkpoint_500.pth
# Expected: Resumes from checkpoint
```

---

### Task 6.8: Implement Evaluation Mode
**Priority**: P1
**Chapter**: 6

**Description**: Test trained policy without training.

**Acceptance Criteria**:
- [ ] Load checkpoint
- [ ] Run deterministic policy
- [ ] Visualize behavior
- [ ] Compute success metrics

**Test Cases**:
```bash
# TC-6.8.1: Play mode
python train.py task=HumanoidCustom test=True checkpoint=best.pth
# Expected: Robot walks in viewer
```

---

### Task 6.9: Train Initial Policy
**Priority**: P1
**Chapter**: 6

**Description**: Train first walking policy.

**Acceptance Criteria**:
- [ ] Training converges
- [ ] Reward increases
- [ ] Robot walks forward
- [ ] Training < 2 hours

**Test Cases**:
```bash
# TC-6.9.1: Full training
python train.py task=HumanoidCustom num_envs=4096 max_iterations=1000
# Expected: Mean reward > 50 after 1000 iterations
```

---

### Task 6.10: Analyze Training Results
**Priority**: P1
**Chapter**: 6

**Description**: Document training metrics and behavior.

**Acceptance Criteria**:
- [ ] Learning curves plotted
- [ ] Success rate computed
- [ ] Video recorded
- [ ] Analysis documented

**Test Cases**:
```
# TC-6.10.1: Analysis
# Document: final reward, success rate, training time
# Record: 30-second video of policy
```

---

## Phase 7: Domain Randomization

### Task 7.1: Implement Mass Randomization
**Priority**: P1
**Chapter**: 7

**Description**: Randomize link masses during training.

**Acceptance Criteria**:
- [ ] Mass varies ±20%
- [ ] Applied per-episode
- [ ] Configurable range
- [ ] Logged for analysis

**Test Cases**:
```python
# TC-7.1.1: Mass randomization
mass_scale = 1.0 + torch.rand(num_envs) * 0.4 - 0.2
self.body_mass = self.default_body_mass * mass_scale
```

---

### Task 7.2: Implement Friction Randomization
**Priority**: P1
**Chapter**: 7

**Description**: Randomize ground friction.

**Acceptance Criteria**:
- [ ] Friction varies 0.5-1.5
- [ ] Per-environment or global
- [ ] Applied to foot contacts

**Test Cases**:
```python
# TC-7.2.1: Friction randomization
friction = 0.5 + torch.rand(num_envs) * 1.0
```

---

### Task 7.3: Implement Observation Noise
**Priority**: P1
**Chapter**: 7

**Description**: Add noise to observations.

**Acceptance Criteria**:
- [ ] Gaussian noise added
- [ ] Noise scale configurable
- [ ] Applied during training only

**Test Cases**:
```python
# TC-7.3.1: Observation noise
noise = torch.randn_like(self.obs_buf) * self.obs_noise_scale
self.obs_buf += noise
```

---

### Task 7.4: Implement Action Delay
**Priority**: P1
**Chapter**: 7

**Description**: Simulate control latency.

**Acceptance Criteria**:
- [ ] 1-3 step delay
- [ ] Randomized per-episode
- [ ] Action buffer implemented

**Test Cases**:
```python
# TC-7.4.1: Action delay
self.action_delay = torch.randint(1, 4, (num_envs,))
delayed_actions = self.action_buffer[self.action_delay]
```

---

### Task 7.5: Implement Joint Property Randomization
**Priority**: P1
**Chapter**: 7

**Description**: Randomize joint damping and stiffness.

**Acceptance Criteria**:
- [ ] Damping varies ±30%
- [ ] Stiffness varies ±20%
- [ ] Per-joint randomization

**Test Cases**:
```python
# TC-7.5.1: Joint randomization
damping_scale = 1.0 + torch.rand(num_envs, num_dofs) * 0.6 - 0.3
self.dof_damping = self.default_dof_damping * damping_scale
```

---

### Task 7.6: Implement External Force Perturbation
**Priority**: P1
**Chapter**: 7

**Description**: Apply random pushes during training.

**Acceptance Criteria**:
- [ ] Random impulses applied
- [ ] Frequency configurable
- [ ] Force magnitude limited

**Test Cases**:
```python
# TC-7.6.1: Push perturbation
if torch.rand(1) < 0.01:  # 1% chance per step
    force = torch.randn(3) * 50  # 50N max
    self.gym.apply_rigid_body_force_at_pos(...)
```

---

### Task 7.7: Create DR Configuration
**Priority**: P1
**Chapter**: 7

**Description**: Make all DR parameters configurable.

**Acceptance Criteria**:
- [ ] All params in YAML
- [ ] Easy enable/disable
- [ ] Range specification
- [ ] Documentation

**Test Cases**:
```yaml
# TC-7.7.1: DR config
domain_randomization:
  enabled: True
  mass_range: [0.8, 1.2]
  friction_range: [0.5, 1.5]
  obs_noise: 0.05
  action_delay: [1, 3]
```

---

### Task 7.8: Train with Domain Randomization
**Priority**: P1
**Chapter**: 7

**Description**: Train policy with all DR enabled.

**Acceptance Criteria**:
- [ ] DR policy trained
- [ ] Comparable reward to baseline
- [ ] Improved robustness
- [ ] Documentation

**Test Cases**:
```bash
# TC-7.8.1: DR training
python train.py task=HumanoidCustom domain_rand=True
# Expected: Similar final reward, better test robustness
```

---

## Phase 8: Curriculum Learning

### Task 8.1: Design Terrain Curriculum
**Priority**: P2
**Chapter**: 8

**Description**: Create progressive terrain difficulty.

**Acceptance Criteria**:
- [ ] Level 0: Flat
- [ ] Level 1: Gentle slopes (5°)
- [ ] Level 2: Slopes (10°) + small steps
- [ ] Level 3: Rough terrain

**Test Cases**:
```python
# TC-8.1.1: Terrain levels
terrain_levels = [
    {"type": "flat"},
    {"type": "slope", "angle": 5},
    {"type": "slope", "angle": 10, "steps": True},
    {"type": "rough", "amplitude": 0.1},
]
```

---

### Task 8.2: Implement Level Tracking
**Priority**: P2
**Chapter**: 8

**Description**: Track each env's curriculum level.

**Acceptance Criteria**:
- [ ] Per-env level tracking
- [ ] Success rate computation
- [ ] Level statistics logged

**Test Cases**:
```python
# TC-8.2.1: Level tracking
self.terrain_levels = torch.zeros(num_envs, dtype=torch.long)
success_rate = (self.episode_success / self.episode_count).mean()
```

---

### Task 8.3: Implement Level Advancement
**Priority**: P2
**Chapter**: 8

**Description**: Advance envs to harder levels.

**Acceptance Criteria**:
- [ ] Advance on 80% success rate
- [ ] Demote on 20% success rate
- [ ] Smooth transitions

**Test Cases**:
```python
# TC-8.3.1: Level advancement
if success_rate[env_id] > 0.8 and level < max_level:
    level[env_id] += 1
elif success_rate[env_id] < 0.2 and level > 0:
    level[env_id] -= 1
```

---

### Task 8.4: Implement Command Curriculum
**Priority**: P2
**Chapter**: 8

**Description**: Progressively increase command ranges.

**Acceptance Criteria**:
- [ ] Start with slow walking
- [ ] Increase speed range
- [ ] Add turning commands
- [ ] Add lateral movement

**Test Cases**:
```python
# TC-8.4.1: Command curriculum
max_vel = 0.5 + 0.5 * curriculum_progress  # 0.5 to 1.0 m/s
self.commands[:, 0] = torch.rand(num_envs) * max_vel
```

---

### Task 8.5: Create Curriculum Configuration
**Priority**: P2
**Chapter**: 8

**Description**: Configure curriculum parameters.

**Acceptance Criteria**:
- [ ] All levels defined
- [ ] Advancement thresholds
- [ ] Progress tracking

**Test Cases**:
```yaml
# TC-8.5.1: Curriculum config
curriculum:
  enabled: True
  terrain_levels: 4
  advance_threshold: 0.8
  demote_threshold: 0.2
```

---

### Task 8.6: Train with Curriculum
**Priority**: P2
**Chapter**: 8

**Description**: Train using curriculum learning.

**Acceptance Criteria**:
- [ ] Curriculum progresses
- [ ] All levels reached
- [ ] Better final performance

**Test Cases**:
```bash
# TC-8.6.1: Curriculum training
python train.py task=HumanoidCustom curriculum=True
# Expected: Envs advance through levels
```

---

### Task 8.7: Evaluate on All Terrains
**Priority**: P2
**Chapter**: 8

**Description**: Test final policy on all terrain types.

**Acceptance Criteria**:
- [ ] Test on flat
- [ ] Test on slopes
- [ ] Test on rough terrain
- [ ] Document success rates

**Test Cases**:
```bash
# TC-8.7.1: Multi-terrain eval
# Test policy on each terrain level
# Document: success rate per level
```

---

## Phase 9: Policy Export

### Task 9.1: Export to ONNX
**Priority**: P1
**Chapter**: 9

**Description**: Export trained policy to ONNX format.

**Acceptance Criteria**:
- [ ] ONNX file created
- [ ] Input/output shapes correct
- [ ] Loads in ONNX Runtime
- [ ] Inference matches PyTorch

**Test Cases**:
```python
# TC-9.1.1: ONNX export
torch.onnx.export(
    model,
    dummy_input,
    "locomotion.onnx",
    input_names=["obs"],
    output_names=["actions"],
    dynamic_axes={"obs": {0: "batch"}, "actions": {0: "batch"}}
)
```

---

### Task 9.2: Export to TorchScript
**Priority**: P1
**Chapter**: 9

**Description**: Export policy as TorchScript.

**Acceptance Criteria**:
- [ ] JIT compiled
- [ ] Loads correctly
- [ ] Inference works
- [ ] GPU compatible

**Test Cases**:
```python
# TC-9.2.1: TorchScript export
scripted = torch.jit.script(model)
scripted.save("locomotion.pt")
```

---

### Task 9.3: Validate ONNX Model
**Priority**: P1
**Chapter**: 9

**Description**: Verify ONNX model correctness.

**Acceptance Criteria**:
- [ ] Model loads
- [ ] Inference runs
- [ ] Output matches PyTorch
- [ ] Performance acceptable

**Test Cases**:
```python
# TC-9.3.1: ONNX validation
import onnxruntime as ort
session = ort.InferenceSession("locomotion.onnx")
onnx_output = session.run(None, {"obs": obs.numpy()})
torch_output = model(obs).detach().numpy()
np.testing.assert_allclose(onnx_output, torch_output, rtol=1e-4)
```

---

### Task 9.4: Create Export Script
**Priority**: P1
**Chapter**: 9

**Description**: Automate model export process.

**Acceptance Criteria**:
- [ ] Loads checkpoint
- [ ] Exports both formats
- [ ] Validates output
- [ ] Creates metadata

**Test Cases**:
```bash
# TC-9.4.1: Export script
python export_policy.py --checkpoint best.pth --output models/
# Expected: locomotion.onnx and locomotion.pt created
```

---

### Task 9.5: Document Model Interface
**Priority**: P1
**Chapter**: 9

**Description**: Document input/output specification.

**Acceptance Criteria**:
- [ ] Input shape documented
- [ ] Output shape documented
- [ ] Normalization documented
- [ ] Scaling documented

**Test Cases**:
```yaml
# TC-9.5.1: Model spec
model_spec:
  input:
    name: obs
    shape: [batch, 48]
    dtype: float32
    normalization: running_mean_std
  output:
    name: actions
    shape: [batch, 14]
    dtype: float32
    scale: 1.0
```

---

### Task 9.6: Create Model Package
**Priority**: P1
**Chapter**: 9

**Description**: Package model with metadata.

**Acceptance Criteria**:
- [ ] ONNX model included
- [ ] Config included
- [ ] Normalization stats included
- [ ] Version info included

**Test Cases**:
```bash
# TC-9.6.1: Model package
ls models/
# Expected: locomotion.onnx, config.yaml, norm_stats.npz
```

---

### Task 9.7: Benchmark Inference Speed
**Priority**: P1
**Chapter**: 9

**Description**: Measure inference performance.

**Acceptance Criteria**:
- [ ] PyTorch latency measured
- [ ] ONNX latency measured
- [ ] GPU vs CPU compared
- [ ] Meets 100 Hz requirement

**Test Cases**:
```python
# TC-9.7.1: Benchmark
# Measure 1000 inferences
# Expected: < 5ms per inference on GPU
```

---

### Task 9.8: Test on Different Hardware
**Priority**: P2
**Chapter**: 9

**Description**: Verify model works on target platforms.

**Acceptance Criteria**:
- [ ] Works on training GPU
- [ ] Works on deployment GPU
- [ ] Works on CPU (slower OK)
- [ ] Consistent outputs

**Test Cases**:
```bash
# TC-9.8.1: Cross-platform test
# Run inference on RTX 3060, RTX 4080, CPU
# Expected: Same outputs within tolerance
```

---

## Phase 10: ROS 2 Deployment

### Task 10.1: Create Policy Node Package
**Priority**: P1
**Chapter**: 9

**Description**: Create ROS 2 package for policy inference.

**Acceptance Criteria**:
- [ ] Package created
- [ ] Dependencies specified
- [ ] Builds successfully

**Test Cases**:
```bash
# TC-10.1.1: Create package
cd ~/humanoid_isaac_ws/src
ros2 pkg create humanoid_policy --build-type ament_python
colcon build --packages-select humanoid_policy
```

---

### Task 10.2: Implement Policy Node
**Priority**: P1
**Chapter**: 9

**Description**: Create ROS 2 node for inference.

**Acceptance Criteria**:
- [ ] Subscribes to `/joint_states`
- [ ] Publishes to `/joint_commands`
- [ ] Runs at 100 Hz
- [ ] Loads ONNX model

**Test Cases**:
```python
# TC-10.2.1: Policy node
class PolicyNode(Node):
    def __init__(self):
        super().__init__('policy_node')
        self.sub = self.create_subscription(
            JointState, '/joint_states', self.state_callback, 10
        )
        self.pub = self.create_publisher(
            Float64MultiArray, '/joint_commands', 10
        )
        self.session = ort.InferenceSession("locomotion.onnx")
```

---

### Task 10.3: Implement Observation Builder
**Priority**: P1
**Chapter**: 9

**Description**: Build observation vector from ROS messages.

**Acceptance Criteria**:
- [ ] Joint positions extracted
- [ ] Joint velocities extracted
- [ ] Base state from TF or IMU
- [ ] Command from topic

**Test Cases**:
```python
# TC-10.3.1: Observation building
def build_observation(self, joint_state, imu, command):
    obs = np.zeros(48)
    obs[0:14] = joint_state.position
    obs[14:28] = joint_state.velocity
    # ... etc
    return obs
```

---

### Task 10.4: Implement Action Publisher
**Priority**: P1
**Chapter**: 9

**Description**: Publish actions to robot controller.

**Acceptance Criteria**:
- [ ] Actions scaled correctly
- [ ] Published at 100 Hz
- [ ] Timestamps correct
- [ ] Error handling

**Test Cases**:
```python
# TC-10.4.1: Action publishing
def publish_actions(self, actions):
    msg = Float64MultiArray()
    msg.data = actions.tolist()
    self.pub.publish(msg)
```

---

### Task 10.5: Add Command Interface
**Priority**: P1
**Chapter**: 9

**Description**: Subscribe to velocity commands.

**Acceptance Criteria**:
- [ ] Subscribe to `/cmd_vel`
- [ ] Extract vx, vy, yaw_rate
- [ ] Default to zero command
- [ ] Smooth command changes

**Test Cases**:
```python
# TC-10.5.1: Command interface
self.cmd_sub = self.create_subscription(
    Twist, '/cmd_vel', self.cmd_callback, 10
)
```

---

### Task 10.6: Add Safety Checks
**Priority**: P1
**Chapter**: 9

**Description**: Implement safety constraints.

**Acceptance Criteria**:
- [ ] Action clipping
- [ ] Velocity limits
- [ ] Watchdog timer
- [ ] Emergency stop

**Test Cases**:
```python
# TC-10.6.1: Safety checks
actions = np.clip(actions, -1.0, 1.0)
if time_since_last_obs > 0.1:
    actions = np.zeros(14)  # Safe state
```

---

### Task 10.7: Create Launch File
**Priority**: P1
**Chapter**: 9

**Description**: Create launch file for policy node.

**Acceptance Criteria**:
- [ ] Node launched
- [ ] Parameters loaded
- [ ] Model path configurable
- [ ] Logging configured

**Test Cases**:
```bash
# TC-10.7.1: Launch policy
ros2 launch humanoid_policy policy.launch.py model:=locomotion.onnx
# Expected: Node starts, subscribes to topics
```

---

### Task 10.8: Test with Simulated Data
**Priority**: P1
**Chapter**: 9

**Description**: Test node with fake joint states.

**Acceptance Criteria**:
- [ ] Responds to joint states
- [ ] Publishes actions
- [ ] No crashes
- [ ] Latency acceptable

**Test Cases**:
```bash
# TC-10.8.1: Test with fake data
ros2 run humanoid_policy policy_node &
ros2 topic pub /joint_states sensor_msgs/JointState "..." -r 100
ros2 topic hz /joint_commands
# Expected: 100 Hz output
```

---

### Task 10.9: Measure End-to-End Latency
**Priority**: P1
**Chapter**: 9

**Description**: Measure total inference latency.

**Acceptance Criteria**:
- [ ] Input-to-output latency < 10ms
- [ ] Consistent timing
- [ ] No dropped messages
- [ ] Documentation

**Test Cases**:
```python
# TC-10.9.1: Latency measurement
# Timestamp messages, compute difference
# Expected: < 10ms average latency
```

---

## Phase 11: Gazebo Integration

### Task 11.1: Create Gazebo Test World
**Priority**: P2
**Chapter**: 9

**Description**: Set up Gazebo for policy testing.

**Acceptance Criteria**:
- [ ] World from Module 2 used
- [ ] Robot spawned
- [ ] Physics matching Isaac

**Test Cases**:
```bash
# TC-11.1.1: Launch Gazebo
ros2 launch humanoid_gazebo humanoid_spawn.launch.py
# Expected: Robot in Gazebo world
```

---

### Task 11.2: Bridge Policy Commands
**Priority**: P2
**Chapter**: 9

**Description**: Connect policy node to Gazebo.

**Acceptance Criteria**:
- [ ] Joint commands bridged
- [ ] Joint states received
- [ ] Control loop closed

**Test Cases**:
```bash
# TC-11.2.1: Full loop
ros2 launch humanoid_policy gazebo_policy.launch.py
# Expected: Policy controls Gazebo robot
```

---

### Task 11.3: Test Standing Balance
**Priority**: P2
**Chapter**: 9

**Description**: Verify robot stands in Gazebo.

**Acceptance Criteria**:
- [ ] Robot maintains balance
- [ ] No falling over
- [ ] Stable for 60 seconds

**Test Cases**:
```bash
# TC-11.3.1: Standing test
# Run policy with zero command for 60s
# Expected: Robot remains standing
```

---

### Task 11.4: Test Walking Forward
**Priority**: P2
**Chapter**: 9

**Description**: Verify walking in Gazebo.

**Acceptance Criteria**:
- [ ] Robot walks forward
- [ ] Tracks velocity command
- [ ] Stable for 20 steps

**Test Cases**:
```bash
# TC-11.4.1: Walking test
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.5}}"
# Expected: Robot walks forward
```

---

### Task 11.5: Compare Isaac vs Gazebo Behavior
**Priority**: P2
**Chapter**: 9

**Description**: Document behavioral differences.

**Acceptance Criteria**:
- [ ] Same commands tested
- [ ] Differences documented
- [ ] Analysis provided

**Test Cases**:
```
# TC-11.5.1: Comparison
# Run same trajectory in both simulators
# Document: velocity tracking, stability differences
```

---

### Task 11.6: Tune for Gazebo
**Priority**: P2
**Chapter**: 9

**Description**: Adjust parameters for Gazebo compatibility.

**Acceptance Criteria**:
- [ ] Action scaling tuned
- [ ] Physics differences compensated
- [ ] Improved behavior

**Test Cases**:
```python
# TC-11.6.1: Tuning
# Adjust action_scale, add filtering
# Expected: Better Gazebo performance
```

---

### Task 11.7: Record Demonstration
**Priority**: P2
**Chapter**: 9

**Description**: Record video of policy in Gazebo.

**Acceptance Criteria**:
- [ ] Standing demo
- [ ] Walking demo
- [ ] Command following demo
- [ ] 30+ second videos

**Test Cases**:
```bash
# TC-11.7.1: Recording
# Record screen/rosbag for demos
# Expected: Clear demonstration videos
```

---

## Phase 12: Sim-to-Real Analysis

### Task 12.1: Identify Gap Sources
**Priority**: P2
**Chapter**: 10

**Description**: Document simulation-reality differences.

**Acceptance Criteria**:
- [ ] Actuator dynamics
- [ ] Sensor characteristics
- [ ] Contact modeling
- [ ] Latency

**Test Cases**:
```
# TC-12.1.1: Gap analysis
# Document each gap source
# Estimate impact (high/medium/low)
```

---

### Task 12.2: Document Mitigation Strategies
**Priority**: P2
**Chapter**: 10

**Description**: Describe how to reduce gap.

**Acceptance Criteria**:
- [ ] System identification
- [ ] Domain randomization benefits
- [ ] Action filtering
- [ ] Observation processing

**Test Cases**:
```
# TC-12.2.1: Mitigation doc
# For each gap source, describe mitigation
```

---

### Task 12.3: Create Deployment Checklist
**Priority**: P2
**Chapter**: 10

**Description**: Checklist for real robot deployment.

**Acceptance Criteria**:
- [ ] Hardware requirements
- [ ] Software setup
- [ ] Safety procedures
- [ ] Testing protocol

**Test Cases**:
```
# TC-12.3.1: Checklist
# [ ] Emergency stop tested
# [ ] Joint limits verified
# [ ] Slow motion test first
# ... etc
```

---

### Task 12.4: Estimate Transfer Success
**Priority**: P2
**Chapter**: 10

**Description**: Predict real-world performance.

**Acceptance Criteria**:
- [ ] Based on DR training
- [ ] Based on Gazebo testing
- [ ] Conservative estimates

**Test Cases**:
```
# TC-12.4.1: Estimation
# Expected success rate on real hardware: X%
# Confidence interval: ...
```

---

### Task 12.5: Document Required Hardware Modifications
**Priority**: P2
**Chapter**: 10

**Description**: List hardware needs for deployment.

**Acceptance Criteria**:
- [ ] Compute requirements
- [ ] Sensor requirements
- [ ] Safety hardware
- [ ] Communication

**Test Cases**:
```
# TC-12.5.1: Hardware doc
# Onboard compute: Jetson Orin or equivalent
# Sensors: IMU, joint encoders
# Safety: E-stop, current limiting
```

---

### Task 12.6: Create Gap Analysis Report
**Priority**: P2
**Chapter**: 10

**Description**: Complete sim-to-real documentation.

**Acceptance Criteria**:
- [ ] Executive summary
- [ ] Detailed analysis
- [ ] Recommendations
- [ ] Risk assessment

**Test Cases**:
```
# TC-12.6.1: Report
# Complete report document
# Review by team
```

---

## Phase 13: Documentation & Testing

### Task 13.1: Write Chapter Content
**Priority**: P1
**Chapter**: All

**Description**: Write all 10 chapter markdown files.

**Acceptance Criteria**:
- [ ] All chapters written
- [ ] Code examples included
- [ ] Diagrams created
- [ ] Exercises defined

**Test Cases**:
```bash
# TC-13.1.1: Chapter count
ls book/module-3/chapters/*.md | wc -l
# Expected: 10
```

---

### Task 13.2: Create Code Examples
**Priority**: P1
**Chapter**: All

**Description**: Create runnable code for all examples.

**Acceptance Criteria**:
- [ ] All code tested
- [ ] Comments included
- [ ] Style consistent

**Test Cases**:
```bash
# TC-13.2.1: Code runs
cd book/module-3/code
python test_all_examples.py
# Expected: All pass
```

---

### Task 13.3: Create Exercise Files
**Priority**: P1
**Chapter**: All

**Description**: Create hands-on exercises.

**Acceptance Criteria**:
- [ ] 5+ exercises
- [ ] Clear instructions
- [ ] Expected outputs
- [ ] Difficulty progression

**Test Cases**:
```bash
# TC-13.3.1: Exercise count
ls book/module-3/exercises/*.md | wc -l
# Expected: 5+
```

---

### Task 13.4: Test Full Pipeline
**Priority**: P1
**Chapter**: All

**Description**: End-to-end pipeline test.

**Acceptance Criteria**:
- [ ] Fresh environment
- [ ] Follow all instructions
- [ ] Complete successfully
- [ ] Document issues

**Test Cases**:
```bash
# TC-13.4.1: Pipeline test
# Start from clean install
# Follow Module 3 chapters
# Expected: Trained, deployed policy
```

---

### Task 13.5: Create README
**Priority**: P1
**Chapter**: N/A

**Description**: Module overview documentation.

**Acceptance Criteria**:
- [ ] Overview section
- [ ] Prerequisites
- [ ] Quick start
- [ ] Chapter links

**Test Cases**:
```bash
# TC-13.5.1: README exists
cat book/module-3/README.md
# Expected: Complete overview
```

---

### Task 13.6: Review and Edit
**Priority**: P1
**Chapter**: All

**Description**: Quality review of all content.

**Acceptance Criteria**:
- [ ] Technical accuracy
- [ ] Grammar/spelling
- [ ] Consistency
- [ ] Completeness

**Test Cases**:
```
# TC-13.6.1: Review
# All chapters reviewed
# Issues addressed
```

---

### Task 13.7: Create PHR
**Priority**: P1
**Chapter**: N/A

**Description**: Document implementation in PHR.

**Acceptance Criteria**:
- [ ] PHR created
- [ ] All files listed
- [ ] Outcomes documented

**Test Cases**:
```bash
# TC-13.7.1: PHR exists
ls history/prompts/constitution/*module3*.prompt.md
# Expected: PHR file
```

---

## Verification Checklist

### Phase Completion

- [ ] Phase 1: Environment Setup (8 tasks)
- [ ] Phase 2: Isaac Sim Configuration (9 tasks)
- [ ] Phase 3: Isaac Gym Setup (8 tasks)
- [ ] Phase 4: Training Environment (10 tasks)
- [ ] Phase 5: Reward System (9 tasks)
- [ ] Phase 6: PPO Training (10 tasks)
- [ ] Phase 7: Domain Randomization (8 tasks)
- [ ] Phase 8: Curriculum Learning (7 tasks)
- [ ] Phase 9: Policy Export (8 tasks)
- [ ] Phase 10: ROS 2 Deployment (9 tasks)
- [ ] Phase 11: Gazebo Integration (7 tasks)
- [ ] Phase 12: Sim-to-Real Analysis (6 tasks)
- [ ] Phase 13: Documentation & Testing (7 tasks)

### Final Deliverables

- [ ] Isaac Sim environment configured
- [ ] Training environment (1024+ envs)
- [ ] Trained locomotion policy
- [ ] Domain randomized training
- [ ] Exported ONNX model
- [ ] ROS 2 policy node
- [ ] Gazebo deployment working
- [ ] Complete documentation
- [ ] All chapters written
- [ ] All exercises created

---

**Governed by**: `specs/constitution.md` v1.0.0
