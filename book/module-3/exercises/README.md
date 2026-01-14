# Module 3 Exercises

This directory contains hands-on exercises for Module 3: AI-Robot Brain with NVIDIA Isaac.

## Exercise Overview

| Exercise | Chapter | Topic | Duration |
|----------|---------|-------|----------|
| 3.1 | Ch 1 | Isaac Sim Installation | 1-2 hours |
| 3.2 | Ch 2 | URDF to USD Conversion | 1-2 hours |
| 3.3 | Ch 3 | Vectorized Environment | 2-3 hours |
| 3.4 | Ch 4 | Training Environment | 2-3 hours |
| 3.5 | Ch 5 | Reward Tuning | 2-3 hours |
| 3.6 | Ch 6 | PPO Training | 3-4 hours |
| 3.7 | Ch 7 | Domain Randomization | 2-3 hours |
| 3.8 | Ch 8 | Curriculum Learning | 2-3 hours |
| 3.9 | Ch 9 | Policy Deployment | 2-3 hours |
| 3.10 | Ch 10 | Transfer Evaluation | 2-3 hours |

---

## Exercise 3.1: Isaac Sim Installation

**Objective**: Install and verify NVIDIA Isaac Sim

### Tasks

1. Install Omniverse Launcher
2. Install Isaac Sim 2023.1+
3. Verify GPU compatibility
4. Launch Isaac Sim
5. Load sample humanoid scene

### Verification

```bash
# Check GPU
nvidia-smi

# Verify Isaac Sim installation
~/.local/share/ov/pkg/isaac_sim-2023.1.1/isaac-sim.sh
```

### Deliverables

- [ ] Screenshot of Isaac Sim running
- [ ] GPU information output
- [ ] Sample scene loaded

---

## Exercise 3.2: URDF to USD Conversion

**Objective**: Convert humanoid URDF to USD format

### Tasks

1. Load humanoid URDF from Module 1
2. Configure import settings
3. Convert to USD
4. Verify joint structure
5. Save configured USD

### Code Template

```python
from omni.isaac.urdf import _urdf

# Configure importer
import_config = _urdf.ImportConfig()
import_config.fix_base = False
import_config.default_drive_type = _urdf.UrdfJointTargetType.JOINT_DRIVE_NONE

# Import
urdf_interface = _urdf.acquire_urdf_interface()
urdf_interface.import_robot(
    "humanoid.urdf",
    "/World/Humanoid",
    import_config,
    ""
)
```

### Deliverables

- [ ] `humanoid.usd` file
- [ ] Screenshot of USD in Isaac Sim
- [ ] Joint verification report

---

## Exercise 3.3: Vectorized Environment

**Objective**: Create Isaac Gym vectorized environment

### Tasks

1. Set up Isaac Gym with PhysX
2. Load humanoid asset
3. Create 64 parallel environments
4. Acquire GPU tensors
5. Verify tensor shapes

### Expected Output

```
Environments: 64
DOFs: 14
Bodies: 15
root_states shape: (64, 13)
dof_states shape: (64, 14, 2)
```

### Deliverables

- [ ] Working environment code
- [ ] Tensor shape verification
- [ ] Screenshot of parallel environments

---

## Exercise 3.4: Training Environment

**Objective**: Implement complete HumanoidTask class

### Tasks

1. Define observation space (48D)
2. Define action space (14D)
3. Implement step function
4. Add reset logic
5. Test with random actions

### Observation Components

| Component | Dimension |
|-----------|-----------|
| Base lin vel | 3 |
| Base ang vel | 3 |
| Gravity proj | 3 |
| DOF positions | 14 |
| DOF velocities | 14 |
| Commands | 3 |
| Last actions | 14 |

### Deliverables

- [ ] `humanoid_task.py` implementation
- [ ] Test results with random actions
- [ ] Episode statistics

---

## Exercise 3.5: Reward Tuning

**Objective**: Design and tune reward function

### Tasks

1. Implement velocity tracking reward
2. Add alive bonus
3. Add energy penalty
4. Implement orientation penalty
5. Tune weights for stable walking

### Reward Structure

```python
reward = (
    velocity_reward * 2.0 +
    alive_reward * 1.0 +
    energy_penalty * -0.0005 +
    orientation_penalty * -0.5
)
```

