/**
 * Forgot password page (T072).
 *
 * Allows users to request a password reset email.
 */

import React, { useCallback } from 'react';
import { ForgotPasswordForm } from '../components/auth/ForgotPasswordForm';
import { useAuth } from '../context/AuthContext';

export const ForgotPassword: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  const handleBackToLogin = useCallback(() => {
    window.location.href = '/login';
  }, []);

  // Show loading while checking auth state
  if (isLoading) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-loading">
            <div className="auth-spinner" />
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  // Redirect if already authenticated - they can change password from settings
  if (isAuthenticated) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-info-icon">i</div>
            <h2 className="auth-form-title">Already Signed In</h2>
            <p className="auth-form-subtitle">
              You're already signed in. You can change your password from your profile settings.
            </p>
            <div className="auth-form-actions">
              <button
                type="button"
                className="auth-btn auth-btn-secondary"
                onClick={() => (window.location.href = '/profile')}
              >
                Go to Profile
              </button>
              <button
                type="button"
                className="auth-btn auth-btn-primary"
                onClick={() => (window.location.href = '/')}
              >
                Back to Textbook
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <ForgotPasswordForm onBackToLogin={handleBackToLogin} />
        </div>

        <div className="auth-footer">
          <p className="auth-footer-text">
            Remember your password?{' '}
            <a href="/login" className="auth-footer-link">
              Sign in instead
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
