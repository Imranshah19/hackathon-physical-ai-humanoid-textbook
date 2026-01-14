# Chapter 9: Evaluation and Benchmarking

**Duration**: 4-5 hours
**Prerequisites**: Chapter 8 (Fine-tuning)

---

## Learning Objectives

By the end of this chapter, you will be able to:
- Define evaluation metrics for VLA systems
- Create benchmark tasks for manipulation
- Measure generalization to new scenarios
- Analyze failure modes systematically
- Generate evaluation reports

---

## 9.1 VLA Evaluation Metrics

```python
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np


@dataclass
class EvaluationMetrics:
    """Standard metrics for VLA evaluation."""

    # Task-level metrics
    task_success_rate: float = 0.0  # % of tasks completed successfully
    partial_completion: float = 0.0  # Average % of task steps completed

    # Action-level metrics
    action_accuracy: float = 0.0  # % of correct action predictions
    action_rmse: float = 0.0  # Root mean square error of actions
    action_mae: float = 0.0  # Mean absolute error

    # Timing metrics
    avg_latency_ms: float = 0.0  # Average inference time
    p99_latency_ms: float = 0.0  # 99th percentile latency

    # Safety metrics
    safety_violations: int = 0  # Number of safety filter activations
    collision_count: int = 0  # Number of collisions

    # Generalization
    novel_object_success: float = 0.0  # Success on unseen objects
    novel_instruction_success: float = 0.0  # Success on paraphrased instructions


class MetricsCalculator:
    """Calculate evaluation metrics."""

    @staticmethod
    def compute_task_success(results: List[Dict]) -> float:
        """Compute task success rate."""
        if not results:
            return 0.0
        successes = sum(1 for r in results if r.get('success', False))
        return successes / len(results)

    @staticmethod
    def compute_action_metrics(
        predictions: np.ndarray,
        ground_truth: np.ndarray
    ) -> Dict[str, float]:
        """Compute action prediction metrics."""
        errors = predictions - ground_truth

        rmse = np.sqrt(np.mean(errors ** 2))
        mae = np.mean(np.abs(errors))

        # Per-dimension metrics
        per_dim_rmse = np.sqrt(np.mean(errors ** 2, axis=0))
        per_dim_mae = np.mean(np.abs(errors), axis=0)

        # Accuracy (within threshold)
        threshold = 0.1  # 10% of action range
        accurate = np.abs(errors) < threshold
        accuracy = np.mean(accurate)

        return {
            'rmse': rmse,
            'mae': mae,
            'accuracy': accuracy,
            'per_dim_rmse': per_dim_rmse.tolist(),
            'per_dim_mae': per_dim_mae.tolist()
        }

    @staticmethod
    def compute_latency_metrics(latencies: List[float]) -> Dict[str, float]:
        """Compute latency statistics."""
        if not latencies:
            return {'mean': 0, 'p50': 0, 'p95': 0, 'p99': 0}

        return {
            'mean': np.mean(latencies),
            'p50': np.percentile(latencies, 50),
            'p95': np.percentile(latencies, 95),
            'p99': np.percentile(latencies, 99)
        }
```

---

## 9.2 Benchmark Task Definitions

