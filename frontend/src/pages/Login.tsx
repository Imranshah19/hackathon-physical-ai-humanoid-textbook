/**
 * Login page integrating LoginForm and SocialLoginButtons (T056).
 *
 * Handles the complete login flow with social auth options.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { SocialLoginButtons } from '../components/auth/SocialLoginButtons';
import { useAuth } from '../context/AuthContext';

export const Login: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated, isLoading } = useAuth();

  // Get redirect URL from query params
  const getRedirectUrl = useCallback(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get('redirect') || '/';
  }, []);

  // Redirect if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      window.location.href = getRedirectUrl();
    }
  }, [isAuthenticated, isLoading, getRedirectUrl]);

  const handleLoginSuccess = useCallback(() => {
    window.location.href = getRedirectUrl();
  }, [getRedirectUrl]);

  const handleSwitchToRegister = useCallback(() => {
    const redirect = getRedirectUrl();
    window.location.href = `/register${redirect !== '/' ? `?redirect=${encodeURIComponent(redirect)}` : ''}`;
  }, [getRedirectUrl]);

  const handleForgotPassword = useCallback(() => {
    window.location.href = '/forgot-password';
  }, []);

  const handleSocialError = useCallback((errorMessage: string) => {
    setError(errorMessage);
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

  // Don't render login form if authenticated (will redirect)
  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-card">
          {error && (
            <div className="auth-error auth-error-general">
              {error}
              <button
                type="button"
                className="auth-error-dismiss"
                onClick={() => setError(null)}
                aria-label="Dismiss error"
              >
                ×
              </button>
            </div>
          )}

          <LoginForm
            onSuccess={handleLoginSuccess}
            onSwitchToRegister={handleSwitchToRegister}
            onForgotPassword={handleForgotPassword}
          />

          <SocialLoginButtons label="Or continue with" onError={handleSocialError} />
        </div>

        <div className="auth-footer">
          <p className="auth-footer-text">
            By signing in, you agree to our{' '}
            <a href="/terms" className="auth-footer-link">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="auth-footer-link">
              Privacy Policy
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
