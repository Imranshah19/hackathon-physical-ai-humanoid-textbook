/**
 * Profile settings page (T065).
 *
 * Displays user profile information and allows editing.
 */

import React, { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { ProfileEditor } from '../components/profile/ProfileEditor';

export const ProfileSettings: React.FC = () => {
  const { user, profile, isLoading, isAuthenticated, hasCheckedSession } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (hasCheckedSession && !isAuthenticated) {
      const currentPath = window.location.pathname;
      window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
    }
  }, [hasCheckedSession, isAuthenticated]);

  if (isLoading || !hasCheckedSession) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="profile-loading">
            <div className="profile-spinner" />
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null; // Will redirect
  }

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar-large">
            {user.image ? (
              <img src={user.image} alt="" className="profile-avatar-img" />
            ) : (
              <div className="profile-avatar-initials">
                {user.name
                  ? user.name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')
                      .toUpperCase()
                      .slice(0, 2)
                  : user.email[0].toUpperCase()}
              </div>
            )}
          </div>
          <div className="profile-header-info">
            <h1 className="profile-name">{user.name || 'User'}</h1>
            <p className="profile-email">{user.email}</p>
            {profile?.profileCompleted ? (
              <span className="profile-status profile-status-complete">
                Profile Complete
              </span>
            ) : (
              <span className="profile-status profile-status-incomplete">
                Profile Incomplete
              </span>
            )}
          </div>
        </div>

        <div className="profile-content">
          <div className="profile-card">
            <h2 className="profile-card-title">Learning Preferences</h2>
            <p className="profile-card-description">
              Your preferences help us personalize chapter content, code examples, and exercises.
            </p>
            <ProfileEditor />
          </div>

          <div className="profile-card">
            <h2 className="profile-card-title">Account Information</h2>
            <div className="profile-info-list">
              <div className="profile-info-item">
                <span className="profile-info-label">Email</span>
                <span className="profile-info-value">{user.email}</span>
              </div>
              <div className="profile-info-item">
                <span className="profile-info-label">Email Verified</span>
                <span className="profile-info-value">
                  {user.emailVerified ? (
                    <span className="profile-verified">✓ Verified</span>
                  ) : (
                    <span className="profile-unverified">Not verified</span>
                  )}
                </span>
              </div>
              <div className="profile-info-item">
                <span className="profile-info-label">Member Since</span>
                <span className="profile-info-value">
                  {new Date(user.createdAt).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>
            </div>
          </div>

          <div className="profile-card profile-card-danger">
            <h2 className="profile-card-title">Security</h2>
            <div className="profile-security-actions">
              <a href="/forgot-password" className="profile-link">
                Change Password
              </a>
              <button
                className="profile-btn profile-btn-danger"
                onClick={() => {
                  if (confirm('Sign out from all devices?')) {
                    // TODO: Call revokeAllSessions
                    alert('Feature coming soon');
                  }
                }}
              >
                Sign Out All Devices
              </button>
            </div>
          </div>
        </div>

        <div className="profile-footer">
          <a href="/" className="profile-back-link">
            ← Back to Textbook
          </a>
        </div>
      </div>
    </div>
  );
};

export default ProfileSettings;