```python
@dataclass
class BenchmarkTask:
    """Definition of a benchmark task."""
    name: str
    instruction: str
    task_type: str  # pick, place, search, etc.
    difficulty: str  # easy, medium, hard
    max_steps: int = 100
    success_criteria: Dict = None
    scene_config: Dict = None


class ManipulationBenchmark:
    """Benchmark suite for manipulation tasks."""

    def __init__(self):
        self.tasks = self._create_tasks()

    def _create_tasks(self) -> List[BenchmarkTask]:
        """Create benchmark task definitions."""
        tasks = []

        # Pick tasks
        pick_objects = ['red block', 'blue cup', 'green ball', 'yellow bowl']
        for obj in pick_objects:
            tasks.append(BenchmarkTask(
                name=f"pick_{obj.replace(' ', '_')}",
                instruction=f"pick up the {obj}",
                task_type="pick",
                difficulty="easy",
                max_steps=50,
                success_criteria={'object_grasped': obj}
            ))

        # Place tasks
        place_targets = ['table', 'tray', 'box', 'shelf']
        for target in place_targets:
            tasks.append(BenchmarkTask(
                name=f"place_on_{target}",
                instruction=f"place the object on the {target}",
                task_type="place",
                difficulty="medium",
                max_steps=80,
                success_criteria={'object_on': target}
            ))

        # Pick-and-place tasks
        for obj in pick_objects[:2]:
            for target in place_targets[:2]:
                tasks.append(BenchmarkTask(
                    name=f"pick_{obj.split()[0]}_place_{target}",
                    instruction=f"pick up the {obj} and put it on the {target}",
                    task_type="pick_place",
                    difficulty="hard",
                    max_steps=150,
                    success_criteria={'object_grasped': obj, 'object_on': target}
                ))

        # Search tasks
        search_objects = ['red block', 'hidden cup', 'small ball']
        for obj in search_objects:
            tasks.append(BenchmarkTask(
                name=f"find_{obj.replace(' ', '_')}",
                instruction=f"find the {obj}",
                task_type="search",
                difficulty="medium",
                max_steps=100,
                success_criteria={'object_found': obj}
            ))

        return tasks

    def get_tasks_by_type(self, task_type: str) -> List[BenchmarkTask]:
        """Filter tasks by type."""
        return [t for t in self.tasks if t.task_type == task_type]

    def get_tasks_by_difficulty(self, difficulty: str) -> List[BenchmarkTask]:
        """Filter tasks by difficulty."""
        return [t for t in self.tasks if t.difficulty == difficulty]


# Generalization benchmark
class GeneralizationBenchmark:
    """Benchmark for testing generalization."""

    def __init__(self, base_tasks: List[BenchmarkTask]):
        self.base_tasks = base_tasks
        self.novel_tasks = self._create_novel_tasks()

    def _create_novel_tasks(self) -> Dict[str, List[BenchmarkTask]]:
        """Create tasks to test generalization."""
        novel = {
            'novel_objects': [],
            'novel_instructions': [],
            'novel_compositions': []
        }

        # Novel objects (not in training)
        novel_objects = ['purple cylinder', 'orange cone', 'pink sphere']
        for obj in novel_objects:
            novel['novel_objects'].append(BenchmarkTask(
                name=f"pick_novel_{obj.replace(' ', '_')}",
                instruction=f"pick up the {obj}",
                task_type="pick",
                difficulty="hard",
                max_steps=50
            ))

        # Novel instruction phrasings
        paraphrases = [
            ("pick up the red block", "grab the crimson cube"),
            ("pick up the red block", "take the red block"),
            ("place on the table", "put it down on the table"),
            ("place on the table", "set it on the desk"),
        ]
        for original, paraphrase in paraphrases:
            novel['novel_instructions'].append(BenchmarkTask(
                name=f"paraphrase_{len(novel['novel_instructions'])}",
                instruction=paraphrase,
                task_type="pick",
                difficulty="medium",
                max_steps=50
            ))

        # Novel compositions
        compositions = [
            "pick up the red block and stack it on the blue block",
            "move the cup from the left to the right side",
            "arrange the blocks in a line",
        ]
        for i, comp in enumerate(compositions):
            novel['novel_compositions'].append(BenchmarkTask(
                name=f"composition_{i}",
                instruction=comp,
                task_type="multi_step",
                difficulty="hard",
                max_steps=200
            ))

        return novel
```

---

## 9.3 Evaluation Runner

