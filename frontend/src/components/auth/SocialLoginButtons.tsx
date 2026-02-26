/**
 * Social login buttons component (T055).
 *
 * Provides Google and GitHub OAuth login options.
 */

import React, { useState, useCallback } from 'react';
import { signInWithSocial } from '../../hooks/useAuth';

interface SocialLoginButtonsProps {
  /** Text to show before buttons (e.g., "Or continue with") */
  label?: string;
  /** Disable buttons during loading */
  disabled?: boolean;
  /** Callback when login starts */
  onLoginStart?: () => void;
  /** Callback on error */
  onError?: (error: string) => void;
}

type Provider = 'google' | 'github';

export const SocialLoginButtons: React.FC<SocialLoginButtonsProps> = ({
  label = 'Or continue with',
  disabled = false,
  onLoginStart,
  onError,
}) => {
  const [loadingProvider, setLoadingProvider] = useState<Provider | null>(null);

  const handleSocialLogin = useCallback(
    async (provider: Provider) => {
      if (disabled || loadingProvider) return;

      setLoadingProvider(provider);
      onLoginStart?.();

      try {
        await signInWithSocial(provider);
        // Note: This will redirect to OAuth provider, so we won't reach here
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Social login failed';
        onError?.(message);
        setLoadingProvider(null);
      }
    },
    [disabled, loadingProvider, onLoginStart, onError]
  );

  const isLoading = loadingProvider !== null;

  return (
    <div className="social-login">
      <div className="social-login-divider">
        <span className="social-login-divider-line" />
        <span className="social-login-divider-text">{label}</span>
        <span className="social-login-divider-line" />
      </div>

      <div className="social-login-buttons">
        <button
          type="button"
          className="social-btn social-btn-google"
          onClick={() => handleSocialLogin('google')}
          disabled={disabled || isLoading}
          aria-label="Sign in with Google"
        >
          <svg
            className="social-btn-icon"
            viewBox="0 0 24 24"
            width="20"
            height="20"
            aria-hidden="true"
          >
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span className="social-btn-text">
            {loadingProvider === 'google' ? 'Connecting...' : 'Google'}
          </span>
        </button>

        <button
          type="button"
          className="social-btn social-btn-github"
          onClick={() => handleSocialLogin('github')}
          disabled={disabled || isLoading}
          aria-label="Sign in with GitHub"
        >
          <svg
            className="social-btn-icon"
            viewBox="0 0 24 24"
            width="20"
            height="20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path d="M12 1.27a11 11 0 00-3.48 21.46c.55.09.73-.28.73-.55v-1.84c-3.03.64-3.67-1.46-3.67-1.46-.55-1.29-1.28-1.65-1.28-1.65-.92-.65.1-.65.1-.65 1.1 0 1.73 1.1 1.73 1.1.92 1.65 2.57 1.2 3.21.92a2 2 0 01.64-1.47c-2.47-.27-5.04-1.19-5.04-5.5 0-1.1.46-2.1 1.2-2.84a3.76 3.76 0 010-2.93s.91-.28 3.11 1.1c1.8-.49 3.7-.49 5.5 0 2.1-1.38 3.02-1.1 3.02-1.1a3.76 3.76 0 010 2.93c.83.74 1.2 1.74 1.2 2.94 0 4.21-2.57 5.13-5.04 5.4.45.37.82.92.82 2.02v3.03c0 .27.1.64.73.55A11 11 0 0012 1.27" />
          </svg>
          <span className="social-btn-text">
            {loadingProvider === 'github' ? 'Connecting...' : 'GitHub'}
          </span>
        </button>
      </div>
    </div>
  );
};

export default SocialLoginButtons;
