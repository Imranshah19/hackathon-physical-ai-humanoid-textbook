/**
 * Registration flow page integrating RegisterForm and ProfileWizard.
 *
 * Flow: Registration Form → Profile Wizard → Redirect to app
 */

import React, { useState, useCallback } from 'react';
import { RegisterForm } from '../components/auth/RegisterForm';
import { ProfileWizard } from '../components/auth/ProfileWizard';
import { useAuth } from '../context/AuthContext';

type RegistrationStep = 'register' | 'profile' | 'complete';

export const Register: React.FC = () => {
  const [step, setStep] = useState<RegistrationStep>('register');
  const { refreshProfile } = useAuth();

  const handleRegistrationSuccess = useCallback(() => {
    setStep('profile');
  }, []);

  const handleProfileComplete = useCallback(async () => {
    await refreshProfile();
    setStep('complete');
    // Redirect after brief delay to show success
    setTimeout(() => {
      window.location.href = '/';
    }, 1500);
  }, [refreshProfile]);

  const handleProfileSkip = useCallback(async () => {
    await refreshProfile();
    // Redirect immediately on skip
    window.location.href = '/';
  }, [refreshProfile]);

  const handleSwitchToLogin = useCallback(() => {
    window.location.href = '/login';
  }, []);

  return (
    <div className="auth-page">
      <div className="auth-container">
        {step === 'register' && (
          <RegisterForm
            onSuccess={handleRegistrationSuccess}
            onSwitchToLogin={handleSwitchToLogin}
          />
        )}

        {step === 'profile' && (
          <ProfileWizard onComplete={handleProfileComplete} onSkip={handleProfileSkip} />
        )}

        {step === 'complete' && (
          <div className="auth-success">
            <div className="auth-success-icon">
              <svg viewBox="0 0 24 24" width="64" height="64" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
              </svg>
            </div>
            <h2 className="auth-success-title">Welcome aboard!</h2>
            <p className="auth-success-message">
              Your profile is set up. Redirecting you to the textbook...
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Register;
