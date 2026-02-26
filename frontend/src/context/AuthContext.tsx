/**
 * Authentication context provider for the application.
 *
 * Provides auth state and profile data to all components.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useSession } from '../hooks/useAuth';
import type {
  AuthState,
  AuthUser,
  AuthSession,
  UserProfile,
} from '../types/auth';

// API base URL for profile endpoints
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AuthContextValue extends AuthState {
  /** Refresh user profile from API */
  refreshProfile: () => Promise<void>;
  /** Clear local auth state (used on logout) */
  clearAuth: () => void;
  /** Whether initial session check has completed (T059) */
  hasCheckedSession: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { data: sessionData, isPending: isSessionLoading } = useSession();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isProfileLoading, setIsProfileLoading] = useState(false);
  const [hasCheckedSession, setHasCheckedSession] = useState(false);

  // Mark session as checked once initial load completes (T059)
  useEffect(() => {
    if (!isSessionLoading && !hasCheckedSession) {
      setHasCheckedSession(true);
    }
  }, [isSessionLoading, hasCheckedSession]);

  // Fetch user profile when authenticated
  const fetchProfile = useCallback(async () => {
    if (!sessionData?.user) {
      setProfile(null);
      return;
    }

    setIsProfileLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/profile`, {
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else if (response.status === 404) {
        // Profile not found - may not be created yet
        setProfile(null);
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      setProfile(null);
    } finally {
      setIsProfileLoading(false);
    }
  }, [sessionData?.user]);

  // Fetch profile on auth state change
  useEffect(() => {
    if (sessionData?.user) {
      fetchProfile();
    } else {
      setProfile(null);
    }
  }, [sessionData?.user, fetchProfile]);

  const refreshProfile = useCallback(async () => {
    await fetchProfile();
  }, [fetchProfile]);

  const clearAuth = useCallback(() => {
    setProfile(null);
  }, []);

  const value: AuthContextValue = {
    user: (sessionData?.user as AuthUser) ?? null,
    session: (sessionData?.session as AuthSession) ?? null,
    profile,
    isLoading: isSessionLoading || isProfileLoading,
    isAuthenticated: !!sessionData?.user,
    profileComplete: profile?.profileCompleted ?? false,
    refreshProfile,
    clearAuth,
    hasCheckedSession,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to access auth context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Hook to check if profile completion is needed
 */
export function useNeedsProfileCompletion(): boolean {
  const { isAuthenticated, profileComplete, profile } = useAuth();
  return isAuthenticated && !profileComplete && (profile?.needsReminder ?? true);
}

/**
 * Hook to get current user (throws if not authenticated)
 */
export function useRequiredUser(): AuthUser {
  const { user, isAuthenticated } = useAuth();
  if (!isAuthenticated || !user) {
    throw new Error('User is not authenticated');
  }
  return user;
}

export default AuthContext;
