# Module 4 Tasks: Physical AI – Vision-Language-Action Models

**Specification**: `specs/module4-vla.spec.md`
**Created**: 2026-01-07
**Status**: Draft
**Total Tasks**: 98

---

## Task Overview

| Phase | Description | Tasks | Priority |
|-------|-------------|-------|----------|
| 1 | Environment Setup | 8 | P0 |
| 2 | VLM Foundations | 10 | P0 |
| 3 | Action Tokenization | 9 | P0 |
| 4 | Language Grounding | 10 | P1 |
| 5 | VLA Pipeline | 12 | P0 |
| 6 | ROS 2 Integration | 10 | P1 |
| 7 | Safety Constraints | 9 | P0 |
| 8 | Fine-tuning | 10 | P2 |
| 9 | Evaluation | 8 | P1 |
| 10 | End-to-End Demo | 7 | P1 |
| 11 | Documentation | 5 | P2 |

---

## Phase 1: Environment Setup

### Task 1.1: Verify System Requirements
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Verify hardware meets VLA model requirements.

**Acceptance Criteria**:
- [ ] GPU has ≥16GB VRAM
- [ ] System has ≥32GB RAM
- [ ] ≥200GB storage available
- [ ] CUDA 11.8+ installed

**Test Case**:
```bash
nvidia-smi --query-gpu=memory.total --format=csv
# Expected: >= 16384 MiB

free -h
# Expected: Mem >= 32G

df -h /
# Expected: >= 200G available
```

---

### Task 1.2: Install PyTorch with CUDA
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Install PyTorch 2.0+ with CUDA support.

**Acceptance Criteria**:
- [ ] PyTorch 2.0+ installed
- [ ] CUDA acceleration working
- [ ] cuDNN available

**Test Case**:
```python
import torch
assert torch.__version__ >= "2.0"
assert torch.cuda.is_available()
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

---

### Task 1.3: Install Transformers Library
**Priority**: P0
**Estimated Effort**: 20 min

**Description**: Install Hugging Face Transformers and related libraries.

**Acceptance Criteria**:
- [ ] transformers installed
- [ ] accelerate installed
- [ ] bitsandbytes installed (for quantization)

**Test Case**:
```python
import transformers
import accelerate
print(f"Transformers: {transformers.__version__}")
```

---

### Task 1.4: Download CLIP Model
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Download and cache CLIP ViT-L model.

**Acceptance Criteria**:
- [ ] CLIP model downloaded
- [ ] Model loads successfully
- [ ] Inference runs on test image

**Test Case**:
```python
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
print("CLIP loaded successfully")
```

---

### Task 1.5: Download OpenVLA Model
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Download OpenVLA-7B model weights.

**Acceptance Criteria**:
- [ ] Model weights downloaded (~15GB)
- [ ] Config files present
- [ ] Model loads without OOM

**Test Case**:
```python
from transformers import AutoModelForVision2Seq, AutoProcessor

