# Chapter 1: Introduction to Vision-Language-Action Models

**Duration**: 3-4 hours
**Prerequisites**: Module 3 (NVIDIA Isaac), Basic understanding of transformers

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Explain what Vision-Language-Action (VLA) models are and why they matter
- Describe the evolution from traditional robot control to end-to-end learning
- Compare key VLA architectures: RT-1, RT-2, OpenVLA, and PaLM-E
- Run OpenVLA inference on sample data
- Visualize attention patterns in VLA models

---

## 1.1 The Vision for Embodied AI

Traditional robot programming requires explicit instructions for every possible situation. A pick-and-place task might need thousands of lines of code handling edge cases. What if robots could understand commands like humans do?

**Vision-Language-Action (VLA) models** enable this by:
- Understanding natural language commands ("pick up the red block")
- Perceiving the visual scene (identifying the red block)
- Generating appropriate robot actions (arm trajectory to grasp)

```
┌─────────────────────────────────────────────────────────────────┐
│                Traditional vs VLA Approach                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Traditional Robotics:                                          │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐     │
│  │ Perception│→│ Planning │→│ Control  │→│ Execution│     │
│  │ Module   │   │ Module   │   │ Module   │   │ Module   │     │
│  └─────────┘   └──────────┘   └──────────┘   └──────────┘     │
│       ↑              ↑              ↑              ↑           │
│  [Hand-crafted rules and parameters for each module]           │
│                                                                  │
│  VLA Approach:                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              End-to-End Neural Network                   │   │
│  │   Image + Text + State  ───→  Robot Actions             │   │
│  │         (Learned from demonstrations)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Why VLA Models Matter

| Advantage | Description |
|-----------|-------------|
| **Generalization** | Transfer knowledge from web data to robot tasks |
| **Zero-shot** | Perform new tasks without task-specific training |
| **Natural Interface** | Accept human language commands directly |
| **Adaptability** | Learn from demonstrations without hand-coding |
| **Scalability** | Improve with more data and compute |

---

## 1.2 Evolution of Robot Learning

### Phase 1: Classical Robotics (1960s-2000s)

- **Hand-coded control**: Every movement explicitly programmed
- **Perception pipelines**: Feature extraction → Object recognition → Planning
- **Limitation**: Brittle to variations, massive engineering effort

### Phase 2: Learning-Based Approaches (2000s-2015)

- **Imitation learning**: Learn from human demonstrations
- **Reinforcement learning**: Learn from trial and error
- **Limitation**: Required task-specific training, poor generalization

### Phase 3: Deep Learning for Robotics (2015-2020)

- **End-to-end visuomotor policies**: Direct image-to-action mapping
- **Sim-to-real transfer**: Train in simulation, deploy on hardware
- **Limitation**: Still required extensive robot-specific data

### Phase 4: Foundation Models for Robotics (2020-Present)

- **Vision-Language Models (VLMs)**: CLIP, LLaVA, GPT-4V
- **Large Language Models (LLMs)**: GPT-4, PaLM, LLaMA
- **Vision-Language-Action (VLAs)**: RT-1, RT-2, OpenVLA

```python
# Evolution in code complexity

# Phase 1: Classical (hundreds of lines per task)
def pick_object_classical(obj_pose, gripper):
    approach_pose = compute_approach(obj_pose)
    pre_grasp = plan_motion(current_pose, approach_pose)
    grasp = compute_grasp_pose(obj_pose, gripper)
    # ... many more steps

# Phase 4: VLA (single model call)
def pick_object_vla(image, instruction, state):
    return vla_model.predict(image, instruction, state)
