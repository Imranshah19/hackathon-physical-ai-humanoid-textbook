# Chapter 3: Action Tokenization and Representation

**Duration**: 4-5 hours
**Prerequisites**: Chapter 2 (VLM Foundations)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Explain why actions need tokenization for VLA models
- Implement bin-based action tokenizers for position and rotation
- Design action vocabularies for humanoid robots
- Evaluate tokenization quality with reconstruction metrics
- Apply learned tokenization using K-means clustering

---

## 3.1 Why Tokenize Actions?

VLA models are built on language model architectures that work with **discrete tokens**, not continuous values. Robot actions (joint angles, velocities) are continuous, requiring tokenization.

### The Tokenization Challenge

```
┌─────────────────────────────────────────────────────────────────┐
│              Continuous vs Discrete Actions                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Continuous Robot Action:                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ [0.1523, -0.2847, 0.0912, 0.0034, -0.0127, 0.0089, 1.0] │   │
│  │   x       y       z      rx      ry       rz    gripper │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓                                       │
│                    Tokenization                                  │
│                          ↓                                       │
│  Discrete Action Tokens:                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │        [167,   73,  140,  130,  124,  131,    1]        │   │
│  │       bin_x bin_y bin_z bin_rx bin_ry bin_rz grip       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Benefits of Tokenization

| Benefit | Description |
|---------|-------------|
| **Architecture compatibility** | Use transformer language models directly |
| **Autoregressive generation** | Generate actions token by token |
| **Discrete optimization** | Cross-entropy loss, no regression issues |
| **Multi-task learning** | Shared vocabulary across tasks |
| **Emergent capabilities** | Transfer from language pre-training |

### Tokenization Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Fine bins (256)** | High precision | Large vocabulary |
| **Coarse bins (16)** | Small vocabulary | Lower precision |
| **Learned (K-means)** | Data-adaptive | Requires training data |
| **Continuous** | No quantization error | Different architecture needed |

---

## 3.2 Bin-Based Tokenization

The simplest approach divides continuous ranges into fixed bins.

### Position Tokenizer

```python
import numpy as np
import torch

class PositionTokenizer:
    """Tokenize 3D positions into discrete bins."""

    def __init__(
        self,
        num_bins: int = 256,
        x_range: tuple = (-0.5, 0.5),
        y_range: tuple = (-0.5, 0.5),
        z_range: tuple = (0.0, 0.6)
    ):
        self.num_bins = num_bins
        self.ranges = {
            'x': x_range,
            'y': y_range,
            'z': z_range
        }

        # Compute bin edges
        self.bin_edges = {
            axis: np.linspace(r[0], r[1], num_bins + 1)
            for axis, r in self.ranges.items()
        }

        # Compute bin centers for decoding
        self.bin_centers = {
            axis: (edges[:-1] + edges[1:]) / 2
            for axis, edges in self.bin_edges.items()
        }

    def encode(self, position: np.ndarray) -> np.ndarray:
        """
        Encode continuous position to bin indices.

        Args:
            position: [x, y, z] continuous values

        Returns:
            tokens: [bin_x, bin_y, bin_z] discrete indices
        """
        tokens = []
        axes = ['x', 'y', 'z']

        for i, axis in enumerate(axes):
            value = position[i]
            low, high = self.ranges[axis]

            # Clip to range
            value = np.clip(value, low, high)

            # Find bin index
            bin_idx = np.digitize(value, self.bin_edges[axis]) - 1
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)

            tokens.append(bin_idx)

        return np.array(tokens, dtype=np.int64)

    def decode(self, tokens: np.ndarray) -> np.ndarray:
        """
        Decode bin indices to continuous position.

        Args:
            tokens: [bin_x, bin_y, bin_z] discrete indices

        Returns:
            position: [x, y, z] continuous values
        """
        position = []
        axes = ['x', 'y', 'z']

        for i, axis in enumerate(axes):
            bin_idx = int(tokens[i])
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)
            value = self.bin_centers[axis][bin_idx]
            position.append(value)

        return np.array(position)

    def get_bin_width(self, axis: str) -> float:
        """Get the width of bins for an axis."""
        low, high = self.ranges[axis]
        return (high - low) / self.num_bins


