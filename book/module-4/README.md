# Module 4: Physical AI - Vision-Language-Action Models

**Duration**: Weeks 7-8
**Prerequisites**: Module 3 (AI-Robot Brain - NVIDIA Isaac)

---

## Overview

This module teaches how to integrate vision-language models with robot actions for natural language task execution. You will build systems where robots understand multimodal instructions and execute physical tasks in simulation and real-world environments.

**Vision-Language-Action (VLA) Models** enable:
- Natural language understanding for robot commands
- Visual scene interpretation and grounding
- Action sequence generation from instructions
- End-to-end learning from demonstrations
- Zero-shot generalization to new tasks

---

## Learning Objectives

By completing this module, you will be able to:

| ID | Objective | Assessment |
|----|-----------|------------|
| LO-4.1 | Explain VLA architectures and design principles | Quiz |
| LO-4.2 | Set up vision-language model inference pipeline | VLM running |
| LO-4.3 | Implement action tokenization for robot control | Action tokens generated |
| LO-4.4 | Ground language instructions to robot observations | Grounding working |
| LO-4.5 | Build end-to-end VLA inference pipeline | Pipeline processes commands |
| LO-4.6 | Integrate VLA with ROS 2 for robot control | Robot responds to text |
| LO-4.7 | Apply safety constraints to VLA outputs | Constraints enforced |
| LO-4.8 | Fine-tune VLA on custom robot data | Improved task success |
| LO-4.9 | Evaluate VLA performance on manipulation tasks | Metrics computed |
| LO-4.10 | Deploy VLA system for real-time operation | Under 2s latency achieved |

---

## Chapter Overview

| Chapter | Title | Duration | Key Topics |
|---------|-------|----------|------------|
| 1 | [Introduction to VLA Models](chapters/ch01-introduction-vla.md) | 3-4h | RT-1, RT-2, OpenVLA, PaLM-E |
| 2 | [Vision-Language Model Foundations](chapters/ch02-vlm-foundations.md) | 4-5h | CLIP, ViT, Multimodal Fusion |
| 3 | [Action Tokenization](chapters/ch03-action-tokenization.md) | 4-5h | Discretization, Vocabulary Design |
| 4 | [Language Grounding](chapters/ch04-language-grounding.md) | 5-6h | Object Detection, Referring Expressions |
| 5 | [VLA Inference Pipeline](chapters/ch05-vla-pipeline.md) | 5-6h | End-to-End Pipeline, Optimization |
| 6 | [ROS 2 VLA Integration](chapters/ch06-ros2-integration.md) | 5-6h | VLA Node, Real-time Control |
| 7 | [Safety Constraints](chapters/ch07-safety-constraints.md) | 4-5h | Bounds Checking, Confidence Filtering |
| 8 | [Fine-tuning VLA](chapters/ch08-finetuning.md) | 5-6h | LoRA, Demonstration Data |
| 9 | [Evaluation and Benchmarking](chapters/ch09-evaluation.md) | 4-5h | Metrics, Failure Analysis |
| 10 | [End-to-End Demo](chapters/ch10-end-to-end-demo.md) | 4-5h | Complete System Integration |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VLA System Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Camera Image │  │    Text      │  │ Robot State  │              │
│  │    (RGB)     │  │ Instruction  │  │   (Joints)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                       │
│         ▼                 ▼                  ▼                       │
│  ┌──────────────────────────────────────────────────────┐          │
│  │              Vision-Language Model                     │          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │          │
│  │  │   Vision    │  │    Text     │  │  Multimodal  │  │          │
│  │  │   Encoder   │  │   Encoder   │  │    Fusion    │  │          │
│  │  │   (ViT)     │  │(Transformer)│  │ (Cross-Attn) │  │          │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │          │
│  └──────────────────────────┬───────────────────────────┘          │
│                             │                                        │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────┐          │
│  │                  Action Decoder                        │          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │          │
│  │  │   Action    │  │   Action    │  │   Action     │  │          │
│  │  │   Tokens    │  │  Detokenize │  │   Output     │  │          │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │          │
│  └──────────────────────────┬───────────────────────────┘          │
│                             │                                        │
│                             ▼                                        │
│  ┌──────────────────────────────────────────────────────┐          │
│  │                   Safety Layer                         │          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │          │
│  │  │   Bounds    │  │ Confidence  │  │   Action     │  │          │
│  │  │   Check     │  │   Filter    │  │  Smoothing   │  │          │
│  │  └─────────────┘  └─────────────┘  └──────────────┘  │          │
│  └──────────────────────────┬───────────────────────────┘          │
│                             │                                        │
│                             ▼                                        │
│                    ┌──────────────┐                                  │
│                    │ Robot Action │                                  │
│                    │  (Joints)    │                                  │
│                    └──────────────┘                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 8 cores | 16 cores |
| RAM | 32 GB | 64 GB |
| GPU | RTX 3080 (10GB) | RTX 4090 (24GB) |
| VRAM | 16 GB | 24 GB |
| Storage | 200 GB SSD | 500 GB NVMe |

---

## Software Dependencies

```bash
# Core ML Libraries
pip install torch>=2.0.0 torchvision torchaudio
pip install transformers>=4.35.0
pip install accelerate bitsandbytes

# Vision-Language Models
pip install open_clip_torch
pip install timm

# ROS 2 (Ubuntu)
sudo apt install ros-humble-desktop

# Additional Tools
pip install opencv-python pillow
pip install scipy numpy
pip install tensorboard wandb
```

