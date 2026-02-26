# Chapter 2: Vision-Language Model Foundations

**Duration**: 4-5 hours
**Prerequisites**: Chapter 1, Basic deep learning knowledge

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand CLIP architecture and contrastive learning
- Work with Vision Transformers (ViT) for image encoding
- Extract and manipulate image and text embeddings
- Compute similarity scores between images and text
- Visualize embedding spaces for debugging

---

## 2.1 The Foundation: CLIP

CLIP (Contrastive Language-Image Pre-training) is the backbone of most VLA models. It learns to align images and text in a shared embedding space.

### How CLIP Works

```
┌─────────────────────────────────────────────────────────────────┐
│                       CLIP Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Image                           Text                          │
│     ↓                               ↓                           │
│  ┌───────────────┐           ┌───────────────┐                 │
│  │ Vision Encoder│           │ Text Encoder  │                 │
│  │    (ViT)      │           │ (Transformer) │                 │
│  └───────┬───────┘           └───────┬───────┘                 │
│          ↓                           ↓                          │
│   ┌─────────────┐             ┌─────────────┐                  │
│   │ Image       │             │ Text        │                  │
│   │ Embedding   │             │ Embedding   │                  │
│   │ (768-d)     │             │ (768-d)     │                  │
│   └──────┬──────┘             └──────┬──────┘                  │
│          │                           │                          │
│          └─────────┬─────────────────┘                          │
│                    ↓                                             │
│            Cosine Similarity                                     │
│                    ↓                                             │
│              Match Score                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Contrastive Learning

CLIP is trained on 400 million image-text pairs from the web using contrastive loss:

```python
def contrastive_loss(image_embeddings, text_embeddings, temperature=0.07):
    """
    InfoNCE contrastive loss used in CLIP training.

    For each image, the matching text is positive, all others are negative.
    """
    # Normalize embeddings
    image_embeddings = F.normalize(image_embeddings, dim=-1)
    text_embeddings = F.normalize(text_embeddings, dim=-1)

    # Compute similarity matrix
    logits = (image_embeddings @ text_embeddings.T) / temperature

    # Labels: diagonal elements are positives
    batch_size = logits.shape[0]
    labels = torch.arange(batch_size, device=logits.device)

    # Cross-entropy loss (both directions)
    loss_i2t = F.cross_entropy(logits, labels)
    loss_t2i = F.cross_entropy(logits.T, labels)

    return (loss_i2t + loss_t2i) / 2
