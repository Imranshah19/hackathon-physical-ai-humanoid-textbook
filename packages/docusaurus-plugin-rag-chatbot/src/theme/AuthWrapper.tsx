/**
 * Authentication wrapper for Docusaurus pages.
 *
 * Provides auth context and redirects unauthenticated users.
 */

import React from 'react';
import { AuthProvider, useAuth } from '../../../../frontend/src/context/AuthContext';
import { ProfileBanner } from './ProfileBanner';

interface AuthWrapperProps {
  children: React.ReactNode;
  /** Whether authentication is required to view content */
  requireAuth?: boolean;
  /** URL to redirect to if not authenticated */
  loginUrl?: string;
}

/**
 * Inner component that uses auth context
 */
const AuthContent: React.FC<AuthWrapperProps> = ({
  children,
  requireAuth = false,
  loginUrl = '/login',
}) => {
  const { isAuthenticated, isLoading, profileComplete } = useAuth();

  // Show loading state
  if (isLoading) {
    return (
      <div className="auth-loading">
        <div className="auth-spinner" />
      </div>
    );
  }

  // Redirect if auth required but not authenticated
  if (requireAuth && !isAuthenticated) {
    // Use Docusaurus router if available, otherwise window.location
    if (typeof window !== 'undefined') {
      const currentPath = window.location.pathname;
      window.location.href = `${loginUrl}?redirect=${encodeURIComponent(currentPath)}`;
    }
    return null;
  }

  return (
    <>
      {/* Show profile completion banner if needed */}
      {isAuthenticated && !profileComplete && <ProfileBanner />}
      {children}
    </>
  );
};

/**
 * Auth wrapper component for Docusaurus
 *
 * Usage in docusaurus.config.js:
 * ```js
 * themeConfig: {
 *   // wrap entire app
 * }
 * ```
 *
 * Or wrap specific pages:
 * ```jsx
 * <AuthWrapper requireAuth>
 *   <ProtectedContent />
 * </AuthWrapper>
 * ```
 */
export const AuthWrapper: React.FC<AuthWrapperProps> = (props) => {
  return (
    <AuthProvider>
      <AuthContent {...props} />
    </AuthProvider>
  );
};

export default AuthWrapper;