model = AutoModelForVision2Seq.from_pretrained(
    "openvla/openvla-7b",
    torch_dtype=torch.float16,
    device_map="auto"
)
print("OpenVLA loaded successfully")
```

---

### Task 1.6: Set Up ROS 2 Workspace
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Create ROS 2 workspace for VLA packages.

**Acceptance Criteria**:
- [ ] Workspace created at `~/humanoid_vla_ws`
- [ ] Source directories created
- [ ] Workspace builds successfully

**Test Case**:
```bash
cd ~/humanoid_vla_ws
colcon build
source install/setup.bash
```

---

### Task 1.7: Install Simulation Dependencies
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Install Gazebo and visualization tools.

**Acceptance Criteria**:
- [ ] Gazebo Fortress/Garden installed
- [ ] RViz2 working
- [ ] ros_gz_bridge available

**Test Case**:
```bash
gz sim --version
ros2 run rviz2 rviz2
```

---

### Task 1.8: Create Package Structure
**Priority**: P0
**Estimated Effort**: 30 min

**Description**: Create ROS 2 package structure for VLA.

**Acceptance Criteria**:
- [ ] humanoid_vla package created
- [ ] humanoid_vla_ros package created
- [ ] humanoid_vla_sim package created
- [ ] All packages build

**Test Case**:
```bash
ros2 pkg list | grep humanoid_vla
# Expected: humanoid_vla, humanoid_vla_ros, humanoid_vla_sim
```

---

## Phase 2: VLM Foundations

### Task 2.1: Implement CLIP Image Encoder
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Create wrapper for CLIP image encoding.

**Acceptance Criteria**:
- [ ] Accepts PIL Image or numpy array
- [ ] Returns normalized embeddings
- [ ] Supports batch processing
- [ ] GPU acceleration enabled

**Test Case**:
```python
encoder = CLIPImageEncoder()
embedding = encoder.encode(image)
assert embedding.shape == (1, 768)
assert torch.allclose(embedding.norm(), torch.tensor(1.0), atol=0.01)
```

---

### Task 2.2: Implement CLIP Text Encoder
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Create wrapper for CLIP text encoding.

**Acceptance Criteria**:
- [ ] Accepts string or list of strings
- [ ] Returns normalized embeddings
- [ ] Handles tokenization internally
- [ ] Truncates long inputs appropriately

**Test Case**:
```python
encoder = CLIPTextEncoder()
embedding = encoder.encode("pick up the red block")
assert embedding.shape == (1, 768)
```

---

### Task 2.3: Implement Similarity Computation
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Compute image-text similarity scores.

**Acceptance Criteria**:
- [ ] Computes cosine similarity
- [ ] Supports batch comparisons
- [ ] Returns normalized scores [0, 1]

**Test Case**:
```python
similarity = compute_similarity(image_emb, text_emb)
assert 0 <= similarity <= 1
```

---

### Task 2.4: Implement Vision Transformer Wrapper
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Create ViT wrapper for feature extraction.

**Acceptance Criteria**:
- [ ] Extracts patch tokens
- [ ] Returns CLS token and patch embeddings
- [ ] Configurable image size
- [ ] Supports different ViT variants

**Test Case**:
```python
vit = ViTWrapper("vit-large-patch16")
features = vit.extract_features(image)
assert features["cls"].shape == (1, 1024)
assert features["patches"].shape == (1, 196, 1024)
```

---

### Task 2.5: Implement Image Preprocessing Pipeline
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create standard image preprocessing.

**Acceptance Criteria**:
- [ ] Resizes to model input size
- [ ] Normalizes with ImageNet stats
- [ ] Converts to tensor
- [ ] Handles different input formats

**Test Case**:
```python
preprocessor = ImagePreprocessor(size=224)
tensor = preprocessor(image)
assert tensor.shape == (1, 3, 224, 224)
assert tensor.min() >= -3 and tensor.max() <= 3
```

---

### Task 2.6: Implement Embedding Visualization
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Visualize embedding spaces with t-SNE/UMAP.

**Acceptance Criteria**:
- [ ] Supports t-SNE and UMAP
- [ ] Plots image and text embeddings
- [ ] Color codes by category
- [ ] Saves visualization to file

**Test Case**:
```python
visualize_embeddings(image_embs, text_embs, labels, method="tsne")
# Saves embedding_space.png
```

---

### Task 2.7: Implement Attention Visualization
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Visualize attention maps from vision model.

**Acceptance Criteria**:
- [ ] Extracts attention weights
- [ ] Overlays on original image
- [ ] Supports multi-head averaging
- [ ] Generates attention heatmap

**Test Case**:
```python
attention_map = visualize_attention(model, image, text)
# Returns PIL Image with attention overlay
```

---

### Task 2.8: Implement Zero-Shot Classification
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Use CLIP for zero-shot object classification.

**Acceptance Criteria**:
- [ ] Accepts image and list of labels
- [ ] Returns probability distribution
- [ ] Top-k predictions available
- [ ] Confidence scores included

**Test Case**:
```python
classifier = ZeroShotClassifier()
results = classifier.classify(image, ["red block", "blue cup", "green ball"])
assert sum(results.values()) == pytest.approx(1.0)
```

---

### Task 2.9: Benchmark VLM Inference Speed
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Measure VLM inference latency.

**Acceptance Criteria**:
- [ ] Measures image encoding time
- [ ] Measures text encoding time
- [ ] Reports mean and p99 latency
- [ ] Tests batch sizes 1, 4, 8

**Test Case**:
```python
benchmark = VLMBenchmark()
results = benchmark.run(model, num_iterations=100)
assert results["image_encode_ms"] < 50
assert results["text_encode_ms"] < 10
```

---

### Task 2.10: Write VLM Foundations Tests
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create unit tests for VLM components.

**Acceptance Criteria**:
- [ ] Tests for image encoder
- [ ] Tests for text encoder
- [ ] Tests for similarity computation
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_vlm_foundations.py -v
# All tests pass
```

---

## Phase 3: Action Tokenization

### Task 3.1: Design Action Vocabulary
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Define action token vocabulary for humanoid.

**Acceptance Criteria**:
- [ ] Position bins defined (256 per axis)
- [ ] Rotation bins defined (256 per axis)
- [ ] Gripper tokens defined (open/close/partial)
- [ ] Special tokens (start, end, pad)
- [ ] Total vocab size documented

**Test Case**:
```python
vocab = ActionVocabulary()
assert vocab.size == 256 * 6 + 3 + 3  # pos + rot + gripper + special
assert vocab.encode_position([0.5, 0.0, 0.3]) is not None
```

---

### Task 3.2: Implement Position Tokenizer
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Tokenize 3D positions into discrete bins.

**Acceptance Criteria**:
- [ ] Maps [-1, 1] to 256 bins per axis
- [ ] Handles clipping for out-of-range
- [ ] Supports batch encoding
- [ ] Invertible with decode()

**Test Case**:
```python
tokenizer = PositionTokenizer(num_bins=256, range=(-1, 1))
tokens = tokenizer.encode([0.5, -0.3, 0.1])
decoded = tokenizer.decode(tokens)
assert np.allclose(decoded, [0.5, -0.3, 0.1], atol=0.01)
```

---

### Task 3.3: Implement Rotation Tokenizer
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Tokenize rotations (Euler or quaternion).

**Acceptance Criteria**:
- [ ] Supports Euler angle input
- [ ] Supports quaternion input
- [ ] 256 bins per rotation axis
- [ ] Handles angle wrapping

**Test Case**:
```python
tokenizer = RotationTokenizer(representation="euler")
tokens = tokenizer.encode([0.0, 0.5, -0.3])  # roll, pitch, yaw
decoded = tokenizer.decode(tokens)
assert np.allclose(decoded, [0.0, 0.5, -0.3], atol=0.02)
```

---

### Task 3.4: Implement Joint Tokenizer
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Tokenize joint positions for humanoid.

**Acceptance Criteria**:
- [ ] Handles 14 DOF humanoid
- [ ] Per-joint normalization based on limits
- [ ] 256 bins per joint
- [ ] Supports named joint access

**Test Case**:
```python
tokenizer = JointTokenizer(joint_limits=HUMANOID_LIMITS)
tokens = tokenizer.encode(joint_positions)
assert len(tokens) == 14
decoded = tokenizer.decode(tokens)
assert np.allclose(decoded, joint_positions, atol=0.02)
```

---

### Task 3.5: Implement Action Sequence Tokenizer
**Priority**: P0
**Estimated Effort**: 3 hours

**Description**: Tokenize full action sequences.