```python
import time
from typing import Callable


class EvaluationRunner:
    """Run evaluation on VLA model."""

    def __init__(
        self,
        model,
        processor,
        action_tokenizer,
        simulator,
        safety_filter=None
    ):
        self.model = model
        self.processor = processor
        self.action_tokenizer = action_tokenizer
        self.simulator = simulator
        self.safety_filter = safety_filter

        self.device = next(model.parameters()).device

    def evaluate_benchmark(
        self,
        benchmark: ManipulationBenchmark,
        episodes_per_task: int = 10,
        verbose: bool = True
    ) -> Dict:
        """
        Evaluate model on benchmark.

        Args:
            benchmark: Benchmark task suite
            episodes_per_task: Number of episodes per task
            verbose: Print progress

        Returns:
            Evaluation results
        """
        results = {
            'tasks': {},
            'overall': {},
            'by_type': {},
            'by_difficulty': {}
        }

        all_latencies = []

        for task in benchmark.tasks:
            if verbose:
                print(f"\nEvaluating: {task.name}")

            task_results = []

            for ep in range(episodes_per_task):
                episode_result = self._run_episode(task)
                task_results.append(episode_result)
                all_latencies.extend(episode_result.get('latencies', []))

            # Compute task metrics
            success_rate = MetricsCalculator.compute_task_success(task_results)
            avg_steps = np.mean([r.get('steps', 0) for r in task_results])

            results['tasks'][task.name] = {
                'success_rate': success_rate,
                'avg_steps': avg_steps,
                'task_type': task.task_type,
                'difficulty': task.difficulty
            }

            if verbose:
                print(f"  Success rate: {success_rate:.1%}, Avg steps: {avg_steps:.1f}")

        # Aggregate metrics
        results['overall'] = {
            'success_rate': np.mean([r['success_rate'] for r in results['tasks'].values()]),
            'latency': MetricsCalculator.compute_latency_metrics(all_latencies)
        }

        # Group by type
        for task_type in ['pick', 'place', 'pick_place', 'search']:
            type_tasks = [r for name, r in results['tasks'].items()
                         if r['task_type'] == task_type]
            if type_tasks:
                results['by_type'][task_type] = {
                    'success_rate': np.mean([t['success_rate'] for t in type_tasks])
                }

        # Group by difficulty
        for difficulty in ['easy', 'medium', 'hard']:
            diff_tasks = [r for name, r in results['tasks'].items()
                         if r['difficulty'] == difficulty]
            if diff_tasks:
                results['by_difficulty'][difficulty] = {
                    'success_rate': np.mean([t['success_rate'] for t in diff_tasks])
                }

        return results

    def _run_episode(self, task: BenchmarkTask) -> Dict:
        """Run single episode."""
        # Reset simulator
        obs = self.simulator.reset(task.scene_config or {})

        episode_latencies = []
        steps = 0
        success = False

        for step in range(task.max_steps):
            # Get image
            image = obs['image']

            # Inference
            start_time = time.perf_counter()
            action = self._get_action(image, task.instruction)
            latency = (time.perf_counter() - start_time) * 1000
            episode_latencies.append(latency)

            # Apply safety filter
            if self.safety_filter:
                action, is_safe, _ = self.safety_filter.filter(
                    action,
                    obs.get('joint_positions', np.zeros(14))
                )

            # Execute action
            obs, reward, done, info = self.simulator.step(action)
            steps += 1

            if done:
                success = info.get('success', False)
                break

        return {
            'success': success,
            'steps': steps,
            'latencies': episode_latencies
        }

    def _get_action(self, image: np.ndarray, instruction: str) -> np.ndarray:
        """Get action from model."""
        from PIL import Image as PILImage
        pil_image = PILImage.fromarray(image)

        prompt = f"In: What action should the robot take to {instruction}?\nOut:"
        inputs = self.processor(text=prompt, images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=20)

        text = self.processor.decode(outputs[0], skip_special_tokens=True)

        # Parse action
        import re
        numbers = re.findall(r'\d+', text.split("Out:")[-1] if "Out:" in text else text)
        if len(numbers) >= 7:
            tokens = np.array([int(n) for n in numbers[:7]])
            return self.action_tokenizer.decode_action(tokens)

        return np.zeros(7)
```

---

## 9.4 Failure Analysis

