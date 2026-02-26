/**
 * Exercise viewer with hardware variants (T046).
 *
 * Displays exercises with hardware-specific instructions.
 */

import React, { useState, useCallback } from 'react';

interface ExerciseViewerProps {
  /** Exercise identifier */
  exerciseId: string;
  /** Exercise title */
  title: string;
  /** Exercise description */
  description: string;
  /** Difficulty level */
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  /** Hardware variant */
  hardwareVariant: string;
  /** Exercise instructions (markdown or HTML) */
  instructions: string;
  /** Hints for the exercise */
  hints: string[];
  /** Solution (only shown if user chooses) */
  solution?: string;
  /** Callback when exercise is marked complete */
  onComplete?: () => void;
  /** Whether to show the solution initially */
  showSolutionInitially?: boolean;
}

const HARDWARE_LABELS: Record<string, { label: string; icon: string }> = {
  simulation: { label: 'Simulation', icon: '🖥️' },
  raspberry_pi: { label: 'Raspberry Pi', icon: '🍓' },
  jetson: { label: 'NVIDIA Jetson', icon: '🔋' },
  robot_arm: { label: 'Robot Arm', icon: '🦾' },
  humanoid: { label: 'Humanoid Robot', icon: '🤖' },
};

const DIFFICULTY_STYLES: Record<string, { label: string; className: string }> = {
  beginner: { label: 'Beginner', className: 'exercise-difficulty-beginner' },
  intermediate: { label: 'Intermediate', className: 'exercise-difficulty-intermediate' },
  advanced: { label: 'Advanced', className: 'exercise-difficulty-advanced' },
};

export const ExerciseViewer: React.FC<ExerciseViewerProps> = ({
  exerciseId,
  title,
  description,
  difficulty,
  hardwareVariant,
  instructions,
  hints,
  solution,
  onComplete,
  showSolutionInitially = false,
}) => {
  const [showHints, setShowHints] = useState(false);
  const [showSolution, setShowSolution] = useState(showSolutionInitially);
  const [revealedHints, setRevealedHints] = useState<number[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);

  // Get hardware info
  const hardware = HARDWARE_LABELS[hardwareVariant] || {
    label: hardwareVariant,
    icon: '📦',
  };

  // Get difficulty info
  const difficultyInfo = DIFFICULTY_STYLES[difficulty] || DIFFICULTY_STYLES.beginner;

  // Handle revealing a hint
  const handleRevealHint = useCallback((index: number) => {
    setRevealedHints((prev) => {
      if (prev.includes(index)) return prev;
      return [...prev, index];
    });
  }, []);

  // Handle marking as complete
  const handleComplete = useCallback(() => {
    setIsCompleted(true);
    onComplete?.();
  }, [onComplete]);

  return (
    <div className={`exercise ${isCompleted ? 'exercise-completed' : ''}`} id={`exercise-${exerciseId}`}>
      {/* Header */}
      <div className="exercise-header">
        <div className="exercise-title-row">
          <h4 className="exercise-title">{title}</h4>
          {isCompleted && <span className="exercise-complete-badge">✓ Completed</span>}
        </div>

        <div className="exercise-meta">
          <span className={`exercise-difficulty ${difficultyInfo.className}`}>
            {difficultyInfo.label}
          </span>
          <span className="exercise-hardware">
            <span className="exercise-hardware-icon">{hardware.icon}</span>
            {hardware.label}
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="exercise-description">{description}</p>

      {/* Instructions */}
      <div className="exercise-instructions">
        <h5 className="exercise-section-title">Instructions</h5>
        <div
          className="exercise-instructions-content"
          dangerouslySetInnerHTML={{ __html: instructions.replace(/\n/g, '<br/>') }}
        />
      </div>

      {/* Hints section */}
      {hints.length > 0 && (
        <div className="exercise-hints">
          <button
            className="exercise-hints-toggle"
            onClick={() => setShowHints(!showHints)}
            aria-expanded={showHints}
          >
            <span className="exercise-hints-icon">{showHints ? '▼' : '▶'}</span>
            Hints ({hints.length})
          </button>

          {showHints && (
            <div className="exercise-hints-list">
              {hints.map((hint, index) => (
                <div key={index} className="exercise-hint">
                  {revealedHints.includes(index) ? (
                    <p className="exercise-hint-text">{hint}</p>
                  ) : (
                    <button
                      className="exercise-hint-reveal"
                      onClick={() => handleRevealHint(index)}
                    >
                      Click to reveal hint {index + 1}
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Solution section */}
      {solution && (
        <div className="exercise-solution">
          <button
            className="exercise-solution-toggle"
            onClick={() => setShowSolution(!showSolution)}
            aria-expanded={showSolution}
          >
            <span className="exercise-solution-icon">{showSolution ? '▼' : '▶'}</span>
            {showSolution ? 'Hide Solution' : 'Show Solution'}
          </button>

          {showSolution && (
            <div className="exercise-solution-content">
              <div className="exercise-solution-warning">
                Try to solve the exercise yourself before looking at the solution!
              </div>
              <pre className="exercise-solution-code">{solution}</pre>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="exercise-actions">
        {!isCompleted ? (
          <button className="exercise-btn exercise-btn-complete" onClick={handleComplete}>
            Mark as Complete
          </button>
        ) : (
          <button
            className="exercise-btn exercise-btn-redo"
            onClick={() => setIsCompleted(false)}
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default ExerciseViewer;