```

### Why CLIP Matters for VLA

| Property | Benefit for VLA |
|----------|-----------------|
| **Aligned embeddings** | Compare images and text directly |
| **Zero-shot transfer** | Recognize objects never seen in robot data |
| **Semantic understanding** | "Red block" maps to actual red blocks |
| **Scalable pretraining** | Leverage 400M+ web examples |

---

## 2.2 Vision Transformers (ViT)

ViT applies the transformer architecture to images by splitting them into patches.

### ViT Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vision Transformer (ViT)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input Image (224 x 224 x 3)                                    │
│         ↓                                                        │
│  Split into patches (14 x 14 = 196 patches of 16x16)            │
│         ↓                                                        │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ [CLS] P1  P2  P3  P4  ...  P196                       │      │
│  │   ↓   ↓   ↓   ↓   ↓   ...   ↓                        │      │
│  │ Linear Projection (768-d each)                        │      │
│  └───────────────────────────────────────────────────────┘      │
│         ↓                                                        │
│  Add Positional Embeddings                                       │
│         ↓                                                        │
│  ┌───────────────────────────────────────────────────────┐      │
│  │           Transformer Encoder (12 layers)              │      │
│  │  ┌────────────────────────────────────────────────┐   │      │
│  │  │  Multi-Head Self-Attention                     │   │      │
│  │  │  Layer Normalization                           │   │      │
│  │  │  MLP (Feed-Forward)                            │   │      │
│  │  │  Layer Normalization                           │   │      │
│  │  └────────────────────────────────────────────────┘   │      │
│  └───────────────────────────────────────────────────────┘      │
│         ↓                                                        │
│  [CLS] token → Image Embedding (768-d)                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### ViT Variants

| Model | Patches | Layers | Hidden | Heads | Parameters |
|-------|---------|--------|--------|-------|------------|
| ViT-B/16 | 16x16 | 12 | 768 | 12 | 86M |
| ViT-L/14 | 14x14 | 24 | 1024 | 16 | 304M |
| ViT-H/14 | 14x14 | 32 | 1280 | 16 | 632M |
| ViT-G/14 | 14x14 | 40 | 1664 | 16 | 1.8B |

---

## 2.3 Implementing CLIP for VLA

### Loading CLIP Models

```python
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class CLIPEncoder:
    """Wrapper for CLIP image and text encoding."""

    def __init__(self, model_name="openai/clip-vit-large-patch14"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load model and processor
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

        # Set to evaluation mode
        self.model.eval()

        print(f"CLIP loaded: {model_name}")
        print(f"Vision hidden size: {self.model.config.vision_config.hidden_size}")
        print(f"Text hidden size: {self.model.config.text_config.hidden_size}")

    @torch.no_grad()
    def encode_image(self, image):
        """
        Encode image to embedding vector.

        Args:
            image: PIL Image or numpy array

        Returns:
            Normalized embedding (1, hidden_size)
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.get_image_features(**inputs)

        # Normalize
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)

        return outputs

    @torch.no_grad()
    def encode_text(self, text):
        """
        Encode text to embedding vector.

        Args:
            text: String or list of strings

        Returns:
            Normalized embedding (batch, hidden_size)
        """
        if isinstance(text, str):
            text = [text]

        inputs = self.processor(text=text, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model.get_text_features(**inputs)

        # Normalize
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)

        return outputs

    def compute_similarity(self, image, texts):
        """
        Compute similarity between image and multiple texts.

        Args:
            image: PIL Image
            texts: List of strings

        Returns:
            Similarity scores (num_texts,)
        """
        image_embedding = self.encode_image(image)
        text_embeddings = self.encode_text(texts)

        # Cosine similarity (embeddings are normalized)
        similarities = (image_embedding @ text_embeddings.T).squeeze(0)

        return similarities.cpu().numpy()


# Usage example
clip = CLIPEncoder()

# Encode image
image = Image.open("robot_scene.jpg")
image_emb = clip.encode_image(image)
print(f"Image embedding shape: {image_emb.shape}")

# Encode text
texts = ["a red block", "a blue cup", "a robot arm"]
text_embs = clip.encode_text(texts)
print(f"Text embeddings shape: {text_embs.shape}")

# Compute similarities
similarities = clip.compute_similarity(image, texts)
for text, sim in zip(texts, similarities):
    print(f"  '{text}': {sim:.3f}")
```

### Extracting Patch Features

For VLA, we often need patch-level features, not just the CLS token:

```python
class CLIPPatchEncoder:
    """Extract patch-level features from CLIP vision encoder."""

    def __init__(self, model_name="openai/clip-vit-large-patch14"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

        # Get patch configuration
        vision_config = self.model.config.vision_config
        self.patch_size = vision_config.patch_size
        self.image_size = vision_config.image_size
        self.num_patches = (self.image_size // self.patch_size) ** 2

        print(f"Patch size: {self.patch_size}")
        print(f"Number of patches: {self.num_patches}")

    @torch.no_grad()
    def extract_patch_features(self, image):
        """
        Extract features for each image patch.

        Returns:
            cls_token: (1, hidden_size) - global image representation
            patch_tokens: (num_patches, hidden_size) - per-patch features
        """
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Get hidden states from vision encoder
        vision_outputs = self.model.vision_model(
            **inputs,
            output_hidden_states=True,
            return_dict=True
        )

        # Last hidden state: (batch, num_patches+1, hidden_size)
        # First token is CLS, rest are patches
        last_hidden = vision_outputs.last_hidden_state[0]

        cls_token = last_hidden[0:1]  # (1, hidden_size)
        patch_tokens = last_hidden[1:]  # (num_patches, hidden_size)

        return cls_token, patch_tokens

    def patches_to_spatial(self, patch_tokens):
        """
        Reshape flat patch tokens to spatial grid.

        Args:
            patch_tokens: (num_patches, hidden_size)

        Returns:
            spatial_features: (H, W, hidden_size)
        """
        h = w = int(self.num_patches ** 0.5)
        hidden_size = patch_tokens.shape[-1]

        spatial = patch_tokens.reshape(h, w, hidden_size)
        return spatial


# Usage
patch_encoder = CLIPPatchEncoder()

image = Image.open("robot_scene.jpg")
cls_token, patch_tokens = patch_encoder.extract_patch_features(image)

print(f"CLS token shape: {cls_token.shape}")  # (1, 1024)
print(f"Patch tokens shape: {patch_tokens.shape}")  # (256, 1024) for 16x16 patches

# Convert to spatial
spatial_features = patch_encoder.patches_to_spatial(patch_tokens)
print(f"Spatial features shape: {spatial_features.shape}")  # (16, 16, 1024)
```

---

## 2.4 Text Encoding for Robot Instructions

### Instruction Preprocessing

Robot instructions need preprocessing to match CLIP's training distribution:

```python
class InstructionEncoder:
    """Encode robot instructions with CLIP text encoder."""

    def __init__(self, clip_encoder):
        self.clip = clip_encoder

        # Instruction templates for better grounding
        self.templates = [
            "{}",
            "a robot arm {}",
            "the robot should {}",
            "an image of a robot {}",
        ]

    def encode_instruction(self, instruction, use_templates=False):
        """
        Encode instruction with optional template augmentation.

        Args:
            instruction: Natural language instruction
            use_templates: Whether to average over templates

        Returns:
            Embedding (1, hidden_size)
        """
        if use_templates:
            # Encode with multiple templates and average
            texts = [template.format(instruction) for template in self.templates]
            embeddings = self.clip.encode_text(texts)
            embedding = embeddings.mean(dim=0, keepdim=True)
            embedding = embedding / embedding.norm(dim=-1, keepdim=True)
        else:
            embedding = self.clip.encode_text(instruction)

        return embedding

    def extract_objects(self, instruction):
        """
        Extract object references from instruction.

        Simple rule-based extraction (can be replaced with NLP model).
        """
        # Common patterns
        import re

        patterns = [
            r"the (\w+ \w+)",  # "the red block"
            r"a (\w+ \w+)",    # "a blue cup"
            r"(\w+) on",       # "cup on"
            r"pick up (\w+)",  # "pick up block"
        ]

        objects = []
        for pattern in patterns:
            matches = re.findall(pattern, instruction.lower())
            objects.extend(matches)

        return list(set(objects))


# Usage
instruction_encoder = InstructionEncoder(clip)

instruction = "pick up the red block and place it on the blue tray"
embedding = instruction_encoder.encode_instruction(instruction)
print(f"Instruction embedding shape: {embedding.shape}")

objects = instruction_encoder.extract_objects(instruction)
print(f"Extracted objects: {objects}")
```

---

## 2.5 Computing Similarity for Grounding

### Image-Text Matching

```python
class GroundingSimilarity:
    """Compute similarities for visual grounding."""

    def __init__(self, clip_encoder):
        self.clip = clip_encoder

    def find_object_in_image(self, image, object_description, top_k=3):
        """
        Find object in image using CLIP similarity.

        Args:
            image: PIL Image
            object_description: Text describing target object
            top_k: Number of candidate regions to return

        Returns:
            Best matching description and score
        """
        # Generate candidate descriptions
        candidates = [
            object_description,
            f"a {object_description}",
            f"the {object_description}",
            f"a photo of {object_description}",
        ]

        similarities = self.clip.compute_similarity(image, candidates)

        best_idx = similarities.argmax()
        return candidates[best_idx], similarities[best_idx]

    def rank_objects(self, image, object_list):
        """
        Rank multiple objects by presence in image.

        Args:
            image: PIL Image
            object_list: List of object descriptions

        Returns:
            Sorted list of (object, score) tuples
        """
        similarities = self.clip.compute_similarity(image, object_list)

        ranked = sorted(
            zip(object_list, similarities),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked

    def compute_patch_similarities(self, image, object_description):
        """
        Compute per-patch similarity for localization.

        Returns:
            Heatmap of similarities (H, W)
        """
        # Get patch features
        _, patch_tokens = self.clip.patch_encoder.extract_patch_features(image)

        # Normalize patches
        patch_tokens = patch_tokens / patch_tokens.norm(dim=-1, keepdim=True)

        # Get text embedding
        text_emb = self.clip.encode_text(object_description)

        # Compute similarities
        similarities = (patch_tokens @ text_emb.T).squeeze(-1)

        # Reshape to spatial grid
        h = w = int(similarities.shape[0] ** 0.5)
        heatmap = similarities.reshape(h, w).cpu().numpy()

        return heatmap


# Usage
grounding = GroundingSimilarity(clip)

image = Image.open("tabletop_scene.jpg")

# Find object
best, score = grounding.find_object_in_image(image, "red block")
print(f"Best match: '{best}' (score: {score:.3f})")

# Rank objects
objects = ["red block", "blue cup", "green ball", "yellow bowl"]
ranked = grounding.rank_objects(image, objects)
print("Object ranking:")
for obj, score in ranked:
    print(f"  {obj}: {score:.3f}")
```

---

## 2.6 Visualizing Embedding Spaces

### t-SNE Visualization

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

class EmbeddingVisualizer:
    """Visualize embedding spaces for debugging."""

    def __init__(self, clip_encoder):
        self.clip = clip_encoder

    def visualize_image_text_space(self, images, texts, labels=None):
        """
        Visualize images and texts in shared embedding space.

        Args:
            images: List of PIL Images
            texts: List of text strings
            labels: Optional labels for coloring
        """
        # Encode all inputs
        image_embeddings = []
        for img in images:
            emb = self.clip.encode_image(img)
            image_embeddings.append(emb.cpu().numpy())
        image_embeddings = np.vstack(image_embeddings)

        text_embeddings = self.clip.encode_text(texts).cpu().numpy()

        # Combine embeddings
        all_embeddings = np.vstack([image_embeddings, text_embeddings])

        # Apply t-SNE
        tsne = TSNE(n_components=2, perplexity=min(30, len(all_embeddings)-1))
        embeddings_2d = tsne.fit_transform(all_embeddings)

        # Split back
        img_2d = embeddings_2d[:len(images)]
        txt_2d = embeddings_2d[len(images):]

        # Plot
        plt.figure(figsize=(12, 8))

        # Plot images
        plt.scatter(img_2d[:, 0], img_2d[:, 1], c='blue', marker='o',
                   s=100, label='Images', alpha=0.7)

        # Plot texts
        plt.scatter(txt_2d[:, 0], txt_2d[:, 1], c='red', marker='^',
                   s=100, label='Texts', alpha=0.7)

        # Add text labels
        for i, txt in enumerate(texts):
            plt.annotate(txt[:20], (txt_2d[i, 0], txt_2d[i, 1]), fontsize=8)

        plt.legend()
        plt.title("CLIP Embedding Space (t-SNE)")
        plt.savefig("embedding_space.png", dpi=150)
        plt.show()

    def visualize_similarity_matrix(self, images, texts):
        """
        Visualize image-text similarity matrix.
        """
        # Compute all similarities
        n_images = len(images)
        n_texts = len(texts)

        similarities = np.zeros((n_images, n_texts))
        for i, img in enumerate(images):
            sims = self.clip.compute_similarity(img, texts)
            similarities[i] = sims

        # Plot heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(similarities, cmap='viridis', aspect='auto')
        plt.colorbar(label='Cosine Similarity')

        plt.xlabel('Texts')
        plt.ylabel('Images')
        plt.xticks(range(n_texts), texts, rotation=45, ha='right')
        plt.yticks(range(n_images), [f'Image {i}' for i in range(n_images)])

        plt.title("Image-Text Similarity Matrix")
        plt.tight_layout()
        plt.savefig("similarity_matrix.png", dpi=150)
        plt.show()

        return similarities


# Usage
visualizer = EmbeddingVisualizer(clip)

# Load sample images
images = [Image.open(f"scene_{i}.jpg") for i in range(5)]
texts = ["red block", "blue cup", "robot arm", "table", "background"]

# Visualize embedding space
visualizer.visualize_image_text_space(images, texts)

# Visualize similarity matrix
sim_matrix = visualizer.visualize_similarity_matrix(images, texts)
```

---

## 2.7 Multimodal Fusion Strategies

VLA models combine vision and language embeddings using various fusion strategies:

### Early Fusion

```python
class EarlyFusion(nn.Module):
    """Concatenate embeddings early and process together."""

    def __init__(self, image_dim, text_dim, hidden_dim):
        super().__init__()
        self.projection = nn.Linear(image_dim + text_dim, hidden_dim)
        self.layers = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(hidden_dim, nhead=8),
            num_layers=4
        )

    def forward(self, image_emb, text_emb):
        # Concatenate
        combined = torch.cat([image_emb, text_emb], dim=-1)

        # Project and process
        projected = self.projection(combined)
        output = self.layers(projected)

        return output
```

### Cross-Attention Fusion

```python
class CrossAttentionFusion(nn.Module):
    """Use cross-attention to fuse modalities."""

    def __init__(self, dim, num_heads=8):
        super().__init__()

        # Image attends to text
        self.image_cross_attn = nn.MultiheadAttention(dim, num_heads)

        # Text attends to image
        self.text_cross_attn = nn.MultiheadAttention(dim, num_heads)

        self.norm1 = nn.LayerNorm(dim)
        self.norm2 = nn.LayerNorm(dim)

    def forward(self, image_tokens, text_tokens):
        """
        Args:
            image_tokens: (seq_len_img, batch, dim)
            text_tokens: (seq_len_txt, batch, dim)
        """
        # Image attends to text
        img_attended, _ = self.image_cross_attn(
            query=image_tokens,
            key=text_tokens,
            value=text_tokens
        )
        image_out = self.norm1(image_tokens + img_attended)

        # Text attends to image
        txt_attended, _ = self.text_cross_attn(
            query=text_tokens,
            key=image_tokens,
            value=image_tokens
        )
        text_out = self.norm2(text_tokens + txt_attended)

        return image_out, text_out
```

### FiLM Conditioning (RT-1 Style)

```python
class FiLMLayer(nn.Module):
    """Feature-wise Linear Modulation."""

    def __init__(self, feature_dim, condition_dim):
        super().__init__()
        self.gamma_net = nn.Linear(condition_dim, feature_dim)
        self.beta_net = nn.Linear(condition_dim, feature_dim)

    def forward(self, features, condition):
        """
        Modulate features based on condition.

        Args:
            features: (batch, ..., feature_dim)
            condition: (batch, condition_dim)
        """
        gamma = self.gamma_net(condition)
        beta = self.beta_net(condition)

        # Add dimensions to broadcast
        while gamma.dim() < features.dim():
            gamma = gamma.unsqueeze(1)
            beta = beta.unsqueeze(1)

        return gamma * features + beta


class FiLMConditionedEncoder(nn.Module):
    """Vision encoder with FiLM conditioning on language."""

    def __init__(self, vision_dim, text_dim, num_layers=4):
        super().__init__()

        self.layers = nn.ModuleList()
        self.film_layers = nn.ModuleList()

        for _ in range(num_layers):
            self.layers.append(
                nn.TransformerEncoderLayer(vision_dim, nhead=8)
            )
            self.film_layers.append(
                FiLMLayer(vision_dim, text_dim)
            )

    def forward(self, image_tokens, text_embedding):
        """
        Process image tokens conditioned on text.

        Args:
            image_tokens: (batch, seq_len, vision_dim)
            text_embedding: (batch, text_dim)
        """
        x = image_tokens

        for layer, film in zip(self.layers, self.film_layers):
            x = layer(x)
            x = film(x, text_embedding)

        return x
```

---

## 2.8 Benchmarking VLM Performance

### Latency Measurement

```python
import time

class VLMBenchmark:
    """Benchmark VLM inference performance."""

    def __init__(self, clip_encoder):
        self.clip = clip_encoder

    def benchmark_image_encoding(self, image, num_runs=100):
        """Measure image encoding latency."""
        # Warmup
        for _ in range(10):
            _ = self.clip.encode_image(image)

        # Timed runs
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            _ = self.clip.encode_image(image)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - start) * 1000)  # ms

        return {
            "mean_ms": np.mean(times),
            "std_ms": np.std(times),
            "p50_ms": np.percentile(times, 50),
            "p99_ms": np.percentile(times, 99)
        }

    def benchmark_text_encoding(self, texts, num_runs=100):
        """Measure text encoding latency."""
        # Warmup
        for _ in range(10):
            _ = self.clip.encode_text(texts)

        # Timed runs
        times = []
        for _ in range(num_runs):
            start = time.perf_counter()
            _ = self.clip.encode_text(texts)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - start) * 1000)

        return {
            "mean_ms": np.mean(times),
            "std_ms": np.std(times),
            "p50_ms": np.percentile(times, 50),
            "p99_ms": np.percentile(times, 99)
        }

    def full_benchmark(self, image, texts):
        """Run complete benchmark suite."""
        print("VLM Benchmark Results")
        print("=" * 50)

        # Image encoding
        img_results = self.benchmark_image_encoding(image)
        print(f"Image Encoding:")
        print(f"  Mean: {img_results['mean_ms']:.2f} ms")
        print(f"  P99:  {img_results['p99_ms']:.2f} ms")

        # Text encoding
        txt_results = self.benchmark_text_encoding(texts)
        print(f"Text Encoding ({len(texts)} texts):")
        print(f"  Mean: {txt_results['mean_ms']:.2f} ms")
        print(f"  P99:  {txt_results['p99_ms']:.2f} ms")

        # Total
        total_mean = img_results['mean_ms'] + txt_results['mean_ms']
        print(f"Total (image + text):")
        print(f"  Mean: {total_mean:.2f} ms")

        return {"image": img_results, "text": txt_results}


# Run benchmark
benchmark = VLMBenchmark(clip)

image = Image.open("test_scene.jpg")
texts = ["red block", "blue cup", "robot arm"]

results = benchmark.full_benchmark(image, texts)
```

---

## 2.9 Summary

In this chapter, you learned:

1. **CLIP Architecture**: Contrastive learning for image-text alignment
2. **Vision Transformers**: Patch-based image encoding with ViT
3. **Image Encoding**: Extracting CLS tokens and patch features
4. **Text Encoding**: Processing robot instructions
5. **Similarity Computation**: Matching images and text for grounding
6. **Embedding Visualization**: Debugging with t-SNE and heatmaps
7. **Fusion Strategies**: Combining vision and language (early, cross-attention, FiLM)
8. **Benchmarking**: Measuring VLM latency

---

## 2.10 Exercises

### Exercise 2.1: CLIP Installation
Set up CLIP and verify image/text encoding works correctly.

### Exercise 2.2: Embedding Analysis
Extract embeddings for 10 images and 10 robot instructions. Visualize with t-SNE.

### Exercise 2.3: Object Ranking
Implement an object ranking system that takes an image and returns the most likely objects present.

### Exercise 2.4: Fusion Comparison
Implement early fusion and cross-attention fusion. Compare their outputs on sample data.

---

## Quick Reference

### CLIP Loading
```python
from transformers import CLIPProcessor, CLIPModel
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
```

### Image Encoding
```python
inputs = processor(images=image, return_tensors="pt")
features = model.get_image_features(**inputs)
```

### Text Encoding
```python
inputs = processor(text=texts, return_tensors="pt", padding=True)
features = model.get_text_features(**inputs)
```

### Similarity
```python
similarity = (image_features @ text_features.T).softmax(dim=-1)
```

---

**Next Chapter**: [Chapter 3 - Action Tokenization and Representation](ch03-action-tokenization.md)
