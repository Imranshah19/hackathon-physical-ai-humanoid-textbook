# Chapter 5: Building the VLA Inference Pipeline

**Duration**: 5-6 hours
**Prerequisites**: Chapters 2-4 (VLM Foundations, Tokenization, Grounding)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Design end-to-end VLA inference pipelines
- Implement efficient input preprocessing
- Build autoregressive action generation
- Optimize for real-time performance
- Profile and debug VLA systems

---

## 5.1 VLA Pipeline Architecture

A complete VLA pipeline orchestrates multiple components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    VLA Pipeline Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Inputs:                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Image   │  │ Instruction  │  │ Robot State  │              │
│  │ (480x640)│  │   (text)     │  │  (14 DOF)    │              │
│  └────┬─────┘  └──────┬───────┘  └──────┬───────┘              │
│       │               │                  │                       │
│       ▼               ▼                  ▼                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Preprocessing                           │   │
│  │  • Resize image to 224x224                              │   │
│  │  • Normalize with ImageNet stats                        │   │
│  │  • Tokenize instruction                                  │   │
│  │  • Normalize robot state                                 │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    VLA Model                             │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐    │   │
│  │  │   Vision    │  │    Text     │  │    State     │    │   │
│  │  │   Encoder   │  │   Encoder   │  │   Encoder    │    │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘    │   │
│  │         └────────────────┼────────────────┘            │   │
│  │                          ▼                              │   │
│  │              ┌─────────────────────┐                   │   │
│  │              │  Multimodal Fusion  │                   │   │
│  │              └──────────┬──────────┘                   │   │
│  │                         ▼                              │   │
│  │              ┌─────────────────────┐                   │   │
│  │              │   Action Decoder    │                   │   │
│  │              └──────────┬──────────┘                   │   │
│  └─────────────────────────┼───────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Postprocessing                          │   │
│  │  • Detokenize action tokens                             │   │
│  │  • Scale to physical ranges                             │   │
│  │  • Apply safety filters                                  │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│                            ▼                                     │
│                    ┌──────────────┐                              │
│                    │Robot Command │                              │
│                    │  (7 DOF)     │                              │
│                    └──────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5.2 Pipeline Implementation

### Core Pipeline Class

