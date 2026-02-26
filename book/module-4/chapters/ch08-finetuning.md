# Chapter 8: Fine-tuning VLA on Custom Data

**Duration**: 5-6 hours
**Prerequisites**: Chapter 5 (VLA Pipeline), Basic PyTorch training knowledge

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Design data collection formats for VLA training
- Collect demonstration data from robot teleoperation
- Implement LoRA fine-tuning for VLA models
- Monitor training with TensorBoard
- Evaluate fine-tuned models on custom tasks

---

## 8.1 Data Collection for VLA

VLA models learn from demonstration data pairing images, instructions, and actions:

```
┌─────────────────────────────────────────────────────────────────┐
│                   VLA Training Data Format                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Episode 001:                                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Instruction: "pick up the red block"                       │ │
│  │                                                             │ │
│  │ Step 0:                                                     │ │
│  │   Image: [480x640 RGB]                                     │ │
│  │   State: [j1=0.1, j2=0.2, ..., j14=0.0]                   │ │
│  │   Action: [0.05, 0.02, -0.01, 0.0, 0.0, 0.0, 0.0]         │ │
│  │                                                             │ │
│  │ Step 1:                                                     │ │
│  │   Image: [480x640 RGB]                                     │ │
│  │   State: [j1=0.15, j2=0.22, ..., j14=0.0]                 │ │
│  │   Action: [0.08, 0.03, -0.02, 0.0, 0.0, 0.0, 0.0]         │ │
│  │                                                             │ │
│  │ ... (50-200 steps per episode)                             │ │
│  │                                                             │ │
│  │ Metadata:                                                   │ │
│  │   success: true                                             │ │
│  │   duration: 12.5s                                          │ │
│  │   task_type: pick_place                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Format Specification

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np
import h5py
from datetime import datetime


@dataclass
class DemoStep:
    """Single step in a demonstration."""
    timestamp: float
    image: np.ndarray  # (H, W, 3)
    state: np.ndarray  # Joint positions
    action: np.ndarray  # Action taken
    ee_pose: Optional[np.ndarray] = None  # End-effector pose


@dataclass
class DemoEpisode:
    """Complete demonstration episode."""
    episode_id: str
    instruction: str
    steps: List[DemoStep]
    success: bool
    metadata: Dict = field(default_factory=dict)

    @property
    def num_steps(self) -> int:
        return len(self.steps)

    @property
    def duration(self) -> float:
        if not self.steps:
            return 0.0
        return self.steps[-1].timestamp - self.steps[0].timestamp


class DemonstrationDataset:
    """Dataset of demonstration episodes."""

    def __init__(self, path: str):
        self.path = path
        self.episodes: List[DemoEpisode] = []

    def add_episode(self, episode: DemoEpisode):
        """Add episode to dataset."""
        self.episodes.append(episode)

    def save(self, filepath: str):
        """Save dataset to HDF5 file."""
        with h5py.File(filepath, 'w') as f:
            f.attrs['num_episodes'] = len(self.episodes)
            f.attrs['created'] = datetime.now().isoformat()

            for i, episode in enumerate(self.episodes):
                grp = f.create_group(f'episode_{i:04d}')
                grp.attrs['episode_id'] = episode.episode_id
                grp.attrs['instruction'] = episode.instruction
                grp.attrs['success'] = episode.success
                grp.attrs['num_steps'] = episode.num_steps

                # Save steps
                steps_grp = grp.create_group('steps')
                for j, step in enumerate(episode.steps):
                    step_grp = steps_grp.create_group(f'step_{j:04d}')
                    step_grp.create_dataset('timestamp', data=step.timestamp)
                    step_grp.create_dataset('image', data=step.image, compression='gzip')
                    step_grp.create_dataset('state', data=step.state)
                    step_grp.create_dataset('action', data=step.action)
                    if step.ee_pose is not None:
                        step_grp.create_dataset('ee_pose', data=step.ee_pose)

        print(f"Saved {len(self.episodes)} episodes to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'DemonstrationDataset':
        """Load dataset from HDF5 file."""
        dataset = cls(filepath)

        with h5py.File(filepath, 'r') as f:
            num_episodes = f.attrs['num_episodes']

            for i in range(num_episodes):
                grp = f[f'episode_{i:04d}']

                steps = []
                steps_grp = grp['steps']
                for j in range(grp.attrs['num_steps']):
                    step_grp = steps_grp[f'step_{j:04d}']
                    steps.append(DemoStep(
                        timestamp=float(step_grp['timestamp'][()]),
                        image=step_grp['image'][()],
                        state=step_grp['state'][()],
                        action=step_grp['action'][()],
                        ee_pose=step_grp['ee_pose'][()] if 'ee_pose' in step_grp else None
                    ))

                episode = DemoEpisode(
                    episode_id=grp.attrs['episode_id'],
                    instruction=grp.attrs['instruction'],
                    steps=steps,
                    success=grp.attrs['success']
                )
                dataset.episodes.append(episode)

        print(f"Loaded {len(dataset.episodes)} episodes from {filepath}")
        return dataset

    def get_statistics(self) -> Dict:
        """Compute dataset statistics."""
        total_steps = sum(e.num_steps for e in self.episodes)
        successful = sum(1 for e in self.episodes if e.success)

        return {
            'num_episodes': len(self.episodes),
            'total_steps': total_steps,
            'success_rate': successful / len(self.episodes) if self.episodes else 0,
            'avg_steps_per_episode': total_steps / len(self.episodes) if self.episodes else 0,
            'unique_instructions': len(set(e.instruction for e in self.episodes))
        }
```

