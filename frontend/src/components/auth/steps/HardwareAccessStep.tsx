/**
 * Hardware access selection step for profile wizard.
 *
 * Multi-select for available hardware platforms (FR-008).
 */

import React from 'react';
import type { ProfileOptionInfo, HardwareOption } from '../../../types/auth';

interface HardwareAccessStepProps {
  /** Available options from API */
  options: ProfileOptionInfo[];
  /** Currently selected values */
  selected: HardwareOption[];
  /** Callback when selection changes */
  onChange: (selected: HardwareOption[]) => void;
  /** Error message if validation fails */
  error?: string;
}

export const HardwareAccessStep: React.FC<HardwareAccessStepProps> = ({
  options,
  selected,
  onChange,
  error,
}) => {
  const handleToggle = (value: HardwareOption) => {
    if (selected.includes(value)) {
      onChange(selected.filter((v) => v !== value));
    } else {
      onChange([...selected, value]);
    }
  };

  return (
    <div className="wizard-step wizard-step-hardware">
      <h3 className="wizard-step-title">What hardware do you have access to?</h3>
      <p className="wizard-step-description">
        Select all the hardware platforms you can work with. We'll tailor exercises and examples
        accordingly.
      </p>

      <div className="wizard-options wizard-options-grid">
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`wizard-option ${
              selected.includes(option.value as HardwareOption) ? 'wizard-option-selected' : ''
            }`}
            onClick={() => handleToggle(option.value as HardwareOption)}
            aria-pressed={selected.includes(option.value as HardwareOption)}
          >
            <span className="wizard-option-label">{option.label}</span>
            <span className="wizard-option-description">{option.description}</span>
          </button>
        ))}
      </div>

      {error && <div className="wizard-error">{error}</div>}

      <div className="wizard-help">
        <p>
          Don't have hardware yet? No problem! Select "Simulation Only" and we'll focus on virtual
          environments.
        </p>
      </div>
    </div>
  );
};

export default HardwareAccessStep;
