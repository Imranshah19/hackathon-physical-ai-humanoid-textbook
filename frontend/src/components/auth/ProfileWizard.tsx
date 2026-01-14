/**
 * Profile wizard component for collecting user personalization data.
 *
 * 3-step wizard: Software Background → Hardware Access → Experience Level
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SoftwareBackgroundStep } from './steps/SoftwareBackgroundStep';
import { HardwareAccessStep } from './steps/HardwareAccessStep';
import { ExperienceLevelStep } from './steps/ExperienceLevelStep';
import type {
  ProfileOptions,
  SoftwareOption,
  HardwareOption,
  ExperienceLevel,
} from '../../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProfileWizardProps {
  /** Callback when profile is completed */
  onComplete?: () => void;
  /** Callback when user skips the wizard */
  onSkip?: () => void;
}

interface WizardErrors {
  softwareBackground?: string;
  hardwareAccess?: string;
  experienceLevel?: string;
  general?: string;
}

type WizardStep = 'software' | 'hardware' | 'experience';

const STEPS: WizardStep[] = ['software', 'hardware', 'experience'];

export const ProfileWizard: React.FC<ProfileWizardProps> = ({ onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState<WizardStep>('software');
  const [options, setOptions] = useState<ProfileOptions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<WizardErrors>({});

  // Profile data
  const [softwareBackground, setSoftwareBackground] = useState<SoftwareOption[]>([]);
  const [hardwareAccess, setHardwareAccess] = useState<HardwareOption[]>([]);
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel | null>(null);

  // Fetch options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/profile/options`);
        if (response.ok) {
          const data = await response.json();
          setOptions({
            softwareBackground: data.software_background,
            hardwareAccess: data.hardware_access,
            experienceLevel: data.experience_level,
          });
        }
      } catch (error) {
        console.error('Failed to fetch profile options:', error);
        setErrors({ general: 'Failed to load options. Please refresh the page.' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchOptions();
  }, []);

  const currentStepIndex = STEPS.indexOf(currentStep);

  const validateCurrentStep = useCallback((): boolean => {
    const newErrors: WizardErrors = {};

    switch (currentStep) {
      case 'software':
        if (softwareBackground.length === 0) {
          newErrors.softwareBackground = 'Please select at least one option';
        }
        break;
      case 'hardware':
        if (hardwareAccess.length === 0) {
          newErrors.hardwareAccess = 'Please select at least one option';
        }
        break;
      case 'experience':
        if (!experienceLevel) {
          newErrors.experienceLevel = 'Please select your experience level';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [currentStep, softwareBackground, hardwareAccess, experienceLevel]);

  const handleNext = useCallback(() => {
    if (!validateCurrentStep()) {
      return;
    }

    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEPS.length) {
      setCurrentStep(STEPS[nextIndex]);
      setErrors({});
    }
  }, [currentStepIndex, validateCurrentStep]);

  const handleBack = useCallback(() => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(STEPS[prevIndex]);
      setErrors({});
    }
  }, [currentStepIndex]);

  const handleSubmit = useCallback(async () => {
    if (!validateCurrentStep()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const response = await fetch(`${API_BASE_URL}/api/profile/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          software_background: softwareBackground,
          hardware_access: hardwareAccess,
          experience_level: experienceLevel,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        setErrors({ general: data.detail || 'Failed to save profile' });
        setIsSubmitting(false);
        return;
      }

      onComplete?.();
    } catch (error) {
      setErrors({ general: 'Network error. Please try again.' });
      setIsSubmitting(false);
    }
  }, [softwareBackground, hardwareAccess, experienceLevel, validateCurrentStep, onComplete]);

  const handleSkip = useCallback(async () => {
    try {
      await fetch(`${API_BASE_URL}/api/profile/skip`, {
        method: 'POST',
        credentials: 'include',
      });
      onSkip?.();
    } catch (error) {
      // Skip anyway on error
      onSkip?.();
    }
  }, [onSkip]);

  if (isLoading) {
    return (
      <div className="wizard-loading">
        <div className="wizard-spinner" />
        <p>Loading...</p>
      </div>
    );
  }

  if (!options) {
    return (
      <div className="wizard-error-container">
        <p>Failed to load profile options.</p>
        <button onClick={() => window.location.reload()} className="auth-btn auth-btn-primary">
          Retry
        </button>
      </div>
    );
  }

  const isLastStep = currentStep === 'experience';

  return (
    <div className="profile-wizard">
      <div className="wizard-header">
        <h2 className="wizard-title">Personalize Your Learning</h2>
        <p className="wizard-subtitle">Help us tailor the content to your background and goals</p>
      </div>

      {/* Progress indicator */}
      <div className="wizard-progress">
        {STEPS.map((step, index) => (
          <div
            key={step}
            className={`wizard-progress-step ${
              index <= currentStepIndex ? 'wizard-progress-step-active' : ''
            } ${index < currentStepIndex ? 'wizard-progress-step-completed' : ''}`}
          >
            <div className="wizard-progress-dot">
              {index < currentStepIndex ? (
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
              ) : (
                index + 1
              )}
            </div>
            <span className="wizard-progress-label">
              {step === 'software' && 'Background'}
              {step === 'hardware' && 'Hardware'}
              {step === 'experience' && 'Experience'}
            </span>
          </div>
        ))}
      </div>

      {errors.general && <div className="wizard-error wizard-error-general">{errors.general}</div>}

      {/* Step content */}
      <div className="wizard-content">
        {currentStep === 'software' && (
          <SoftwareBackgroundStep
            options={options.softwareBackground}
            selected={softwareBackground}
            onChange={setSoftwareBackground}
            error={errors.softwareBackground}
          />
        )}
        {currentStep === 'hardware' && (
          <HardwareAccessStep
            options={options.hardwareAccess}
            selected={hardwareAccess}
            onChange={setHardwareAccess}
            error={errors.hardwareAccess}
          />
        )}
        {currentStep === 'experience' && (
          <ExperienceLevelStep
            options={options.experienceLevel}
            selected={experienceLevel}
            onChange={setExperienceLevel}
            error={errors.experienceLevel}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="wizard-footer">
        <div className="wizard-footer-left">
          {currentStepIndex > 0 && (
            <button
              type="button"
              className="auth-btn auth-btn-secondary"
              onClick={handleBack}
              disabled={isSubmitting}
            >
              Back
            </button>
          )}
        </div>

        <div className="wizard-footer-center">
          <button
            type="button"
            className="auth-link"
            onClick={handleSkip}
            disabled={isSubmitting}
          >
            Skip for now
          </button>
        </div>

        <div className="wizard-footer-right">
          {isLastStep ? (
            <button
              type="button"
              className="auth-btn auth-btn-primary"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Complete'}
            </button>
          ) : (
            <button
              type="button"
              className="auth-btn auth-btn-primary"
              onClick={handleNext}
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileWizard;
