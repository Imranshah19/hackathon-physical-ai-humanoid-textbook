/**
 * Experience level selection step for profile wizard.
 *
 * Single-select for experience level (FR-009).
 */

import React from 'react';
import type { ProfileOptionInfo, ExperienceLevel } from '../../../types/auth';

interface ExperienceLevelStepProps {
  /** Available options from API */
  options: ProfileOptionInfo[];
  /** Currently selected value */
  selected: ExperienceLevel | null;
  /** Callback when selection changes */
  onChange: (selected: ExperienceLevel) => void;
  /** Error message if validation fails */
  error?: string;
}

export const ExperienceLevelStep: React.FC<ExperienceLevelStepProps> = ({
  options,
  selected,
  onChange,
  error,
}) => {
  return (
    <div className="wizard-step wizard-step-experience">
      <h3 className="wizard-step-title">What's your experience level with robotics?</h3>
      <p className="wizard-step-description">
        This helps us adjust the complexity and depth of explanations throughout the textbook.
      </p>

      <div className="wizard-options wizard-options-list">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`wizard-option wizard-option-full ${
              selected === option.value ? 'wizard-option-selected' : ''
            }`}
            onClick={() => onChange(option.value as ExperienceLevel)}
            aria-pressed={selected === option.value}
          >
            <div className="wizard-option-content">
              <span className="wizard-option-label">{option.label}</span>
              <span className="wizard-option-description">{option.description}</span>
            </div>
            <div className="wizard-option-check">
              {selected === option.value && (
                <svg
                  viewBox="0 0 24 24"
                  width="24"
                  height="24"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              )}
            </div>
          </button>
        ))}
      </div>

      {error && <div className="wizard-error">{error}</div>}

      <div className="wizard-help">
        <p>
          Not sure? Start with Intermediate — you can always adjust the content difficulty as you
          learn.
        </p>
      </div>
    </div>
  );
};

export default ExperienceLevelStep;
