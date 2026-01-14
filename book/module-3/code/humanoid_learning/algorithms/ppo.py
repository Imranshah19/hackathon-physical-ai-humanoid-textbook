#!/usr/bin/env python3
"""
Proximal Policy Optimization (PPO) Algorithm.

This module provides the PPO training algorithm for
reinforcement learning with actor-critic networks.
"""

import torch
import torch.nn as nn
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class PPOConfig:
    """PPO training configuration."""

    # Environment
    num_envs: int = 4096
    num_steps_per_env: int = 24

    # Training
    max_iterations: int = 10000
    learning_rate: float = 3e-4

    # PPO specific
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_range: float = 0.2
    clip_value: bool = True
    num_epochs: int = 5
    minibatch_size: int = 4096

    # Loss coefficients
    value_coef: float = 1.0
    entropy_coef: float = 0.01

    # Optimization
    max_grad_norm: float = 1.0

    # Network
    hidden_dims: list = field(default_factory=lambda: [256, 256, 256])
    activation: str = "elu"
    init_noise_std: float = 1.0

    # Logging
    log_interval: int = 10
    save_interval: int = 500


class RolloutBuffer:
    """
    Buffer for storing rollout data.

    Stores transitions (obs, action, reward, done, value, log_prob)
    and computes returns and advantages using GAE.
    """

    def __init__(
        self,
        num_envs: int,
        num_steps: int,
        obs_dim: int,
        action_dim: int,
        device: str = "cuda",
    ):
        self.num_envs = num_envs
        self.num_steps = num_steps
        self.device = device

        # Storage tensors
        self.observations = torch.zeros(
            num_steps, num_envs, obs_dim, device=device
        )
        self.actions = torch.zeros(
            num_steps, num_envs, action_dim, device=device
        )
        self.rewards = torch.zeros(num_steps, num_envs, device=device)
        self.dones = torch.zeros(num_steps, num_envs, device=device)
        self.values = torch.zeros(num_steps, num_envs, device=device)
        self.log_probs = torch.zeros(num_steps, num_envs, device=device)

        # Computed values
        self.advantages = torch.zeros(num_steps, num_envs, device=device)
        self.returns = torch.zeros(num_steps, num_envs, device=device)

        self.step = 0

    def add(self, obs, action, reward, done, value, log_prob):
        """Add transition to buffer."""
        self.observations[self.step] = obs
        self.actions[self.step] = action
        self.rewards[self.step] = reward
        self.dones[self.step] = done
        self.values[self.step] = value
        self.log_probs[self.step] = log_prob
        self.step += 1

    def compute_returns_and_advantages(
        self,
        last_values: torch.Tensor,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
    ):
        """
        Compute returns and GAE advantages.

        Args:
            last_values: Value estimates for last state
            gamma: Discount factor
            gae_lambda: GAE lambda parameter
        """
        last_gae = 0

        for t in reversed(range(self.num_steps)):
            if t == self.num_steps - 1:
                next_values = last_values
            else:
                next_values = self.values[t + 1]

            next_non_terminal = 1.0 - self.dones[t]

            # TD error
            delta = (
                self.rewards[t]
                + gamma * next_values * next_non_terminal
                - self.values[t]
            )

            # GAE
            last_gae = delta + gamma * gae_lambda * next_non_terminal * last_gae
            self.advantages[t] = last_gae

        # Returns = advantages + values
        self.returns = self.advantages + self.values

    def get_minibatch_generator(self, minibatch_size: int):
        """
        Generate minibatches for training.

        Yields:
            Tuple of (obs, actions, log_probs, advantages, returns)
        """
        total_size = self.num_steps * self.num_envs
        indices = torch.randperm(total_size, device=self.device)

        # Flatten tensors
        obs_flat = self.observations.view(-1, self.observations.shape[-1])
        actions_flat = self.actions.view(-1, self.actions.shape[-1])
        log_probs_flat = self.log_probs.view(-1)
        advantages_flat = self.advantages.view(-1)
        returns_flat = self.returns.view(-1)

        for start in range(0, total_size, minibatch_size):
            end = start + minibatch_size
            batch_indices = indices[start:end]

            yield (
                obs_flat[batch_indices],
                actions_flat[batch_indices],
                log_probs_flat[batch_indices],
                advantages_flat[batch_indices],
                returns_flat[batch_indices],
            )

    def reset(self):
        """Reset buffer for next rollout."""
        self.step = 0


