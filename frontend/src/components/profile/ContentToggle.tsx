/**
 * Content toggle component for manual variant switching (T044).
 *
 * Allows users to override automatic personalization settings.
 */

import React, { useState, useCallback } from 'react';

interface ContentToggleProps {
  /** Current content variant */
  currentVariant: string;
  /** Available variants */
  variants: Array<{ value: string; label: string }>;
  /** Current preferred language */
  currentLanguage: string;
  /** Available languages */
  languages: Array<{ value: string; label: string }>;
  /** Whether auto-personalization is enabled */
  autoPersonalize: boolean;
  /** Callback when settings change */
  onChange: (settings: {
    variant?: string;
    language?: string;
    autoPersonalize?: boolean;
  }) => void;
  /** Whether the toggle is disabled */
  disabled?: boolean;
}

export const ContentToggle: React.FC<ContentToggleProps> = ({
  currentVariant,
  variants,
  currentLanguage,
  languages,
  autoPersonalize,
  onChange,
  disabled = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleVariantChange = useCallback(
    (variant: string) => {
      onChange({ variant, autoPersonalize: false });
    },
    [onChange]
  );

  const handleLanguageChange = useCallback(
    (language: string) => {
      onChange({ language, autoPersonalize: false });
    },
    [onChange]
  );

  const handleAutoToggle = useCallback(() => {
    onChange({ autoPersonalize: !autoPersonalize });
  }, [autoPersonalize, onChange]);

  const currentVariantLabel = variants.find((v) => v.value === currentVariant)?.label || currentVariant;
  const currentLanguageLabel = languages.find((l) => l.value === currentLanguage)?.label || currentLanguage;

  return (
    <div className="content-toggle">
      <button
        className="content-toggle-trigger"
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={disabled}
        aria-expanded={isExpanded}
        aria-controls="content-toggle-panel"
      >
        <span className="content-toggle-icon">{isExpanded ? '▼' : '▶'}</span>
        <span className="content-toggle-label">Content Settings</span>
        <span className="content-toggle-summary">
          {currentVariantLabel} · {currentLanguageLabel}
          {autoPersonalize && <span className="content-toggle-auto"> (Auto)</span>}
        </span>
      </button>

      {isExpanded && (
        <div id="content-toggle-panel" className="content-toggle-panel">
          {/* Auto-personalization toggle */}
          <div className="content-toggle-section">
            <label className="content-toggle-checkbox">
              <input
                type="checkbox"
                checked={autoPersonalize}
                onChange={handleAutoToggle}
                disabled={disabled}
              />
              <span className="content-toggle-checkbox-label">
                Auto-personalize based on my profile
              </span>
            </label>
            <p className="content-toggle-hint">
              When enabled, content adapts to your experience level and preferences.
            </p>
          </div>

          {/* Variant selection */}
          <div className="content-toggle-section">
            <label className="content-toggle-section-label">Content Level</label>
            <div className="content-toggle-options">
              {variants.map((variant) => (
                <button
                  key={variant.value}
                  className={`content-toggle-option ${
                    currentVariant === variant.value ? 'content-toggle-option-active' : ''
                  }`}
                  onClick={() => handleVariantChange(variant.value)}
                  disabled={disabled || autoPersonalize}
                >
                  {variant.label}
                </button>
              ))}
            </div>
          </div>

          {/* Language selection */}
          <div className="content-toggle-section">
            <label className="content-toggle-section-label">Code Language</label>
            <div className="content-toggle-options">
              {languages.map((lang) => (
                <button
                  key={lang.value}
                  className={`content-toggle-option ${
                    currentLanguage === lang.value ? 'content-toggle-option-active' : ''
                  }`}
                  onClick={() => handleLanguageChange(lang.value)}
                  disabled={disabled || autoPersonalize}
                >
                  {lang.label}
                </button>
              ))}
            </div>
          </div>

          {autoPersonalize && (
            <p className="content-toggle-auto-notice">
              Disable auto-personalization to manually select content settings.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Default variant options
export const DEFAULT_VARIANTS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
];

// Default language options
export const DEFAULT_LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'cpp', label: 'C++' },
  { value: 'both', label: 'Both' },
];

export default ContentToggle;