```python
from enum import Enum
from collections import Counter


class FailureMode(Enum):
    """Categories of VLA failures."""
    GROUNDING_ERROR = "grounding_error"  # Wrong object identified
    ACTION_ERROR = "action_error"  # Wrong action predicted
    TIMING_ERROR = "timing_error"  # Action at wrong time
    HALLUCINATION = "hallucination"  # Action for non-existent object
    LOW_CONFIDENCE = "low_confidence"  # Confidence too low
    SAFETY_VIOLATION = "safety_violation"  # Safety filter blocked
    TIMEOUT = "timeout"  # Exceeded max steps
    UNKNOWN = "unknown"


@dataclass
class FailureCase:
    """Single failure case."""
    task_name: str
    instruction: str
    failure_mode: FailureMode
    step: int
    details: Dict


class FailureAnalyzer:
    """Analyze VLA failure cases."""

    def __init__(self):
        self.failures: List[FailureCase] = []

    def add_failure(
        self,
        task_name: str,
        instruction: str,
        failure_mode: FailureMode,
        step: int,
        details: Dict = None
    ):
        """Record a failure case."""
        self.failures.append(FailureCase(
            task_name=task_name,
            instruction=instruction,
            failure_mode=failure_mode,
            step=step,
            details=details or {}
        ))

    def analyze(self) -> Dict:
        """Analyze failure patterns."""
        if not self.failures:
            return {'total_failures': 0}

        # Count by mode
        mode_counts = Counter(f.failure_mode.value for f in self.failures)

        # Count by task
        task_counts = Counter(f.task_name for f in self.failures)

        # Analyze step distribution
        steps = [f.step for f in self.failures]
        step_stats = {
            'mean': np.mean(steps),
            'median': np.median(steps),
            'early_failures': sum(1 for s in steps if s < 10),  # First 10 steps
            'late_failures': sum(1 for s in steps if s > 50)
        }

        return {
            'total_failures': len(self.failures),
            'by_mode': dict(mode_counts.most_common()),
            'by_task': dict(task_counts.most_common(10)),
            'step_distribution': step_stats
        }

    def get_recommendations(self) -> List[str]:
        """Generate improvement recommendations based on failures."""
        analysis = self.analyze()
        recommendations = []

        if not analysis.get('by_mode'):
            return ["No failures to analyze"]

        mode_counts = analysis['by_mode']

        # Grounding errors
        if mode_counts.get('grounding_error', 0) > len(self.failures) * 0.2:
            recommendations.append(
                "High grounding error rate. Consider:\n"
                "  - Improving object detection model\n"
                "  - Adding more diverse training scenes\n"
                "  - Implementing referring expression clarification"
            )

        # Action errors
        if mode_counts.get('action_error', 0) > len(self.failures) * 0.2:
            recommendations.append(
                "High action error rate. Consider:\n"
                "  - More demonstration data for failing tasks\n"
                "  - Finer action tokenization\n"
                "  - Action chunking for temporal consistency"
            )

        # Timeouts
        if mode_counts.get('timeout', 0) > len(self.failures) * 0.15:
            recommendations.append(
                "Many timeout failures. Consider:\n"
                "  - Increasing max steps\n"
                "  - Breaking complex tasks into subtasks\n"
                "  - Adding progress monitoring"
            )

        # Safety violations
        if mode_counts.get('safety_violation', 0) > len(self.failures) * 0.1:
            recommendations.append(
                "Frequent safety violations. Consider:\n"
                "  - Fine-tuning on safer demonstrations\n"
                "  - Adjusting safety thresholds\n"
                "  - Adding safety-aware reward shaping"
            )

        return recommendations if recommendations else ["No specific recommendations - failures are diverse"]

    def generate_report(self, save_path: str = None) -> str:
        """Generate detailed failure analysis report."""
        analysis = self.analyze()

        report = []
        report.append("=" * 60)
        report.append("VLA Failure Analysis Report")
        report.append("=" * 60)
        report.append("")

        report.append(f"Total Failures: {analysis['total_failures']}")
        report.append("")

        report.append("Failures by Mode:")
        for mode, count in analysis.get('by_mode', {}).items():
            pct = count / analysis['total_failures'] * 100
            report.append(f"  {mode}: {count} ({pct:.1f}%)")
        report.append("")

        report.append("Top Failing Tasks:")
        for task, count in list(analysis.get('by_task', {}).items())[:5]:
            report.append(f"  {task}: {count}")
        report.append("")

        report.append("Step Distribution:")
        step_stats = analysis.get('step_distribution', {})
        report.append(f"  Mean failure step: {step_stats.get('mean', 0):.1f}")
        report.append(f"  Early failures (step < 10): {step_stats.get('early_failures', 0)}")
        report.append(f"  Late failures (step > 50): {step_stats.get('late_failures', 0)}")
        report.append("")

        report.append("Recommendations:")
        for rec in self.get_recommendations():
            report.append(rec)
            report.append("")

        report_text = "\n".join(report)

        if save_path:
            with open(save_path, 'w') as f:
                f.write(report_text)

        return report_text
```

---

## 9.5 Evaluation Dashboard

