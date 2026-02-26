"""
OpenVLA Model Wrapper for Humanoid Robotics

This module provides a clean interface to the OpenVLA model for
vision-language-action inference in humanoid robot control.

Reference: Chapter 1 - Introduction to VLA Models
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from PIL import Image
import torch
import torch.nn as nn


@dataclass
class VLAConfig:
    """Configuration for VLA model."""
    model_name: str = "openvla/openvla-7b"
    action_dim: int = 7  # 6 DoF pose + gripper
    max_action_tokens: int = 20
    use_quantization: bool = True
    quantization_bits: int = 4
    device: str = "cuda"
    cache_kv: bool = True
    torch_dtype: str = "bfloat16"

    # Safety bounds
    action_bounds: Tuple[float, float] = (-1.0, 1.0)
    confidence_threshold: float = 0.5


@dataclass
class VLAOutput:
    """Output from VLA inference."""
    actions: np.ndarray  # Shape: (action_dim,) or (horizon, action_dim)
    action_tokens: List[int] = field(default_factory=list)
    confidence: float = 0.0
    raw_text: str = ""
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class OpenVLAWrapper:
    """
    Wrapper for OpenVLA model providing humanoid-specific functionality.

    Example:
        >>> config = VLAConfig(action_dim=22)  # Full humanoid joints
        >>> vla = OpenVLAWrapper(config)
        >>> output = vla.predict(image, "Pick up the red cube")
        >>> print(output.actions)  # Robot joint commands
    """

    def __init__(self, config: VLAConfig):
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self._load_model()

    def _load_model(self) -> None:
        """Load model with optional quantization."""
        try:
            from transformers import AutoModelForVision2Seq, AutoProcessor
            from transformers import BitsAndBytesConfig
        except ImportError:
            raise ImportError(
                "transformers library required. Install with: "
                "pip install transformers>=4.40.0"
            )

        # Configure quantization for memory efficiency
        quantization_config = None
        if self.config.use_quantization:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=(self.config.quantization_bits == 4),
                load_in_8bit=(self.config.quantization_bits == 8),
                bnb_4bit_compute_dtype=getattr(torch, self.config.torch_dtype),
                bnb_4bit_use_double_quant=True,
            )

        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            self.config.model_name,
            trust_remote_code=True,
        )

        # Load model
        dtype = getattr(torch, self.config.torch_dtype)
        self.model = AutoModelForVision2Seq.from_pretrained(
            self.config.model_name,
            torch_dtype=dtype,
            quantization_config=quantization_config,
            device_map="auto" if self.config.use_quantization else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

        if not self.config.use_quantization:
            self.model = self.model.to(self.device)

        self.model.eval()
        print(f"Loaded {self.config.model_name} on {self.device}")

    def predict(
        self,
        image: Image.Image,
        instruction: str,
        robot_state: Optional[np.ndarray] = None,
    ) -> VLAOutput:
        """
        Generate action from image and instruction.

        Args:
            image: RGB image from robot camera
            instruction: Natural language task instruction
            robot_state: Optional current joint positions

        Returns:
            VLAOutput with predicted actions
        """
        import time
        start_time = time.perf_counter()

        # Build prompt with optional state information
        prompt = self._build_prompt(instruction, robot_state)

        # Process inputs
        inputs = self.processor(
            text=prompt,
            images=image,
            return_tensors="pt",
        ).to(self.device)

        # Generate action tokens
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_action_tokens,
                do_sample=False,
                use_cache=self.config.cache_kv,
                output_scores=True,
                return_dict_in_generate=True,
            )

        # Parse output
        generated_ids = outputs.sequences[0, inputs['input_ids'].shape[1]:]
        generated_text = self.processor.decode(generated_ids, skip_special_tokens=True)

        # Extract actions and confidence
        actions, action_tokens, confidence = self._parse_actions(
            generated_text,
            outputs.scores if hasattr(outputs, 'scores') else None
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        return VLAOutput(
            actions=actions,
            action_tokens=action_tokens,
            confidence=confidence,
            raw_text=generated_text,
            latency_ms=latency_ms,
            metadata={
                "prompt": prompt,
                "robot_state": robot_state.tolist() if robot_state is not None else None,
            }
        )

    def _build_prompt(
        self,
        instruction: str,
        robot_state: Optional[np.ndarray] = None
    ) -> str:
        """Build the prompt for VLA inference."""
        prompt = f"In: What action should the robot take to {instruction}?\n"

        if robot_state is not None:
            state_str = ", ".join([f"{x:.3f}" for x in robot_state[:6]])
            prompt += f"Robot state: [{state_str}]\n"

        prompt += "Out:"
        return prompt

    def _parse_actions(
        self,
        generated_text: str,
        scores: Optional[List[torch.Tensor]] = None
    ) -> Tuple[np.ndarray, List[int], float]:
        """Parse action tokens from generated text."""
        # Extract numeric values from text
        import re
        numbers = re.findall(r'-?\d+\.?\d*', generated_text)

        if len(numbers) >= self.config.action_dim:
            actions = np.array([float(n) for n in numbers[:self.config.action_dim]])
        else:
            # Pad with zeros if not enough values
            actions = np.zeros(self.config.action_dim)
            for i, n in enumerate(numbers):
                actions[i] = float(n)

        # Clip to valid range
        actions = np.clip(
            actions,
            self.config.action_bounds[0],
            self.config.action_bounds[1]
        )

        # Calculate confidence from scores
        confidence = 1.0
        if scores is not None and len(scores) > 0:
            probs = [torch.softmax(s, dim=-1).max().item() for s in scores]
            confidence = float(np.mean(probs))

        # Action tokens (placeholder - actual implementation varies)
        action_tokens = list(range(len(numbers)))

        return actions, action_tokens, confidence

    def predict_trajectory(
        self,
        image: Image.Image,
        instruction: str,
        horizon: int = 10,
        robot_state: Optional[np.ndarray] = None,
    ) -> List[VLAOutput]:
        """
        Generate action trajectory using autoregressive prediction.

        Args:
            image: Initial observation image
            instruction: Task instruction
            horizon: Number of steps to predict
            robot_state: Initial robot state

        Returns:
            List of VLAOutputs for the trajectory
        """
        trajectory = []
        current_state = robot_state

        for step in range(horizon):
            output = self.predict(image, instruction, current_state)
            trajectory.append(output)

            # Update state for next prediction (simple integration)
            if current_state is not None:
                current_state = current_state + output.actions * 0.1  # dt=0.1

        return trajectory


class ActionTokenizer:
    """
    Tokenizer for converting continuous actions to discrete tokens.

    Uses bin-based discretization matching OpenVLA's action vocabulary.
    """

    def __init__(
        self,
        action_dim: int = 7,
        num_bins: int = 256,
        action_range: Tuple[float, float] = (-1.0, 1.0),
        special_token_offset: int = 32000,
    ):
        self.action_dim = action_dim
        self.num_bins = num_bins
        self.action_range = action_range
        self.special_token_offset = special_token_offset

        # Create bin edges
        self.bin_edges = np.linspace(
            action_range[0], action_range[1], num_bins + 1
        )

    def encode(self, actions: np.ndarray) -> np.ndarray:
        """
        Encode continuous actions to discrete tokens.

        Args:
            actions: Array of shape (action_dim,) with values in action_range

        Returns:
            Array of token IDs
        """
        actions = np.clip(actions, self.action_range[0], self.action_range[1])

        tokens = []
        for i, action in enumerate(actions):
            # Normalize to [0, 1]
            normalized = (action - self.action_range[0]) / (
                self.action_range[1] - self.action_range[0]
            )
            # Convert to bin index
            bin_idx = int(normalized * (self.num_bins - 1))
            bin_idx = np.clip(bin_idx, 0, self.num_bins - 1)
            # Add offset for this dimension
            token_id = self.special_token_offset + i * self.num_bins + bin_idx
            tokens.append(token_id)

        return np.array(tokens)

    def decode(self, tokens: np.ndarray) -> np.ndarray:
        """
        Decode discrete tokens to continuous actions.

        Args:
            tokens: Array of token IDs

        Returns:
            Array of continuous action values
        """
        actions = []
        for i, token in enumerate(tokens):
            # Remove offset
            local_token = token - self.special_token_offset - i * self.num_bins
            # Convert to normalized value
            normalized = local_token / (self.num_bins - 1)
            # Scale to action range
            action = normalized * (self.action_range[1] - self.action_range[0]) + \
                     self.action_range[0]
            actions.append(action)

        return np.array(actions)


# Utility functions
def load_vla_model(
    model_name: str = "openvla/openvla-7b",
    action_dim: int = 7,
    use_quantization: bool = True,
) -> OpenVLAWrapper:
    """
    Convenience function to load VLA model.

    Args:
        model_name: HuggingFace model identifier
        action_dim: Robot action dimensionality
        use_quantization: Whether to use 4-bit quantization

    Returns:
        Configured OpenVLAWrapper instance
    """
    config = VLAConfig(
        model_name=model_name,
        action_dim=action_dim,
        use_quantization=use_quantization,
    )
    return OpenVLAWrapper(config)


if __name__ == "__main__":
    # Example usage
    print("OpenVLA Wrapper Module")
    print("=" * 50)

    # Create configuration
    config = VLAConfig(
        action_dim=22,  # Humanoid robot joints
        use_quantization=True,
    )
    print(f"Configuration: {config}")

    # Test tokenizer
    tokenizer = ActionTokenizer(action_dim=7)
    test_actions = np.array([0.5, -0.3, 0.1, 0.0, 0.8, -0.5, 1.0])
    tokens = tokenizer.encode(test_actions)
    decoded = tokenizer.decode(tokens)

    print(f"\nTokenizer test:")
    print(f"  Original: {test_actions}")
    print(f"  Tokens:   {tokens}")
    print(f"  Decoded:  {decoded}")
    print(f"  Error:    {np.abs(test_actions - decoded).max():.6f}")