```

---

## 1.3 Key VLA Architectures

### RT-1: Robotics Transformer (Google, 2022)

RT-1 was the first large-scale robot transformer, trained on 130k demonstrations across 700+ tasks.

**Architecture**:
- **Input**: 6 camera images (current + 5 history) + text instruction
- **Backbone**: EfficientNet (vision) + FiLM conditioning (language)
- **Output**: Discretized actions (8 bins per dimension)

**Key Innovation**: Demonstrated that transformer architectures scale for robot learning.

```
RT-1 Architecture:
┌───────────────────────────────────────────────────┐
│  Images (6x)  ──→ EfficientNet ──→ Token Sequence │
│                                         ↓         │
│  Instruction  ──→ USE Encoder ──→ FiLM Layers    │
│                                         ↓         │
│                              Transformer Decoder  │
│                                         ↓         │
│                              Action Tokens (256)  │
└───────────────────────────────────────────────────┘
```

### RT-2: Vision-Language-Action Model (Google, 2023)

RT-2 showed that pre-trained VLMs can be fine-tuned for robot control, transferring web knowledge to physical tasks.

**Architecture**:
- **Backbone**: PaLM-E (55B) or PaLI-X (55B) VLM
- **Input**: Image + instruction + robot state
- **Output**: Actions expressed as text tokens

**Key Innovation**: Web-scale pretraining transfers to robot tasks (emergent capabilities like reasoning about object relationships).

```python
# RT-2 treats actions as language tokens
# Instead of: [0.1, 0.2, 0.05, ...]  (continuous)
# RT-2 outputs: "1 128 50 ..."        (text tokens)

# Example output sequence:
# "The robot should move to position token_x=128, token_y=50,
#  token_z=200, grasp=CLOSE"
```

### PaLM-E: Embodied Multimodal Language Model (Google, 2023)

PaLM-E is a 562B parameter model that integrates continuous sensor data directly into language models.

**Architecture**:
- **Backbone**: PaLM (540B) language model
- **Vision Encoder**: ViT-22B
- **Multimodal Tokens**: Sensor data embedded as "soft" tokens

**Key Innovation**: Single model for multiple embodiments and task types.

### OpenVLA: Open-Source VLA (Berkeley, 2024)

OpenVLA provides an accessible, open-source implementation of VLA principles.

**Architecture**:
- **Backbone**: LLaVA-style (Vicuna-7B + CLIP ViT-L)
- **Training**: Open X-Embodiment dataset (970k trajectories)
- **Size**: 7B parameters (runnable on consumer GPUs)

**Key Innovation**: Open weights, code, and training recipes for research.

```python
# OpenVLA is accessible to run
from transformers import AutoModelForVision2Seq, AutoProcessor

model = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b",
    torch_dtype=torch.float16
)
```

### Architecture Comparison

| Model | Parameters | Vision | Language | Open Source |
|-------|------------|--------|----------|-------------|
| RT-1 | ~35M | EfficientNet | USE | No |
| RT-2 | 55B | ViT-22B | PaLM-E | No |
| PaLM-E | 562B | ViT-22B | PaLM | No |
| OpenVLA | 7B | CLIP ViT-L | Vicuna-7B | Yes |

---

## 1.4 How VLA Models Work

### Input Processing

VLA models process three types of input:

```python
class VLAInput:
    """Standard VLA input format"""

    def __init__(self):
        # Visual input: camera image(s)
        self.image: np.ndarray  # Shape: (H, W, 3) or (T, H, W, 3)

        # Language input: natural language instruction
        self.instruction: str  # e.g., "pick up the red block"

        # Proprioceptive input: robot state
        self.state: np.ndarray  # Joint positions, velocities, etc.
```

### Tokenization

All inputs are converted to tokens for the transformer:

```python
def tokenize_inputs(image, instruction, state):
    """Convert multimodal inputs to tokens"""

    # Image → patch tokens via ViT
    image_tokens = vision_encoder(image)  # (num_patches, hidden_dim)

    # Text → word tokens via tokenizer
    text_tokens = text_encoder(instruction)  # (seq_len, hidden_dim)

    # State → embedded vector
    state_tokens = state_encoder(state)  # (1, hidden_dim)

    # Concatenate all tokens
    return torch.cat([image_tokens, text_tokens, state_tokens], dim=0)
```

### Action Generation

Actions are generated autoregressively as tokens:

```python
def generate_actions(model, input_tokens, num_action_tokens=7):
    """Generate action tokens autoregressively"""

    generated = []
    for _ in range(num_action_tokens):
        # Get next token probabilities
        logits = model(input_tokens)

        # Sample or argmax
        next_token = torch.argmax(logits[:, -1, :], dim=-1)
        generated.append(next_token)

        # Append to input for next iteration
        input_tokens = torch.cat([input_tokens, next_token.unsqueeze(1)], dim=1)

    return torch.stack(generated)
