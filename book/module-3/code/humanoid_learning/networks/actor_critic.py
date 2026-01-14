#!/usr/bin/env python3
"""
Actor-Critic Network for PPO Training.

This module provides neural network architectures for policy
and value function approximation.
"""

import torch
import torch.nn as nn
import numpy as np
from torch.distributions import Normal
from typing import Tuple


class ActorCritic(nn.Module):
    """
    Actor-Critic network for PPO.

    The actor outputs action distribution parameters (mean, std).
    The critic outputs state value estimates.

    Args:
        obs_dim: Observation dimension
        action_dim: Action dimension
        hidden_dims: List of hidden layer dimensions
        activation: Activation function name
        init_noise_std: Initial action noise standard deviation
    """

    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        hidden_dims: list = [256, 256, 256],
        activation: str = "elu",
        init_noise_std: float = 1.0,
    ):
        super().__init__()

        self.obs_dim = obs_dim
        self.action_dim = action_dim

        # Activation function
        activation_map = {
            "elu": nn.ELU(),
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "leaky_relu": nn.LeakyReLU(),
        }
        self.activation = activation_map.get(activation, nn.ELU())

        # Build shared encoder
        encoder_layers = []
        prev_dim = obs_dim
        for hidden_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, hidden_dim))
            encoder_layers.append(self.activation)
            prev_dim = hidden_dim

        self.encoder = nn.Sequential(*encoder_layers)

        # Actor head (action mean)
        self.actor_mean = nn.Linear(hidden_dims[-1], action_dim)

        # Learnable action std (log scale for numerical stability)
        self.actor_log_std = nn.Parameter(
            torch.ones(action_dim) * np.log(init_noise_std)
        )

        # Critic head
        self.critic = nn.Linear(hidden_dims[-1], 1)

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize network weights using orthogonal initialization."""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.orthogonal_(m.weight, gain=np.sqrt(2))
                nn.init.constant_(m.bias, 0)

        # Actor output layer with smaller initialization
        nn.init.orthogonal_(self.actor_mean.weight, gain=0.01)
        nn.init.constant_(self.actor_mean.bias, 0)

        # Critic output layer
        nn.init.orthogonal_(self.critic.weight, gain=1.0)
        nn.init.constant_(self.critic.bias, 0)

    def forward(
        self, obs: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass through network.

        Args:
            obs: (batch, obs_dim) observations

        Returns:
            actions: (batch, action_dim) sampled actions
            log_probs: (batch,) log probabilities
            values: (batch,) value estimates
        """
        # Shared encoding
        features = self.encoder(obs)

        # Actor: action distribution
        action_mean = self.actor_mean(features)
        action_std = torch.exp(self.actor_log_std)

        # Sample action from Gaussian
        dist = Normal(action_mean, action_std)
        actions = dist.sample()
        log_probs = dist.log_prob(actions).sum(dim=-1)

        # Critic: value estimate
        values = self.critic(features).squeeze(-1)

        return actions, log_probs, values

    def evaluate(
        self, obs: torch.Tensor, actions: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions for PPO update.

        Args:
            obs: (batch, obs_dim) observations
            actions: (batch, action_dim) actions taken

        Returns:
            log_probs: (batch,) log probabilities
            values: (batch,) value estimates
            entropy: (batch,) action entropy
        """
        features = self.encoder(obs)

        # Action distribution
        action_mean = self.actor_mean(features)
        action_std = torch.exp(self.actor_log_std)
        dist = Normal(action_mean, action_std)

        # Log probability of taken actions
        log_probs = dist.log_prob(actions).sum(dim=-1)

        # Entropy for exploration bonus
        entropy = dist.entropy().sum(dim=-1)

        # Value estimate
        values = self.critic(features).squeeze(-1)

        return log_probs, values, entropy

    def act(
        self, obs: torch.Tensor, deterministic: bool = False
    ) -> torch.Tensor:
        """
        Get action for inference.

        Args:
            obs: (batch, obs_dim) observations
            deterministic: If True, return mean action

        Returns:
            actions: (batch, action_dim) actions
        """
        features = self.encoder(obs)
        action_mean = self.actor_mean(features)

        if deterministic:
            return action_mean
        else:
            action_std = torch.exp(self.actor_log_std)
            dist = Normal(action_mean, action_std)
            return dist.sample()

    def get_value(self, obs: torch.Tensor) -> torch.Tensor:
        """
        Get value estimate only.

        Args:
            obs: (batch, obs_dim) observations

        Returns:
            values: (batch,) value estimates
        """
        features = self.encoder(obs)
        return self.critic(features).squeeze(-1)

    @property
    def action_std(self) -> torch.Tensor:
        """Get current action standard deviation."""
        return torch.exp(self.actor_log_std)


class ActorForExport(nn.Module):
    """
    Wrapper to export only the actor (policy) part.

    Used for ONNX export when we only need the policy
    for deployment (no value function needed).
    """

    def __init__(self, actor_critic: ActorCritic):
        super().__init__()
        self.encoder = actor_critic.encoder
        self.actor_mean = actor_critic.actor_mean

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for deterministic action.

        Args:
            obs: (batch, obs_dim) observations

        Returns:
            actions: (batch, action_dim) deterministic actions
        """
        features = self.encoder(obs)
        actions = self.actor_mean(features)
        return actions


def export_policy_onnx(
    actor_critic: ActorCritic,
    obs_dim: int,
    output_path: str,
    opset_version: int = 11,
):
    """
    Export trained policy to ONNX format.

    Args:
        actor_critic: Trained ActorCritic model
        obs_dim: Observation dimension
        output_path: Path to save ONNX file
        opset_version: ONNX opset version
    """
    actor = ActorForExport(actor_critic)
    actor.eval()

    dummy_input = torch.randn(1, obs_dim)

    torch.onnx.export(
        actor,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["observation"],
        output_names=["action"],
        dynamic_axes={
            "observation": {0: "batch_size"},
            "action": {0: "batch_size"},
        },
    )

    print(f"Exported ONNX model to {output_path}")
