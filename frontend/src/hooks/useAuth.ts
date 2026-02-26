/**
 * Authentication hook using better-auth React client.
 *
 * Provides authentication state and actions for the application.
 */

import { createAuthClient } from 'better-auth/react';
import type { AuthUser, AuthSession } from '../types/auth';

// Create the auth client pointing to auth service
const AUTH_BASE_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:3001';

export const authClient = createAuthClient({
  baseURL: AUTH_BASE_URL,
});

// Re-export hooks from better-auth client
export const {
  useSession,
  signIn,
  signUp,
  signOut,
  // Social login helpers
} = authClient;

/**
 * Hook to get current user if authenticated
 */
export function useUser(): AuthUser | null {
  const { data: session } = useSession();
  return session?.user ?? null;
}

/**
 * Hook to check if user is authenticated
 */
export function useIsAuthenticated(): boolean {
  const { data: session, isPending } = useSession();
  return !isPending && !!session?.user;
}

/**
 * Sign up with email and password
 */
export async function signUpWithEmail(
  email: string,
  password: string,
  name: string
): Promise<{ user: AuthUser; session: AuthSession } | { error: string }> {
  try {
    const result = await signUp.email({
      email,
      password,
      name,
    });
    return result;
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Sign up failed' };
  }
}

/**
 * Sign in with email and password
 */
export async function signInWithEmail(
  email: string,
  password: string
): Promise<{ user: AuthUser; session: AuthSession } | { error: string }> {
  try {
    const result = await signIn.email({
      email,
      password,
    });
    return result;
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Sign in failed' };
  }
}

/**
 * Sign in with social provider
 */
export async function signInWithSocial(
  provider: 'google' | 'github'
): Promise<void> {
  await signIn.social({
    provider,
    callbackURL: window.location.origin,
  });
}

/**
 * Sign out current session
 */
export async function signOutUser(): Promise<void> {
  await signOut();
}

/**
 * Request password reset email
 */
export async function requestPasswordReset(
  email: string
): Promise<{ success: boolean } | { error: string }> {
  try {
    await authClient.forgetPassword({
      email,
      redirectTo: `${window.location.origin}/reset-password`,
    });
    return { success: true };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Request failed' };
  }
}

/**
 * Reset password with token
 */
export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ success: boolean } | { error: string }> {
  try {
    await authClient.resetPassword({
      token,
      newPassword,
    });
    return { success: true };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Reset failed' };
  }
}

/**
 * Revoke all sessions for the current user (T060)
 *
 * Signs out from all devices/browsers.
 */
export async function revokeAllSessions(): Promise<{ success: boolean } | { error: string }> {
  try {
    await authClient.revokeAllSessions();
    return { success: true };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to revoke sessions' };
  }
}

/**
 * Get all active sessions for the current user
 */
export async function listSessions(): Promise<
  { sessions: AuthSession[] } | { error: string }
> {
  try {
    const sessions = await authClient.listSessions();
    return { sessions: sessions as AuthSession[] };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to list sessions' };
  }
}

/**
 * Revoke a specific session by ID
 */
export async function revokeSession(
  sessionId: string
): Promise<{ success: boolean } | { error: string }> {
  try {
    await authClient.revokeSession({ id: sessionId });
    return { success: true };
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Failed to revoke session' };
  }
}
