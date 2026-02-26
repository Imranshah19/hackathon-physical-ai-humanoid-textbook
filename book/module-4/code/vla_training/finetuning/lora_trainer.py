"""
LoRA Fine-tuning for VLA Models

Parameter-efficient fine-tuning using Low-Rank Adaptation (LoRA)
for adapting VLA models to custom robots and tasks.

Reference: Chapter 8 - Fine-tuning VLA Models
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from pathlib import Path
import json
import time

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

try:
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False

try:
    from transformers import AutoModelForVision2Seq, AutoProcessor
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class LoRAConfig:
    """Configuration for LoRA fine-tuning."""
    # LoRA parameters
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "v_proj", "k_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])

    # Training parameters
    learning_rate: float = 1e-4
    weight_decay: float = 0.01
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    max_epochs: int = 10
    warmup_steps: int = 100

    # Optimization
    max_grad_norm: float = 1.0
    use_mixed_precision: bool = True
    gradient_checkpointing: bool = True

    # Logging
    log_interval: int = 10
    eval_interval: int = 100
    save_interval: int = 500

    # Paths
    output_dir: str = "./lora_checkpoints"
    logging_dir: str = "./logs"


@dataclass
class TrainingState:
    """Track training progress."""
    epoch: int = 0
    global_step: int = 0
    best_eval_loss: float = float('inf')
    train_losses: List[float] = field(default_factory=list)
    eval_losses: List[float] = field(default_factory=list)


class VLADataset(Dataset):
    """
    Dataset for VLA fine-tuning.

    Expected data format:
    - image: RGB image as numpy array or PIL Image
    - instruction: Task instruction string
    - action: Robot action array
    - state: Optional robot state array
    """

    def __init__(
        self,
        data_path: str,
        processor: Any,
        action_dim: int = 7,
        max_length: int = 512,
    ):
        self.data_path = Path(data_path)
        self.processor = processor
        self.action_dim = action_dim
        self.max_length = max_length

        # Load data index
        self.samples = self._load_data_index()

    def _load_data_index(self) -> List[Dict]:
        """Load dataset index from disk."""
        samples = []

        # Support multiple formats
        if self.data_path.suffix == '.json':
            with open(self.data_path) as f:
                samples = json.load(f)
        elif self.data_path.is_dir():
            # Load from HDF5 files or image directories
            for h5_file in self.data_path.glob("*.h5"):
                samples.extend(self._load_h5_index(h5_file))
            for json_file in self.data_path.glob("*.json"):
                with open(json_file) as f:
                    samples.extend(json.load(f))

        return samples

    def _load_h5_index(self, h5_path: Path) -> List[Dict]:
        """Load sample indices from HDF5 file."""
        try:
            import h5py
            samples = []
            with h5py.File(h5_path, 'r') as f:
                num_episodes = len([k for k in f.keys() if k.startswith('episode_')])
                for ep_idx in range(num_episodes):
                    ep_key = f'episode_{ep_idx}'
                    if ep_key in f:
                        num_steps = f[ep_key]['actions'].shape[0]
                        for step_idx in range(num_steps):
                            samples.append({
                                'h5_file': str(h5_path),
                                'episode': ep_idx,
                                'step': step_idx,
                            })
            return samples
        except ImportError:
            return []

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sample = self.samples[idx]

        # Load actual data
        if 'h5_file' in sample:
            data = self._load_h5_sample(sample)
        else:
            data = self._load_json_sample(sample)

        # Process image and text
        prompt = self._build_prompt(data['instruction'], data.get('state'))

        inputs = self.processor(
            text=prompt,
            images=data['image'],
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
        )

        # Build target (action tokens)
        action_str = self._action_to_string(data['action'])
        target_text = prompt + " " + action_str

        target_inputs = self.processor.tokenizer(
            target_text,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(0),
            'attention_mask': inputs['attention_mask'].squeeze(0),
            'pixel_values': inputs['pixel_values'].squeeze(0),
            'labels': target_inputs['input_ids'].squeeze(0),
        }

    def _load_h5_sample(self, sample: Dict) -> Dict[str, Any]:
        """Load sample from HDF5 file."""
        import h5py
        from PIL import Image

        with h5py.File(sample['h5_file'], 'r') as f:
            ep_key = f"episode_{sample['episode']}"
            step = sample['step']

            image_data = f[ep_key]['images'][step]
            action = f[ep_key]['actions'][step]
            instruction = f[ep_key].attrs.get('instruction', 'Execute task')

            if isinstance(instruction, bytes):
                instruction = instruction.decode('utf-8')

            # Handle state if available
            state = None
            if 'states' in f[ep_key]:
                state = f[ep_key]['states'][step]

        return {
            'image': Image.fromarray(image_data),
            'action': np.array(action),
            'instruction': instruction,
            'state': state,
        }

    def _load_json_sample(self, sample: Dict) -> Dict[str, Any]:
        """Load sample from JSON reference."""
        from PIL import Image

        image = Image.open(sample['image_path']).convert('RGB')
        action = np.array(sample['action'])
        instruction = sample.get('instruction', 'Execute task')
        state = np.array(sample['state']) if 'state' in sample else None

        return {
            'image': image,
            'action': action,
            'instruction': instruction,
            'state': state,
        }

    def _build_prompt(
        self,
        instruction: str,
        state: Optional[np.ndarray] = None,
    ) -> str:
        """Build VLA prompt."""
        prompt = f"In: What action should the robot take to {instruction}?\n"
        if state is not None:
            state_str = ", ".join([f"{x:.3f}" for x in state[:6]])
            prompt += f"State: [{state_str}]\n"
        prompt += "Out:"
        return prompt

    def _action_to_string(self, action: np.ndarray) -> str:
        """Convert action array to string representation."""
        return " ".join([f"{x:.4f}" for x in action])


class LoRATrainer:
    """
    LoRA fine-tuning trainer for VLA models.

    Example:
        >>> config = LoRAConfig(lora_rank=16, max_epochs=5)
        >>> trainer = LoRATrainer("openvla/openvla-7b", config)
        >>> trainer.train(train_dataset, val_dataset)
        >>> trainer.save_adapter("./my_adapter")
    """

    def __init__(
        self,
        model_name: str,
        config: LoRAConfig,
        device: str = "cuda",
    ):
        if not PEFT_AVAILABLE:
            raise ImportError("peft library required. Install with: pip install peft")
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers required. Install with: pip install transformers")

        self.model_name = model_name
        self.config = config
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")

        # Training state
        self.state = TrainingState()

        # Initialize model and processor
        self._init_model()

        # Setup optimizer and scheduler
        self._init_optimizer()

        # Setup logging
        self._init_logging()

    def _init_model(self) -> None:
        """Initialize model with LoRA."""
        print(f"Loading base model: {self.model_name}")

        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            trust_remote_code=True,
        )

        # Load base model
        self.base_model = AutoModelForVision2Seq.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

        # Enable gradient checkpointing
        if self.config.gradient_checkpointing:
            self.base_model.gradient_checkpointing_enable()

        # Create LoRA configuration
        lora_config = LoraConfig(
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules,
            task_type=TaskType.CAUSAL_LM,
            bias="none",
        )

        # Apply LoRA
        self.model = get_peft_model(self.base_model, lora_config)
        self.model.to(self.device)

        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"Trainable parameters: {trainable_params:,} / {total_params:,} "
              f"({100 * trainable_params / total_params:.2f}%)")

    def _init_optimizer(self) -> None:
        """Initialize optimizer and scheduler."""
        self.optimizer = AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )

        # Will be set during training
        self.scheduler = None

    def _init_logging(self) -> None:
        """Initialize logging."""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.logging_dir).mkdir(parents=True, exist_ok=True)

        try:
            from torch.utils.tensorboard import SummaryWriter
            self.writer = SummaryWriter(self.config.logging_dir)
        except ImportError:
            self.writer = None
            print("TensorBoard not available, logging to console only")

    def train(
        self,
        train_dataset: Dataset,
        val_dataset: Optional[Dataset] = None,
    ) -> Dict[str, Any]:
        """
        Run training loop.

        Args:
            train_dataset: Training dataset
            val_dataset: Optional validation dataset

        Returns:
            Training history
        """
        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True,
        )

        val_loader = None
        if val_dataset is not None:
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=4,
            )

        # Setup scheduler
        total_steps = len(train_loader) * self.config.max_epochs
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=total_steps,
            eta_min=self.config.learning_rate * 0.1,
        )

        # Mixed precision scaler
        scaler = torch.cuda.amp.GradScaler() if self.config.use_mixed_precision else None

        # Training loop
        self.model.train()
        start_time = time.time()

        for epoch in range(self.config.max_epochs):
            self.state.epoch = epoch
            epoch_loss = 0.0

            for batch_idx, batch in enumerate(train_loader):
                # Move batch to device
                batch = {k: v.to(self.device) for k, v in batch.items()}

                # Forward pass with mixed precision
                with torch.cuda.amp.autocast(enabled=self.config.use_mixed_precision):
                    outputs = self.model(
                        input_ids=batch['input_ids'],
                        attention_mask=batch['attention_mask'],
                        pixel_values=batch['pixel_values'],
                        labels=batch['labels'],
                    )
                    loss = outputs.loss / self.config.gradient_accumulation_steps

                # Backward pass
                if scaler is not None:
                    scaler.scale(loss).backward()
                else:
                    loss.backward()

                epoch_loss += loss.item() * self.config.gradient_accumulation_steps

                # Gradient accumulation
                if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                    if scaler is not None:
                        scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            self.config.max_grad_norm,
                        )
                        scaler.step(self.optimizer)
                        scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(
                            self.model.parameters(),
                            self.config.max_grad_norm,
                        )
                        self.optimizer.step()

                    self.scheduler.step()
                    self.optimizer.zero_grad()
                    self.state.global_step += 1

                    # Logging
                    if self.state.global_step % self.config.log_interval == 0:
                        avg_loss = epoch_loss / (batch_idx + 1)
                        lr = self.scheduler.get_last_lr()[0]
                        print(f"Epoch {epoch+1}/{self.config.max_epochs} | "
                              f"Step {self.state.global_step} | "
                              f"Loss: {avg_loss:.4f} | "
                              f"LR: {lr:.2e}")

                        if self.writer is not None:
                            self.writer.add_scalar('train/loss', avg_loss, self.state.global_step)
                            self.writer.add_scalar('train/lr', lr, self.state.global_step)

                    # Evaluation
                    if val_loader is not None and self.state.global_step % self.config.eval_interval == 0:
                        eval_loss = self.evaluate(val_loader)
                        self.state.eval_losses.append(eval_loss)

                        if eval_loss < self.state.best_eval_loss:
                            self.state.best_eval_loss = eval_loss
                            self.save_adapter(Path(self.config.output_dir) / "best_adapter")

                        self.model.train()

                    # Save checkpoint
                    if self.state.global_step % self.config.save_interval == 0:
                        self.save_checkpoint()

            # End of epoch
            avg_epoch_loss = epoch_loss / len(train_loader)
            self.state.train_losses.append(avg_epoch_loss)
            print(f"Epoch {epoch+1} completed | Average loss: {avg_epoch_loss:.4f}")

        # Final save
        self.save_adapter(Path(self.config.output_dir) / "final_adapter")

        elapsed = time.time() - start_time
        print(f"Training completed in {elapsed/60:.1f} minutes")

        return {
            'train_losses': self.state.train_losses,
            'eval_losses': self.state.eval_losses,
            'best_eval_loss': self.state.best_eval_loss,
            'total_steps': self.state.global_step,
        }

    def evaluate(self, val_loader: DataLoader) -> float:
        """Run evaluation."""
        self.model.eval()
        total_loss = 0.0

        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}

                with torch.cuda.amp.autocast(enabled=self.config.use_mixed_precision):
                    outputs = self.model(
                        input_ids=batch['input_ids'],
                        attention_mask=batch['attention_mask'],
                        pixel_values=batch['pixel_values'],
                        labels=batch['labels'],
                    )
                    total_loss += outputs.loss.item()

        avg_loss = total_loss / len(val_loader)
        print(f"Evaluation loss: {avg_loss:.4f}")

        if self.writer is not None:
            self.writer.add_scalar('eval/loss', avg_loss, self.state.global_step)

        return avg_loss

    def save_adapter(self, output_path: str) -> None:
        """Save LoRA adapter weights."""
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        self.model.save_pretrained(output_path)
        self.processor.save_pretrained(output_path)

        # Save config
        config_path = output_path / "training_config.json"
        with open(config_path, 'w') as f:
            json.dump({
                'lora_rank': self.config.lora_rank,
                'lora_alpha': self.config.lora_alpha,
                'target_modules': self.config.target_modules,
                'base_model': self.model_name,
                'best_eval_loss': self.state.best_eval_loss,
                'total_steps': self.state.global_step,
            }, f, indent=2)

        print(f"Adapter saved to {output_path}")

    def save_checkpoint(self) -> None:
        """Save training checkpoint."""
        ckpt_path = Path(self.config.output_dir) / f"checkpoint_{self.state.global_step}"
        ckpt_path.mkdir(parents=True, exist_ok=True)

        # Save model
        self.model.save_pretrained(ckpt_path)

        # Save optimizer state
        torch.save({
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'training_state': {
                'epoch': self.state.epoch,
                'global_step': self.state.global_step,
                'best_eval_loss': self.state.best_eval_loss,
            }
        }, ckpt_path / "training_state.pt")

        print(f"Checkpoint saved at step {self.state.global_step}")

    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load training checkpoint."""
        ckpt_path = Path(checkpoint_path)

        # Load model weights
        self.model = PeftModel.from_pretrained(
            self.base_model,
            ckpt_path,
        )
        self.model.to(self.device)

        # Load training state
        state_path = ckpt_path / "training_state.pt"
        if state_path.exists():
            state_dict = torch.load(state_path)
            self.optimizer.load_state_dict(state_dict['optimizer_state_dict'])
            if self.scheduler and state_dict['scheduler_state_dict']:
                self.scheduler.load_state_dict(state_dict['scheduler_state_dict'])
            self.state.epoch = state_dict['training_state']['epoch']
            self.state.global_step = state_dict['training_state']['global_step']
            self.state.best_eval_loss = state_dict['training_state']['best_eval_loss']

        print(f"Loaded checkpoint from {checkpoint_path}")