```

### Action Detokenization

Discrete tokens are converted back to continuous actions:

```python
def detokenize_actions(action_tokens, tokenizer):
    """Convert action tokens to continuous values"""

    actions = []
    for i, token in enumerate(action_tokens):
        # Get action dimension (x, y, z, rx, ry, rz, gripper)
        dim = i % 7

        # Map token (0-255) to action range
        action_range = ACTION_RANGES[dim]
        value = action_range[0] + (token / 255) * (action_range[1] - action_range[0])
        actions.append(value)

    return np.array(actions)
```

---

## 1.5 Hands-On: Running OpenVLA

### Setup Environment

```bash
# Create virtual environment
python -m venv vla_env
source vla_env/bin/activate

# Install dependencies
pip install torch torchvision transformers
pip install accelerate bitsandbytes
pip install pillow numpy
```

### Download and Load Model

```python
import torch
from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load model (requires ~16GB VRAM)
model = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b",
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True
)

# Load processor
processor = AutoProcessor.from_pretrained("openvla/openvla-7b")

print("Model loaded successfully!")
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
```

### Run Inference

```python
def run_vla_inference(image_path, instruction):
    """Run VLA inference on image with instruction"""

    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")

    # Format prompt
    prompt = f"In: What action should the robot take to {instruction}?\nOut:"

    # Process inputs
    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(device, torch.float16)

    # Generate action tokens
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False
        )

    # Decode output
    action_text = processor.decode(outputs[0], skip_special_tokens=True)

    return action_text


# Example usage
image_path = "test_scene.jpg"  # Your test image
instruction = "pick up the red block"

result = run_vla_inference(image_path, instruction)
print(f"VLA Output: {result}")
```

### Parse Action Output

```python
import re

def parse_action_output(action_text):
    """Parse VLA text output to action values"""

    # OpenVLA outputs actions as space-separated integers
    # Format: "x y z rx ry rz gripper"

    # Extract numbers from output
    numbers = re.findall(r'\d+', action_text.split("Out:")[-1])

    if len(numbers) >= 7:
        tokens = [int(n) for n in numbers[:7]]

        # Convert tokens to continuous actions
        actions = {
            'x': (tokens[0] / 255) * 0.4 - 0.2,      # [-0.2, 0.2]
            'y': (tokens[1] / 255) * 0.4 - 0.2,      # [-0.2, 0.2]
            'z': (tokens[2] / 255) * 0.4 - 0.2,      # [-0.2, 0.2]
            'rx': (tokens[3] / 255) * 0.2 - 0.1,    # [-0.1, 0.1]
            'ry': (tokens[4] / 255) * 0.2 - 0.1,    # [-0.1, 0.1]
            'rz': (tokens[5] / 255) * 0.2 - 0.1,    # [-0.1, 0.1]
            'gripper': 1.0 if tokens[6] > 127 else 0.0
        }
        return actions

    return None


# Parse the result
actions = parse_action_output(result)
if actions:
    print(f"Parsed actions: {actions}")
```

---

## 1.6 Visualizing VLA Attention

Understanding what the model "sees" helps debug and improve performance.

### Extract Attention Weights

```python
def get_attention_maps(model, processor, image, instruction):
    """Extract attention maps from VLA model"""

    # Process inputs
    prompt = f"In: What action should the robot take to {instruction}?\nOut:"
    inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(device, torch.float16)

    # Forward pass with attention output
    with torch.no_grad():
        outputs = model(
            **inputs,
            output_attentions=True,
            return_dict=True
        )

    # Get attention from last layer
    # Shape: (batch, num_heads, seq_len, seq_len)
    attentions = outputs.attentions[-1]

    return attentions


