/**
 * Profile completion reminder banner.
 *
 * Shown when user has incomplete profile (FR-010).
 */

import React, { useState, useCallback } from 'react';
import { useAuth, useNeedsProfileCompletion } from '../../../../frontend/src/context/AuthContext';

interface ProfileBannerProps {
  /** URL to profile completion page */
  profileUrl?: string;
  /** Custom message to display */
  message?: string;
}

export const ProfileBanner: React.FC<ProfileBannerProps> = ({
  profileUrl = '/register?step=profile',
  message = 'Complete your profile to get personalized content recommendations.',
}) => {
  const [isDismissed, setIsDismissed] = useState(false);
  const needsProfileCompletion = useNeedsProfileCompletion();
  const { refreshProfile } = useAuth();

  const handleDismiss = useCallback(async () => {
    setIsDismissed(true);
    // Call skip endpoint to record dismissal
    const API_BASE_URL = import.meta.env?.VITE_API_URL || 'http://localhost:8000';
    try {
      await fetch(`${API_BASE_URL}/api/profile/skip`, {
        method: 'POST',
        credentials: 'include',
      });
      await refreshProfile();
    } catch (error) {
      // Dismiss locally even if API call fails
      console.error('Failed to record profile skip:', error);
    }
  }, [refreshProfile]);

  const handleComplete = useCallback(() => {
    window.location.href = profileUrl;
  }, [profileUrl]);

  // Don't show if profile is complete, dismissed, or reminder not needed
  if (!needsProfileCompletion || isDismissed) {
    return null;
  }

  return (
    <div className="profile-banner" role="alert">
      <div className="profile-banner-content">
        <div className="profile-banner-icon">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
          </svg>
        </div>
        <p className="profile-banner-message">{message}</p>
        <div className="profile-banner-actions">
          <button
            type="button"
            className="profile-banner-btn profile-banner-btn-primary"
            onClick={handleComplete}
          >
            Complete Profile
          </button>
          <button
            type="button"
            className="profile-banner-btn profile-banner-btn-dismiss"
            onClick={handleDismiss}
            aria-label="Dismiss"
          >
            Remind me later
          </button>
        </div>
      </div>
      <button
        type="button"
        className="profile-banner-close"
        onClick={handleDismiss}
        aria-label="Close banner"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
        </svg>
      </button>
    </div>
  );
};

export default ProfileBanner;