**Acceptance Criteria**:
- [ ] Combines position, rotation, gripper tokens
- [ ] Adds sequence tokens (start, end)
- [ ] Supports variable length sequences
- [ ] Handles padding for batching

**Test Case**:
```python
tokenizer = ActionSequenceTokenizer()
sequence = [action1, action2, action3]
tokens = tokenizer.encode(sequence)
assert tokens[0] == tokenizer.START_TOKEN
assert tokens[-1] == tokenizer.END_TOKEN
```

---

### Task 3.6: Implement K-Means Action Tokenizer
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Learn action clusters from demonstration data.

**Acceptance Criteria**:
- [ ] Fits K-means on action data
- [ ] Configurable number of clusters (256, 512, 1024)
- [ ] Saves and loads cluster centers
- [ ] Reports cluster statistics

**Test Case**:
```python
tokenizer = KMeansActionTokenizer(n_clusters=256)
tokenizer.fit(demonstration_actions)
tokens = tokenizer.encode(new_actions)
reconstruction_error = tokenizer.evaluate(test_actions)
assert reconstruction_error < 0.05
```

---

### Task 3.7: Implement Action Detokenizer
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Convert action tokens back to continuous values.

**Acceptance Criteria**:
- [ ] Inverts tokenization exactly
- [ ] Handles all action types
- [ ] Supports autoregressive decoding
- [ ] Reports confidence per token

**Test Case**:
```python
detokenizer = ActionDetokenizer(vocab)
actions = detokenizer.decode(token_sequence)
assert actions.shape == (seq_len, action_dim)
```

---

### Task 3.8: Evaluate Tokenization Quality
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Measure tokenization reconstruction error.

**Acceptance Criteria**:
- [ ] Computes per-axis RMSE
- [ ] Reports percentile errors
- [ ] Compares tokenization schemes
- [ ] Generates quality report

**Test Case**:
```python
evaluator = TokenizationEvaluator()
metrics = evaluator.evaluate(tokenizer, test_actions)
assert metrics["rmse"] < 0.05
assert metrics["p99_error"] < 0.1
```

---

### Task 3.9: Write Action Tokenization Tests
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create comprehensive tokenization tests.

**Acceptance Criteria**:
- [ ] Tests for all tokenizer types
- [ ] Round-trip encoding tests
- [ ] Edge case handling
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_action_tokenization.py -v
# All tests pass
```

---

## Phase 4: Language Grounding

### Task 4.1: Integrate Object Detection Model
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Set up object detection (YOLO/DETR).

**Acceptance Criteria**:
- [ ] Model loads successfully
- [ ] Detects common objects
- [ ] Returns bounding boxes and labels
- [ ] Inference < 100ms

**Test Case**:
```python
detector = ObjectDetector("yolov8n")
detections = detector.detect(image)
assert len(detections) > 0
assert all(d.confidence > 0.5 for d in detections)
```

---

### Task 4.2: Implement Open-Vocabulary Detection
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Detect objects from text descriptions.

**Acceptance Criteria**:
- [ ] Accepts arbitrary text queries
- [ ] Uses CLIP for matching
- [ ] Returns bounding boxes
- [ ] Supports multiple queries

**Test Case**:
```python
detector = OpenVocabDetector()
boxes = detector.detect(image, ["red block", "blue cup"])
assert len(boxes) == 2
```

---

### Task 4.3: Implement Referring Expression Comprehension
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Localize objects from referring expressions.

**Acceptance Criteria**:
- [ ] Handles spatial references ("on the left")
- [ ] Handles relative references ("next to the cup")
- [ ] Returns single best match
- [ ] Confidence score provided

**Test Case**:
```python
grounder = ReferringExpressionGrounder()
box = grounder.ground(image, "the red block on the left")
assert box is not None
assert box.confidence > 0.7
```

---

### Task 4.4: Implement Spatial Relationship Parser
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Parse spatial relationships from text.

**Acceptance Criteria**:
- [ ] Extracts subject and object
- [ ] Identifies spatial relation (on, under, left, right)
- [ ] Handles multiple relations
- [ ] Returns structured output

**Test Case**:
```python
parser = SpatialParser()
relations = parser.parse("put the red block on top of the blue box")
assert relations[0].subject == "red block"
assert relations[0].object == "blue box"
assert relations[0].relation == "on_top_of"
```

---

### Task 4.5: Implement Scene Graph Builder
**Priority**: P2
**Estimated Effort**: 3 hours

**Description**: Build scene graph from image and detections.

**Acceptance Criteria**:
- [ ] Nodes represent detected objects
- [ ] Edges represent spatial relationships
- [ ] Attributes include position, size, color
- [ ] Exportable to JSON

**Test Case**:
```python
builder = SceneGraphBuilder()
graph = builder.build(image, detections)
assert len(graph.nodes) == len(detections)
assert graph.has_edge("red_block", "table")
```

---

### Task 4.6: Implement Affordance Prediction
**Priority**: P2
**Estimated Effort**: 3 hours

**Description**: Predict action affordances for objects.

**Acceptance Criteria**:
- [ ] Predicts graspable regions
- [ ] Identifies functional parts
- [ ] Returns affordance masks
- [ ] Supports common actions (grasp, push, place)

**Test Case**:
```python
predictor = AffordancePredictor()
affordances = predictor.predict(image, "cup")
assert "graspable" in affordances
assert affordances["graspable"].shape == image.shape[:2]
```

---

### Task 4.7: Implement Instruction Parser
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Parse robot instructions into structured commands.

**Acceptance Criteria**:
- [ ] Extracts action verb (pick, place, move)
- [ ] Extracts target object
- [ ] Extracts destination (if applicable)
- [ ] Handles multi-step instructions

**Test Case**:
```python
parser = InstructionParser()
command = parser.parse("pick up the red block and put it in the box")
assert command.actions[0].verb == "pick"
assert command.actions[0].target == "red block"
assert command.actions[1].verb == "place"
assert command.actions[1].destination == "box"
```

---

### Task 4.8: Implement Grounding Fusion
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Combine detection and language grounding.

**Acceptance Criteria**:
- [ ] Fuses detection boxes with text queries
- [ ] Ranks matches by confidence
- [ ] Handles ambiguity
- [ ] Returns top-k matches

**Test Case**:
```python
fusion = GroundingFusion(detector, text_encoder)
matches = fusion.ground(image, "the red object")
assert len(matches) > 0
assert matches[0].confidence > 0.8
```

---

### Task 4.9: Implement Clarification Generator
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Generate clarification questions for ambiguous inputs.

**Acceptance Criteria**:
- [ ] Detects ambiguity (multiple matches)
- [ ] Generates natural questions
- [ ] Provides options to user
- [ ] Handles user response

**Test Case**:
```python
clarifier = ClarificationGenerator()
if clarifier.is_ambiguous(matches):
    question = clarifier.generate_question(matches)
    assert "which" in question.lower() or "do you mean" in question.lower()