```python
import torch
import numpy as np
from PIL import Image
from typing import Dict, Optional, Union
from dataclasses import dataclass
import time

@dataclass
class VLAConfig:
    """Configuration for VLA pipeline."""
    model_path: str = "openvla/openvla-7b"
    device: str = "cuda"
    dtype: torch.dtype = torch.float16

    # Input sizes
    image_size: int = 224
    max_instruction_length: int = 128

    # Action configuration
    action_dim: int = 7
    num_action_bins: int = 256
    action_chunk_size: int = 1  # Number of actions to predict

    # Safety
    max_action_magnitude: float = 1.0
    min_confidence: float = 0.5

    # Performance
    use_quantization: bool = True
    quantization_bits: int = 4
    use_flash_attention: bool = True


@dataclass
class VLAOutput:
    """Output from VLA pipeline."""
    actions: np.ndarray  # (chunk_size, action_dim)
    action_tokens: np.ndarray
    confidence: float
    latency_ms: float
    metadata: Dict


class VLAPipeline:
    """End-to-end VLA inference pipeline."""

    def __init__(self, config: VLAConfig):
        self.config = config
        self.device = torch.device(config.device)

        # Load model
        self._load_model()

        # Initialize preprocessors
        self._init_preprocessors()

        # Initialize tokenizers
        self._init_tokenizers()

        # Warmup
        self._warmup()

    def _load_model(self):
        """Load VLA model with optional quantization."""
        from transformers import AutoModelForVision2Seq, AutoProcessor

        print(f"Loading VLA model from {self.config.model_path}...")

        # Quantization config
        if self.config.use_quantization:
            from transformers import BitsAndBytesConfig

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=self.config.quantization_bits == 4,
                load_in_8bit=self.config.quantization_bits == 8,
                bnb_4bit_compute_dtype=self.config.dtype,
                bnb_4bit_use_double_quant=True,
            )
        else:
            quantization_config = None

        # Load model
        self.model = AutoModelForVision2Seq.from_pretrained(
            self.config.model_path,
            torch_dtype=self.config.dtype,
            device_map="auto" if self.device.type == "cuda" else None,
            quantization_config=quantization_config,
            low_cpu_mem_usage=True,
        )

        self.processor = AutoProcessor.from_pretrained(self.config.model_path)

        self.model.eval()

        # Get memory usage
        if self.device.type == "cuda":
            memory_gb = torch.cuda.max_memory_allocated() / 1e9
            print(f"Model loaded. GPU memory: {memory_gb:.2f} GB")

    def _init_preprocessors(self):
        """Initialize image and state preprocessors."""
        from torchvision import transforms

        self.image_transform = transforms.Compose([
            transforms.Resize((self.config.image_size, self.config.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _init_tokenizers(self):
        """Initialize action tokenizers."""
        from action_tokenizer import ActionVocabulary

        self.action_vocab = ActionVocabulary(
            num_bins=self.config.num_action_bins,
            action_dim=self.config.action_dim
        )

    def _warmup(self):
        """Warmup model with dummy inputs."""
        print("Warming up model...")

        dummy_image = Image.new('RGB', (640, 480), color='gray')
        dummy_instruction = "pick up the object"

        # Run a few iterations
        for _ in range(3):
            _ = self.predict(dummy_image, dummy_instruction)

        print("Warmup complete.")

    def preprocess_image(self, image: Union[Image.Image, np.ndarray]) -> torch.Tensor:
        """Preprocess image for model input."""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Apply transforms
        tensor = self.image_transform(image)

        # Add batch dimension
        tensor = tensor.unsqueeze(0)

        return tensor.to(self.device, self.config.dtype)

    def preprocess_instruction(self, instruction: str) -> Dict[str, torch.Tensor]:
        """Tokenize instruction text."""
        # Format prompt (model-specific)
        prompt = f"In: What action should the robot take to {instruction}?\nOut:"

        # Tokenize
        inputs = self.processor.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.config.max_instruction_length
        )

        return {k: v.to(self.device) for k, v in inputs.items()}

    def preprocess_state(self, state: Optional[np.ndarray]) -> Optional[torch.Tensor]:
        """Preprocess robot state."""
        if state is None:
            return None

        # Normalize state to [-1, 1] (assuming joint limits are known)
        # This should be customized for your robot
        normalized = np.clip(state, -1, 1)

        tensor = torch.from_numpy(normalized).float()
        tensor = tensor.unsqueeze(0)

        return tensor.to(self.device, self.config.dtype)

    @torch.no_grad()
    def predict(
        self,
        image: Union[Image.Image, np.ndarray],
        instruction: str,
        state: Optional[np.ndarray] = None,
        return_raw: bool = False
    ) -> VLAOutput:
        """
        Run VLA inference.

        Args:
            image: Camera image (PIL or numpy)
            instruction: Natural language instruction
            state: Optional robot state
            return_raw: Whether to return raw model outputs

        Returns:
            VLAOutput with actions and metadata
        """
        start_time = time.perf_counter()

        # Preprocess inputs
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Use model's processor for correct formatting
        prompt = f"In: What action should the robot take to {instruction}?\nOut:"

        inputs = self.processor(
            text=prompt,
            images=image,
            return_tensors="pt"
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Convert to correct dtype
        if 'pixel_values' in inputs:
            inputs['pixel_values'] = inputs['pixel_values'].to(self.config.dtype)

        # Generate action tokens
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.config.action_dim * self.config.action_chunk_size + 10,
            do_sample=False,
            pad_token_id=self.processor.tokenizer.pad_token_id,
        )

        # Decode output
        generated_text = self.processor.decode(outputs[0], skip_special_tokens=True)

        # Parse action tokens from text
        actions, action_tokens, confidence = self._parse_action_output(generated_text)

        # Compute latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        return VLAOutput(
            actions=actions,
            action_tokens=action_tokens,
            confidence=confidence,
            latency_ms=latency_ms,
            metadata={
                'raw_output': generated_text if return_raw else None,
                'instruction': instruction,
            }
        )

    def _parse_action_output(self, output_text: str) -> tuple:
        """Parse action tokens from model output text."""
        import re

        # Extract numbers from output
        # OpenVLA outputs space-separated integers
        out_section = output_text.split("Out:")[-1] if "Out:" in output_text else output_text
        numbers = re.findall(r'\d+', out_section)

        if len(numbers) >= self.config.action_dim:
            tokens = np.array([int(n) for n in numbers[:self.config.action_dim]])

            # Decode to continuous actions
            actions = self.action_vocab.decode_action(tokens)

            # Estimate confidence (simple heuristic)
            confidence = 0.8  # Could be based on token probabilities

            return actions.reshape(1, -1), tokens, confidence

        # Failed to parse - return zero action
        return np.zeros((1, self.config.action_dim)), np.zeros(self.config.action_dim), 0.0

    def predict_chunk(
        self,
        image: Image.Image,
        instruction: str,
        chunk_size: int = 8
    ) -> np.ndarray:
        """
        Predict action chunk for temporal consistency.

        Args:
            image: Current camera image
            instruction: Task instruction
            chunk_size: Number of actions to predict

        Returns:
            Action sequence (chunk_size, action_dim)
        """
        # For models that support chunked prediction
        # This is a simplified version - real implementation
        # would use a model trained for chunked output

        actions = []
        for _ in range(chunk_size):
            output = self.predict(image, instruction)
            actions.append(output.actions[0])

        return np.array(actions)


# Usage example
config = VLAConfig(
    model_path="openvla/openvla-7b",
    use_quantization=True,
    quantization_bits=4
)

pipeline = VLAPipeline(config)

# Run inference
image = Image.open("robot_camera.jpg")
instruction = "pick up the red block"

output = pipeline.predict(image, instruction)

print(f"Actions: {output.actions}")
print(f"Confidence: {output.confidence:.2f}")
print(f"Latency: {output.latency_ms:.1f} ms")
```