### Experiments

| Experiment | velocity | alive | energy | orientation |
|------------|----------|-------|--------|-------------|
| Baseline | 2.0 | 1.0 | -0.0005 | -0.5 |
| High vel | 4.0 | 1.0 | -0.0005 | -0.5 |
| Low energy | 2.0 | 1.0 | -0.001 | -0.5 |

### Deliverables

- [ ] Reward implementation
- [ ] Tuning experiment results
- [ ] Optimal weight configuration

---

## Exercise 3.6: PPO Training

**Objective**: Train locomotion policy with PPO

### Tasks

1. Implement ActorCritic network
2. Configure PPO hyperparameters
3. Train for 5000 iterations
4. Monitor with TensorBoard
5. Evaluate final policy

### Hyperparameters

```python
learning_rate = 3e-4
clip_range = 0.2
num_epochs = 5
minibatch_size = 4096
gamma = 0.99
gae_lambda = 0.95
```

### Training Command

```bash
python train_humanoid.py --num_envs 4096 --max_iterations 5000
tensorboard --logdir runs/
```

### Deliverables

- [ ] Training script
- [ ] TensorBoard screenshots
- [ ] Final policy checkpoint
- [ ] Training curve analysis

---

## Exercise 3.7: Domain Randomization

**Objective**: Implement domain randomization

### Tasks

1. Add mass randomization (±20%)
2. Add friction randomization (0.5-1.5)
3. Add observation noise
4. Add action delay (0-2 steps)
5. Compare with baseline

### Randomization Config

```python
mass_range = 0.2
friction_range = (0.5, 1.5)
obs_noise = 0.1
action_delay_steps = 2
```

### Comparison

| Metric | No DR | With DR |
|--------|-------|---------|
| Training reward | | |
| Success rate | | |
| Robustness | | |

### Deliverables

- [ ] Domain randomization implementation
- [ ] Comparison results
- [ ] Robustness evaluation

---

## Exercise 3.8: Curriculum Learning

**Objective**: Implement terrain curriculum

### Tasks

1. Create flat terrain (Level 0)
2. Create slope terrain (Level 1-2)
3. Create rough terrain (Level 3-4)
4. Implement level advancement
5. Train with curriculum

### Curriculum Levels

| Level | Terrain | Threshold |
|-------|---------|-----------|
| 0 | Flat | 50 |
| 1 | Slope 5° | 75 |
| 2 | Slope 10° | 100 |
| 3 | Rough low | 125 |
| 4 | Rough high | 150 |

### Deliverables

- [ ] Terrain generation code
- [ ] Curriculum manager
- [ ] Level progression logs

---

## Exercise 3.9: Policy Deployment

**Objective**: Export and deploy policy to ROS 2

### Tasks

1. Export policy to ONNX
2. Create ROS 2 policy node
3. Test in Gazebo
4. Measure inference latency
5. Verify action bounds

### Export Command

```python
torch.onnx.export(model, dummy_input, "policy.onnx")
```

### ROS 2 Launch

```bash
ros2 launch humanoid_policy policy.launch.py
```

### Deliverables

- [ ] ONNX model file
- [ ] ROS 2 node implementation
- [ ] Gazebo test video
- [ ] Latency benchmark

---

## Exercise 3.10: Transfer Evaluation

**Objective**: Evaluate sim-to-real transfer

### Tasks

1. Run gap analysis
2. Measure tracking performance
3. Evaluate stability
4. Compute energy efficiency
5. Generate transfer report

### Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Tracking RMSE | < 0.3 m/s | |
| Success rate | > 90% | |
| CoT | < 5.0 | |

### Deliverables

- [ ] Gap analysis report
- [ ] Transfer metrics
- [ ] Deployment checklist
- [ ] Recommendations

---

## Submission Guidelines

1. Create separate directory for each exercise
2. Include all code files
3. Add README with results
4. Include screenshots/videos
5. Document any issues encountered

## Grading Criteria

| Criterion | Points |
|-----------|--------|
| Code completeness | 30 |
| Correct implementation | 30 |
| Results quality | 20 |
| Documentation | 20 |

Total: 100 points per exercise