---

## 8.2 Data Collection Tool

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np
import time
from threading import Lock


class DataCollectionNode(Node):
    """ROS 2 node for collecting demonstration data."""

    def __init__(self):
        super().__init__('data_collection')

        # Parameters
        self.declare_parameter('output_dir', 'demos/')
        self.declare_parameter('control_rate', 10.0)

        self.output_dir = self.get_parameter('output_dir').value
        self.control_rate = self.get_parameter('control_rate').value

        self.cv_bridge = CvBridge()
        self.lock = Lock()

        # State
        self.is_recording = False
        self.current_instruction = ""
        self.current_episode: Optional[DemoEpisode] = None
        self.latest_image = None
        self.latest_state = None
        self.latest_action = None
        self.episode_count = 0

        # Dataset
        self.dataset = DemonstrationDataset(self.output_dir)

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10
        )
        self.state_sub = self.create_subscription(
            JointState, '/joint_states', self.state_callback, 10
        )
        self.action_sub = self.create_subscription(
            JointState, '/teleop/action', self.action_callback, 10
        )

        # Timer for recording
        self.record_timer = self.create_timer(
            1.0 / self.control_rate, self.record_callback
        )

        self.get_logger().info("Data collection node ready")
        self.print_instructions()

    def print_instructions(self):
        """Print usage instructions."""
        print("\n" + "=" * 50)
        print("VLA Data Collection")
        print("=" * 50)
        print("Commands:")
        print("  start <instruction>  - Start recording episode")
        print("  stop                 - Stop recording (success)")
        print("  abort                - Abort episode (failure)")
        print("  save                 - Save dataset to file")
        print("  stats                - Show statistics")
        print("  quit                 - Exit")
        print("=" * 50 + "\n")

    def image_callback(self, msg):
        """Handle camera images."""
        with self.lock:
            self.latest_image = self.cv_bridge.imgmsg_to_cv2(msg, 'rgb8')

    def state_callback(self, msg):
        """Handle joint states."""
        with self.lock:
            self.latest_state = np.array(msg.position)

    def action_callback(self, msg):
        """Handle teleop actions."""
        with self.lock:
            self.latest_action = np.array(msg.position)

    def record_callback(self):
        """Record current step if recording."""
        if not self.is_recording:
            return

        with self.lock:
            if self.latest_image is None or self.latest_state is None:
                return

            # Use latest action or compute from state change
            action = self.latest_action if self.latest_action is not None else np.zeros(7)

            step = DemoStep(
                timestamp=time.time(),
                image=self.latest_image.copy(),
                state=self.latest_state.copy(),
                action=action.copy()
            )

            self.current_episode.steps.append(step)

            # Log progress
            if len(self.current_episode.steps) % 10 == 0:
                print(f"  Recording... {len(self.current_episode.steps)} steps", end='\r')

    def start_recording(self, instruction: str):
        """Start recording a new episode."""
        if self.is_recording:
            print("Already recording. Stop current episode first.")
            return

        self.current_instruction = instruction
        self.current_episode = DemoEpisode(
            episode_id=f"ep_{self.episode_count:04d}",
            instruction=instruction,
            steps=[],
            success=False
        )
        self.is_recording = True
        self.episode_count += 1

        print(f"\nStarted recording episode {self.current_episode.episode_id}")
        print(f"Instruction: '{instruction}'")

    def stop_recording(self, success: bool = True):
        """Stop recording and save episode."""
        if not self.is_recording:
            print("Not currently recording.")
            return

        self.is_recording = False
        self.current_episode.success = success

        if len(self.current_episode.steps) > 5:  # Minimum steps
            self.dataset.add_episode(self.current_episode)
            print(f"\nSaved episode: {len(self.current_episode.steps)} steps, success={success}")
        else:
            print(f"\nDiscarded episode (too few steps: {len(self.current_episode.steps)})")

        self.current_episode = None

    def save_dataset(self, filename: str = None):
        """Save dataset to file."""
        if filename is None:
            filename = f"vla_demos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.hdf5"

        filepath = f"{self.output_dir}/{filename}"
        self.dataset.save(filepath)

    def run_interactive(self):
        """Run interactive command loop."""
        while rclpy.ok():
            try:
                cmd = input("collect> ").strip()

                if not cmd:
                    continue

                parts = cmd.split(maxsplit=1)
                command = parts[0].lower()

                if command == 'start':
                    if len(parts) > 1:
                        self.start_recording(parts[1])
                    else:
                        print("Usage: start <instruction>")

                elif command == 'stop':
                    self.stop_recording(success=True)

                elif command == 'abort':
                    self.stop_recording(success=False)

                elif command == 'save':
                    self.save_dataset()

                elif command == 'stats':
                    stats = self.dataset.get_statistics()
                    print(f"\nDataset Statistics:")
                    for k, v in stats.items():
                        print(f"  {k}: {v}")

                elif command == 'quit':
                    break

                else:
                    print(f"Unknown command: {command}")

            except (EOFError, KeyboardInterrupt):
                break


