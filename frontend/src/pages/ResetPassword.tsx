/**
 * Reset password page with token parameter (T073).
 *
 * Allows users to set a new password using a reset link.
 */

import React, { useCallback, useMemo } from 'react';
import { ResetPasswordForm } from '../components/auth/ResetPasswordForm';
import { useAuth } from '../context/AuthContext';

export const ResetPassword: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  // Extract token from URL query params
  const token = useMemo(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('token') || '';
  }, []);

  const handleGoToLogin = useCallback(() => {
    window.location.href = '/login';
  }, []);

  const handleSuccess = useCallback(() => {
    // Auto-redirect to login after 3 seconds
    setTimeout(() => {
      window.location.href = '/login';
    }, 3000);
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

  // If authenticated, suggest going to profile settings instead
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

  // Show error if no token provided
  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="auth-card">
            <div className="auth-error-icon">!</div>
            <h2 className="auth-form-title">Invalid Reset Link</h2>
            <p className="auth-form-subtitle">
              This password reset link is missing or incomplete. Please request a new password reset
              link.
            </p>
            <div className="auth-form-actions">
              <button
                type="button"
                className="auth-btn auth-btn-primary"
                onClick={() => (window.location.href = '/forgot-password')}
              >
                Request New Link
              </button>
            </div>
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
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          <ResetPasswordForm token={token} onSuccess={handleSuccess} onGoToLogin={handleGoToLogin} />
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

export default ResetPassword;