```

---

### Task 4.10: Write Language Grounding Tests
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create tests for grounding components.

**Acceptance Criteria**:
- [ ] Tests for object detection
- [ ] Tests for referring expressions
- [ ] Tests for instruction parsing
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_language_grounding.py -v
# All tests pass
```

---

## Phase 5: VLA Pipeline

### Task 5.1: Implement VLA Model Wrapper
**Priority**: P0
**Estimated Effort**: 3 hours

**Description**: Create unified interface for VLA model.

**Acceptance Criteria**:
- [ ] Wraps OpenVLA or similar model
- [ ] Handles input preprocessing
- [ ] Manages GPU memory
- [ ] Supports quantization (4-bit, 8-bit)

**Test Case**:
```python
vla = VLAModelWrapper("openvla/openvla-7b", quantization="4bit")
outputs = vla.generate(image, instruction, robot_state)
assert outputs.action_tokens is not None
```

---

### Task 5.2: Implement Multi-Image Input Handler
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Handle multiple images (current + history).

**Acceptance Criteria**:
- [ ] Accepts list of images
- [ ] Maintains temporal order
- [ ] Configurable history length
- [ ] Efficient memory management

**Test Case**:
```python
handler = MultiImageHandler(history_length=2)
inputs = handler.prepare([img_t, img_t_minus_1])
assert inputs.shape[1] == 2  # Two images
```

---

### Task 5.3: Implement State Conditioning
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Condition VLA on robot state.

**Acceptance Criteria**:
- [ ] Accepts joint positions
- [ ] Accepts end-effector pose
- [ ] Normalizes state values
- [ ] Embeds state into model input

**Test Case**:
```python
conditioner = StateConditioner()
state_embedding = conditioner.embed(joint_positions, ee_pose)
assert state_embedding.shape[-1] == model.hidden_size
```

---

### Task 5.4: Implement Autoregressive Action Generation
**Priority**: P0
**Estimated Effort**: 3 hours

**Description**: Generate actions autoregressively.

**Acceptance Criteria**:
- [ ] Generates one token at a time
- [ ] Stops at end token or max length
- [ ] Supports temperature sampling
- [ ] Returns confidence per token

**Test Case**:
```python
generator = ActionGenerator(model, tokenizer)
actions = generator.generate(
    image, instruction, state,
    max_tokens=10, temperature=0.7
)
assert len(actions) <= 10
```

---

### Task 5.5: Implement Beam Search for Actions
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Use beam search for action generation.

**Acceptance Criteria**:
- [ ] Maintains top-k hypotheses
- [ ] Configurable beam width
- [ ] Returns multiple action sequences
- [ ] Includes sequence scores

**Test Case**:
```python
generator = BeamSearchGenerator(model, tokenizer, beam_width=5)
sequences = generator.generate(image, instruction, state)
assert len(sequences) == 5
assert sequences[0].score >= sequences[1].score
```

---

### Task 5.6: Implement Action Chunk Prediction
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Predict action chunks for temporal consistency.

**Acceptance Criteria**:
- [ ] Predicts multiple timesteps at once
- [ ] Configurable chunk size (4-16 steps)
- [ ] Smooth interpolation between chunks
- [ ] Handles variable execution speed

**Test Case**:
```python
predictor = ActionChunkPredictor(chunk_size=8)
chunk = predictor.predict(image, instruction, state)
assert chunk.shape == (8, action_dim)
```

---

### Task 5.7: Implement Pipeline Orchestrator
**Priority**: P0
**Estimated Effort**: 3 hours

**Description**: Orchestrate full VLA pipeline.

**Acceptance Criteria**:
- [ ] Coordinates all components
- [ ] Manages data flow
- [ ] Handles errors gracefully
- [ ] Provides timing statistics

**Test Case**:
```python
pipeline = VLAPipeline(config)
result = pipeline.process(image, instruction, state)
assert result.actions is not None
assert result.latency_ms < 2000
```

---

### Task 5.8: Implement Caching Layer
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Cache intermediate computations.

**Acceptance Criteria**:
- [ ] Caches image embeddings
- [ ] Caches text embeddings
- [ ] LRU eviction policy
- [ ] Configurable cache size

**Test Case**:
```python
cache = VLACache(max_size=100)
# First call computes
result1 = pipeline.process(image, instruction, state, cache=cache)
# Second call uses cache
result2 = pipeline.process(image, instruction, state, cache=cache)
assert result2.cache_hit == True
```

---

### Task 5.9: Implement Pipeline Profiler
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Profile VLA pipeline performance.

**Acceptance Criteria**:
- [ ] Measures per-component latency
- [ ] Tracks GPU memory usage
- [ ] Identifies bottlenecks
- [ ] Generates performance report

