# Chapter 4: Language Grounding for Robotics

**Duration**: 5-6 hours
**Prerequisites**: Chapter 2 (VLM Foundations), Chapter 3 (Action Tokenization)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Understand language grounding and its role in VLA systems
- Integrate object detection models (YOLO, DETR)
- Implement referring expression comprehension
- Parse spatial relationships from natural language
- Build a complete grounding pipeline

---

## 4.1 What is Language Grounding?

Language grounding connects words to the physical world. When a robot hears "pick up the red block," it must:

1. **Understand** the command structure (action: pick up, target: red block)
2. **Locate** the red block in the visual scene
3. **Identify** which specific object if multiple matches exist

```
┌─────────────────────────────────────────────────────────────────┐
│                   Language Grounding Pipeline                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  "Pick up the red block on the left"                            │
│                  ↓                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Instruction Parser                          │   │
│  │  Action: pick_up                                         │   │
│  │  Target: "red block"                                     │   │
│  │  Modifier: "on the left"                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                  ↓                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Object Detection                            │   │
│  │  [block1: (x1,y1,w1,h1), block2: (x2,y2,w2,h2), ...]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                  ↓                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Attribute Matching                          │   │
│  │  Filter: color=red → [block1, block3]                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                  ↓                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Spatial Reasoning                           │   │
│  │  Filter: position=left → [block1]                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                  ↓                                               │
│  Target: block1 at (x1, y1, w1, h1)                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4.2 Object Detection Integration

### Using YOLO for Real-time Detection

```python
from ultralytics import YOLO
import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Detection:
    """Single object detection result."""
    class_name: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    center: tuple  # (cx, cy)
    area: float

    @property
    def x1(self):
        return self.bbox[0]

    @property
    def y1(self):
        return self.bbox[1]

    @property
    def x2(self):
        return self.bbox[2]

    @property
    def y2(self):
        return self.bbox[3]


class ObjectDetector:
    """YOLO-based object detection for robot manipulation."""

    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.5):
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold

        # Common manipulation objects
        self.manipulation_classes = [
            'bottle', 'cup', 'bowl', 'banana', 'apple', 'sandwich',
            'orange', 'broccoli', 'carrot', 'cell phone', 'book',
            'scissors', 'teddy bear', 'toothbrush', 'remote', 'keyboard',
            'mouse', 'laptop', 'vase', 'potted plant'
        ]

    def detect(self, image: Image.Image) -> List[Detection]:
        """
        Run object detection on image.

        Args:
            image: PIL Image

        Returns:
            List of Detection objects
        """
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image

        # Run inference
        results = self.model(image_np, verbose=False)

        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                # Get bounding box
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                bbox = (float(x1), float(y1), float(x2), float(y2))

                # Compute center and area
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                area = (x2 - x1) * (y2 - y1)

                detections.append(Detection(
                    class_name=class_name,
                    confidence=conf,
                    bbox=bbox,
                    center=(cx, cy),
                    area=area
                ))

        return detections

    def detect_and_visualize(self, image: Image.Image) -> tuple:
        """Detect objects and return annotated image."""
        image_np = np.array(image)
        results = self.model(image_np, verbose=False)

        # Get annotated image
        annotated = results[0].plot()

        detections = self.detect(image)

        return detections, Image.fromarray(annotated)


# Usage
detector = ObjectDetector("yolov8n.pt", confidence_threshold=0.5)

image = Image.open("tabletop_scene.jpg")
detections = detector.detect(image)

print(f"Found {len(detections)} objects:")
for det in detections:
    print(f"  {det.class_name}: {det.confidence:.2f} at {det.center}")
```

### Using DETR for Better Accuracy

```python
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch

class DETRDetector:
    """DETR-based object detection (higher accuracy, slower)."""

    def __init__(self, model_name: str = "facebook/detr-resnet-50"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.processor = DetrImageProcessor.from_pretrained(model_name)
        self.model = DetrForObjectDetection.from_pretrained(model_name).to(self.device)
        self.model.eval()

        self.confidence_threshold = 0.7

    @torch.no_grad()
    def detect(self, image: Image.Image) -> List[Detection]:
        """Run DETR detection."""
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        outputs = self.model(**inputs)

        # Post-process
        target_sizes = torch.tensor([image.size[::-1]]).to(self.device)
        results = self.processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=self.confidence_threshold
        )[0]

        detections = []
        for score, label, box in zip(
            results["scores"], results["labels"], results["boxes"]
        ):
            box = box.cpu().numpy()
            x1, y1, x2, y2 = box

            class_name = self.model.config.id2label[label.item()]

            detections.append(Detection(
                class_name=class_name,
                confidence=float(score),
                bbox=(x1, y1, x2, y2),
                center=((x1 + x2) / 2, (y1 + y2) / 2),
                area=(x2 - x1) * (y2 - y1)
            ))

        return detections


