/**
 * Software background selection step for profile wizard.
 *
 * Multi-select for programming languages and frameworks (FR-007).
 */

import React from 'react';
import type { ProfileOptionInfo, SoftwareOption } from '../../../types/auth';

interface SoftwareBackgroundStepProps {
  /** Available options from API */
  options: ProfileOptionInfo[];
  /** Currently selected values */
  selected: SoftwareOption[];
  /** Callback when selection changes */
  onChange: (selected: SoftwareOption[]) => void;
  /** Error message if validation fails */
  error?: string;
}

export const SoftwareBackgroundStep: React.FC<SoftwareBackgroundStepProps> = ({
  options,
  selected,
  onChange,
  error,
}) => {
  const handleToggle = (value: SoftwareOption) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  return (
    <div className="wizard-step wizard-step-software">
      <h3 className="wizard-step-title">What's your programming background?</h3>
      <p className="wizard-step-description">
        Select all languages and frameworks you're familiar with. This helps us show you relevant
        code examples.
      </p>

      <div className="wizard-options wizard-options-grid">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`wizard-option ${
              selected.includes(option.value as SoftwareOption) ? 'wizard-option-selected' : ''
            }`}
            onClick={() => handleToggle(option.value as SoftwareOption)}
            aria-pressed={selected.includes(option.value as SoftwareOption)}
          >
            <span className="wizard-option-label">{option.label}</span>
            <span className="wizard-option-description">{option.description}</span>
          </button>
        ))}
      </div>

      {error && <div className="wizard-error">{error}</div>}

      <div className="wizard-help">
        <p>Don't worry — you can always change this later in your profile settings.</p>
      </div>
    </div>
  );
};

export default SoftwareBackgroundStep;