**Test Case**:
```python
profiler = PipelineProfiler()
with profiler:
    result = pipeline.process(image, instruction, state)
report = profiler.get_report()
assert "vision_encode_ms" in report
assert "action_decode_ms" in report
```

---

### Task 5.10: Implement Model Quantization
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Quantize VLA model for faster inference.

**Acceptance Criteria**:
- [ ] Supports 8-bit quantization
- [ ] Supports 4-bit quantization
- [ ] Measures accuracy impact
- [ ] Measures speedup

**Test Case**:
```python
quantizer = ModelQuantizer()
model_4bit = quantizer.quantize(model, bits=4)
assert model_4bit.memory_footprint < model.memory_footprint / 2
```

---

### Task 5.11: Benchmark End-to-End Latency
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Measure full pipeline latency.

**Acceptance Criteria**:
- [ ] End-to-end latency < 2 seconds
- [ ] Reports p50, p95, p99
- [ ] Tests multiple input sizes
- [ ] Documents optimization paths

**Test Case**:
```python
benchmark = PipelineBenchmark(pipeline)
results = benchmark.run(num_iterations=100)
assert results["p99_ms"] < 2000
```

---

### Task 5.12: Write VLA Pipeline Tests
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create integration tests for VLA pipeline.

**Acceptance Criteria**:
- [ ] Tests for full pipeline
- [ ] Tests for error handling
- [ ] Tests for edge cases
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_vla_pipeline.py -v
# All tests pass
```

---

## Phase 6: ROS 2 Integration

### Task 6.1: Create VLA Message Definitions
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Define custom ROS 2 messages for VLA.

**Acceptance Criteria**:
- [ ] VLACommand.msg defined
- [ ] VLAAction.msg defined
- [ ] VLAStatus.msg defined
- [ ] Messages build successfully

**Test Case**:
```python
from humanoid_vla_ros.msg import VLACommand, VLAAction
cmd = VLACommand()
cmd.instruction = "pick up the red block"
```

---

### Task 6.2: Create VLA Service Definitions
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Define services for task execution.

**Acceptance Criteria**:
- [ ] ExecuteTask.srv defined
- [ ] GetStatus.srv defined
- [ ] StopExecution.srv defined
- [ ] Services build successfully

**Test Case**:
```bash
ros2 interface show humanoid_vla_ros/srv/ExecuteTask
```

---

### Task 6.3: Implement Camera Subscriber
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Subscribe to camera image topics.

**Acceptance Criteria**:
- [ ] Subscribes to `/camera/image_raw`
- [ ] Handles compressed images
- [ ] Converts to PIL/numpy format
- [ ] Manages image buffer

**Test Case**:
```python
subscriber = CameraSubscriber("/camera/image_raw")
image = subscriber.get_latest_image()
assert image is not None
assert image.shape[2] == 3
```

---

### Task 6.4: Implement Command Subscriber
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Subscribe to text command topics.

**Acceptance Criteria**:
- [ ] Subscribes to `/vla/instruction`
- [ ] Queues incoming commands
- [ ] Handles command cancellation
- [ ] Logs command history

**Test Case**:
```python
subscriber = CommandSubscriber("/vla/instruction")
# Publish command from another terminal
command = subscriber.get_next_command()
assert command.instruction != ""
```

---

### Task 6.5: Implement State Subscriber
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Subscribe to robot state topics.

**Acceptance Criteria**:
- [ ] Subscribes to `/joint_states`
- [ ] Subscribes to `/robot_pose` (optional)
- [ ] Maintains latest state
- [ ] Handles missing data

**Test Case**:
```python
subscriber = StateSubscriber()
state = subscriber.get_current_state()
assert len(state.positions) == 14
```

---

### Task 6.6: Implement Action Publisher
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Publish robot commands.

**Acceptance Criteria**:
- [ ] Publishes to `/joint_commands`
- [ ] Supports position and effort modes
- [ ] Rate-limited publishing
- [ ] Handles controller type

**Test Case**:
```python
publisher = ActionPublisher("/joint_commands")
publisher.publish(joint_positions)
# Robot moves to commanded position
```

---

### Task 6.7: Implement Main VLA Node
**Priority**: P0
**Estimated Effort**: 4 hours

**Description**: Create main VLA inference node.

**Acceptance Criteria**:
- [ ] Integrates all subscribers/publishers
- [ ] Runs VLA pipeline on callbacks
- [ ] Publishes at stable rate (10 Hz)
- [ ] Handles lifecycle events

**Test Case**:
```bash
ros2 run humanoid_vla_ros vla_node
# Node starts and responds to commands
```

---

### Task 6.8: Implement Task Execution Service
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Service for task execution requests.

**Acceptance Criteria**:
- [ ] Accepts ExecuteTask requests
- [ ] Returns success/failure
- [ ] Provides progress updates
- [ ] Supports timeout

**Test Case**:
```bash
ros2 service call /vla/execute_task humanoid_vla_ros/srv/ExecuteTask \
  "{instruction: 'pick up the red block'}"