---

## 5.3 Autoregressive Action Generation

For more control over generation:

```python
class AutoregressiveActionGenerator:
    """Generate actions autoregressively with control over sampling."""

    def __init__(self, model, processor, config: VLAConfig):
        self.model = model
        self.processor = processor
        self.config = config
        self.device = torch.device(config.device)

    @torch.no_grad()
    def generate(
        self,
        image: Image.Image,
        instruction: str,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.95,
        max_tokens: int = 10
    ) -> Dict:
        """
        Generate actions with controlled sampling.

        Args:
            image: Input image
            instruction: Task instruction
            temperature: Sampling temperature (higher = more random)
            top_k: Top-k filtering
            top_p: Nucleus sampling threshold
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with tokens, actions, and probabilities
        """
        # Prepare inputs
        prompt = f"In: What action should the robot take to {instruction}?\nOut:"

        inputs = self.processor(
            text=prompt,
            images=image,
            return_tensors="pt"
        ).to(self.device)

        # Get input length
        input_len = inputs['input_ids'].shape[1]

        generated_tokens = []
        token_probs = []

        # Generate token by token
        for _ in range(max_tokens):
            # Forward pass
            outputs = self.model(**inputs)
            logits = outputs.logits[:, -1, :]  # Last position

            # Apply temperature
            logits = logits / temperature

            # Apply top-k filtering
            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = float('-inf')

            # Apply top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = 0
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = float('-inf')

            # Sample or argmax
            if temperature > 0:
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                token_prob = probs[0, next_token[0, 0]].item()
            else:
                next_token = torch.argmax(logits, dim=-1, keepdim=True)
                token_prob = 1.0

            generated_tokens.append(next_token[0, 0].item())
            token_probs.append(token_prob)

            # Check for end token
            if next_token[0, 0].item() == self.processor.tokenizer.eos_token_id:
                break

            # Append to input for next iteration
            inputs['input_ids'] = torch.cat([inputs['input_ids'], next_token], dim=1)
            if 'attention_mask' in inputs:
                inputs['attention_mask'] = torch.cat([
                    inputs['attention_mask'],
                    torch.ones((1, 1), device=self.device, dtype=inputs['attention_mask'].dtype)
                ], dim=1)

        # Decode tokens to text
        generated_text = self.processor.tokenizer.decode(generated_tokens)

        # Parse actions
        import re
        numbers = re.findall(r'\d+', generated_text)
        if len(numbers) >= self.config.action_dim:
            action_tokens = np.array([int(n) for n in numbers[:self.config.action_dim]])
        else:
            action_tokens = np.zeros(self.config.action_dim)

        # Compute confidence from token probabilities
        confidence = np.mean(token_probs) if token_probs else 0.0

        return {
            'tokens': generated_tokens,
            'action_tokens': action_tokens,
            'text': generated_text,
            'token_probs': token_probs,
            'confidence': confidence
        }


# Usage
generator = AutoregressiveActionGenerator(model, processor, config)

result = generator.generate(
    image,
    instruction="pick up the red block",
    temperature=0.7,
    top_k=50
)

print(f"Generated text: {result['text']}")
print(f"Action tokens: {result['action_tokens']}")
print(f"Confidence: {result['confidence']:.2f}")
```

