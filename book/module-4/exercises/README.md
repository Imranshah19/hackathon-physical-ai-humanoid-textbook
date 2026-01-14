# Module 4 Exercises

This directory contains hands-on exercises for Module 4: Vision-Language-Action Models for Humanoids.

## Exercise Overview

| Exercise | Chapter | Topic | Duration |
|----------|---------|-------|----------|
| 4.1 | Ch 1 | VLA Model Setup | 1-2 hours |
| 4.2 | Ch 2 | CLIP Feature Extraction | 2-3 hours |
| 4.3 | Ch 3 | Action Tokenization | 2-3 hours |
| 4.4 | Ch 4 | Language Grounding | 2-3 hours |
| 4.5 | Ch 5 | VLA Pipeline | 3-4 hours |
| 4.6 | Ch 6 | ROS 2 Integration | 3-4 hours |
| 4.7 | Ch 7 | Safety Constraints | 2-3 hours |
| 4.8 | Ch 8 | LoRA Fine-tuning | 4-6 hours |
| 4.9 | Ch 9 | Evaluation Benchmarks | 2-3 hours |
| 4.10 | Ch 10 | End-to-End Demo | 4-6 hours |

---

## Exercise 4.1: VLA Model Setup

**Objective**: Install and verify OpenVLA model

### Prerequisites

- NVIDIA GPU with 24GB+ VRAM (or 16GB with quantization)
- CUDA 11.8+
- Python 3.10+

### Tasks

1. Install required packages
2. Download OpenVLA model
3. Configure 4-bit quantization
4. Run basic inference test
5. Verify action output format

### Setup Commands

```bash
# Create environment
conda create -n vla python=3.10
conda activate vla

# Install packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install transformers>=4.40.0 accelerate bitsandbytes peft
pip install pillow numpy opencv-python
```

### Verification

```python
from transformers import AutoModelForVision2Seq, AutoProcessor

model_name = "openvla/openvla-7b"
processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)

print(f"Processor loaded: {processor}")
print(f"Image size: {processor.image_processor.size}")
```

### Deliverables

- [ ] Working Python environment
- [ ] Successful model download
- [ ] Test inference output
- [ ] Memory usage report

---

## Exercise 4.2: CLIP Feature Extraction

**Objective**: Extract and analyze CLIP visual embeddings

### Tasks

1. Load CLIP ViT-L/14 model
2. Extract features from sample images
3. Compute image-text similarity
4. Visualize attention patterns
5. Analyze embedding space

### Code Template

```python
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

# Load image
image = Image.open("robot_scene.jpg")

# Process
inputs = processor(
    text=["a red cube", "a blue sphere", "robot arm"],
    images=image,
    return_tensors="pt",
    padding=True
)

# Extract features
outputs = model(**inputs)
image_embeds = outputs.image_embeds  # (1, 768)
text_embeds = outputs.text_embeds    # (3, 768)

# Compute similarities
similarity = (image_embeds @ text_embeds.T).softmax(dim=-1)
print(f"Similarities: {similarity}")
```

### Experiments

| Object | CLIP Score | Ground Truth |
|--------|------------|--------------|
| Red cube | | Present/Absent |
| Blue sphere | | Present/Absent |
| Robot arm | | Present/Absent |

### Deliverables

- [ ] Feature extraction code
- [ ] Similarity matrix for 10 images
- [ ] Attention visualization
- [ ] Embedding t-SNE plot

---

## Exercise 4.3: Action Tokenization

**Objective**: Implement and test action tokenizers

### Tasks

1. Build bin-based tokenizer (256 bins)
2. Implement K-means tokenizer
3. Compare reconstruction accuracy
4. Test with real robot trajectories
5. Analyze quantization error

### Tokenizer Comparison

```python
import numpy as np

class BinTokenizer:
    def __init__(self, num_bins=256, action_range=(-1, 1)):
        self.num_bins = num_bins
        self.action_range = action_range

    def encode(self, action):
        normalized = (action - self.action_range[0]) / \
                    (self.action_range[1] - self.action_range[0])
        tokens = (normalized * (self.num_bins - 1)).astype(int)
        return np.clip(tokens, 0, self.num_bins - 1)

    def decode(self, tokens):
        normalized = tokens / (self.num_bins - 1)
        return normalized * (self.action_range[1] - self.action_range[0]) + \
               self.action_range[0]
```

### Accuracy Analysis

| Tokenizer | Bins/Clusters | RMSE | Max Error |
|-----------|---------------|------|-----------|
| Bin-based | 256 | | |
| Bin-based | 512 | | |
| K-means | 256 | | |
| K-means | 512 | | |

### Deliverables

- [ ] Both tokenizer implementations
- [ ] Accuracy comparison table
- [ ] Error distribution plots
- [ ] Recommendations for action_dim=22

---

## Exercise 4.4: Language Grounding

**Objective**: Implement object detection and referring expressions

### Tasks

1. Set up YOLO object detection
2. Implement referring expression parser
3. Build grounding pipeline
4. Handle spatial relationships
5. Test with ambiguous instructions

### Code Template