```python
import matplotlib.pyplot as plt


class EvaluationDashboard:
    """Generate visual evaluation reports."""

    def __init__(self, results: Dict, failure_analysis: Dict = None):
        self.results = results
        self.failure_analysis = failure_analysis

    def plot_success_rates(self, save_path: str = None):
        """Plot success rates by task."""
        tasks = list(self.results['tasks'].keys())
        success_rates = [self.results['tasks'][t]['success_rate'] for t in tasks]

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = ['green' if r > 0.8 else 'orange' if r > 0.5 else 'red'
                  for r in success_rates]

        bars = ax.barh(tasks, success_rates, color=colors)
        ax.set_xlabel('Success Rate')
        ax.set_title('Task Success Rates')
        ax.set_xlim(0, 1)

        # Add value labels
        for bar, rate in zip(bars, success_rates):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{rate:.1%}', va='center')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_by_difficulty(self, save_path: str = None):
        """Plot success rates by difficulty."""
        difficulties = ['easy', 'medium', 'hard']
        rates = [self.results['by_difficulty'].get(d, {}).get('success_rate', 0)
                 for d in difficulties]

        fig, ax = plt.subplots(figsize=(8, 5))

        colors = ['green', 'orange', 'red']
        ax.bar(difficulties, rates, color=colors)
        ax.set_ylabel('Success Rate')
        ax.set_title('Success Rate by Difficulty')
        ax.set_ylim(0, 1)

        for i, rate in enumerate(rates):
            ax.text(i, rate + 0.02, f'{rate:.1%}', ha='center')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def plot_failure_distribution(self, save_path: str = None):
        """Plot failure mode distribution."""
        if not self.failure_analysis or 'by_mode' not in self.failure_analysis:
            return

        modes = list(self.failure_analysis['by_mode'].keys())
        counts = list(self.failure_analysis['by_mode'].values())

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.pie(counts, labels=modes, autopct='%1.1f%%', startangle=90)
        ax.set_title('Failure Mode Distribution')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150)
        plt.show()

    def generate_html_report(self, save_path: str):
        """Generate HTML evaluation report."""
        html = []
        html.append("<html><head><title>VLA Evaluation Report</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 40px; }")
        html.append("table { border-collapse: collapse; width: 100%; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #4CAF50; color: white; }")
        html.append(".success { color: green; } .failure { color: red; }")
        html.append("</style></head><body>")

        html.append("<h1>VLA Evaluation Report</h1>")

        # Overall metrics
        html.append("<h2>Overall Metrics</h2>")
        html.append(f"<p><strong>Success Rate:</strong> {self.results['overall']['success_rate']:.1%}</p>")

        latency = self.results['overall'].get('latency', {})
        html.append(f"<p><strong>Average Latency:</strong> {latency.get('mean', 0):.1f} ms</p>")
        html.append(f"<p><strong>P99 Latency:</strong> {latency.get('p99', 0):.1f} ms</p>")

        # Task results table
        html.append("<h2>Task Results</h2>")
        html.append("<table>")
        html.append("<tr><th>Task</th><th>Success Rate</th><th>Avg Steps</th><th>Type</th><th>Difficulty</th></tr>")

        for task_name, task_result in self.results['tasks'].items():
            rate = task_result['success_rate']
            rate_class = 'success' if rate > 0.7 else 'failure'
            html.append(f"<tr>")
            html.append(f"<td>{task_name}</td>")
            html.append(f"<td class='{rate_class}'>{rate:.1%}</td>")
            html.append(f"<td>{task_result['avg_steps']:.1f}</td>")
            html.append(f"<td>{task_result['task_type']}</td>")
            html.append(f"<td>{task_result['difficulty']}</td>")
            html.append(f"</tr>")

        html.append("</table>")

        html.append("</body></html>")

        with open(save_path, 'w') as f:
            f.write("\n".join(html))

        print(f"Report saved to {save_path}")
```

---

## 9.6 Summary

In this chapter, you learned:

1. **Evaluation Metrics**: Success rate, action accuracy, latency
2. **Benchmark Tasks**: Pick, place, search, multi-step
3. **Generalization Testing**: Novel objects, instructions, compositions
4. **Evaluation Runner**: Systematic benchmark execution
5. **Failure Analysis**: Categorizing and understanding failures
6. **Reporting**: Visualizations and HTML reports

---

## 9.7 Exercises

### Exercise 9.1: Benchmark Creation
Create a custom benchmark for your robot and tasks.

### Exercise 9.2: Evaluation Run
Evaluate a VLA model on the manipulation benchmark.

### Exercise 9.3: Failure Analysis
Collect and analyze failure cases. Generate improvement recommendations.

### Exercise 9.4: Generalization Test
Test model on novel objects and paraphrased instructions.

---

## Quick Reference

### Run Evaluation
```python
runner = EvaluationRunner(model, processor, tokenizer, simulator)
results = runner.evaluate_benchmark(benchmark, episodes_per_task=10)
```

### Failure Analysis
```python
analyzer = FailureAnalyzer()
analyzer.add_failure(task, instruction, FailureMode.GROUNDING_ERROR, step=5)
report = analyzer.generate_report()
```

---

**Next Chapter**: [Chapter 10 - End-to-End VLA Demo](ch10-end-to-end-demo.md)
