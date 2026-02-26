# Chapter 10: End-to-End VLA Demo

**Duration**: 4-5 hours
**Prerequisites**: Chapters 1-9 (All previous chapters)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Integrate all VLA components into a complete system
- Create demonstration scenarios for various tasks
- Build a user-friendly command interface
- Record and document VLA demos
- Identify future improvement directions

---

## 10.1 System Integration

The end-to-end VLA demo brings together all components:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Complete VLA Demo System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────┐        ┌───────────────────────────────┐ │
│  │    User Input     │        │     Simulation Environment     │ │
│  │  ┌─────────────┐  │        │  ┌─────────────────────────┐  │ │
│  │  │ Text Command│  │        │  │   Gazebo + Humanoid     │  │ │
│  │  │ Interface   │  │        │  │   + Objects             │  │ │
│  │  └──────┬──────┘  │        │  └───────────┬─────────────┘  │ │
│  └─────────┼─────────┘        └──────────────┼────────────────┘ │
│            │                                  │                  │
│            ▼                                  ▼                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      VLA Node                                ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  ││
│  │  │   Camera     │  │   Language   │  │     Safety       │  ││
│  │  │  Processor   │  │   Grounder   │  │     Filter       │  ││
│  │  └──────┬───────┘  └──────┬───────┘  └──────────┬───────┘  ││
│  │         │                 │                      │          ││
│  │         └─────────────────┼──────────────────────┘          ││
│  │                           ▼                                 ││
│  │              ┌─────────────────────────┐                   ││
│  │              │      VLA Pipeline       │                   ││
│  │              │  (OpenVLA + Fine-tuned) │                   ││
│  │              └────────────┬────────────┘                   ││
│  └───────────────────────────┼─────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Visual Feedback                            ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │ Camera Feed │  │  Detection  │  │  Status Display     │ ││
│  │  │ with        │  │  Overlays   │  │  + Confidence       │ ││
│  │  │ Annotations │  │             │  │                     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10.2 Demo Scenario Definitions

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import yaml


@dataclass
class DemoScenario:
    """Definition of a demo scenario."""
    name: str
    description: str
    instruction: str
    scene_config: Dict
    expected_behavior: str
    success_criteria: Dict
    max_duration_sec: float = 60.0