# Usage example
pos_tokenizer = PositionTokenizer(num_bins=256)

# Encode
position = np.array([0.15, -0.23, 0.42])
tokens = pos_tokenizer.encode(position)
print(f"Position: {position}")
print(f"Tokens: {tokens}")

# Decode
decoded = pos_tokenizer.decode(tokens)
print(f"Decoded: {decoded}")

# Quantization error
error = np.abs(position - decoded)
print(f"Quantization error: {error}")
print(f"Max error: {error.max():.6f}")
```

### Rotation Tokenizer

```python
class RotationTokenizer:
    """Tokenize rotations (Euler angles or axis-angle)."""

    def __init__(
        self,
        num_bins: int = 256,
        representation: str = "euler",  # "euler" or "axis_angle"
        euler_range: tuple = (-np.pi, np.pi)
    ):
        self.num_bins = num_bins
        self.representation = representation
        self.euler_range = euler_range

        if representation == "euler":
            # Roll, Pitch, Yaw
            self.axes = ['roll', 'pitch', 'yaw']
            self.ranges = {axis: euler_range for axis in self.axes}
        elif representation == "axis_angle":
            # Axis (unit vector) + angle
            self.axes = ['ax', 'ay', 'az', 'angle']
            self.ranges = {
                'ax': (-1, 1), 'ay': (-1, 1), 'az': (-1, 1),
                'angle': (0, np.pi)
            }

        # Compute bin centers
        self.bin_centers = {
            axis: np.linspace(r[0], r[1], num_bins)
            for axis, r in self.ranges.items()
        }

    def encode(self, rotation: np.ndarray) -> np.ndarray:
        """
        Encode rotation to bin indices.

        Args:
            rotation: Euler angles [roll, pitch, yaw] or axis-angle [ax, ay, az, angle]

        Returns:
            tokens: Discrete bin indices
        """
        tokens = []

        for i, axis in enumerate(self.axes):
            value = rotation[i]
            low, high = self.ranges[axis]

            # Handle angle wrapping for Euler
            if self.representation == "euler":
                while value > high:
                    value -= 2 * np.pi
                while value < low:
                    value += 2 * np.pi

            # Clip and discretize
            value = np.clip(value, low, high)
            bin_idx = int((value - low) / (high - low) * (self.num_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)

            tokens.append(bin_idx)

        return np.array(tokens, dtype=np.int64)

    def decode(self, tokens: np.ndarray) -> np.ndarray:
        """Decode bin indices to rotation values."""
        rotation = []

        for i, axis in enumerate(self.axes):
            bin_idx = int(tokens[i])
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)
            value = self.bin_centers[axis][bin_idx]
            rotation.append(value)

        return np.array(rotation)


# Usage
rot_tokenizer = RotationTokenizer(num_bins=256, representation="euler")

rotation = np.array([0.1, -0.05, 0.3])  # roll, pitch, yaw
tokens = rot_tokenizer.encode(rotation)
decoded = rot_tokenizer.decode(tokens)