```python
from ultralytics import YOLO
import spacy

# Object detection
yolo = YOLO("yolov8m.pt")

# NLP
nlp = spacy.load("en_core_web_sm")

def ground_instruction(image, instruction):
    # Detect objects
    results = yolo(image)
    objects = parse_detections(results)

    # Parse instruction
    doc = nlp(instruction)
    target = extract_target_object(doc)

    # Match
    grounded_object = match_object(target, objects)
    return grounded_object
```

### Test Cases

| Instruction | Expected Target | Spatial Relation |
|-------------|-----------------|------------------|
| "Pick up the red cube" | red cube | none |
| "Move to the left of the table" | table | left_of |
| "Put the ball on the box" | ball, box | on_top |
| "Get the closest apple" | apple | nearest |

### Deliverables

- [ ] Grounding pipeline implementation
- [ ] Test results for 20 instructions
- [ ] Error analysis
- [ ] Spatial relationship handler

---

## Exercise 4.5: VLA Pipeline

**Objective**: Build complete VLA inference pipeline

### Tasks

1. Implement VLAPipeline class
2. Add image preprocessing
3. Configure KV-cache
4. Add inference profiling
5. Test end-to-end latency

### Pipeline Architecture

```
Image → Preprocess → Vision Encoder → Fusion → LLM → Action Decoder → Robot
                          ↑
                    Instruction
```

### Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| First token latency | < 100ms | |
| Total latency | < 200ms | |
| Memory usage | < 16GB | |
| Throughput | > 5 Hz | |

### Profiling

```python
import time
import torch

with torch.profiler.profile(
    activities=[torch.profiler.ProfilerActivity.CPU,
                torch.profiler.ProfilerActivity.CUDA],
) as prof:
    output = pipeline.predict(image, instruction)

print(prof.key_averages().table())
```

### Deliverables

- [ ] VLAPipeline class
- [ ] Profiling results
- [ ] Latency breakdown chart
- [ ] Memory optimization report

---

## Exercise 4.6: ROS 2 Integration

**Objective**: Deploy VLA as ROS 2 node

### Tasks

1. Create VLA ROS 2 package
2. Define custom messages
3. Implement VLANode
4. Add camera subscriber
5. Test with simulated robot

### Message Definitions

```
# VLACommand.msg
string instruction
bool active

# VLAAction.msg
float32[] joint_positions
float32 confidence
string status
```

### ROS 2 Package Structure

```
vla_ros/
├── CMakeLists.txt
├── package.xml
├── msg/
│   ├── VLACommand.msg
│   └── VLAAction.msg
├── src/
│   └── vla_node.py
└── launch/
    └── vla.launch.py
```

### Test Commands

```bash
# Build
cd ~/ros2_ws && colcon build --packages-select vla_ros

# Launch
ros2 launch vla_ros vla.launch.py

# Send command
ros2 topic pub /vla/command vla_ros/msg/VLACommand "{instruction: 'pick up the red cube', active: true}"
```

### Deliverables

- [ ] Complete ROS 2 package
- [ ] Working message definitions
- [ ] Test with simulated camera
- [ ] Latency measurements

---

## Exercise 4.7: Safety Constraints

**Objective**: Implement multi-layer safety filter

### Tasks

1. Implement joint limit checking
2. Add velocity limiting
3. Implement workspace bounds
4. Add confidence filtering
5. Test emergency stop

### Safety Layers

```python
class SafetyFilter:
    def filter(self, action, state, confidence):
        # Layer 1: Confidence check
        if confidence < 0.3:
            action = action * (confidence / 0.5)

        # Layer 2: Joint limits
        action = np.clip(action, self.joint_min, self.joint_max)

        # Layer 3: Velocity limit
        action = self.limit_velocity(action)

        # Layer 4: Workspace check
        if not self.in_workspace(action):
            action = self.project_to_workspace(action)

        return action
```

### Test Scenarios

| Scenario | Input | Expected Output | Pass/Fail |
|----------|-------|-----------------|-----------|
| Low confidence (0.2) | Normal action | Scaled action | |
| Joint limit violation | [3.0, ...] | [2.0, ...] | |
| High velocity | Large delta | Clamped delta | |
| Outside workspace | x=2.0m | x=1.0m | |

### Deliverables

- [ ] SafetyFilter implementation
- [ ] Unit tests for all layers
- [ ] Integration test results
- [ ] Safety documentation

---

## Exercise 4.8: LoRA Fine-tuning

**Objective**: Fine-tune VLA with LoRA for custom task

### Tasks

1. Collect demonstration data (50 episodes)
2. Prepare dataset in HDF5 format
3. Configure LoRA (rank=16)
4. Train for 5 epochs
5. Evaluate fine-tuned model

### Data Collection

```python
import h5py
import numpy as np

def collect_demonstration(env, task_instruction):
    episode = {
        'images': [],
        'actions': [],
        'states': [],
    }

    obs = env.reset()
    done = False

    while not done:
        # Get human action (teleoperation)
        action = get_human_action()

        episode['images'].append(obs['image'])
        episode['actions'].append(action)
        episode['states'].append(obs['state'])

        obs, _, done, _ = env.step(action)

    return episode
```