class PPOTrainer:
    """
    PPO training algorithm.

    Implements the clipped PPO objective with GAE
    advantage estimation.
    """

    def __init__(
        self,
        env,
        network: nn.Module,
        cfg: PPOConfig,
    ):
        self.env = env
        self.network = network
        self.cfg = cfg
        self.device = env.device

        # Optimizer
        self.optimizer = torch.optim.Adam(
            network.parameters(),
            lr=cfg.learning_rate,
            eps=1e-5,
        )

        # Rollout buffer
        self.buffer = RolloutBuffer(
            num_envs=env.num_envs,
            num_steps=cfg.num_steps_per_env,
            obs_dim=env.num_obs,
            action_dim=env.num_actions,
            device=self.device,
        )

        # Tracking
        self.iteration = 0
        self.total_timesteps = 0

    def collect_rollouts(self):
        """Collect rollout data from environment."""
        self.buffer.reset()
        obs = self.env.obs_buf

        for step in range(self.cfg.num_steps_per_env):
            # Get action from policy
            with torch.no_grad():
                actions, log_probs, values = self.network(obs)

            # Step environment
            next_obs, rewards, dones, info = self.env.step(actions)

            # Store transition
            self.buffer.add(
                obs=obs,
                action=actions,
                reward=rewards,
                done=dones.float(),
                value=values,
                log_prob=log_probs,
            )

            obs = next_obs

        # Compute final value for bootstrapping
        with torch.no_grad():
            _, _, last_values = self.network(obs)

        # Compute advantages
        self.buffer.compute_returns_and_advantages(
            last_values,
            gamma=self.cfg.gamma,
            gae_lambda=self.cfg.gae_lambda,
        )

        self.total_timesteps += self.cfg.num_steps_per_env * self.env.num_envs

    def update(self) -> Dict[str, float]:
        """
        Perform PPO update.

        Returns:
            Dictionary of training metrics
        """
        # Normalize advantages
        advantages = self.buffer.advantages.view(-1)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        self.buffer.advantages = advantages.view(
            self.cfg.num_steps_per_env, self.env.num_envs
        )

        # Training metrics
        total_loss = 0
        total_policy_loss = 0
        total_value_loss = 0
        total_entropy = 0
        num_updates = 0

        # Multiple epochs over collected data
        for epoch in range(self.cfg.num_epochs):
            for batch in self.buffer.get_minibatch_generator(
                self.cfg.minibatch_size
            ):
                obs, actions, old_log_probs, advantages, returns = batch

                # Evaluate actions with current policy
                new_log_probs, values, entropy = self.network.evaluate(
                    obs, actions
                )

                # Policy loss (clipped)
                ratio = torch.exp(new_log_probs - old_log_probs)
                surr1 = ratio * advantages
                surr2 = (
                    torch.clamp(
                        ratio, 1 - self.cfg.clip_range, 1 + self.cfg.clip_range
                    )
                    * advantages
                )
                policy_loss = -torch.min(surr1, surr2).mean()

                # Value loss
                value_loss = 0.5 * ((values - returns) ** 2).mean()

                # Entropy bonus
                entropy_loss = -entropy.mean()

                # Total loss
                loss = (
                    policy_loss
                    + self.cfg.value_coef * value_loss
                    + self.cfg.entropy_coef * entropy_loss
                )

                # Update
                self.optimizer.zero_grad()
                loss.backward()

                # Gradient clipping
                if self.cfg.max_grad_norm > 0:
                    torch.nn.utils.clip_grad_norm_(
                        self.network.parameters(), self.cfg.max_grad_norm
                    )

                self.optimizer.step()

                # Track metrics
                total_loss += loss.item()
                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += entropy.mean().item()
                num_updates += 1

        self.iteration += 1

        return {
            "loss": total_loss / num_updates,
            "policy_loss": total_policy_loss / num_updates,
            "value_loss": total_value_loss / num_updates,
            "entropy": total_entropy / num_updates,
        }

    def train(self, max_iterations: int, callback=None):
        """
        Main training loop.

        Args:
            max_iterations: Number of training iterations
            callback: Optional callback function called each iteration
        """
        self.env.reset()

        for iteration in range(max_iterations):
            # Collect rollouts
            self.collect_rollouts()

            # Update policy
            metrics = self.update()

            # Callback
            if callback is not None:
                callback(iteration, metrics, self)

            # Logging
            if iteration % self.cfg.log_interval == 0:
                mean_reward = self.buffer.rewards.mean().item()
                print(
                    f"[{iteration:5d}] "
                    f"reward={mean_reward:7.3f}, "
                    f"loss={metrics['loss']:.4f}, "
                    f"entropy={metrics['entropy']:.3f}"
                )

    def save_checkpoint(self, path: str):
        """Save training checkpoint."""
        torch.save(
            {
                "iteration": self.iteration,
                "total_timesteps": self.total_timesteps,
                "network_state": self.network.state_dict(),
                "optimizer_state": self.optimizer.state_dict(),
            },
            path,
        )

    def load_checkpoint(self, path: str):
        """Load training checkpoint."""
        checkpoint = torch.load(path)
        self.iteration = checkpoint["iteration"]
        self.total_timesteps = checkpoint["total_timesteps"]
        self.network.load_state_dict(checkpoint["network_state"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state"])