def main():
    rclpy.init()
    node = DataCollectionNode()

    # Run in separate thread
    import threading
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    node.run_interactive()

    node.destroy_node()
    rclpy.shutdown()
```

---

## 8.3 PyTorch Dataset for Training

```python
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Tuple
import random


class VLATrainingDataset(Dataset):
    """PyTorch Dataset for VLA training."""

    def __init__(
        self,
        demo_dataset: DemonstrationDataset,
        processor,
        action_tokenizer,
        max_instruction_length: int = 128,
        augment: bool = True
    ):
        self.demo_dataset = demo_dataset
        self.processor = processor
        self.action_tokenizer = action_tokenizer
        self.max_instruction_length = max_instruction_length
        self.augment = augment

        # Build index of all steps
        self.samples = []
        for episode in demo_dataset.episodes:
            if not episode.success:
                continue  # Only use successful episodes

            for i, step in enumerate(episode.steps[:-1]):  # Exclude last step (no action)
                self.samples.append({
                    'episode_id': episode.episode_id,
                    'instruction': episode.instruction,
                    'step_idx': i,
                    'image': step.image,
                    'state': step.state,
                    'action': step.action
                })

        print(f"Created dataset with {len(self.samples)} samples from "
              f"{len(demo_dataset.episodes)} episodes")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]

        # Get image
        image = sample['image']

        # Apply augmentation
        if self.augment:
            image = self._augment_image(image)

        # Convert to PIL for processor
        from PIL import Image as PILImage
        pil_image = PILImage.fromarray(image)

        # Process with model's processor
        prompt = f"In: What action should the robot take to {sample['instruction']}?\nOut:"

        inputs = self.processor(
            text=prompt,
            images=pil_image,
            return_tensors="pt",
            padding="max_length",
            max_length=self.max_instruction_length,
            truncation=True
        )

        # Remove batch dimension
        inputs = {k: v.squeeze(0) for k, v in inputs.items()}

        # Tokenize action for labels
        action_tokens = self.action_tokenizer.encode_action(sample['action'])

        # Create labels (action tokens)
        inputs['labels'] = torch.tensor(action_tokens, dtype=torch.long)

        return inputs

    def _augment_image(self, image: np.ndarray) -> np.ndarray:
        """Apply image augmentation."""
        import cv2

        augmented = image.copy()

        # Random brightness
        if random.random() < 0.3:
            factor = random.uniform(0.8, 1.2)
            augmented = np.clip(augmented * factor, 0, 255).astype(np.uint8)

        # Random horizontal flip (be careful with spatial reasoning!)
        # Disabled by default for manipulation tasks
        # if random.random() < 0.5:
        #     augmented = np.fliplr(augmented)

        # Random noise
        if random.random() < 0.2:
            noise = np.random.randn(*augmented.shape) * 10
            augmented = np.clip(augmented + noise, 0, 255).astype(np.uint8)

        return augmented