---

## 5.4 Caching for Efficiency

Cache intermediate computations:

```python
from collections import OrderedDict
import hashlib

class VLACache:
    """LRU cache for VLA computations."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _compute_key(self, image: Image.Image, instruction: str) -> str:
        """Compute cache key from inputs."""
        # Hash image content
        img_bytes = image.tobytes()
        img_hash = hashlib.md5(img_bytes).hexdigest()[:8]

        # Hash instruction
        instr_hash = hashlib.md5(instruction.encode()).hexdigest()[:8]

        return f"{img_hash}_{instr_hash}"

    def get(self, image: Image.Image, instruction: str):
        """Get cached result if available."""
        key = self._compute_key(image, instruction)

        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

        self.misses += 1
        return None

    def put(self, image: Image.Image, instruction: str, result):
        """Cache a result."""
        key = self._compute_key(image, instruction)

        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # Remove oldest
                self.cache.popitem(last=False)
            self.cache[key] = result

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache)
        }

    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0


class CachedVLAPipeline(VLAPipeline):
    """VLA pipeline with caching."""

    def __init__(self, config: VLAConfig, cache_size: int = 100):
        super().__init__(config)
        self.cache = VLACache(max_size=cache_size)

        # Also cache intermediate computations
        self.image_embedding_cache = VLACache(max_size=cache_size)

    def predict(
        self,
        image: Union[Image.Image, np.ndarray],
        instruction: str,
        state: Optional[np.ndarray] = None,
        use_cache: bool = True
    ) -> VLAOutput:
        """Predict with optional caching."""
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Check cache
        if use_cache:
            cached = self.cache.get(image, instruction)
            if cached is not None:
                cached.metadata['cache_hit'] = True
                return cached

        # Run inference
        result = super().predict(image, instruction, state)

        # Cache result
        if use_cache:
            self.cache.put(image, instruction, result)
            result.metadata['cache_hit'] = False

        return result

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return self.cache.get_stats()


# Usage
cached_pipeline = CachedVLAPipeline(config, cache_size=100)

# First call - cache miss
result1 = cached_pipeline.predict(image, instruction)
print(f"First call latency: {result1.latency_ms:.1f} ms")

# Second call with same inputs - cache hit
result2 = cached_pipeline.predict(image, instruction)
print(f"Second call (cached): {result2.metadata.get('cache_hit', False)}")

# Check stats
stats = cached_pipeline.get_cache_stats()
print(f"Cache stats: {stats}")
```

---

## 5.5 Pipeline Profiling

Profile performance bottlenecks:

```python
import time
from contextlib import contextmanager
from typing import Dict, List
import torch

class PipelineProfiler:
    """Profile VLA pipeline performance."""

    def __init__(self):
        self.timings = {}
        self.memory_snapshots = []

    @contextmanager
    def timer(self, name: str):
        """Time a code block."""
        start = time.perf_counter()
        yield
        elapsed = (time.perf_counter() - start) * 1000  # ms

        if name not in self.timings:
            self.timings[name] = []
        self.timings[name].append(elapsed)

    def snapshot_memory(self, label: str):
        """Snapshot GPU memory usage."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            self.memory_snapshots.append({
                'label': label,
                'allocated_gb': allocated,
                'reserved_gb': reserved
            })

    def get_report(self) -> Dict:
        """Generate profiling report."""
        report = {}

        for name, times in self.timings.items():
            report[name] = {
                'mean_ms': np.mean(times),
                'std_ms': np.std(times),
                'min_ms': np.min(times),
                'max_ms': np.max(times),
                'count': len(times)
            }

        # Total time
        all_times = list(self.timings.values())
        if all_times:
            report['total'] = {
                'mean_ms': sum(np.mean(t) for t in all_times),
            }

        report['memory'] = self.memory_snapshots

        return report

    def print_report(self):
        """Print formatted report."""
        report = self.get_report()

        print("\n" + "=" * 60)
        print("VLA Pipeline Profiling Report")
        print("=" * 60)

        # Timing breakdown
        print("\nTiming Breakdown:")
        print("-" * 40)

        total = report.get('total', {}).get('mean_ms', 0)

        for name, stats in report.items():
            if name in ['total', 'memory']:
                continue
            pct = (stats['mean_ms'] / total * 100) if total > 0 else 0
            print(f"  {name:25s}: {stats['mean_ms']:7.2f} ms ({pct:5.1f}%)")

        print("-" * 40)
        print(f"  {'Total':25s}: {total:7.2f} ms")

        # Memory
        if report['memory']:
            print("\nMemory Usage:")
            print("-" * 40)
            for snap in report['memory']:
                print(f"  {snap['label']:25s}: {snap['allocated_gb']:.2f} GB allocated")

    def reset(self):
        """Reset profiler."""
        self.timings.clear()
        self.memory_snapshots.clear()


class ProfiledVLAPipeline(VLAPipeline):
    """VLA pipeline with profiling."""

    def __init__(self, config: VLAConfig):
        self.profiler = PipelineProfiler()
        super().__init__(config)

    def predict(
        self,
        image: Union[Image.Image, np.ndarray],
        instruction: str,
        state: Optional[np.ndarray] = None,
        profile: bool = True
    ) -> VLAOutput:
        """Predict with profiling."""
        if not profile:
            return super().predict(image, instruction, state)

        self.profiler.snapshot_memory("start")

        # Preprocess image
        with self.profiler.timer("image_preprocess"):
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)

        # Prepare inputs
        with self.profiler.timer("tokenize"):
            prompt = f"In: What action should the robot take to {instruction}?\nOut:"
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

        self.profiler.snapshot_memory("after_preprocess")

        # Model inference
        with self.profiler.timer("model_forward"):
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=20,
                    do_sample=False,
                )

        self.profiler.snapshot_memory("after_inference")

        # Decode and parse
        with self.profiler.timer("decode"):
            generated_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            actions, action_tokens, confidence = self._parse_action_output(generated_text)

        return VLAOutput(
            actions=actions,
            action_tokens=action_tokens,
            confidence=confidence,
            latency_ms=sum(self.profiler.timings.get(k, [0])[-1] for k in self.profiler.timings),
            metadata={'profiled': True}
        )


# Usage
profiled_pipeline = ProfiledVLAPipeline(config)

# Run multiple inferences
for i in range(10):
    result = profiled_pipeline.predict(image, instruction)

# Print profiling report
profiled_pipeline.profiler.print_report()
```

---

## 5.6 Model Quantization

Reduce memory and improve speed with quantization:

```python
def load_quantized_model(
    model_path: str,
    bits: int = 4,
    device: str = "cuda"
) -> tuple:
    """
    Load quantized VLA model.

    Args:
        model_path: HuggingFace model path
        bits: Quantization bits (4 or 8)
        device: Target device

    Returns:
        (model, processor)
    """
    from transformers import AutoModelForVision2Seq, AutoProcessor, BitsAndBytesConfig

    print(f"Loading {bits}-bit quantized model...")

    # Configure quantization
    if bits == 4:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    elif bits == 8:
        quant_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )
    else:
        raise ValueError(f"Unsupported bits: {bits}")

    # Load model
    model = AutoModelForVision2Seq.from_pretrained(
        model_path,
        quantization_config=quant_config,
        device_map="auto",
        low_cpu_mem_usage=True,
    )

    processor = AutoProcessor.from_pretrained(model_path)

    # Report memory
    if torch.cuda.is_available():
        memory_gb = torch.cuda.max_memory_allocated() / 1e9
        print(f"Model memory: {memory_gb:.2f} GB ({bits}-bit)")

    return model, processor


def compare_quantization(model_path: str, image: Image.Image, instruction: str):
    """Compare different quantization levels."""
    results = {}

    for bits in [None, 8, 4]:
        print(f"\n{'='*40}")
        print(f"Testing {bits or 'FP16'} quantization")
        print('='*40)

        if bits:
            model, processor = load_quantized_model(model_path, bits)
        else:
            from transformers import AutoModelForVision2Seq, AutoProcessor
            model = AutoModelForVision2Seq.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            processor = AutoProcessor.from_pretrained(model_path)

        # Warmup
        for _ in range(3):
            inputs = processor(text="test", images=image, return_tensors="pt")
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
            with torch.no_grad():
                _ = model.generate(**inputs, max_new_tokens=10)

        # Benchmark
        times = []
        for _ in range(10):
            inputs = processor(
                text=f"In: What action should the robot take to {instruction}?\nOut:",
                images=image,
                return_tensors="pt"
            )
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

            start = time.perf_counter()
            with torch.no_grad():
                outputs = model.generate(**inputs, max_new_tokens=20)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - start) * 1000)

        memory_gb = torch.cuda.max_memory_allocated() / 1e9

        results[bits or 'fp16'] = {
            'mean_ms': np.mean(times),
            'std_ms': np.std(times),
            'memory_gb': memory_gb
        }

        print(f"Latency: {np.mean(times):.1f} +/- {np.std(times):.1f} ms")
        print(f"Memory: {memory_gb:.2f} GB")

        # Clean up
        del model
        torch.cuda.empty_cache()

    return results
```

---

## 5.7 Summary

In this chapter, you learned:

1. **Pipeline Architecture**: End-to-end design from inputs to actions
2. **Core Implementation**: VLAPipeline class with preprocessing and inference
3. **Autoregressive Generation**: Token-by-token control with sampling
4. **Caching**: LRU cache for repeated inputs
5. **Profiling**: Identifying performance bottlenecks
6. **Quantization**: 4-bit and 8-bit models for efficiency

---

## 5.8 Exercises

### Exercise 5.1: Pipeline Setup
Implement the basic VLAPipeline and test on sample images.

### Exercise 5.2: Profiling
Profile your pipeline and identify the slowest component.

### Exercise 5.3: Caching Strategy
Implement instruction-level caching for repeated commands.

### Exercise 5.4: Quantization Comparison
Compare FP16, INT8, and INT4 models for latency and accuracy.

---

## Quick Reference

### Pipeline Initialization
```python
config = VLAConfig(model_path="openvla/openvla-7b", use_quantization=True)
pipeline = VLAPipeline(config)
```

### Inference
```python
output = pipeline.predict(image, instruction)
actions = output.actions  # (1, 7) numpy array
```

### Profiling
```python
profiled = ProfiledVLAPipeline(config)
result = profiled.predict(image, instruction)
profiled.profiler.print_report()
```

---

**Next Chapter**: [Chapter 6 - ROS 2 VLA Node Implementation](ch06-ros2-integration.md)
