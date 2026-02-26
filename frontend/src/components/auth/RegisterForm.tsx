/**
 * Registration form component for new user signup.
 *
 * Handles email/password registration with validation.
 */

import React, { useState, useCallback } from 'react';
import { signUpWithEmail } from '../../hooks/useAuth';

interface RegisterFormProps {
  /** Callback when registration is successful */
  onSuccess?: () => void;
  /** Callback when user wants to switch to login */
  onSwitchToLogin?: () => void;
}

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  const validateForm = useCallback((): boolean => {
    const newErrors: FormErrors = {};

    // Name validation
    if (!name.trim()) {
      newErrors.name = 'Name is required';
    } else if (name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Email validation
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Password validation (FR-004: min 8 chars, mixed case, number)
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[a-z]/.test(password)) {
      newErrors.password = 'Password must contain a lowercase letter';
    } else if (!/[A-Z]/.test(password)) {
      newErrors.password = 'Password must contain an uppercase letter';
    } else if (!/\d/.test(password)) {
      newErrors.password = 'Password must contain a number';
    }

    // Confirm password
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [name, email, password, confirmPassword]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) {
        return;
      }

      setIsLoading(true);
      setErrors({});

      const result = await signUpWithEmail(email, password, name);

      if ('error' in result) {
        setErrors({ general: result.error });
        setIsLoading(false);
        return;
      }

      setIsLoading(false);
      onSuccess?.();
    },
    [email, password, name, validateForm, onSuccess]
  );

  return (
    <div className="auth-register-form">
      <h2 className="auth-form-title">Create Account</h2>
      <p className="auth-form-subtitle">Join the Physical AI & Humanoid Robotics community</p>

      <form onSubmit={handleSubmit} className="auth-form">
        {errors.general && <div className="auth-error auth-error-general">{errors.general}</div>}

        <div className="auth-field">
          <label htmlFor="register-name" className="auth-label">
            Name
          </label>
          <input
            id="register-name"
            type="text"
            className={`auth-input ${errors.name ? 'auth-input-error' : ''}`}
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            disabled={isLoading}
            autoComplete="name"
          />
          {errors.name && <span className="auth-field-error">{errors.name}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="register-email" className="auth-label">
            Email
          </label>
          <input
            id="register-email"
            type="email"
            className={`auth-input ${errors.email ? 'auth-input-error' : ''}`}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            disabled={isLoading}
            autoComplete="email"
          />
          {errors.email && <span className="auth-field-error">{errors.email}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="register-password" className="auth-label">
            Password
          </label>
          <input
            id="register-password"
            type="password"
            className={`auth-input ${errors.password ? 'auth-input-error' : ''}`}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Min 8 chars, mixed case, 1 number"
            disabled={isLoading}
            autoComplete="new-password"
          />
          {errors.password && <span className="auth-field-error">{errors.password}</span>}
        </div>

        <div className="auth-field">
          <label htmlFor="register-confirm" className="auth-label">
            Confirm Password
          </label>
          <input
            id="register-confirm"
            type="password"
            className={`auth-input ${errors.confirmPassword ? 'auth-input-error' : ''}`}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            disabled={isLoading}
            autoComplete="new-password"
          />
          {errors.confirmPassword && (
            <span className="auth-field-error">{errors.confirmPassword}</span>
          )}
        </div>

        <button type="submit" className="auth-btn auth-btn-primary" disabled={isLoading}>
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>

      <div className="auth-form-footer">
        <span>Already have an account?</span>
        <button type="button" className="auth-link" onClick={onSwitchToLogin}>
          Sign in
        </button>
      </div>
    </div>
  );
};

export default RegisterForm;