# Usage
detr_detector = DETRDetector()
detections = detr_detector.detect(image)
```

---

## 4.3 Open-Vocabulary Detection

Standard detectors only find predefined classes. Open-vocabulary detection finds objects described in natural language:

```python
class OpenVocabDetector:
    """Detect objects from text descriptions using CLIP."""

    def __init__(self, clip_encoder, base_detector):
        self.clip = clip_encoder
        self.detector = base_detector

    def detect_by_description(
        self,
        image: Image.Image,
        description: str,
        top_k: int = 3
    ) -> List[Detection]:
        """
        Find objects matching text description.

        Args:
            image: Input image
            description: Text description (e.g., "red block")
            top_k: Number of best matches to return

        Returns:
            Matching detections sorted by relevance
        """
        # First run base detection
        detections = self.detector.detect(image)

        if not detections:
            return []

        # Crop each detection and compute CLIP similarity
        image_np = np.array(image)
        scores = []

        for det in detections:
            # Crop detection region
            x1, y1, x2, y2 = map(int, det.bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image_np.shape[1], x2), min(image_np.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                scores.append(-1)
                continue

            crop = image_np[y1:y2, x1:x2]
            crop_pil = Image.fromarray(crop)

            # Compute CLIP similarity
            similarity = self.clip.compute_similarity(crop_pil, [description])
            scores.append(float(similarity[0]))

        # Sort by score
        scored_detections = list(zip(detections, scores))
        scored_detections.sort(key=lambda x: x[1], reverse=True)

        # Return top-k
        results = [det for det, score in scored_detections[:top_k] if score > 0]

        return results

    def detect_multiple(
        self,
        image: Image.Image,
        descriptions: List[str]
    ) -> dict:
        """
        Find objects for multiple descriptions.

        Returns:
            Dict mapping description to best matching detection
        """
        results = {}

        for desc in descriptions:
            matches = self.detect_by_description(image, desc, top_k=1)
            results[desc] = matches[0] if matches else None

        return results


# Usage
open_vocab = OpenVocabDetector(clip_encoder, detector)

# Find specific objects
matches = open_vocab.detect_by_description(image, "red block", top_k=3)
print(f"Found {len(matches)} matches for 'red block'")

# Find multiple objects
objects = ["red block", "blue cup", "yellow ball"]
results = open_vocab.detect_multiple(image, objects)
for desc, det in results.items():
    if det:
        print(f"'{desc}': found at {det.center}")
    else:
        print(f"'{desc}': not found")
```

---

## 4.4 Referring Expression Comprehension

Handle complex references like "the cup on the left side of the table":

```python
import re
from typing import Tuple

class ReferringExpressionGrounder:
    """Ground referring expressions to specific objects."""

    def __init__(self, detector, clip_encoder):
        self.detector = detector
        self.clip = clip_encoder

        # Spatial relationship parsers
        self.spatial_patterns = {
            'left': r'\b(left|leftmost|left-hand|left side)\b',
            'right': r'\b(right|rightmost|right-hand|right side)\b',
            'top': r'\b(top|upper|above|highest)\b',
            'bottom': r'\b(bottom|lower|below|lowest)\b',
            'center': r'\b(center|middle|central)\b',
            'front': r'\b(front|foreground|nearest)\b',
            'back': r'\b(back|background|farthest)\b',
            'big': r'\b(big|large|biggest|largest)\b',
            'small': r'\b(small|little|smallest|tiniest)\b',
        }

    def parse_expression(self, expression: str) -> dict:
        """
        Parse referring expression into components.

        Args:
            expression: "the red block on the left"

        Returns:
            Dict with object_type, attributes, spatial_relations
        """
        expression = expression.lower().strip()

        # Extract spatial relations
        spatial_relations = []
        for rel, pattern in self.spatial_patterns.items():
            if re.search(pattern, expression):
                spatial_relations.append(rel)

        # Extract color (common manipulation scenario)
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple',
                  'pink', 'brown', 'black', 'white', 'gray']
        found_colors = [c for c in colors if c in expression]

        # Extract object type (remove articles and modifiers)
        # Simple heuristic: last noun-like word
        words = expression.split()
        object_type = words[-1] if words else ""

        # Remove common suffixes
        for suffix in ['s', 'es']:
            if object_type.endswith(suffix) and len(object_type) > 3:
                object_type = object_type[:-len(suffix)]

        return {
            'object_type': object_type,
            'colors': found_colors,
            'spatial': spatial_relations,
            'raw': expression
        }

    def filter_by_spatial(
        self,
        detections: List[Detection],
        spatial_relations: List[str],
        image_size: Tuple[int, int]
    ) -> List[Detection]:
        """
        Filter detections by spatial relations.

        Args:
            detections: List of detections
            spatial_relations: ['left', 'big', etc.]
            image_size: (width, height)

        Returns:
            Filtered detections
        """
        if not detections or not spatial_relations:
            return detections

        filtered = detections.copy()
        width, height = image_size

        for relation in spatial_relations:
            if relation == 'left':
                # Keep objects in left half
                filtered = [d for d in filtered if d.center[0] < width / 2]
            elif relation == 'right':
                filtered = [d for d in filtered if d.center[0] > width / 2]
            elif relation == 'top':
                filtered = [d for d in filtered if d.center[1] < height / 2]
            elif relation == 'bottom':
                filtered = [d for d in filtered if d.center[1] > height / 2]
            elif relation == 'big':
                if len(filtered) > 1:
                    max_area = max(d.area for d in filtered)
                    filtered = [d for d in filtered if d.area > max_area * 0.7]
            elif relation == 'small':
                if len(filtered) > 1:
                    min_area = min(d.area for d in filtered)
                    filtered = [d for d in filtered if d.area < min_area * 1.3]
            elif relation == 'leftmost':
                if filtered:
                    leftmost = min(filtered, key=lambda d: d.center[0])
                    filtered = [leftmost]
            elif relation == 'rightmost':
                if filtered:
                    rightmost = max(filtered, key=lambda d: d.center[0])
                    filtered = [rightmost]

        return filtered

    def ground(
        self,
        image: Image.Image,
        expression: str
    ) -> Optional[Detection]:
        """
        Ground referring expression to specific object.

        Args:
            image: Input image
            expression: Natural language reference

        Returns:
            Best matching Detection or None
        """
        # Parse expression
        parsed = self.parse_expression(expression)

        # Get all detections
        detections = self.detector.detect(image)

        if not detections:
            return None

        # Filter by object type using CLIP
        # Create search query from parsed components
        search_query = parsed['raw']
        if parsed['colors']:
            search_query = f"{parsed['colors'][0]} {parsed['object_type']}"

        # Score detections with CLIP
        image_np = np.array(image)
        scored = []

        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image_np.shape[1], x2), min(image_np.shape[0], y2)

            if x2 <= x1 or y2 <= y1:
                continue

            crop = image_np[y1:y2, x1:x2]
            crop_pil = Image.fromarray(crop)

            similarity = self.clip.compute_similarity(crop_pil, [search_query])
            scored.append((det, float(similarity[0])))

        # Filter by minimum similarity
        scored = [(d, s) for d, s in scored if s > 0.2]

        if not scored:
            return None

        # Apply spatial filtering
        filtered_dets = [d for d, s in scored]
        filtered_dets = self.filter_by_spatial(
            filtered_dets,
            parsed['spatial'],
            image.size
        )

        if not filtered_dets:
            # Fallback to highest scoring
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[0][0]

        # Return best match among spatially filtered
        filtered_with_scores = [(d, s) for d, s in scored if d in filtered_dets]
        if filtered_with_scores:
            filtered_with_scores.sort(key=lambda x: x[1], reverse=True)
            return filtered_with_scores[0][0]

        return filtered_dets[0]