def visualize_image_attention(attentions, image, patch_size=14):
    """Visualize attention over image patches"""
    import matplotlib.pyplot as plt

    # Average over heads
    attn = attentions[0].mean(dim=0)  # (seq_len, seq_len)

    # Get attention to image tokens (first N tokens)
    num_image_tokens = (image.size[0] // patch_size) * (image.size[1] // patch_size)

    # Attention from action tokens to image tokens
    image_attention = attn[-7:, :num_image_tokens].mean(dim=0)  # (num_image_tokens,)

    # Reshape to 2D
    h = image.size[1] // patch_size
    w = image.size[0] // patch_size
    attention_map = image_attention.reshape(h, w).cpu().numpy()

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].imshow(image)
    axes[0].set_title("Original Image")
    axes[0].axis('off')

    axes[1].imshow(image)
    axes[1].imshow(
        attention_map,
        alpha=0.6,
        cmap='hot',
        interpolation='bilinear',
        extent=[0, image.size[0], image.size[1], 0]
    )
    axes[1].set_title("Attention Overlay")
    axes[1].axis('off')

    plt.tight_layout()
    plt.savefig("attention_visualization.png")
    plt.show()
```

### Interpret Attention Patterns

Good VLA attention typically shows:
- **Object focus**: High attention on task-relevant objects
- **Spatial awareness**: Attention to target locations
- **Gripper tracking**: Attention to end-effector when relevant

```python
# Example analysis
attentions = get_attention_maps(model, processor, image, "pick up the red block")
visualize_image_attention(attentions, image)

# Check if attention focuses on the red block
# High attention values in the red block region indicate good grounding
```

---

## 1.7 Current Limitations and Challenges

### Technical Limitations

| Limitation | Description | Mitigation |
|------------|-------------|------------|
| **Latency** | 0.5-2s inference time | Model quantization, caching |
| **Memory** | 16-24GB VRAM required | 4-bit quantization |
| **Precision** | Action discretization error | Finer bins, learned tokenization |
| **Hallucination** | Invalid actions for scene | Safety filters, confidence thresholds |

### Research Challenges

1. **Data Efficiency**: Current models need 100k+ demonstrations
2. **Long-horizon Tasks**: Struggle with multi-step reasoning
3. **Real-time Control**: Too slow for reactive tasks
4. **Safety**: No inherent understanding of physical constraints

### What's Next

- **Smaller, faster models**: Distillation and efficient architectures
- **Better grounding**: Tighter vision-language alignment
- **World models**: Learning physics for planning
- **Multi-robot**: Coordinated VLA for multiple agents

---

## 1.8 Summary

In this chapter, you learned:

1. **VLA Concept**: Models that map vision + language to robot actions
2. **Evolution**: From hand-coded to end-to-end learned control
3. **Architectures**: RT-1, RT-2, PaLM-E, and OpenVLA
4. **How It Works**: Tokenization → Transformer → Action generation
5. **Practical Usage**: Running OpenVLA inference
6. **Visualization**: Understanding attention patterns
7. **Limitations**: Current challenges and future directions

---

## 1.9 Exercises

### Exercise 1.1: OpenVLA Installation
Install OpenVLA and verify it loads correctly. Document GPU memory usage.

### Exercise 1.2: Inference Testing
Run inference on 5 different images with varied instructions. Analyze the outputs.

### Exercise 1.3: Attention Analysis
Visualize attention for 3 tasks. Does the model attend to the correct objects?

### Exercise 1.4: Architecture Comparison
Create a comparison table of RT-1, RT-2, and OpenVLA with your own analysis.

---

## Quick Reference

### VLA Input Format
```python
image: PIL.Image or np.ndarray (H, W, 3)
instruction: str
state: np.ndarray (optional robot state)
```

### Model Loading
```python
from transformers import AutoModelForVision2Seq, AutoProcessor
model = AutoModelForVision2Seq.from_pretrained("openvla/openvla-7b")
processor = AutoProcessor.from_pretrained("openvla/openvla-7b")
```

### Key Papers
- RT-1: arxiv.org/abs/2212.06817
- RT-2: arxiv.org/abs/2307.15818
- OpenVLA: arxiv.org/abs/2406.09246

---

**Next Chapter**: [Chapter 2 - Vision-Language Model Foundations](ch02-vlm-foundations.md)