def create_dataloaders(
    demo_dataset: DemonstrationDataset,
    processor,
    action_tokenizer,
    batch_size: int = 8,
    val_split: float = 0.1
) -> Tuple[DataLoader, DataLoader]:
    """Create train and validation dataloaders."""

    # Split episodes
    episodes = demo_dataset.episodes.copy()
    random.shuffle(episodes)

    split_idx = int(len(episodes) * (1 - val_split))
    train_episodes = episodes[:split_idx]
    val_episodes = episodes[split_idx:]

    # Create separate datasets
    train_demo = DemonstrationDataset("")
    train_demo.episodes = train_episodes

    val_demo = DemonstrationDataset("")
    val_demo.episodes = val_episodes

    train_dataset = VLATrainingDataset(
        train_demo, processor, action_tokenizer, augment=True
    )
    val_dataset = VLATrainingDataset(
        val_demo, processor, action_tokenizer, augment=False
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )

    return train_loader, val_loader
```

---

## 8.4 LoRA Fine-tuning

```python
from peft import LoraConfig, get_peft_model, TaskType
from transformers import AutoModelForVision2Seq, AutoProcessor
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm


class VLALoRATrainer:
    """LoRA fine-tuning for VLA models."""

    def __init__(
        self,
        model_path: str,
        lora_rank: int = 16,
        lora_alpha: int = 32,
        lora_dropout: float = 0.1,
        target_modules: List[str] = None
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load base model
        print(f"Loading base model from {model_path}...")
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_path)

        # Default target modules for LLaVA-style models
        if target_modules is None:
            target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

        # Configure LoRA
        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )

        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)

        # Print trainable parameters
        trainable = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.model.parameters())
        print(f"Trainable parameters: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 10,
        learning_rate: float = 1e-4,
        warmup_steps: int = 100,
        save_dir: str = "checkpoints/"
    ):
        """Train the model."""
        import os
        from torch.utils.tensorboard import SummaryWriter

        os.makedirs(save_dir, exist_ok=True)
        writer = SummaryWriter(log_dir=f"{save_dir}/logs")

        # Optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=learning_rate,
            weight_decay=0.01
        )

        # Scheduler
        total_steps = len(train_loader) * epochs
        scheduler = CosineAnnealingLR(optimizer, T_max=total_steps)

        # Training loop
        global_step = 0
        best_val_loss = float('inf')

        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0

            progress = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")

            for batch in progress:
                # Move to device
                batch = {k: v.to(self.device) for k, v in batch.items()}

                # Forward pass
                outputs = self.model(**batch)
                loss = outputs.loss

                # Backward pass
                optimizer.zero_grad()
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                optimizer.step()
                scheduler.step()

                # Logging
                train_loss += loss.item()
                global_step += 1

                progress.set_postfix({
                    'loss': f"{loss.item():.4f}",
                    'lr': f"{scheduler.get_last_lr()[0]:.2e}"
                })

                if global_step % 100 == 0:
                    writer.add_scalar('train/loss', loss.item(), global_step)
                    writer.add_scalar('train/lr', scheduler.get_last_lr()[0], global_step)

            # Validation
            val_loss = self.validate(val_loader)
            writer.add_scalar('val/loss', val_loss, epoch)

            avg_train_loss = train_loss / len(train_loader)
            print(f"\nEpoch {epoch+1}: train_loss={avg_train_loss:.4f}, val_loss={val_loss:.4f}")

            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_adapter(f"{save_dir}/best_adapter")
                print(f"Saved best model (val_loss={val_loss:.4f})")

            # Save checkpoint
            self.save_adapter(f"{save_dir}/epoch_{epoch+1}")

        writer.close()
        print("\nTraining complete!")

    @torch.no_grad()
    def validate(self, val_loader: DataLoader) -> float:
        """Run validation."""
        self.model.eval()
        total_loss = 0.0

        for batch in val_loader:
            batch = {k: v.to(self.device) for k, v in batch.items()}
            outputs = self.model(**batch)
            total_loss += outputs.loss.item()

        return total_loss / len(val_loader)

    def save_adapter(self, path: str):
        """Save LoRA adapter weights."""
        self.model.save_pretrained(path)
        print(f"Saved adapter to {path}")

    def load_adapter(self, path: str):
        """Load LoRA adapter weights."""
        from peft import PeftModel
        self.model = PeftModel.from_pretrained(self.model.base_model, path)
        print(f"Loaded adapter from {path}")