### Training Configuration

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
```

### Evaluation Metrics

| Metric | Before Fine-tuning | After Fine-tuning |
|--------|-------------------|-------------------|
| Success rate | | |
| Action RMSE | | |
| Task completion time | | |

### Deliverables

- [ ] Demonstration dataset (50 episodes)
- [ ] LoRA training script
- [ ] Fine-tuned adapter weights
- [ ] Comparison evaluation

---

## Exercise 4.9: Evaluation Benchmarks

**Objective**: Evaluate VLA performance systematically

### Tasks

1. Define benchmark tasks (5 tasks)
2. Implement evaluation runner
3. Collect metrics over 100 trials
4. Perform failure analysis
5. Generate evaluation report

### Benchmark Tasks

| Task | Instruction | Success Criteria |
|------|-------------|------------------|
| Pick red cube | "Pick up the red cube" | Cube lifted 10cm |
| Place on table | "Put the cube on the table" | Cube stable on table |
| Open drawer | "Open the drawer" | Drawer open > 15cm |
| Pour water | "Pour water into the cup" | Water in cup |
| Stack blocks | "Stack the blocks" | 3 blocks stacked |

### Evaluation Runner

```python
def evaluate_task(vla, env, task, num_trials=100):
    results = []
    for trial in range(num_trials):
        obs = env.reset()
        success = False

        for step in range(max_steps):
            action = vla.predict(obs['image'], task.instruction)
            obs, reward, done, info = env.step(action)

            if task.check_success(obs):
                success = True
                break

        results.append({
            'success': success,
            'steps': step,
            'final_state': obs
        })

    return results
```

### Metrics

| Task | Success Rate | Avg Steps | Latency (ms) |
|------|--------------|-----------|--------------|
| Pick | | | |
| Place | | | |
| Open | | | |
| Pour | | | |
| Stack | | | |

### Deliverables

- [ ] Benchmark task definitions
- [ ] Evaluation runner
- [ ] Results for 100 trials per task
- [ ] Failure mode analysis

---

## Exercise 4.10: End-to-End Demo

**Objective**: Build complete VLA demo application

### Tasks

1. Set up demo environment
2. Create interactive UI
3. Integrate all components
4. Add visual feedback
5. Record demo video

### Demo Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Demo Application                  │
├──────────────┬──────────────┬───────────────────────┤
│   Camera     │     VLA      │      Robot            │
│   Input      │   Pipeline   │      Control          │
├──────────────┼──────────────┼───────────────────────┤
│   UI/Display │   Safety     │      Status           │
│              │   Filter     │      Monitor          │
└──────────────┴──────────────┴───────────────────────┘
```

### Demo Scenarios

1. **Object Manipulation**: Pick, place, stack
2. **Tool Use**: Use hammer, screwdriver
3. **Multi-step Tasks**: Make coffee sequence
4. **Error Recovery**: Handle failures gracefully

### UI Features

```python
import gradio as gr

def create_demo_ui(vla_pipeline):
    with gr.Blocks() as demo:
        with gr.Row():
            camera_view = gr.Image(label="Camera Feed")
            instruction = gr.Textbox(label="Instruction")

        with gr.Row():
            action_display = gr.JSON(label="Predicted Action")
            confidence = gr.Number(label="Confidence")

        submit_btn = gr.Button("Execute")
        submit_btn.click(
            fn=vla_pipeline.predict,
            inputs=[camera_view, instruction],
            outputs=[action_display, confidence]
        )

    return demo
```

### Demo Checklist

- [ ] Camera feed working
- [ ] VLA inference responsive (< 200ms)
- [ ] Safety filter active
- [ ] Visual feedback clear
- [ ] Error handling robust
- [ ] Demo video recorded (2-3 min)

### Deliverables

- [ ] Complete demo application
- [ ] User documentation
- [ ] Demo video
- [ ] Performance metrics

---

## Submission Guidelines

1. Create separate directory for each exercise
2. Include all code files with comments
3. Add README with setup and results
4. Include screenshots/videos where applicable
5. Document any issues or limitations

## Grading Criteria

| Criterion | Points |
|-----------|--------|
| Code completeness | 30 |
| Correct implementation | 30 |
| Results quality | 20 |
| Documentation | 20 |

Total: 100 points per exercise

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU VRAM | 16GB (quantized) | 24GB+ |
| System RAM | 32GB | 64GB |
| Storage | 50GB | 100GB |
| CUDA | 11.8 | 12.0+ |

## Troubleshooting

### Out of Memory

```python
# Enable gradient checkpointing
model.gradient_checkpointing_enable()

# Use 4-bit quantization
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(load_in_4bit=True)
```

### Slow Inference

```python
# Enable KV-cache
outputs = model.generate(..., use_cache=True)

# Use Flash Attention 2
model = AutoModel.from_pretrained(..., attn_implementation="flash_attention_2")
```

### Import Errors

```bash
# Update transformers
pip install transformers --upgrade

# Install missing dependencies
pip install accelerate bitsandbytes peft sentencepiece
```