class DemoScenarioManager:
    """Manage and load demo scenarios."""

    def __init__(self, scenarios_dir: str = "scenarios/"):
        self.scenarios_dir = scenarios_dir
        self.scenarios = self._load_default_scenarios()

    def _load_default_scenarios(self) -> List[DemoScenario]:
        """Load default demo scenarios."""
        scenarios = []

        # Scenario 1: Pick red block
        scenarios.append(DemoScenario(
            name="pick_red_block",
            description="Pick up a red block from the table",
            instruction="pick up the red block",
            scene_config={
                'objects': [
                    {'type': 'block', 'color': 'red', 'position': [0.3, 0.0, 0.05]},
                    {'type': 'block', 'color': 'blue', 'position': [-0.2, 0.1, 0.05]},
                    {'type': 'cup', 'color': 'white', 'position': [0.0, -0.2, 0.0]},
                ],
                'robot_start': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            },
            expected_behavior="Robot moves arm to red block location, grasps block, lifts it",
            success_criteria={'object_grasped': 'red_block', 'lifted': True}
        ))

        # Scenario 2: Place cup on tray
        scenarios.append(DemoScenario(
            name="place_cup_on_tray",
            description="Place a cup onto a tray",
            instruction="put the cup on the tray",
            scene_config={
                'objects': [
                    {'type': 'cup', 'color': 'blue', 'position': [0.2, 0.1, 0.0]},
                    {'type': 'tray', 'color': 'gray', 'position': [0.0, -0.3, 0.0]},
                ],
                'robot_start': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5]  # Start holding cup
            },
            expected_behavior="Robot moves cup to tray, places it down, releases gripper",
            success_criteria={'object_on': 'tray', 'released': True}
        ))

        # Scenario 3: Find and pick
        scenarios.append(DemoScenario(
            name="find_green_ball",
            description="Find and pick up a green ball",
            instruction="find the green ball and pick it up",
            scene_config={
                'objects': [
                    {'type': 'ball', 'color': 'green', 'position': [-0.3, 0.2, 0.03]},
                    {'type': 'ball', 'color': 'red', 'position': [0.3, 0.0, 0.03]},
                    {'type': 'box', 'color': 'brown', 'position': [0.0, 0.0, 0.0]},
                ],
            },
            expected_behavior="Robot searches scene, identifies green ball, picks it up",
            success_criteria={'object_found': 'green_ball', 'object_grasped': 'green_ball'}
        ))

        # Scenario 4: Multi-step
        scenarios.append(DemoScenario(
            name="sort_blocks",
            description="Sort blocks by color",
            instruction="pick up the red block and put it in the red box",
            scene_config={
                'objects': [
                    {'type': 'block', 'color': 'red', 'position': [0.2, 0.0, 0.05]},
                    {'type': 'block', 'color': 'blue', 'position': [-0.2, 0.0, 0.05]},
                    {'type': 'box', 'color': 'red', 'position': [0.3, -0.3, 0.0]},
                    {'type': 'box', 'color': 'blue', 'position': [-0.3, -0.3, 0.0]},
                ],
            },
            expected_behavior="Robot picks red block, moves to red box, places block",
            success_criteria={'object_in_box': ('red_block', 'red_box')},
            max_duration_sec=90.0
        ))

        return scenarios

    def get_scenario(self, name: str) -> Optional[DemoScenario]:
        """Get scenario by name."""
        for s in self.scenarios:
            if s.name == name:
                return s
        return None

    def list_scenarios(self) -> List[str]:
        """List all available scenarios."""
        return [s.name for s in self.scenarios]

    def save_scenario(self, scenario: DemoScenario, filename: str):
        """Save scenario to YAML file."""
        data = {
            'name': scenario.name,
            'description': scenario.description,
            'instruction': scenario.instruction,
            'scene_config': scenario.scene_config,
            'expected_behavior': scenario.expected_behavior,
            'success_criteria': scenario.success_criteria,
            'max_duration_sec': scenario.max_duration_sec
        }

        with open(f"{self.scenarios_dir}/{filename}", 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    def load_scenario(self, filename: str) -> DemoScenario:
        """Load scenario from YAML file."""
        with open(f"{self.scenarios_dir}/{filename}", 'r') as f:
            data = yaml.safe_load(f)

        return DemoScenario(**data)
```

---

## 10.3 Demo Runner

```python
import time
from enum import Enum


class DemoState(Enum):
    """Demo execution state."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class DemoRunner:
    """Run VLA demos with recording."""

    def __init__(
        self,
        vla_pipeline,
        simulator,
        safety_filter,
        scenario_manager: DemoScenarioManager
    ):
        self.vla_pipeline = vla_pipeline
        self.simulator = simulator
        self.safety_filter = safety_filter
        self.scenario_manager = scenario_manager

        self.state = DemoState.IDLE
        self.current_scenario: Optional[DemoScenario] = None
        self.recording = False
        self.recording_data = []

    def run_scenario(
        self,
        scenario_name: str,
        record: bool = True,
        visualize: bool = True,
        verbose: bool = True
    ) -> Dict:
        """
        Run a demo scenario.

        Args:
            scenario_name: Name of scenario to run
            record: Whether to record the demo
            visualize: Whether to show visualization
            verbose: Print progress

        Returns:
            Demo results
        """
        scenario = self.scenario_manager.get_scenario(scenario_name)
        if scenario is None:
            return {'success': False, 'error': f'Scenario {scenario_name} not found'}

        self.current_scenario = scenario
        self.state = DemoState.RUNNING
        self.recording = record
        self.recording_data = []

        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Demo: {scenario.name}")
            print(f"Instruction: {scenario.instruction}")
            print(f"{'='*60}\n")

        # Reset simulator with scene config
        obs = self.simulator.reset(scenario.scene_config)

        start_time = time.time()
        step = 0
        success = False
        actions_taken = []

        try:
            while self.state == DemoState.RUNNING:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > scenario.max_duration_sec:
                    if verbose:
                        print(f"\nTimeout after {elapsed:.1f}s")
                    break

                # Get image
                image = obs['image']

                # Run VLA inference
                output = self.vla_pipeline.predict(image, scenario.instruction)

                # Apply safety filter
                safe_action, is_safe, modifications = self.safety_filter.filter(
                    output.actions[0],
                    obs.get('joint_positions', np.zeros(14)),
                    output.confidence
                )

                # Record step
                if self.recording:
                    self.recording_data.append({
                        'step': step,
                        'timestamp': elapsed,
                        'image': image.copy(),
                        'action': safe_action.copy(),
                        'confidence': output.confidence,
                        'safety_modified': len(modifications) > 0
                    })

                # Execute action
                obs, reward, done, info = self.simulator.step(safe_action)
                actions_taken.append(safe_action)
                step += 1

                # Print progress
                if verbose and step % 10 == 0:
                    print(f"Step {step}: conf={output.confidence:.2f}, "
                          f"elapsed={elapsed:.1f}s")

                # Check completion
                if done:
                    success = info.get('success', False)
                    if verbose:
                        status = "SUCCESS" if success else "FAILED"
                        print(f"\nDemo {status} at step {step}")
                    break

        except KeyboardInterrupt:
            if verbose:
                print("\nDemo interrupted")
            self.state = DemoState.FAILED

        except Exception as e:
            if verbose:
                print(f"\nDemo error: {e}")
            self.state = DemoState.FAILED

        # Set final state
        if success:
            self.state = DemoState.COMPLETED
        else:
            self.state = DemoState.FAILED

        # Compile results
        results = {
            'scenario': scenario.name,
            'success': success,
            'steps': step,
            'duration_sec': time.time() - start_time,
            'actions': actions_taken,
        }

        if self.recording:
            results['recording'] = self.recording_data

        return results

    def run_all_scenarios(self, verbose: bool = True) -> Dict:
        """Run all demo scenarios."""
        all_results = {}

        for scenario_name in self.scenario_manager.list_scenarios():
            results = self.run_scenario(scenario_name, record=True, verbose=verbose)
            all_results[scenario_name] = results

        # Summary
        successes = sum(1 for r in all_results.values() if r['success'])
        total = len(all_results)

        if verbose:
            print(f"\n{'='*60}")
            print(f"Demo Summary: {successes}/{total} scenarios passed")
            print(f"{'='*60}")

        return all_results

    def save_recording(self, filepath: str):
        """Save recording to file."""
        import pickle

        data = {
            'scenario': self.current_scenario.name if self.current_scenario else None,
            'recording': self.recording_data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        print(f"Recording saved to {filepath}")
```

---

## 10.4 Visual Feedback Display

```python
import cv2
import numpy as np
from threading import Thread
from queue import Queue


class VisualFeedbackDisplay:
    """Display camera feed with VLA annotations."""

    def __init__(self, window_name: str = "VLA Demo"):
        self.window_name = window_name
        self.running = False
        self.display_queue = Queue(maxsize=2)

    def start(self):
        """Start display thread."""
        self.running = True
        self.display_thread = Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()

    def stop(self):
        """Stop display."""
        self.running = False
        cv2.destroyAllWindows()

    def update(
        self,
        image: np.ndarray,
        instruction: str,
        confidence: float,
        detections: List = None,
        status: str = "Running"
    ):
        """Update display with new frame."""
        if not self.running:
            return

        frame_data = {
            'image': image.copy(),
            'instruction': instruction,
            'confidence': confidence,
            'detections': detections or [],
            'status': status
        }

        # Non-blocking put
        if not self.display_queue.full():
            self.display_queue.put(frame_data)

    def _display_loop(self):
        """Main display loop."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        while self.running:
            try:
                frame_data = self.display_queue.get(timeout=0.1)
            except:
                continue

            # Create annotated frame
            annotated = self._annotate_frame(frame_data)

            # Display
            cv2.imshow(self.window_name, cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
                break

    def _annotate_frame(self, frame_data: Dict) -> np.ndarray:
        """Add annotations to frame."""
        image = frame_data['image'].copy()

        # Draw detection boxes
        for det in frame_data['detections']:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, det.class_name, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Draw status bar
        h, w = image.shape[:2]
        status_bar = np.zeros((80, w, 3), dtype=np.uint8)

        # Instruction
        cv2.putText(status_bar, f"Instruction: {frame_data['instruction']}",
                   (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Confidence bar
        conf = frame_data['confidence']
        conf_color = (0, 255, 0) if conf > 0.7 else (0, 165, 255) if conf > 0.5 else (0, 0, 255)
        cv2.rectangle(status_bar, (10, 40), (int(10 + 200 * conf), 55), conf_color, -1)
        cv2.putText(status_bar, f"Confidence: {conf:.2f}",
                   (220, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Status
        cv2.putText(status_bar, f"Status: {frame_data['status']}",
                   (400, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Combine
        annotated = np.vstack([image, status_bar])

        return annotated
```

---

## 10.5 Demo Video Recording

```python
import cv2
import os
from datetime import datetime


class DemoVideoRecorder:
    """Record demo videos."""

    def __init__(
        self,
        output_dir: str = "recordings/",
        fps: int = 10,
        resolution: tuple = (1280, 720)
    ):
        self.output_dir = output_dir
        self.fps = fps
        self.resolution = resolution
        os.makedirs(output_dir, exist_ok=True)

        self.writer = None
        self.is_recording = False

    def start_recording(self, filename: str = None):
        """Start video recording."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"demo_{timestamp}.mp4"

        filepath = os.path.join(self.output_dir, filename)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            filepath,
            fourcc,
            self.fps,
            self.resolution
        )

        self.is_recording = True
        self.filepath = filepath
        print(f"Recording started: {filepath}")

    def add_frame(self, frame: np.ndarray):
        """Add frame to recording."""
        if not self.is_recording or self.writer is None:
            return

        # Resize if needed
        if frame.shape[:2] != self.resolution[::-1]:
            frame = cv2.resize(frame, self.resolution)

        # Convert RGB to BGR for OpenCV
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        self.writer.write(frame)

    def stop_recording(self):
        """Stop recording and save file."""
        if self.writer is not None:
            self.writer.release()
            self.writer = None
            self.is_recording = False
            print(f"Recording saved: {self.filepath}")

    def create_demo_video(
        self,
        recording_data: List[Dict],
        scenario_name: str,
        instruction: str
    ) -> str:
        """Create video from recording data."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{scenario_name}_{timestamp}.mp4"

        self.start_recording(filename)

        for frame_data in recording_data:
            image = frame_data['image']

            # Add annotations
            annotated = self._add_annotations(
                image,
                instruction,
                frame_data.get('confidence', 0),
                frame_data.get('step', 0)
            )

            self.add_frame(annotated)

        self.stop_recording()
        return self.filepath

    def _add_annotations(
        self,
        image: np.ndarray,
        instruction: str,
        confidence: float,
        step: int
    ) -> np.ndarray:
        """Add text annotations to frame."""
        annotated = image.copy()

        # Add text overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(annotated, f"Step: {step}", (10, 30), font, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated, f"Instruction: {instruction}", (10, 60), font, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated, f"Confidence: {confidence:.2f}", (10, 90), font, 0.6, (255, 255, 255), 2)

        return annotated
```

---

## 10.6 Complete Demo Application

```python
class VLADemoApplication:
    """Complete VLA demo application."""

    def __init__(
        self,
        model_path: str,
        use_simulation: bool = True
    ):
        print("Initializing VLA Demo Application...")

        # Initialize components
        self._init_vla_pipeline(model_path)
        self._init_simulator(use_simulation)
        self._init_safety()
        self._init_scenarios()
        self._init_display()

        print("Initialization complete!")

    def _init_vla_pipeline(self, model_path: str):
        """Initialize VLA pipeline."""
        from vla_pipeline import VLAPipeline, VLAConfig

        config = VLAConfig(
            model_path=model_path,
            use_quantization=True,
            quantization_bits=4
        )
        self.vla_pipeline = VLAPipeline(config)

    def _init_simulator(self, use_simulation: bool):
        """Initialize simulator."""
        if use_simulation:
            # Use mock simulator for demo
            self.simulator = MockSimulator()
        else:
            # Connect to real robot
            pass

    def _init_safety(self):
        """Initialize safety filter."""
        from safety_filter import SafetyFilter, SafetyConfig

        config = SafetyConfig(
            joint_limits=HUMANOID_JOINT_LIMITS,
            max_joint_velocity=2.0,
            min_confidence=0.5
        )
        self.safety_filter = SafetyFilter(config)

    def _init_scenarios(self):
        """Initialize scenario manager."""
        self.scenario_manager = DemoScenarioManager()

    def _init_display(self):
        """Initialize display."""
        self.display = VisualFeedbackDisplay()
        self.recorder = DemoVideoRecorder()

    def run_interactive(self):
        """Run interactive demo mode."""
        print("\n" + "=" * 60)
        print("VLA Demo Application")
        print("=" * 60)
        print("\nCommands:")
        print("  list              - List available scenarios")
        print("  run <scenario>    - Run a scenario")
        print("  record <scenario> - Run and record scenario")
        print("  all               - Run all scenarios")
        print("  quit              - Exit")
        print("=" * 60 + "\n")

        self.display.start()

        while True:
            try:
                cmd = input("demo> ").strip()

                if not cmd:
                    continue

                parts = cmd.split()
                command = parts[0].lower()

                if command == 'quit':
                    break

                elif command == 'list':
                    print("\nAvailable scenarios:")
                    for name in self.scenario_manager.list_scenarios():
                        scenario = self.scenario_manager.get_scenario(name)
                        print(f"  {name}: {scenario.description}")

                elif command == 'run':
                    if len(parts) < 2:
                        print("Usage: run <scenario_name>")
                        continue
                    self._run_demo(parts[1], record=False)

                elif command == 'record':
                    if len(parts) < 2:
                        print("Usage: record <scenario_name>")
                        continue
                    self._run_demo(parts[1], record=True)

                elif command == 'all':
                    self._run_all_demos()

                else:
                    print(f"Unknown command: {command}")

            except (EOFError, KeyboardInterrupt):
                break

        self.display.stop()
        print("\nDemo application closed.")

    def _run_demo(self, scenario_name: str, record: bool = False):
        """Run a single demo."""
        runner = DemoRunner(
            self.vla_pipeline,
            self.simulator,
            self.safety_filter,
            self.scenario_manager
        )

        results = runner.run_scenario(scenario_name, record=record, verbose=True)

        if record and results.get('recording'):
            filepath = self.recorder.create_demo_video(
                results['recording'],
                scenario_name,
                self.scenario_manager.get_scenario(scenario_name).instruction
            )
            print(f"Video saved: {filepath}")

        return results

    def _run_all_demos(self):
        """Run all demo scenarios."""
        runner = DemoRunner(
            self.vla_pipeline,
            self.simulator,
            self.safety_filter,
            self.scenario_manager
        )

        results = runner.run_all_scenarios(verbose=True)
        return results


class MockSimulator:
    """Mock simulator for testing."""

    def __init__(self):
        self.step_count = 0
        self.max_steps = 50

    def reset(self, config: Dict = None) -> Dict:
        """Reset simulator."""
        self.step_count = 0
        return {
            'image': np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
            'joint_positions': np.zeros(14)
        }

    def step(self, action: np.ndarray) -> tuple:
        """Execute action."""
        self.step_count += 1

        obs = {
            'image': np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
            'joint_positions': action[:14] if len(action) >= 14 else np.zeros(14)
        }

        done = self.step_count >= self.max_steps
        success = done and np.random.random() > 0.3  # 70% success rate

        return obs, 0.0, done, {'success': success}


# Main entry point
def main():
    app = VLADemoApplication(
        model_path="openvla/openvla-7b",
        use_simulation=True
    )
    app.run_interactive()


if __name__ == "__main__":
    main()
```

---

## 10.7 Future Directions

### Areas for Improvement

1. **Better Models**
   - Smaller, faster VLA architectures
   - Better action tokenization
   - Improved grounding

2. **More Capabilities**
   - Multi-object manipulation
   - Tool use
   - Long-horizon tasks

3. **Real-World Deployment**
   - Hardware integration
   - Real-time optimization
   - Safety certification

4. **Learning**
   - Online learning from feedback
   - Self-improvement
   - Human-in-the-loop

---

## 10.8 Summary

In this chapter, you learned:

1. **System Integration**: Combining all VLA components
2. **Demo Scenarios**: Defining and managing test scenarios
3. **Demo Runner**: Executing and recording demos
4. **Visual Feedback**: Real-time display with annotations
5. **Video Recording**: Creating demo videos
6. **Complete Application**: Interactive demo system

---

## 10.9 Exercises

### Exercise 10.1: Custom Scenario
Create a new demo scenario for your specific task.

### Exercise 10.2: Full Demo
Run all demo scenarios and record results.

### Exercise 10.3: Video Editing
Add title cards and annotations to demo videos.

### Exercise 10.4: Real Robot
Adapt the demo system for your real robot hardware.

---

## Quick Reference

### Run Demo
```python
app = VLADemoApplication(model_path, use_simulation=True)
app.run_interactive()
```

### Run Specific Scenario
```bash
demo> run pick_red_block
demo> record sort_blocks
```

---

## Congratulations!

You have completed Module 4: Vision-Language-Action Models!

You now understand:
- VLA model architectures and principles
- Vision-language model foundations
- Action tokenization for robots
- Language grounding for manipulation
- Complete VLA inference pipelines
- ROS 2 integration
- Safety constraints
- Fine-tuning on custom data
- Evaluation methodologies
- End-to-end system integration

**Next Steps:**
- Deploy on real robot hardware
- Collect more demonstration data
- Fine-tune for your specific tasks
- Contribute to open-source VLA research
