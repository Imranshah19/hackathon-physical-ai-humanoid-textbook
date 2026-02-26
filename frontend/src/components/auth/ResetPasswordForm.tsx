/**
 * Reset password form component (T071).
 *
 * Allows users to set a new password using a reset token.
 */

import React, { useState, useCallback } from 'react';
import { resetPassword } from '../../hooks/useAuth';

interface ResetPasswordFormProps {
  /** The reset token from the URL */
  token: string;
  /** Callback when password reset is successful */
  onSuccess?: () => void;
  /** Callback when user wants to go to login */
  onGoToLogin?: () => void;
}

interface FormErrors {
  password?: string;
  confirmPassword?: string;
  general?: string;
}

export const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({
  token,
  onSuccess,
  onGoToLogin,
}) => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(password)) {
      newErrors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[a-z]/.test(password)) {
      newErrors.password = 'Password must contain at least one lowercase letter';
    } else if (!/[0-9]/.test(password)) {
      newErrors.password = 'Password must contain at least one number';
    }

    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [password, confirmPassword]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) {
        return;
      }

      setIsLoading(true);
      setErrors({});

      const result = await resetPassword(token, password);

      if ('error' in result) {
        // Map common errors to user-friendly messages
        let errorMessage = result.error;
        if (result.error.toLowerCase().includes('expired')) {
          errorMessage = 'This reset link has expired. Please request a new one.';
        } else if (result.error.toLowerCase().includes('invalid')) {
          errorMessage = 'This reset link is invalid. Please request a new one.';
        } else if (result.error.toLowerCase().includes('already used')) {
          errorMessage = 'This reset link has already been used. Please request a new one.';
        }
        setErrors({ general: errorMessage });
        setIsLoading(false);
        return;
      }

      setIsSuccess(true);
      setIsLoading(false);
      onSuccess?.();
    },
    [token, password, validateForm, onSuccess]
  );

  if (isSuccess) {
    return (
      <div className="auth-reset-form">
        <div className="auth-success-icon">✓</div>
        <h2 className="auth-form-title">Password Reset!</h2>
        <p className="auth-form-subtitle">
          Your password has been successfully reset. You can now sign in with your new password.
        </p>
        <button type="button" className="auth-btn auth-btn-primary" onClick={onGoToLogin}>
          Sign In
        </button>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="auth-reset-form">
        <div className="auth-error-icon">!</div>
        <h2 className="auth-form-title">Invalid Link</h2>
        <p className="auth-form-subtitle">
          This password reset link is missing or invalid. Please request a new one.
        </p>
        <button
          type="button"
          className="auth-btn auth-btn-primary"
          onClick={() => (window.location.href = '/forgot-password')}
        >
          Request New Link
        </button>
      </div>
    );
  }

  return (
    <div className="auth-reset-form">
      <h2 className="auth-form-title">Set New Password</h2>
      <p className="auth-form-subtitle">
        Enter your new password below. It must be at least 8 characters with mixed case and a
        number.
      </p>

      <form onSubmit={handleSubmit} className="auth-form">
        {errors.general && <div className="auth-error auth-error-general">{errors.general}</div>}

        <div className="auth-field">
          <label htmlFor="reset-password" className="auth-label">
            New Password
          </label>
          <input
            id="reset-password"
            type="password"
            className={`auth-input ${errors.password ? 'auth-input-error' : ''}`}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter new password"
            disabled={isLoading}
            autoComplete="new-password"
            autoFocus
          />
          {errors.password && <span className="auth-field-error">{errors.password}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="reset-confirm-password" className="auth-label">
            Confirm Password
          </label>
          <input
            id="reset-confirm-password"
            type="password"
            className={`auth-input ${errors.confirmPassword ? 'auth-input-error' : ''}`}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
            disabled={isLoading}
            autoComplete="new-password"
          />
          {errors.confirmPassword && (
            <span className="auth-field-error">{errors.confirmPassword}</span>
          )}
        </div>

        <div className="auth-password-requirements">
          <p className="auth-requirements-title">Password must contain:</p>
          <ul className="auth-requirements-list">
            <li className={password.length >= 8 ? 'auth-req-met' : ''}>At least 8 characters</li>
            <li className={/[A-Z]/.test(password) ? 'auth-req-met' : ''}>
              One uppercase letter (A-Z)
            </li>
            <li className={/[a-z]/.test(password) ? 'auth-req-met' : ''}>
              One lowercase letter (a-z)
            </li>
            <li className={/[0-9]/.test(password) ? 'auth-req-met' : ''}>One number (0-9)</li>
          </ul>
        </div>

        <button type="submit" className="auth-btn auth-btn-primary" disabled={isLoading}>
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
    </div>
  );
};

export default ResetPasswordForm;
