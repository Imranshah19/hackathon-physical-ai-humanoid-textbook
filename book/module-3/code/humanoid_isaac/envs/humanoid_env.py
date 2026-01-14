#!/usr/bin/env python3
"""
Humanoid Training Environment for Isaac Gym.

This module provides a vectorized humanoid locomotion environment
for reinforcement learning training.
"""

from isaacgym import gymapi, gymtorch
import torch
import numpy as np
from typing import Dict, Tuple, Optional


class HumanoidEnv:
    """
    Vectorized humanoid locomotion environment.

    Attributes:
        num_envs: Number of parallel environments
        num_obs: Observation dimension (48)
        num_actions: Action dimension (14)
        device: Compute device (cuda/cpu)
    """

    def __init__(
        self,
        num_envs: int = 4096,
        device: str = "cuda:0",
        headless: bool = True,
        cfg: Optional[dict] = None,
    ):
        """
        Initialize humanoid environment.

        Args:
            num_envs: Number of parallel environments
            device: Compute device
            headless: Run without visualization
            cfg: Configuration dictionary
        """
        self.num_envs = num_envs
        self.device = device
        self.headless = headless
        self.cfg = cfg or self._default_config()

        # Environment dimensions
        self.num_obs = 48
        self.num_actions = 14

        # Initialize Isaac Gym
        self.gym = gymapi.acquire_gym()
        self.sim = self._create_sim()

        # Create environments
        self._create_envs()

        # Prepare tensors
        self.gym.prepare_sim(self.sim)
        self._init_buffers()

        # Create viewer if not headless
        self.viewer = None
        if not headless:
            self._create_viewer()

    def _default_config(self) -> dict:
        """Get default configuration."""
        return {
            "dt": 1.0 / 120.0,
            "substeps": 2,
            "env_spacing": 2.5,
            "episode_length": 1000,
            "friction": 1.0,
            "action_scale": 0.5,
            "obs_scales": {
                "lin_vel": 2.0,
                "ang_vel": 0.25,
                "dof_pos": 1.0,
                "dof_vel": 0.05,
            },
        }

    def _create_sim(self):
        """Create Isaac Gym simulation."""
        sim_params = gymapi.SimParams()
        sim_params.dt = self.cfg["dt"]
        sim_params.substeps = self.cfg["substeps"]
        sim_params.up_axis = gymapi.UP_AXIS_Z
        sim_params.gravity = gymapi.Vec3(0.0, 0.0, -9.81)

        # PhysX GPU settings
        sim_params.physx.use_gpu = True
        sim_params.physx.solver_type = 1
        sim_params.physx.num_position_iterations = 4
        sim_params.physx.num_velocity_iterations = 1
        sim_params.physx.contact_offset = 0.02
        sim_params.physx.rest_offset = 0.001
        sim_params.physx.bounce_threshold_velocity = 0.2

        return self.gym.create_sim(0, 0, gymapi.SIM_PHYSX, sim_params)

    def _create_envs(self):
        """Create parallel environments."""
        # Ground plane
        plane_params = gymapi.PlaneParams()
        plane_params.normal = gymapi.Vec3(0, 0, 1)
        plane_params.static_friction = self.cfg["friction"]
        plane_params.dynamic_friction = self.cfg["friction"]
        plane_params.restitution = 0.0
        self.gym.add_ground(self.sim, plane_params)

        # Load humanoid asset
        asset_options = gymapi.AssetOptions()
        asset_options.fix_base_link = False
        asset_options.default_dof_drive_mode = gymapi.DOF_MODE_EFFORT
        asset_options.angular_damping = 0.01

        self.humanoid_asset = self.gym.load_asset(
            self.sim, "assets/", "humanoid.urdf", asset_options
        )

        self.num_dof = self.gym.get_asset_dof_count(self.humanoid_asset)
        self.num_bodies = self.gym.get_asset_rigid_body_count(self.humanoid_asset)

        # Environment bounds
        spacing = self.cfg["env_spacing"]
        lower = gymapi.Vec3(-spacing, -spacing, 0)
        upper = gymapi.Vec3(spacing, spacing, spacing)

        # Create environments
        self.envs = []
        self.actors = []
        envs_per_row = int(np.sqrt(self.num_envs))

        for i in range(self.num_envs):
            env = self.gym.create_env(self.sim, lower, upper, envs_per_row)

            pose = gymapi.Transform()
            pose.p = gymapi.Vec3(0, 0, 1.0)
            pose.r = gymapi.Quat(0, 0, 0, 1)

            actor = self.gym.create_actor(
                env, self.humanoid_asset, pose, f"humanoid_{i}", i, 1
            )

            # Configure DOF properties
            dof_props = self.gym.get_actor_dof_properties(env, actor)
            dof_props['driveMode'].fill(gymapi.DOF_MODE_EFFORT)
            dof_props['stiffness'].fill(0.0)
            dof_props['damping'].fill(0.5)
            self.gym.set_actor_dof_properties(env, actor, dof_props)

            self.envs.append(env)
            self.actors.append(actor)

    def _init_buffers(self):
        """Initialize tensor buffers."""
        # Acquire state tensors
        _root = self.gym.acquire_actor_root_state_tensor(self.sim)
        _dof = self.gym.acquire_dof_state_tensor(self.sim)
        _contact = self.gym.acquire_net_contact_force_tensor(self.sim)

        # Wrap as PyTorch tensors
        self.root_states = gymtorch.wrap_tensor(_root)
        self.dof_states = gymtorch.wrap_tensor(_dof).view(
            self.num_envs, self.num_dof, 2
        )
        self.contact_forces = gymtorch.wrap_tensor(_contact).view(
            self.num_envs, self.num_bodies, 3
        )

        # Separate position and velocity views
        self.dof_pos = self.dof_states[:, :, 0]
        self.dof_vel = self.dof_states[:, :, 1]

        # Base state
        self.base_pos = self.root_states[:, 0:3]
        self.base_quat = self.root_states[:, 3:7]
        self.base_lin_vel = self.root_states[:, 7:10]
        self.base_ang_vel = self.root_states[:, 10:13]

        # Initial states for reset
        self.initial_root_states = self.root_states.clone()
        self.default_dof_pos = torch.zeros(self.num_dof, device=self.device)

        # Commands (vx, vy, yaw_rate)
        self.commands = torch.zeros(self.num_envs, 3, device=self.device)

        # Action buffers
        self.actions = torch.zeros(
            self.num_envs, self.num_actions, device=self.device
        )
        self.last_actions = torch.zeros_like(self.actions)

        # Torque limits
        self.torque_limits = torch.ones(self.num_actions, device=self.device) * 100.0

        # Episode tracking
        self.episode_length = torch.zeros(self.num_envs, device=self.device)
        self.max_episode_length = self.cfg["episode_length"]

        # Reset and done buffers
        self.reset_buf = torch.zeros(
            self.num_envs, dtype=torch.bool, device=self.device
        )
        self.timeout_buf = torch.zeros_like(self.reset_buf)

        # Reward and observation buffers
        self.rew_buf = torch.zeros(self.num_envs, device=self.device)
        self.obs_buf = torch.zeros(
            self.num_envs, self.num_obs, device=self.device
        )

    def reset(self) -> torch.Tensor:
        """Reset all environments."""
        all_ids = torch.arange(self.num_envs, device=self.device)
        self._reset_envs(all_ids)
        return self.obs_buf

    def _reset_envs(self, env_ids: torch.Tensor):
        """Reset specified environments."""
        if len(env_ids) == 0:
            return

        # Reset root states
        self.root_states[env_ids] = self.initial_root_states[env_ids]
        self.root_states[env_ids, 0:2] += torch.randn(
            len(env_ids), 2, device=self.device
        ) * 0.1

        # Reset DOF states
        self.dof_pos[env_ids] = self.default_dof_pos
        self.dof_vel[env_ids] = 0.0

        # Apply reset
        env_ids_int32 = env_ids.to(torch.int32)
        self.gym.set_actor_root_state_tensor_indexed(
            self.sim,
            gymtorch.unwrap_tensor(self.root_states),
            gymtorch.unwrap_tensor(env_ids_int32),
            len(env_ids)
        )
        self.gym.set_dof_state_tensor_indexed(
            self.sim,
            gymtorch.unwrap_tensor(self.dof_states.view(-1, 2)),
            gymtorch.unwrap_tensor(env_ids_int32),
            len(env_ids)
        )

        # Reset episode tracking
        self.episode_length[env_ids] = 0
        self.actions[env_ids] = 0
        self.last_actions[env_ids] = 0

        # Randomize commands
        self._resample_commands(env_ids)

        # Compute initial observations
        self._compute_observations()

    def _resample_commands(self, env_ids: torch.Tensor):
        """Sample new velocity commands."""
        n = len(env_ids)
        self.commands[env_ids, 0] = torch.rand(n, device=self.device) * 2.0 - 0.5
        self.commands[env_ids, 1] = torch.rand(n, device=self.device) * 0.6 - 0.3
        self.commands[env_ids, 2] = torch.rand(n, device=self.device) * 0.5 - 0.25

    def step(
        self, actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Dict]:
        """
        Execute one environment step.

        Args:
            actions: (N, num_actions) in [-1, 1]

        Returns:
            obs: (N, num_obs) observations
            rewards: (N,) rewards
            dones: (N,) done flags
            info: dict with additional info
        """
        # Store actions
        self.last_actions = self.actions.clone()
        self.actions = torch.clamp(actions, -1.0, 1.0)

        # Scale to torques
        torques = self.actions * self.cfg["action_scale"] * self.torque_limits

        # Apply torques
        self.gym.set_dof_actuation_force_tensor(
            self.sim, gymtorch.unwrap_tensor(torques.flatten())
        )

        # Step simulation
        self.gym.simulate(self.sim)
        self.gym.fetch_results(self.sim, True)

        # Refresh tensors
        self.gym.refresh_actor_root_state_tensor(self.sim)
        self.gym.refresh_dof_state_tensor(self.sim)
        self.gym.refresh_net_contact_force_tensor(self.sim)

        # Update episode length
        self.episode_length += 1

        # Compute observations, rewards, termination
        self._compute_observations()
        self._compute_rewards()
        self._check_termination()

        # Reset terminated environments
        reset_ids = self.reset_buf.nonzero(as_tuple=False).squeeze(-1)
        if len(reset_ids) > 0:
            self._reset_envs(reset_ids)

        # Render
        if self.viewer is not None:
            self.gym.step_graphics(self.sim)
            self.gym.draw_viewer(self.viewer, self.sim, True)

        info = {"episode_length": self.episode_length.clone()}
        return self.obs_buf, self.rew_buf, self.reset_buf, info

    def _compute_observations(self):
        """Compute observation vector."""
        scales = self.cfg["obs_scales"]

        # Base velocities in local frame
        base_lin_vel_local = quat_rotate_inverse(
            self.base_quat, self.base_lin_vel
        ) * scales["lin_vel"]

        base_ang_vel_local = quat_rotate_inverse(
            self.base_quat, self.base_ang_vel
        ) * scales["ang_vel"]

        # Gravity projection
        gravity = torch.tensor([0., 0., -1.], device=self.device)
        projected_gravity = quat_rotate_inverse(
            self.base_quat, gravity.expand(self.num_envs, -1)
        )

        # Scaled DOF state
        dof_pos_scaled = (self.dof_pos - self.default_dof_pos) * scales["dof_pos"]
        dof_vel_scaled = self.dof_vel * scales["dof_vel"]

        # Build observation
        self.obs_buf = torch.cat([
            base_lin_vel_local,
            base_ang_vel_local,
            projected_gravity,
            dof_pos_scaled,
            dof_vel_scaled,
            self.commands,
            self.last_actions,
        ], dim=-1)

        self.obs_buf = torch.clip(self.obs_buf, -100.0, 100.0)

    def _compute_rewards(self):
        """Compute reward components."""
        # Velocity tracking
        lin_vel_error = torch.sum(
            torch.square(self.commands[:, :2] - self.base_lin_vel[:, :2]),
            dim=-1
        )
        vel_reward = torch.exp(-lin_vel_error / 0.25) * 2.0

        # Alive bonus
        alive_reward = torch.ones(self.num_envs, device=self.device)

        # Energy penalty
        energy_penalty = torch.sum(torch.square(self.actions), dim=-1) * 0.0005

        # Total reward
        self.rew_buf = vel_reward + alive_reward - energy_penalty

    def _check_termination(self):
        """Check termination conditions."""
        base_height = self.base_pos[:, 2]
        fallen = base_height < 0.3
        tilted = torch.abs(self.base_quat[:, 3]) < 0.5
        self.timeout_buf = self.episode_length >= self.max_episode_length
        self.reset_buf = fallen | tilted | self.timeout_buf

    def _create_viewer(self):
        """Create visualization viewer."""
        cam_props = gymapi.CameraProperties()
        cam_props.width = 1280
        cam_props.height = 720
        self.viewer = self.gym.create_viewer(self.sim, cam_props)

    def close(self):
        """Cleanup resources."""
        if self.viewer is not None:
            self.gym.destroy_viewer(self.viewer)
        self.gym.destroy_sim(self.sim)


@torch.jit.script
def quat_rotate_inverse(q: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """Rotate vector by inverse quaternion."""
    q_w = q[:, 3:4]
    q_vec = q[:, 0:3]
    a = v * (2.0 * q_w ** 2 - 1.0)
    b = torch.cross(q_vec, v, dim=-1) * q_w * 2.0
    c = q_vec * torch.sum(q_vec * v, dim=-1, keepdim=True) * 2.0
    return a - b + c