# Usage
trainer = VLALoRATrainer(
    model_path="openvla/openvla-7b",
    lora_rank=16,
    lora_alpha=32
)

# Create dataloaders
train_loader, val_loader = create_dataloaders(
    demo_dataset,
    trainer.processor,
    action_tokenizer,
    batch_size=4
)

# Train
trainer.train(
    train_loader,
    val_loader,
    epochs=10,
    learning_rate=1e-4,
    save_dir="vla_finetuned/"
)
```

---

## 8.5 Training Monitoring

```python
class TrainingMonitor:
    """Monitor VLA training progress."""

    def __init__(self, log_dir: str = "logs/"):
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(log_dir=log_dir)

        self.train_losses = []
        self.val_losses = []
        self.action_accuracies = []

    def log_step(self, step: int, loss: float, lr: float):
        """Log training step."""
        self.writer.add_scalar('train/loss', loss, step)
        self.writer.add_scalar('train/learning_rate', lr, step)
        self.train_losses.append(loss)

    def log_epoch(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        action_accuracy: float = None
    ):
        """Log epoch metrics."""
        self.writer.add_scalar('epoch/train_loss', train_loss, epoch)
        self.writer.add_scalar('epoch/val_loss', val_loss, epoch)
        self.val_losses.append(val_loss)

        if action_accuracy is not None:
            self.writer.add_scalar('epoch/action_accuracy', action_accuracy, epoch)
            self.action_accuracies.append(action_accuracy)

    def log_action_distribution(self, step: int, actions: np.ndarray):
        """Log action distribution."""
        for i in range(actions.shape[1]):
            self.writer.add_histogram(f'actions/dim_{i}', actions[:, i], step)

    def plot_training_curves(self, save_path: str = None):
        """Plot training curves."""
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 4))

        # Loss curve
        axes[0].plot(self.train_losses, label='Train', alpha=0.7)
        axes[0].set_xlabel('Step')
        axes[0].set_ylabel('Loss')
        axes[0].set_title('Training Loss')
        axes[0].legend()

        # Validation loss
        axes[1].plot(self.val_losses, label='Validation')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].set_title('Validation Loss')
        axes[1].legend()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
        plt.show()

    def close(self):
        """Close writer."""
        self.writer.close()