print(f"Rotation: {rotation}")
print(f"Tokens: {tokens}")
print(f"Decoded: {decoded}")
print(f"Error: {np.abs(rotation - decoded)}")
```

---

## 3.3 Joint Tokenizer for Humanoids

Humanoid robots have multiple joints with different ranges:

```python
class JointTokenizer:
    """Tokenize humanoid joint positions."""

    # Standard humanoid joint configuration
    HUMANOID_JOINTS = {
        # Name: (min_angle, max_angle) in radians
        'left_hip_yaw': (-0.5, 0.5),
        'left_hip_roll': (-0.3, 0.5),
        'left_hip_pitch': (-1.5, 0.5),
        'left_knee': (0.0, 2.0),
        'left_ankle_pitch': (-0.5, 0.5),
        'left_ankle_roll': (-0.3, 0.3),
        'right_hip_yaw': (-0.5, 0.5),
        'right_hip_roll': (-0.5, 0.3),
        'right_hip_pitch': (-1.5, 0.5),
        'right_knee': (0.0, 2.0),
        'right_ankle_pitch': (-0.5, 0.5),
        'right_ankle_roll': (-0.3, 0.3),
        'torso_yaw': (-0.5, 0.5),
        'torso_pitch': (-0.3, 0.3),
    }

    def __init__(
        self,
        joint_limits: dict = None,
        num_bins: int = 256
    ):
        self.joint_limits = joint_limits or self.HUMANOID_JOINTS
        self.num_bins = num_bins
        self.joint_names = list(self.joint_limits.keys())
        self.num_joints = len(self.joint_names)

        # Precompute bin centers for each joint
        self.bin_centers = {}
        for name, (low, high) in self.joint_limits.items():
            self.bin_centers[name] = np.linspace(low, high, num_bins)

    def encode(self, joint_positions: np.ndarray) -> np.ndarray:
        """
        Encode joint positions to tokens.

        Args:
            joint_positions: Array of joint angles [num_joints]

        Returns:
            tokens: Discrete indices [num_joints]
        """
        tokens = []

        for i, name in enumerate(self.joint_names):
            value = joint_positions[i]
            low, high = self.joint_limits[name]

            # Clip to limits
            value = np.clip(value, low, high)

            # Discretize
            bin_idx = int((value - low) / (high - low) * (self.num_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)

            tokens.append(bin_idx)

        return np.array(tokens, dtype=np.int64)

    def decode(self, tokens: np.ndarray) -> np.ndarray:
        """Decode tokens to joint positions."""
        positions = []

        for i, name in enumerate(self.joint_names):
            bin_idx = int(tokens[i])
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)
            value = self.bin_centers[name][bin_idx]
            positions.append(value)

        return np.array(positions)

    def encode_delta(self, current: np.ndarray, target: np.ndarray) -> np.ndarray:
        """
        Encode delta actions (relative movements).

        Args:
            current: Current joint positions
            target: Target joint positions

        Returns:
            tokens: Delta action tokens
        """
        delta = target - current

        # Normalize deltas to [-1, 1] based on joint range
        normalized = []
        for i, name in enumerate(self.joint_names):
            low, high = self.joint_limits[name]
            range_size = high - low
            norm_delta = delta[i] / range_size  # Now in [-1, 1] approximately
            norm_delta = np.clip(norm_delta, -1, 1)
            normalized.append(norm_delta)

        # Encode normalized deltas to bins
        tokens = []
        for norm_val in normalized:
            bin_idx = int((norm_val + 1) / 2 * (self.num_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)
            tokens.append(bin_idx)

        return np.array(tokens, dtype=np.int64)


# Usage
joint_tokenizer = JointTokenizer(num_bins=256)

# Sample joint positions
joint_positions = np.random.uniform(-0.5, 0.5, joint_tokenizer.num_joints)

tokens = joint_tokenizer.encode(joint_positions)
decoded = joint_tokenizer.decode(tokens)

print(f"Number of joints: {joint_tokenizer.num_joints}")
print(f"Joint names: {joint_tokenizer.joint_names[:5]}...")
print(f"Tokens: {tokens[:5]}...")
print(f"Max error: {np.abs(joint_positions - decoded).max():.6f}")
```

---

## 3.4 Action Vocabulary Design

A complete action vocabulary combines all action dimensions:

```python
class ActionVocabulary:
    """Complete action vocabulary for VLA models."""

    # Special tokens
    PAD_TOKEN = 0
    START_TOKEN = 1
    END_TOKEN = 2
    SPECIAL_TOKENS = 3

    def __init__(
        self,
        num_bins: int = 256,
        action_dim: int = 7,  # x, y, z, rx, ry, rz, gripper
        use_delta: bool = True
    ):
        self.num_bins = num_bins
        self.action_dim = action_dim
        self.use_delta = use_delta

        # Vocabulary size: special tokens + bins per dimension
        self.vocab_size = self.SPECIAL_TOKENS + (num_bins * action_dim)

        # Token ranges for each action dimension
        self.token_ranges = {}
        for i in range(action_dim):
            start = self.SPECIAL_TOKENS + (i * num_bins)
            end = start + num_bins
            self.token_ranges[i] = (start, end)

        print(f"Action Vocabulary:")
        print(f"  Bins per dimension: {num_bins}")
        print(f"  Action dimensions: {action_dim}")
        print(f"  Total vocabulary size: {self.vocab_size}")

    def encode_action(self, action: np.ndarray) -> np.ndarray:
        """
        Encode continuous action to vocabulary tokens.

        Args:
            action: Continuous action [action_dim]

        Returns:
            tokens: Vocabulary token IDs [action_dim]
        """
        tokens = []

        for i in range(self.action_dim):
            # Assume action values are in [-1, 1]
            value = np.clip(action[i], -1, 1)

            # Map to bin index
            bin_idx = int((value + 1) / 2 * (self.num_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)

            # Convert to vocabulary token
            start, _ = self.token_ranges[i]
            token = start + bin_idx
            tokens.append(token)

        return np.array(tokens, dtype=np.int64)

    def decode_action(self, tokens: np.ndarray) -> np.ndarray:
        """
        Decode vocabulary tokens to continuous action.

        Args:
            tokens: Vocabulary token IDs [action_dim]

        Returns:
            action: Continuous action [action_dim]
        """
        action = []

        for i in range(self.action_dim):
            token = int(tokens[i])
            start, end = self.token_ranges[i]

            # Check if token is in valid range
            if token < start or token >= end:
                # Invalid token, use midpoint
                bin_idx = self.num_bins // 2
            else:
                bin_idx = token - start

            # Map bin to continuous value
            value = (bin_idx / (self.num_bins - 1)) * 2 - 1  # [-1, 1]
            action.append(value)

        return np.array(action)

    def encode_sequence(self, actions: np.ndarray) -> np.ndarray:
        """
        Encode action sequence with start/end tokens.

        Args:
            actions: [seq_len, action_dim]

        Returns:
            tokens: [seq_len * action_dim + 2] with start/end
        """
        tokens = [self.START_TOKEN]

        for action in actions:
            action_tokens = self.encode_action(action)
            tokens.extend(action_tokens.tolist())

        tokens.append(self.END_TOKEN)

        return np.array(tokens, dtype=np.int64)

    def decode_sequence(self, tokens: np.ndarray) -> np.ndarray:
        """
        Decode token sequence to actions.

        Args:
            tokens: Token sequence

        Returns:
            actions: [num_actions, action_dim]
        """
        # Remove special tokens
        tokens = tokens.tolist()
        if tokens[0] == self.START_TOKEN:
            tokens = tokens[1:]
        if tokens[-1] == self.END_TOKEN:
            tokens = tokens[:-1]

        # Group into actions
        actions = []
        for i in range(0, len(tokens), self.action_dim):
            if i + self.action_dim <= len(tokens):
                action_tokens = np.array(tokens[i:i + self.action_dim])
                action = self.decode_action(action_tokens)
                actions.append(action)

        return np.array(actions) if actions else np.array([]).reshape(0, self.action_dim)


# Usage
vocab = ActionVocabulary(num_bins=256, action_dim=7)

# Single action
action = np.array([0.1, -0.2, 0.3, 0.0, 0.05, -0.1, 1.0])
tokens = vocab.encode_action(action)
decoded = vocab.decode_action(tokens)

print(f"\nSingle action:")
print(f"Original: {action}")
print(f"Tokens: {tokens}")
print(f"Decoded: {decoded}")
print(f"Error: {np.abs(action - decoded).max():.6f}")

# Action sequence
actions = np.random.uniform(-1, 1, (5, 7))
seq_tokens = vocab.encode_sequence(actions)
decoded_actions = vocab.decode_sequence(seq_tokens)

print(f"\nAction sequence:")
print(f"Original shape: {actions.shape}")
print(f"Token sequence length: {len(seq_tokens)}")
print(f"Decoded shape: {decoded_actions.shape}")
```

---

## 3.5 K-Means Action Tokenization

Learn action clusters from demonstration data for better discretization:

```python
from sklearn.cluster import MiniBatchKMeans
import pickle

class KMeansActionTokenizer:
    """Learned action tokenization using K-means clustering."""

    def __init__(
        self,
        n_clusters: int = 256,
        action_dim: int = 7,
        random_state: int = 42
    ):
        self.n_clusters = n_clusters
        self.action_dim = action_dim
        self.random_state = random_state

        self.kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            random_state=random_state,
            batch_size=1024
        )
        self.fitted = False

    def fit(self, actions: np.ndarray):
        """
        Fit tokenizer on action data.

        Args:
            actions: Training actions [num_samples, action_dim]
        """
        print(f"Fitting K-means on {len(actions)} actions...")

        # Normalize actions
        self.action_mean = actions.mean(axis=0)
        self.action_std = actions.std(axis=0) + 1e-8

        normalized = (actions - self.action_mean) / self.action_std

        # Fit K-means
        self.kmeans.fit(normalized)
        self.fitted = True

        # Compute cluster statistics
        distances = self.kmeans.transform(normalized)
        min_distances = distances.min(axis=1)

        print(f"Fitting complete!")
        print(f"  Clusters: {self.n_clusters}")
        print(f"  Mean quantization error: {min_distances.mean():.4f}")
        print(f"  Max quantization error: {min_distances.max():.4f}")

    def encode(self, action: np.ndarray) -> int:
        """
        Encode action to cluster index.

        Args:
            action: Continuous action [action_dim]

        Returns:
            cluster_idx: Cluster index (token)
        """
        if not self.fitted:
            raise RuntimeError("Tokenizer not fitted. Call fit() first.")

        normalized = (action - self.action_mean) / self.action_std
        normalized = normalized.reshape(1, -1)

        cluster_idx = self.kmeans.predict(normalized)[0]
        return int(cluster_idx)

    def decode(self, token: int) -> np.ndarray:
        """
        Decode cluster index to action.

        Args:
            token: Cluster index

        Returns:
            action: Cluster center [action_dim]
        """
        if not self.fitted:
            raise RuntimeError("Tokenizer not fitted. Call fit() first.")

        token = int(np.clip(token, 0, self.n_clusters - 1))

        normalized = self.kmeans.cluster_centers_[token]
        action = normalized * self.action_std + self.action_mean

        return action

    def encode_batch(self, actions: np.ndarray) -> np.ndarray:
        """Encode batch of actions."""
        normalized = (actions - self.action_mean) / self.action_std
        tokens = self.kmeans.predict(normalized)
        return tokens

    def decode_batch(self, tokens: np.ndarray) -> np.ndarray:
        """Decode batch of tokens."""
        tokens = np.clip(tokens, 0, self.n_clusters - 1)
        normalized = self.kmeans.cluster_centers_[tokens]
        actions = normalized * self.action_std + self.action_mean
        return actions

    def evaluate(self, actions: np.ndarray) -> dict:
        """
        Evaluate tokenization quality.

        Returns reconstruction metrics.
        """
        tokens = self.encode_batch(actions)
        reconstructed = self.decode_batch(tokens)

        errors = np.abs(actions - reconstructed)

        return {
            'mean_error': errors.mean(),
            'max_error': errors.max(),
            'per_dim_error': errors.mean(axis=0),
            'p50_error': np.percentile(errors, 50),
            'p95_error': np.percentile(errors, 95),
            'p99_error': np.percentile(errors, 99)
        }

    def save(self, path: str):
        """Save tokenizer to file."""
        data = {
            'kmeans': self.kmeans,
            'action_mean': self.action_mean,
            'action_std': self.action_std,
            'n_clusters': self.n_clusters,
            'action_dim': self.action_dim,
            'fitted': self.fitted
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved tokenizer to {path}")

    @classmethod
    def load(cls, path: str) -> 'KMeansActionTokenizer':
        """Load tokenizer from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)

        tokenizer = cls(
            n_clusters=data['n_clusters'],
            action_dim=data['action_dim']
        )
        tokenizer.kmeans = data['kmeans']
        tokenizer.action_mean = data['action_mean']
        tokenizer.action_std = data['action_std']
        tokenizer.fitted = data['fitted']

        print(f"Loaded tokenizer from {path}")
        return tokenizer


# Usage with simulated data
# Generate synthetic demonstration data
np.random.seed(42)
demo_actions = np.random.randn(10000, 7) * 0.3  # Simulated actions

# Fit tokenizer
kmeans_tokenizer = KMeansActionTokenizer(n_clusters=256, action_dim=7)
kmeans_tokenizer.fit(demo_actions)

# Evaluate
metrics = kmeans_tokenizer.evaluate(demo_actions[:1000])
print(f"\nTokenization Quality:")
print(f"  Mean error: {metrics['mean_error']:.4f}")
print(f"  P95 error: {metrics['p95_error']:.4f}")
print(f"  Per-dim error: {metrics['per_dim_error']}")

# Save and load
kmeans_tokenizer.save("action_tokenizer.pkl")
loaded_tokenizer = KMeansActionTokenizer.load("action_tokenizer.pkl")
```

---

## 3.6 Comparing Tokenization Strategies

### Evaluation Framework

```python
class TokenizationEvaluator:
    """Compare different tokenization strategies."""

    def __init__(self, test_actions: np.ndarray):
        self.test_actions = test_actions

    def evaluate_binned(self, num_bins: int) -> dict:
        """Evaluate uniform binning."""
        vocab = ActionVocabulary(num_bins=num_bins, action_dim=self.test_actions.shape[1])

        errors = []
        for action in self.test_actions:
            # Scale to [-1, 1] for vocab
            scaled = action / (np.abs(action).max() + 1e-8)
            tokens = vocab.encode_action(scaled)
            decoded = vocab.decode_action(tokens)
            error = np.abs(scaled - decoded)
            errors.append(error)

        errors = np.array(errors)

        return {
            'method': f'Uniform Bins ({num_bins})',
            'mean_error': errors.mean(),
            'max_error': errors.max(),
            'p95_error': np.percentile(errors, 95),
            'vocab_size': vocab.vocab_size
        }

    def evaluate_kmeans(self, n_clusters: int) -> dict:
        """Evaluate K-means tokenization."""
        # Use 80% for fitting, 20% for evaluation
        split = int(len(self.test_actions) * 0.8)
        train_actions = self.test_actions[:split]
        eval_actions = self.test_actions[split:]

        tokenizer = KMeansActionTokenizer(n_clusters=n_clusters, action_dim=self.test_actions.shape[1])
        tokenizer.fit(train_actions)

        metrics = tokenizer.evaluate(eval_actions)

        return {
            'method': f'K-means ({n_clusters})',
            'mean_error': metrics['mean_error'],
            'max_error': metrics['max_error'],
            'p95_error': metrics['p95_error'],
            'vocab_size': n_clusters
        }

    def compare_all(self) -> pd.DataFrame:
        """Run all comparisons."""
        results = []

        # Binned tokenizers
        for num_bins in [16, 64, 128, 256, 512]:
            results.append(self.evaluate_binned(num_bins))

        # K-means tokenizers
        for n_clusters in [64, 128, 256, 512, 1024]:
            results.append(self.evaluate_kmeans(n_clusters))

        import pandas as pd
        df = pd.DataFrame(results)
        return df


# Compare tokenization strategies
test_actions = np.random.randn(5000, 7) * 0.3

evaluator = TokenizationEvaluator(test_actions)
comparison = evaluator.compare_all()
print("\nTokenization Comparison:")
print(comparison.to_string())
```

---

## 3.7 Action Detokenizer

Convert model outputs back to robot commands:

```python
class ActionDetokenizer:
    """Convert VLA model outputs to executable robot actions."""

    def __init__(
        self,
        vocab: ActionVocabulary,
        action_ranges: dict = None
    ):
        self.vocab = vocab

        # Physical action ranges for the robot
        self.action_ranges = action_ranges or {
            'x': (-0.5, 0.5),      # End-effector position
            'y': (-0.5, 0.5),
            'z': (0.0, 0.6),
            'rx': (-0.5, 0.5),    # End-effector rotation
            'ry': (-0.5, 0.5),
            'rz': (-0.5, 0.5),
            'gripper': (0.0, 1.0)  # Gripper state
        }

        self.action_names = list(self.action_ranges.keys())

    def detokenize(
        self,
        tokens: np.ndarray,
        return_dict: bool = False
    ) -> np.ndarray:
        """
        Convert tokens to robot action.

        Args:
            tokens: Action tokens from VLA model
            return_dict: Whether to return named dictionary

        Returns:
            action: Continuous robot action
        """
        # First decode to [-1, 1] range
        normalized = self.vocab.decode_action(tokens)

        # Scale to physical ranges
        action = []
        for i, name in enumerate(self.action_names):
            low, high = self.action_ranges[name]
            value = (normalized[i] + 1) / 2 * (high - low) + low
            action.append(value)

        action = np.array(action)

        if return_dict:
            return {name: action[i] for i, name in enumerate(self.action_names)}
        return action

    def detokenize_sequence(
        self,
        token_sequence: np.ndarray,
        include_confidence: bool = False
    ) -> np.ndarray:
        """
        Detokenize full action sequence.

        Args:
            token_sequence: Sequence of tokens
            include_confidence: Whether to include confidence scores

        Returns:
            actions: Array of robot actions
        """
        actions = self.vocab.decode_sequence(token_sequence)

        # Scale each action
        scaled_actions = []
        for normalized in actions:
            action = []
            for i, name in enumerate(self.action_names):
                low, high = self.action_ranges[name]
                value = (normalized[i] + 1) / 2 * (high - low) + low
                action.append(value)
            scaled_actions.append(action)

        return np.array(scaled_actions)

    def validate_action(self, action: np.ndarray) -> tuple:
        """
        Validate action is within bounds.

        Returns:
            (is_valid, violations)
        """
        violations = []

        for i, name in enumerate(self.action_names):
            low, high = self.action_ranges[name]
            value = action[i]

            if value < low:
                violations.append(f"{name}: {value:.3f} < {low}")
            elif value > high:
                violations.append(f"{name}: {value:.3f} > {high}")

        is_valid = len(violations) == 0
        return is_valid, violations


# Usage
vocab = ActionVocabulary(num_bins=256, action_dim=7)
detokenizer = ActionDetokenizer(vocab)

# Simulate VLA output tokens
tokens = np.array([130, 120, 180, 128, 130, 125, 200])

# Detokenize
action = detokenizer.detokenize(tokens)
action_dict = detokenizer.detokenize(tokens, return_dict=True)

print(f"Tokens: {tokens}")
print(f"Action array: {action}")
print(f"Action dict: {action_dict}")

# Validate
is_valid, violations = detokenizer.validate_action(action)
print(f"Valid: {is_valid}, Violations: {violations}")
```

---

## 3.8 Summary

In this chapter, you learned:

1. **Why Tokenization**: VLA models need discrete tokens, not continuous values
2. **Bin-Based**: Simple uniform discretization (256 bins common)
3. **Position/Rotation**: Separate tokenizers for different action types
4. **Joint Tokenizer**: Per-joint normalization for humanoids
5. **Action Vocabulary**: Complete vocabulary with special tokens
6. **K-Means**: Learned tokenization from demonstration data
7. **Comparison**: Trade-offs between approaches
8. **Detokenization**: Converting back to robot commands

---

## 3.9 Exercises

### Exercise 3.1: Position Tokenizer
Implement and test a position tokenizer with 256 bins. Measure reconstruction error.

### Exercise 3.2: Joint Vocabulary
Design a joint tokenizer for a 14-DOF humanoid. Handle asymmetric joint limits.

### Exercise 3.3: K-Means Training
Train a K-means tokenizer on simulated demonstration data. Compare with uniform bins.

### Exercise 3.4: Ablation Study
Compare reconstruction error for 64, 128, 256, and 512 bins. Plot the trade-off.

---

## Quick Reference

### Bin-Based Encoding
```python
bin_idx = int((value - low) / (high - low) * (num_bins - 1))
value = (bin_idx / (num_bins - 1)) * (high - low) + low
```

### Action Vocabulary Size
```
vocab_size = special_tokens + (num_bins * action_dim)
           = 3 + (256 * 7) = 1795
```

### K-Means Tokenizer
```python
tokenizer = KMeansActionTokenizer(n_clusters=256)
tokenizer.fit(demonstration_actions)
token = tokenizer.encode(action)
```

---

**Next Chapter**: [Chapter 4 - Language Grounding for Robotics](ch04-language-grounding.md)