---

## Model Downloads

| Model | Size | Purpose | Download |
|-------|------|---------|----------|
| OpenVLA-7B | ~15GB | Main VLA model | `huggingface-cli download openvla/openvla-7b` |
| CLIP ViT-L | ~1.5GB | Vision encoder | Auto-downloaded |
| YOLO v8 | ~25MB | Object detection | `pip install ultralytics` |

---

## Package Structure

```
humanoid_vla_ws/
├── src/
│   ├── humanoid_vla/               # VLA Core
│   │   ├── models/
│   │   │   ├── openvla_wrapper.py
│   │   │   ├── action_tokenizer.py
│   │   │   └── vision_encoder.py
│   │   ├── inference/
│   │   │   ├── vla_pipeline.py
│   │   │   └── batch_inference.py
│   │   ├── safety/
│   │   │   ├── safety_filter.py
│   │   │   └── workspace_bounds.py
│   │   └── grounding/
│   │       ├── object_detector.py
│   │       └── language_grounder.py
│   │
│   ├── humanoid_vla_ros/           # ROS 2 Interface
│   │   ├── src/
│   │   │   ├── vla_node.py
│   │   │   ├── camera_processor.py
│   │   │   └── command_interface.py
│   │   ├── msg/
│   │   │   ├── VLACommand.msg
│   │   │   └── VLAAction.msg
│   │   └── srv/
│   │       └── ExecuteTask.srv
│   │
│   └── humanoid_vla_sim/           # Simulation
│       ├── worlds/
│       │   └── manipulation_scene.world
│       └── scenarios/
│           └── pick_place.yaml
│
├── models/                          # Pretrained Models
│   ├── openvla-7b/
│   └── clip-vit-large/
│
└── data/                           # Training Data
    ├── demonstrations/
    └── evaluation/
```

---

## Quick Start

### 1. Environment Setup

```bash
# Create workspace
mkdir -p ~/humanoid_vla_ws/src
cd ~/humanoid_vla_ws

# Clone packages (if available)
# Or create from scratch following chapters

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Download Models

```python
from transformers import AutoModelForVision2Seq, AutoProcessor

# Download OpenVLA
model = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b",
    torch_dtype=torch.float16,
    device_map="auto"
)
processor = AutoProcessor.from_pretrained("openvla/openvla-7b")
```

### 3. Run VLA Inference

```python
from humanoid_vla.inference import VLAPipeline

# Initialize pipeline
pipeline = VLAPipeline(model_path="openvla/openvla-7b")

# Process command
image = load_camera_image()
instruction = "pick up the red block"
robot_state = get_joint_positions()

# Get action
action = pipeline.predict(image, instruction, robot_state)
print(f"Action: {action}")
```

### 4. Launch ROS 2 Node

```bash
# Build workspace
cd ~/humanoid_vla_ws
colcon build

# Source and launch
source install/setup.bash
ros2 launch humanoid_vla_ros vla_demo.launch.py
```

---

## Key Concepts

### Vision-Language-Action Models

| Concept | Description |
|---------|-------------|
| **VLA** | Models that take vision + language input and output robot actions |
| **RT-2** | Google's VLA model using PaLM-E backbone |
| **OpenVLA** | Open-source VLA based on LLaVA architecture |
| **Action Tokens** | Discretized representation of continuous robot actions |
| **Grounding** | Connecting language references to physical objects |

### Safety Principles

| Principle | Implementation |
|-----------|----------------|
| Joint Limits | Clip actions to URDF-defined ranges |
| Workspace Bounds | Reject actions outside safe workspace |
| Velocity Limits | Smooth rapid action changes |
| Confidence Filter | Require minimum prediction confidence |
| Emergency Stop | Hardware and software kill switches |

---

## Success Criteria

- [ ] OpenVLA inference running successfully
- [ ] Action tokenizer achieves under 5% reconstruction error
- [ ] Grounding localizes objects with over 80% accuracy
- [ ] VLA pipeline processes commands in under 2 seconds
- [ ] Safety filter catches 100% of limit violations
- [ ] ROS 2 node runs at stable 10 Hz
- [ ] End-to-end demo completes pick-and-place task

---

## Code Examples

Example code for this module is located in:

```
book/module-4/code/
├── humanoid_vla/
│   ├── models/
│   │   ├── vision_encoder.py      # CLIP wrapper
│   │   └── action_tokenizer.py    # Action discretization
│   ├── inference/
│   │   └── vla_pipeline.py        # End-to-end pipeline
│   ├── grounding/
│   │   └── language_grounder.py   # Object grounding
│   └── safety/
│       └── safety_filter.py       # Constraint enforcement
│
└── humanoid_vla_ros/
    └── src/
        └── vla_node.py            # ROS 2 node
```

---

## Exercises

Hands-on exercises are provided in [exercises/README.md](exercises/README.md).

---

## References

1. **RT-1**: Brohan et al., "RT-1: Robotics Transformer for Real-World Control at Scale" (2022)
2. **RT-2**: Brohan et al., "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control" (2023)
3. **PaLM-E**: Driess et al., "PaLM-E: An Embodied Multimodal Language Model" (2023)
4. **OpenVLA**: Kim et al., "OpenVLA: An Open-Source Vision-Language-Action Model" (2024)
5. **CLIP**: Radford et al., "Learning Transferable Visual Models From Natural Language Supervision" (2021)

---

**Next**: [Chapter 1 - Introduction to VLA Models](chapters/ch01-introduction-vla.md)
