/**
 * Login form component for returning users (T054).
 *
 * Handles email/password login with validation.
 */

import React, { useState, useCallback } from 'react';
import { signInWithEmail } from '../../hooks/useAuth';

interface LoginFormProps {
  /** Callback when login is successful */
  onSuccess?: () => void;
  /** Callback when user wants to switch to registration */
  onSwitchToRegister?: () => void;
  /** Callback when user clicks forgot password */
  onForgotPassword?: () => void;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
  onForgotPassword,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [email, password]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) {
        return;
      }

      setIsLoading(true);
      setErrors({});

      const result = await signInWithEmail(email, password);

      if ('error' in result) {
        // Map common errors to user-friendly messages
        let errorMessage = result.error;
        if (result.error.toLowerCase().includes('invalid')) {
          errorMessage = 'Invalid email or password';
        } else if (result.error.toLowerCase().includes('not found')) {
          errorMessage = 'No account found with this email';
        } else if (result.error.toLowerCase().includes('rate limit')) {
          errorMessage = 'Too many attempts. Please try again later.';
        }
        setErrors({ general: errorMessage });
        setIsLoading(false);
        return;
      }

      setIsLoading(false);
      onSuccess?.();
    },
    [email, password, validateForm, onSuccess]
  );

  return (
    <div className="auth-login-form">
      <h2 className="auth-form-title">Welcome Back</h2>
      <p className="auth-form-subtitle">Sign in to continue your learning journey</p>

      <form onSubmit={handleSubmit} className="auth-form">
        {errors.general && <div className="auth-error auth-error-general">{errors.general}</div>}

        <div className="auth-field">
          <label htmlFor="login-email" className="auth-label">
            Email
          </label>
          <input
            id="login-email"
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

        <div className="auth-field">
          <div className="auth-label-row">
            <label htmlFor="login-password" className="auth-label">
              Password
            </label>
            {onForgotPassword && (
              <button
                type="button"
                className="auth-link auth-forgot-link"
                onClick={onForgotPassword}
              >
                Forgot password?
              </button>
            )}
          </div>
          <input
            id="login-password"
            type="password"
            className={`auth-input ${errors.password ? 'auth-input-error' : ''}`}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            disabled={isLoading}
            autoComplete="current-password"
          />
          {errors.password && <span className="auth-field-error">{errors.password}</span>}
        </div>

        <button type="submit" className="auth-btn auth-btn-primary" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>

      <div className="auth-form-footer">
        <span>Don't have an account?</span>
        <button type="button" className="auth-link" onClick={onSwitchToRegister}>
          Create one
        </button>
      </div>
    </div>
  );
};

export default LoginForm;