def load_finetuned_model(
    base_model_name: str,
    adapter_path: str,
    device: str = "cuda",
) -> Tuple[Any, Any]:
    """
    Load a fine-tuned VLA model with LoRA adapter.

    Args:
        base_model_name: HuggingFace model name
        adapter_path: Path to saved adapter
        device: Device to load model on

    Returns:
        Tuple of (model, processor)
    """
    from transformers import AutoModelForVision2Seq, AutoProcessor
    from peft import PeftModel

    processor = AutoProcessor.from_pretrained(adapter_path, trust_remote_code=True)

    base_model = AutoModelForVision2Seq.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )

    model = PeftModel.from_pretrained(base_model, adapter_path)
    model = model.to(device)
    model.eval()

    return model, processor


if __name__ == "__main__":
    print("LoRA Training Module")
    print("=" * 50)

    # Example configuration
    config = LoRAConfig(
        lora_rank=16,
        lora_alpha=32,
        learning_rate=1e-4,
        batch_size=4,
        max_epochs=5,
    )

    print(f"Configuration:")
    print(f"  LoRA rank: {config.lora_rank}")
    print(f"  LoRA alpha: {config.lora_alpha}")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Batch size: {config.batch_size}")
    print(f"  Max epochs: {config.max_epochs}")
    print(f"  Target modules: {config.target_modules}")