```

---

## 8.6 Evaluation During Training

```python
class TrainingEvaluator:
    """Evaluate VLA during training."""

    def __init__(
        self,
        model,
        processor,
        action_tokenizer,
        eval_dataset,
        device: str = "cuda"
    ):
        self.model = model
        self.processor = processor
        self.action_tokenizer = action_tokenizer
        self.eval_dataset = eval_dataset
        self.device = device

    @torch.no_grad()
    def evaluate_action_accuracy(self, num_samples: int = 100) -> Dict:
        """
        Evaluate action prediction accuracy.

        Returns per-dimension accuracy metrics.
        """
        self.model.eval()

        correct_per_dim = np.zeros(7)
        total = 0

        indices = random.sample(range(len(self.eval_dataset)), min(num_samples, len(self.eval_dataset)))

        for idx in indices:
            sample = self.eval_dataset[idx]

            # Get prediction
            inputs = {k: v.unsqueeze(0).to(self.device) for k, v in sample.items() if k != 'labels'}
            outputs = self.model.generate(**inputs, max_new_tokens=20)

            # Parse predicted action
            pred_text = self.processor.decode(outputs[0], skip_special_tokens=True)
            pred_action = self._parse_action(pred_text)

            # Compare with ground truth
            gt_action = sample['labels'].numpy()

            if pred_action is not None and len(pred_action) == len(gt_action):
                # Check per-dimension accuracy (within 10% of bin range)
                for i in range(len(gt_action)):
                    if abs(pred_action[i] - gt_action[i]) <= 25:  # ~10% of 256 bins
                        correct_per_dim[i] += 1

            total += 1

        accuracy_per_dim = correct_per_dim / total if total > 0 else np.zeros(7)

        return {
            'overall_accuracy': np.mean(accuracy_per_dim),
            'per_dim_accuracy': accuracy_per_dim.tolist(),
            'num_samples': total
        }

    def _parse_action(self, text: str) -> Optional[np.ndarray]:
        """Parse action from model output text."""
        import re
        numbers = re.findall(r'\d+', text.split("Out:")[-1] if "Out:" in text else text)
        if len(numbers) >= 7:
            return np.array([int(n) for n in numbers[:7]])
        return None

    def evaluate_task_success(
        self,
        simulator,
        tasks: List[Dict],
        num_episodes: int = 10
    ) -> Dict:
        """
        Evaluate task success in simulation.

        Args:
            simulator: Simulation environment
            tasks: List of task specifications
            num_episodes: Episodes per task

        Returns:
            Success rates and statistics
        """
        results = {}

        for task in tasks:
            task_name = task['name']
            successes = 0

            for _ in range(num_episodes):
                # Reset simulator
                obs = simulator.reset(task)

                # Run episode
                for step in range(task.get('max_steps', 100)):
                    # Get action from model
                    image = obs['image']
                    instruction = task['instruction']

                    action = self._get_action(image, instruction)

                    # Execute action
                    obs, reward, done, info = simulator.step(action)

                    if done:
                        if info.get('success', False):
                            successes += 1
                        break

            results[task_name] = {
                'success_rate': successes / num_episodes,
                'num_episodes': num_episodes
            }

        return results

    def _get_action(self, image, instruction):
        """Get action from model."""
        from PIL import Image as PILImage
        pil_image = PILImage.fromarray(image)

        prompt = f"In: What action should the robot take to {instruction}?\nOut:"
        inputs = self.processor(text=prompt, images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.generate(**inputs, max_new_tokens=20)
        text = self.processor.decode(outputs[0], skip_special_tokens=True)

        action_tokens = self._parse_action(text)
        if action_tokens is not None:
            return self.action_tokenizer.decode_action(action_tokens)
        return np.zeros(7)
```

---

## 8.7 Summary

In this chapter, you learned:

1. **Data Format**: HDF5 storage for images, instructions, and actions
2. **Data Collection**: ROS 2 node for teleoperated demonstrations
3. **PyTorch Dataset**: Training data loading and augmentation
4. **LoRA Fine-tuning**: Parameter-efficient adaptation
5. **Training Monitoring**: TensorBoard logging and visualization
6. **Evaluation**: Action accuracy and task success metrics

---

## 8.8 Exercises

### Exercise 8.1: Data Collection
Collect 50 demonstration episodes for a pick-and-place task.

### Exercise 8.2: Data Augmentation
Implement additional augmentation (color jitter, rotation for non-spatial tasks).

### Exercise 8.3: LoRA Training
Fine-tune OpenVLA with LoRA on your collected data.

### Exercise 8.4: Evaluation
Evaluate fine-tuned model vs base model on held-out tasks.

---

## Quick Reference

### Data Collection
```bash
ros2 run humanoid_vla collect_demo --output demos/
```

### LoRA Training
```python
trainer = VLALoRATrainer(model_path, lora_rank=16)
trainer.train(train_loader, val_loader, epochs=10)
trainer.save_adapter("finetuned/")
```

### Load Fine-tuned Model
```python
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "finetuned/")
```

---

**Next Chapter**: [Chapter 9 - Evaluation and Benchmarking](ch09-evaluation.md)
