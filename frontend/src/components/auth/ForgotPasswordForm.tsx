/**
 * Forgot password form component (T070).
 *
 * Allows users to request a password reset email.
 */

import React, { useState, useCallback } from 'react';
import { requestPasswordReset } from '../../hooks/useAuth';

interface ForgotPasswordFormProps {
  /** Callback when reset email is sent successfully */
  onSuccess?: () => void;
  /** Callback when user wants to go back to login */
  onBackToLogin?: () => void;
}

interface FormErrors {
  email?: string;
  general?: string;
}

export const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({
  onSuccess,
  onBackToLogin,
}) => {
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [email]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) {
        return;
      }

      setIsLoading(true);
      setErrors({});

      const result = await requestPasswordReset(email);

      if ('error' in result) {
        // Map common errors to user-friendly messages
        let errorMessage = result.error;
        if (result.error.toLowerCase().includes('rate limit')) {
          errorMessage = 'Too many requests. Please try again later.';
        } else if (result.error.toLowerCase().includes('not found')) {
          // Don't reveal if email exists - show success anyway for security
          setIsSuccess(true);
          setIsLoading(false);
          onSuccess?.();
          return;
        }
        setErrors({ general: errorMessage });
        setIsLoading(false);
        return;
      }

      setIsSuccess(true);
      setIsLoading(false);
      onSuccess?.();
    },
    [email, validateForm, onSuccess]
  );

  if (isSuccess) {
    return (
      <div className="auth-forgot-form">
        <div className="auth-success-icon">✓</div>
        <h2 className="auth-form-title">Check Your Email</h2>
        <p className="auth-form-subtitle">
          If an account exists for <strong>{email}</strong>, we've sent password reset
          instructions. The link will expire in 24 hours.
        </p>
        <p className="auth-form-note">
          Didn't receive the email? Check your spam folder or try again.
        </p>
        <div className="auth-form-actions">
          <button
            type="button"
            className="auth-btn auth-btn-secondary"
            onClick={() => {
              setIsSuccess(false);
              setEmail('');
            }}
          >
            Try Another Email
          </button>
          <button type="button" className="auth-btn auth-btn-primary" onClick={onBackToLogin}>
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-forgot-form">
      <h2 className="auth-form-title">Forgot Password?</h2>
      <p className="auth-form-subtitle">
        Enter your email address and we'll send you a link to reset your password.
      </p>

      <form onSubmit={handleSubmit} className="auth-form">
        {errors.general && <div className="auth-error auth-error-general">{errors.general}</div>}

        <div className="auth-field">
          <label htmlFor="forgot-email" className="auth-label">
            Email Address
          </label>
          <input
            id="forgot-email"
            type="email"
            className={`auth-input ${errors.email ? 'auth-input-error' : ''}`}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            disabled={isLoading}
            autoComplete="email"
            autoFocus
          />
          {errors.email && <span className="auth-field-error">{errors.email}</span>}
        </div>

        <button type="submit" className="auth-btn auth-btn-primary" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>

      <div className="auth-form-footer">
        <button type="button" className="auth-link" onClick={onBackToLogin}>
          ← Back to Login
        </button>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;