# Usage
grounder = ReferringExpressionGrounder(detector, clip_encoder)

# Ground complex expressions
expressions = [
    "the red block",
    "the cup on the left",
    "the big blue box",
    "the smallest ball",
]

for expr in expressions:
    result = grounder.ground(image, expr)
    if result:
        print(f"'{expr}' → {result.class_name} at {result.center}")
    else:
        print(f"'{expr}' → not found")
```

---

## 4.5 Instruction Parser

Parse robot instructions into structured commands:

```python
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class ActionType(Enum):
    PICK = "pick"
    PLACE = "place"
    MOVE = "move"
    PUSH = "push"
    OPEN = "open"
    CLOSE = "close"
    POUR = "pour"
    UNKNOWN = "unknown"


@dataclass
class ParsedAction:
    """Single parsed action from instruction."""
    action_type: ActionType
    target: Optional[str] = None
    destination: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)


@dataclass
class ParsedInstruction:
    """Fully parsed instruction."""
    raw_text: str
    actions: List[ParsedAction]
    is_multi_step: bool


class InstructionParser:
    """Parse natural language robot instructions."""

    def __init__(self):
        # Action verb patterns
        self.action_patterns = {
            ActionType.PICK: [
                r'\b(pick up|pick|grab|grasp|get|take|lift)\b',
            ],
            ActionType.PLACE: [
                r'\b(place|put|set|drop|release)\b',
            ],
            ActionType.MOVE: [
                r'\b(move|bring|carry|transport)\b',
            ],
            ActionType.PUSH: [
                r'\b(push|slide|shove)\b',
            ],
            ActionType.OPEN: [
                r'\b(open)\b',
            ],
            ActionType.CLOSE: [
                r'\b(close|shut)\b',
            ],
            ActionType.POUR: [
                r'\b(pour|fill|empty)\b',
            ],
        }

        # Destination prepositions
        self.destination_preps = [
            'on', 'onto', 'into', 'in', 'to', 'towards',
            'inside', 'above', 'over', 'next to', 'beside'
        ]

    def _extract_action_type(self, text: str) -> ActionType:
        """Extract action type from text."""
        text_lower = text.lower()

        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return action_type

        return ActionType.UNKNOWN

    def _split_compound_instruction(self, text: str) -> List[str]:
        """Split compound instructions (e.g., 'pick X and place on Y')."""
        # Split on common conjunctions
        parts = re.split(r'\band\b|\bthen\b|,\s*then|;\s*', text.lower())
        return [p.strip() for p in parts if p.strip()]

    def _extract_target_and_destination(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract target object and destination from text."""
        text_lower = text.lower()

        # Find destination phrase
        destination = None
        target_text = text_lower

        for prep in self.destination_preps:
            pattern = rf'\b{prep}\s+(the\s+)?(.+?)(?:\s*$|\s+and\b)'
            match = re.search(pattern, text_lower)
            if match:
                destination = match.group(2).strip()
                # Remove destination from target search
                target_text = text_lower[:match.start()]
                break

        # Find target (usually after the verb)
        target = None
        # Look for "the X" pattern
        target_match = re.search(r'(?:pick up|grab|get|take|put|place|move)\s+(the\s+)?(.+?)(?:\s+(?:on|in|to)|$)', target_text)
        if target_match:
            target = target_match.group(2).strip()

        return target, destination

    def parse(self, instruction: str) -> ParsedInstruction:
        """
        Parse natural language instruction.

        Args:
            instruction: "pick up the red block and put it on the tray"

        Returns:
            ParsedInstruction with actions list
        """
        parts = self._split_compound_instruction(instruction)
        is_multi_step = len(parts) > 1

        actions = []
        last_target = None

        for part in parts:
            action_type = self._extract_action_type(part)
            target, destination = self._extract_target_and_destination(part)

            # Handle pronouns
            if target in ['it', 'them', 'that', 'this'] and last_target:
                target = last_target
            elif target:
                last_target = target

            actions.append(ParsedAction(
                action_type=action_type,
                target=target,
                destination=destination
            ))

        return ParsedInstruction(
            raw_text=instruction,
            actions=actions,
            is_multi_step=is_multi_step
        )


# Usage
parser = InstructionParser()

instructions = [
    "pick up the red block",
    "put the cup on the tray",
    "pick up the red block and place it on the blue box",
    "move the ball to the corner",
    "grab the apple and put it in the bowl",
]

for instr in instructions:
    parsed = parser.parse(instr)
    print(f"\nInstruction: '{instr}'")
    print(f"Multi-step: {parsed.is_multi_step}")
    for i, action in enumerate(parsed.actions):
        print(f"  Action {i+1}: {action.action_type.value}")
        print(f"    Target: {action.target}")
        print(f"    Destination: {action.destination}")
```

---

## 4.6 Complete Grounding Pipeline

Combine all components into a unified pipeline:

```python
@dataclass
class GroundingResult:
    """Complete grounding result."""
    instruction: str
    parsed: ParsedInstruction
    target_detection: Optional[Detection]
    destination_detection: Optional[Detection]
    confidence: float
    needs_clarification: bool
    clarification_reason: Optional[str]


class GroundingPipeline:
    """Complete language grounding pipeline for VLA."""

    def __init__(
        self,
        detector: ObjectDetector,
        clip_encoder,
        confidence_threshold: float = 0.5
    ):
        self.detector = detector
        self.clip = clip_encoder
        self.confidence_threshold = confidence_threshold

        self.parser = InstructionParser()
        self.grounder = ReferringExpressionGrounder(detector, clip_encoder)

    def ground(self, image: Image.Image, instruction: str) -> GroundingResult:
        """
        Ground instruction to objects in image.

        Args:
            image: Camera image
            instruction: Natural language instruction

        Returns:
            GroundingResult with target and destination
        """
        # Parse instruction
        parsed = self.parser.parse(instruction)

        if not parsed.actions:
            return GroundingResult(
                instruction=instruction,
                parsed=parsed,
                target_detection=None,
                destination_detection=None,
                confidence=0.0,
                needs_clarification=True,
                clarification_reason="Could not parse instruction"
            )

        # Ground first action's target
        first_action = parsed.actions[0]
        target_det = None
        dest_det = None
        confidence = 0.0

        if first_action.target:
            target_det = self.grounder.ground(image, first_action.target)
            if target_det:
                confidence = target_det.confidence

        if first_action.destination:
            dest_det = self.grounder.ground(image, first_action.destination)
            if dest_det and target_det:
                # Average confidence
                confidence = (target_det.confidence + dest_det.confidence) / 2

        # Check for ambiguity
        needs_clarification = False
        clarification_reason = None

        if first_action.target and not target_det:
            needs_clarification = True
            clarification_reason = f"Could not find '{first_action.target}' in the scene"
        elif target_det and target_det.confidence < self.confidence_threshold:
            needs_clarification = True
            clarification_reason = f"Low confidence ({target_det.confidence:.2f}) for '{first_action.target}'"

        return GroundingResult(
            instruction=instruction,
            parsed=parsed,
            target_detection=target_det,
            destination_detection=dest_det,
            confidence=confidence,
            needs_clarification=needs_clarification,
            clarification_reason=clarification_reason
        )

    def get_target_position(self, grounding_result: GroundingResult) -> Optional[np.ndarray]:
        """
        Get 3D target position from grounding result.

        Note: Requires depth information for accurate 3D position.
        This returns 2D center for demonstration.
        """
        if grounding_result.target_detection:
            det = grounding_result.target_detection
            return np.array([det.center[0], det.center[1], 0.0])
        return None

    def visualize(self, image: Image.Image, result: GroundingResult) -> Image.Image:
        """Visualize grounding result on image."""
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(image)

        # Draw target
        if result.target_detection:
            det = result.target_detection
            rect = Rectangle(
                (det.x1, det.y1),
                det.x2 - det.x1,
                det.y2 - det.y1,
                fill=False,
                edgecolor='green',
                linewidth=2
            )
            ax.add_patch(rect)
            ax.text(det.x1, det.y1 - 10, f"Target: {result.parsed.actions[0].target}",
                   color='green', fontsize=10, weight='bold')

        # Draw destination
        if result.destination_detection:
            det = result.destination_detection
            rect = Rectangle(
                (det.x1, det.y1),
                det.x2 - det.x1,
                det.y2 - det.y1,
                fill=False,
                edgecolor='blue',
                linewidth=2,
                linestyle='--'
            )
            ax.add_patch(rect)
            ax.text(det.x1, det.y1 - 10, f"Dest: {result.parsed.actions[0].destination}",
                   color='blue', fontsize=10, weight='bold')

        ax.set_title(f"Instruction: {result.instruction}\nConfidence: {result.confidence:.2f}")
        ax.axis('off')

        # Convert to PIL Image
        fig.canvas.draw()
        vis_image = Image.frombytes(
            'RGB',
            fig.canvas.get_width_height(),
            fig.canvas.tostring_rgb()
        )
        plt.close()

        return vis_image


# Usage
pipeline = GroundingPipeline(detector, clip_encoder)

image = Image.open("manipulation_scene.jpg")
instruction = "pick up the red block and put it on the blue tray"

result = pipeline.ground(image, instruction)

print(f"Instruction: {result.instruction}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Needs clarification: {result.needs_clarification}")
if result.clarification_reason:
    print(f"Reason: {result.clarification_reason}")
if result.target_detection:
    print(f"Target: {result.target_detection.class_name} at {result.target_detection.center}")
if result.destination_detection:
    print(f"Destination: {result.destination_detection.class_name} at {result.destination_detection.center}")
```

---

## 4.7 Handling Ambiguity

When grounding is uncertain, request clarification:

```python
class ClarificationGenerator:
    """Generate clarification questions for ambiguous situations."""

    def __init__(self, detector, clip_encoder):
        self.detector = detector
        self.clip = clip_encoder

    def check_ambiguity(
        self,
        image: Image.Image,
        expression: str,
        threshold: float = 0.8
    ) -> Tuple[bool, List[Detection]]:
        """
        Check if expression is ambiguous in the scene.

        Returns:
            (is_ambiguous, candidate_detections)
        """
        # Get all detections
        detections = self.detector.detect(image)

        if not detections:
            return True, []

        # Score all detections
        image_np = np.array(image)
        scored = []

        for det in detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            crop = image_np[max(0,y1):y2, max(0,x1):x2]
            if crop.size == 0:
                continue

            crop_pil = Image.fromarray(crop)
            similarity = self.clip.compute_similarity(crop_pil, [expression])
            scored.append((det, float(similarity[0])))

        # Filter by threshold
        candidates = [(d, s) for d, s in scored if s > threshold * 0.5]

        if not candidates:
            return True, []

        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Check if multiple candidates are close in score
        if len(candidates) >= 2:
            top_score = candidates[0][1]
            second_score = candidates[1][1]

            # If second best is within 90% of best, it's ambiguous
            if second_score > top_score * 0.9:
                return True, [d for d, s in candidates[:3]]

        return False, [candidates[0][0]]

    def generate_question(
        self,
        expression: str,
        candidates: List[Detection],
        image_size: Tuple[int, int]
    ) -> str:
        """
        Generate clarification question.

        Args:
            expression: Original expression
            candidates: Ambiguous candidate detections
            image_size: (width, height)

        Returns:
            Natural language question
        """
        if not candidates:
            return f"I cannot find '{expression}' in the scene. Could you point to it or describe it differently?"

        if len(candidates) == 1:
            return f"Did you mean the {expression} in the center of the scene?"

        # Describe candidates by position
        width, height = image_size
        descriptions = []

        for det in candidates:
            cx, cy = det.center

            # Determine position
            h_pos = "left" if cx < width / 3 else ("right" if cx > 2 * width / 3 else "center")
            v_pos = "top" if cy < height / 3 else ("bottom" if cy > 2 * height / 3 else "middle")

            descriptions.append(f"the one on the {h_pos}")

        # Generate question
        options = " or ".join(descriptions)
        return f"I see multiple objects that could be '{expression}'. Do you mean {options}?"


# Usage
clarifier = ClarificationGenerator(detector, clip_encoder)

is_ambiguous, candidates = clarifier.check_ambiguity(image, "the block")
if is_ambiguous:
    question = clarifier.generate_question("the block", candidates, image.size)
    print(f"Clarification needed: {question}")
```

---

## 4.8 Summary

In this chapter, you learned:

1. **Language Grounding**: Connecting words to physical objects
2. **Object Detection**: Using YOLO and DETR for finding objects
3. **Open-Vocabulary**: CLIP-based detection for arbitrary descriptions
4. **Referring Expressions**: Handling "the red block on the left"
5. **Instruction Parsing**: Extracting actions, targets, and destinations
6. **Complete Pipeline**: End-to-end grounding system
7. **Ambiguity Handling**: Generating clarification questions

---

## 4.9 Exercises

### Exercise 4.1: Object Detection
Set up YOLO detection and test on 5 manipulation scenes. Report precision/recall.

### Exercise 4.2: Referring Expressions
Implement and test referring expression grounding with spatial relations.

### Exercise 4.3: Instruction Parser
Extend the parser to handle more complex multi-step instructions.

### Exercise 4.4: Clarification System
Build a clarification dialogue system for ambiguous situations.

---

## Quick Reference

### YOLO Detection
```python
from ultralytics import YOLO
model = YOLO("yolov8n.pt")
results = model(image)
```

### CLIP Similarity
```python
similarity = clip.compute_similarity(crop, [description])
```

### Instruction Parsing
```python
parser = InstructionParser()
parsed = parser.parse("pick up the red block")
```

---

**Next Chapter**: [Chapter 5 - Building the VLA Inference Pipeline](ch05-vla-pipeline.md)