```

---

### Task 6.9: Create Launch File
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Create launch file for VLA system.

**Acceptance Criteria**:
- [ ] Launches VLA node
- [ ] Configures parameters
- [ ] Sets up remappings
- [ ] Includes simulation option

**Test Case**:
```bash
ros2 launch humanoid_vla_ros vla_demo.launch.py
# All nodes start successfully
```

---

### Task 6.10: Write ROS 2 Integration Tests
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Create ROS 2 integration tests.

**Acceptance Criteria**:
- [ ] Tests message passing
- [ ] Tests service calls
- [ ] Tests node lifecycle
- [ ] All tests pass

**Test Case**:
```bash
colcon test --packages-select humanoid_vla_ros
# All tests pass
```

---

## Phase 7: Safety Constraints

### Task 7.1: Implement Joint Limit Checker
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Check actions against joint limits.

**Acceptance Criteria**:
- [ ] Loads joint limits from URDF
- [ ] Clips actions to limits
- [ ] Logs violations
- [ ] Supports soft limits

**Test Case**:
```python
checker = JointLimitChecker(urdf_path)
safe_action = checker.clip(unsafe_action)
assert all(checker.is_within_limits(safe_action))
```

---

### Task 7.2: Implement Workspace Boundary Checker
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Check end-effector stays in workspace.

**Acceptance Criteria**:
- [ ] Defines workspace as box or convex hull
- [ ] Computes forward kinematics
- [ ] Rejects out-of-workspace actions
- [ ] Provides distance to boundary

**Test Case**:
```python
checker = WorkspaceBoundaryChecker(workspace_limits)
if not checker.is_valid(action, current_state):
    action = checker.project_to_boundary(action)
```

---

### Task 7.3: Implement Velocity Limiter
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Limit joint velocities.

**Acceptance Criteria**:
- [ ] Computes velocity from position change
- [ ] Clips velocity to limits
- [ ] Scales position change accordingly
- [ ] Handles variable timestep

**Test Case**:
```python
limiter = VelocityLimiter(max_velocities)
safe_action = limiter.limit(current_pos, target_pos, dt)
velocity = (safe_action - current_pos) / dt
assert all(abs(velocity) <= max_velocities)
```

---

### Task 7.4: Implement Acceleration Limiter
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Limit joint accelerations.

**Acceptance Criteria**:
- [ ] Tracks velocity history
- [ ] Computes acceleration
- [ ] Clips to limits
- [ ] Smooth trajectory modification

**Test Case**:
```python
limiter = AccelerationLimiter(max_accelerations)
safe_action = limiter.limit(current_vel, target_vel, dt)
```

---

### Task 7.5: Implement Confidence Filter
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Filter actions by model confidence.

**Acceptance Criteria**:
- [ ] Rejects low-confidence predictions
- [ ] Configurable threshold
- [ ] Provides fallback action
- [ ] Logs rejection reasons

**Test Case**:
```python
filter = ConfidenceFilter(threshold=0.7)
if not filter.accept(action, confidence):
    action = filter.get_safe_fallback()
```

---

### Task 7.6: Implement Collision Checker
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Check for self-collision and environment collision.

**Acceptance Criteria**:
- [ ] Self-collision detection
- [ ] Environment collision (basic)
- [ ] Uses simplified collision geometry
- [ ] Fast enough for real-time

**Test Case**:
```python
checker = CollisionChecker(robot_model, environment)
if checker.is_collision(action):
    action = checker.find_collision_free(action)
```

---

### Task 7.7: Implement Action Smoother
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Smooth action sequences.

**Acceptance Criteria**:
- [ ] Moving average filter
- [ ] Exponential smoothing option
- [ ] Maintains responsiveness
- [ ] Configurable window size

**Test Case**:
```python
smoother = ActionSmoother(window_size=5, method="ema")
smooth_action = smoother.smooth(raw_action)
```

---

### Task 7.8: Implement Emergency Stop
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Emergency stop mechanism.

**Acceptance Criteria**:
- [ ] Triggered by service call
- [ ] Triggered by anomaly detection
- [ ] Holds current position
- [ ] Requires explicit reset

**Test Case**:
```bash
ros2 service call /vla/emergency_stop std_srvs/srv/Trigger
# Robot stops immediately
```

---

### Task 7.9: Write Safety Tests
**Priority**: P0
**Estimated Effort**: 2 hours

**Description**: Create comprehensive safety tests.

**Acceptance Criteria**:
- [ ] Tests for all safety components
- [ ] Adversarial input tests
- [ ] Integration tests
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_safety.py -v
# All tests pass
```

---

## Phase 8: Fine-tuning

### Task 8.1: Design Data Collection Format
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Define demonstration data format.

**Acceptance Criteria**:
- [ ] Stores images, instructions, actions
- [ ] Includes robot state
- [ ] Timestamped entries
- [ ] Efficient storage format (HDF5/zarr)

**Test Case**:
```python
demo = DemonstrationData()
demo.add_step(image, instruction, action, state)
demo.save("episode_001.hdf5")
```

---

### Task 8.2: Implement Data Collection Tool
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Tool for collecting demonstrations.

**Acceptance Criteria**:
- [ ] Records teleoperation data
- [ ] Prompts for text instruction
- [ ] Handles episode boundaries
- [ ] Validates collected data

**Test Case**:
```bash
ros2 run humanoid_vla collect_demo --output demos/
# Collects demonstration with instructions
```

---

### Task 8.3: Implement Data Augmentation
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Augment demonstration data.

**Acceptance Criteria**:
- [ ] Image augmentation (crop, color, flip)
- [ ] Language paraphrasing
- [ ] Action noise injection
- [ ] Balanced augmentation

**Test Case**:
```python
augmenter = DemoAugmenter()
augmented = augmenter.augment(demo, factor=5)
assert len(augmented) == 5 * len(demo)
```

---

### Task 8.4: Implement Dataset Loader
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: PyTorch dataset for VLA training.

**Acceptance Criteria**:
- [ ] Loads from HDF5/zarr
- [ ] Supports train/val split
- [ ] Efficient batching
- [ ] Handles variable sequence lengths

**Test Case**:
```python
dataset = VLADataset("demos/")
loader = DataLoader(dataset, batch_size=8)
batch = next(iter(loader))
assert "image" in batch and "instruction" in batch
```

---

### Task 8.5: Implement LoRA Fine-tuning
**Priority**: P1
**Estimated Effort**: 3 hours

**Description**: Fine-tune VLA with LoRA.

**Acceptance Criteria**:
- [ ] Adds LoRA adapters to model
- [ ] Configurable rank (8, 16, 32)
- [ ] Freezes base model
- [ ] Saves adapter weights only

**Test Case**:
```python
trainer = LoRATrainer(model, rank=16)
trainer.train(dataset, epochs=10)
trainer.save_adapters("lora_weights/")
```

---

### Task 8.6: Implement Full Fine-tuning
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Full model fine-tuning option.

**Acceptance Criteria**:
- [ ] Updates all parameters
- [ ] Gradient checkpointing for memory
- [ ] Learning rate scheduling
- [ ] Mixed precision training

**Test Case**:
```python
trainer = FullFinetuner(model)
trainer.train(dataset, epochs=5, lr=1e-5)
trainer.save("fine_tuned_model/")
```

---

### Task 8.7: Implement Training Monitor
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Monitor training progress.

**Acceptance Criteria**:
- [ ] Logs loss curves
- [ ] Tracks action accuracy
- [ ] Validates periodically
- [ ] TensorBoard integration

**Test Case**:
```bash
tensorboard --logdir runs/
# Shows training metrics
```

---

### Task 8.8: Implement Model Checkpointing
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Save and load training checkpoints.

**Acceptance Criteria**:
- [ ] Saves model, optimizer, scheduler
- [ ] Resumes training from checkpoint
- [ ] Keeps best N checkpoints
- [ ] Saves on validation improvement

**Test Case**:
```python
trainer.save_checkpoint("checkpoint_epoch_5.pt")
trainer.load_checkpoint("checkpoint_epoch_5.pt")
# Training resumes correctly
```

---

### Task 8.9: Implement Evaluation During Training
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Evaluate model during training.

**Acceptance Criteria**:
- [ ] Runs on validation set
- [ ] Computes task success (simulation)
- [ ] Reports metrics periodically
- [ ] Early stopping option

**Test Case**:
```python
evaluator = TrainingEvaluator(val_dataset, simulator)
metrics = evaluator.evaluate(model)
assert "success_rate" in metrics
```

---

### Task 8.10: Write Fine-tuning Tests
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Create tests for fine-tuning pipeline.

**Acceptance Criteria**:
- [ ] Tests for data loading
- [ ] Tests for training step
- [ ] Tests for checkpointing
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_finetuning.py -v
# All tests pass
```

---

## Phase 9: Evaluation

### Task 9.1: Define Evaluation Metrics
**Priority**: P0
**Estimated Effort**: 1 hour

**Description**: Define VLA evaluation metrics.

**Acceptance Criteria**:
- [ ] Task success rate
- [ ] Partial completion score
- [ ] Execution time
- [ ] Safety violations
- [ ] Generalization metrics

**Test Case**:
```python
metrics = EvaluationMetrics()
score = metrics.compute(predictions, ground_truth)
assert "success_rate" in score
assert "safety_violations" in score
```

---

### Task 9.2: Create Pick-and-Place Benchmark
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Benchmark for pick-and-place tasks.

**Acceptance Criteria**:
- [ ] Multiple object configurations
- [ ] Varied language instructions
- [ ] 50+ test cases
- [ ] Ground truth annotations

**Test Case**:
```python
benchmark = PickPlaceBenchmark()
results = benchmark.evaluate(vla_pipeline, simulator)
assert results["success_rate"] > 0.5
```

---

### Task 9.3: Create Object Search Benchmark
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Benchmark for finding objects.

**Acceptance Criteria**:
- [ ] Objects at various locations
- [ ] Referring expression queries
- [ ] Occlusion scenarios
- [ ] 30+ test cases

**Test Case**:
```python
benchmark = ObjectSearchBenchmark()
results = benchmark.evaluate(grounding_pipeline)
assert results["localization_accuracy"] > 0.8
```

---

### Task 9.4: Create Multi-Step Task Benchmark
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Benchmark for multi-step instructions.

**Acceptance Criteria**:
- [ ] 2-5 step instructions
- [ ] Sequential dependencies
- [ ] Partial credit scoring
- [ ] 20+ test cases

**Test Case**:
```python
benchmark = MultiStepBenchmark()
results = benchmark.evaluate(vla_pipeline, simulator)
assert results["completion_rate"] > 0.3
```

---

### Task 9.5: Implement Generalization Tests
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Test generalization to new scenarios.

**Acceptance Criteria**:
- [ ] New objects (not in training)
- [ ] New instructions (paraphrased)
- [ ] New environments
- [ ] Reports generalization gap

**Test Case**:
```python
gen_test = GeneralizationTester()
results = gen_test.evaluate(model, novel_scenarios)
assert results["novel_object_success"] > 0.3
```

---

### Task 9.6: Implement Failure Analysis
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Analyze failure cases.

**Acceptance Criteria**:
- [ ] Categorizes failure modes
- [ ] Extracts common patterns
- [ ] Generates failure report
- [ ] Suggests improvements

**Test Case**:
```python
analyzer = FailureAnalyzer()
report = analyzer.analyze(evaluation_results)
assert "grounding_failures" in report
assert "action_failures" in report
```

---

### Task 9.7: Create Evaluation Dashboard
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Visual dashboard for evaluation results.

**Acceptance Criteria**:
- [ ] Success rate plots
- [ ] Confusion matrices
- [ ] Per-task breakdown
- [ ] Exportable report

**Test Case**:
```python
dashboard = EvaluationDashboard()
dashboard.generate_report(results, output_path="eval_report/")
# HTML report generated
```

---

### Task 9.8: Write Evaluation Tests
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Create tests for evaluation suite.

**Acceptance Criteria**:
- [ ] Tests for metrics computation
- [ ] Tests for benchmarks
- [ ] Tests for analysis tools
- [ ] All tests pass

**Test Case**:
```bash
pytest tests/test_evaluation.py -v
# All tests pass
```

---

## Phase 10: End-to-End Demo

### Task 10.1: Create Manipulation Scene
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Gazebo scene for VLA demo.

**Acceptance Criteria**:
- [ ] Table with various objects
- [ ] Colored blocks (red, blue, green)
- [ ] Cups and containers
- [ ] Appropriate lighting

**Test Case**:
```bash
ros2 launch humanoid_vla_sim manipulation_scene.launch.py
# Scene loads with objects
```

---

### Task 10.2: Create Command Interface
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: User interface for text commands.

**Acceptance Criteria**:
- [ ] Terminal-based input
- [ ] Optional web interface
- [ ] Command history
- [ ] Help display

**Test Case**:
```bash
ros2 run humanoid_vla_ros command_interface
# Type: pick up the red block
# Robot responds
```

---

### Task 10.3: Implement Visual Feedback Display
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Display camera feed with annotations.

**Acceptance Criteria**:
- [ ] Shows camera image
- [ ] Overlays detected objects
- [ ] Shows current instruction
- [ ] Displays action confidence

**Test Case**:
```bash
ros2 run humanoid_vla_ros visual_feedback
# Window shows annotated camera feed
```

---

### Task 10.4: Create Demo Scenarios
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Define scripted demo scenarios.

**Acceptance Criteria**:
- [ ] "Pick up the red block" scenario
- [ ] "Put the cup on the tray" scenario
- [ ] "Find the green ball" scenario
- [ ] Documented expected behavior

**Test Case**:
```python
scenario = load_scenario("pick_red_block")
result = demo_runner.run(scenario)
assert result.success
```

---

### Task 10.5: Implement Demo Runner
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Automated demo execution.

**Acceptance Criteria**:
- [ ] Loads scenario from YAML
- [ ] Executes commands in sequence
- [ ] Records results
- [ ] Generates video

**Test Case**:
```bash
ros2 run humanoid_vla demo_runner --scenario pick_place --record
# Runs demo and records video
```

---

### Task 10.6: Record Demo Video
**Priority**: P1
**Estimated Effort**: 1 hour

**Description**: Record polished demo video.

**Acceptance Criteria**:
- [ ] Shows multiple scenarios
- [ ] Clear text overlays
- [ ] Good camera angles
- [ ] 2-3 minute length

**Test Case**:
- [ ] Video file exists
- [ ] All scenarios shown
- [ ] Quality acceptable

---

### Task 10.7: Write Demo Documentation
**Priority**: P1
**Estimated Effort**: 2 hours

**Description**: Document demo setup and execution.

**Acceptance Criteria**:
- [ ] Prerequisites listed
- [ ] Step-by-step instructions
- [ ] Troubleshooting guide
- [ ] Screenshots included

**Test Case**:
- [ ] README exists
- [ ] Instructions work when followed
- [ ] Troubleshooting covers common issues

---

## Phase 11: Documentation

### Task 11.1: Write Chapter Content
**Priority**: P1
**Estimated Effort**: 10 hours

**Description**: Write all 10 chapters for book.

**Acceptance Criteria**:
- [ ] All chapters written
- [ ] Code examples included
- [ ] Exercises defined
- [ ] Follows book format

---

### Task 11.2: Create Code Examples
**Priority**: P1
**Estimated Effort**: 4 hours

**Description**: Create standalone code examples.

**Acceptance Criteria**:
- [ ] Examples for each chapter
- [ ] Well-commented code
- [ ] Runnable without modification
- [ ] Tests pass

---

### Task 11.3: Write API Documentation
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Document public APIs.

**Acceptance Criteria**:
- [ ] Docstrings for all public functions
- [ ] Type hints included
- [ ] Examples in docstrings
- [ ] Generated HTML docs

---

### Task 11.4: Create Troubleshooting Guide
**Priority**: P2
**Estimated Effort**: 2 hours

**Description**: Guide for common issues.

**Acceptance Criteria**:
- [ ] GPU memory issues
- [ ] Model loading problems
- [ ] ROS 2 connectivity
- [ ] Performance optimization

---

### Task 11.5: Write PHR for Implementation
**Priority**: P1
**Estimated Effort**: 30 min

**Description**: Create PHR for module implementation.

**Acceptance Criteria**:
- [ ] PHR created
- [ ] All fields populated
- [ ] Files listed
- [ ] Outcome documented

---

## Task Summary

| Phase | Tasks | P0 | P1 | P2 |
|-------|-------|----|----|----|
| 1. Environment Setup | 8 | 8 | 0 | 0 |
| 2. VLM Foundations | 10 | 6 | 4 | 0 |
| 3. Action Tokenization | 9 | 6 | 3 | 0 |
| 4. Language Grounding | 10 | 4 | 4 | 2 |
| 5. VLA Pipeline | 12 | 7 | 5 | 0 |
| 6. ROS 2 Integration | 10 | 8 | 2 | 0 |
| 7. Safety Constraints | 9 | 6 | 3 | 0 |
| 8. Fine-tuning | 10 | 0 | 8 | 2 |
| 9. Evaluation | 8 | 1 | 5 | 2 |
| 10. End-to-End Demo | 7 | 0 | 6 | 1 |
| 11. Documentation | 5 | 0 | 3 | 2 |
| **Total** | **98** | **46** | **43** | **9** |

---

## Execution Order

**Phase 1-5 (Core VLA)**: Weeks 1-2
- Environment setup
- VLM foundations
- Action tokenization
- Language grounding
- VLA pipeline

**Phase 6-7 (Integration)**: Week 3
- ROS 2 integration
- Safety constraints

**Phase 8-10 (Advanced)**: Week 4
- Fine-tuning
- Evaluation
- End-to-end demo

**Phase 11 (Documentation)**: Ongoing

---

**Governed by**: `specs/constitution.md` v1.0.0
