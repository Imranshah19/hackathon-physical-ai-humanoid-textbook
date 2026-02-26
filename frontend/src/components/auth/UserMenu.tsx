/**
 * User menu component with profile and logout options (T058).
 *
 * Dropdown menu for authenticated users.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { signOutUser } from '../../hooks/useAuth';

interface UserMenuProps {
  /** URL to profile settings page */
  profileUrl?: string;
  /** Callback after logout */
  onLogout?: () => void;
}

export const UserMenu: React.FC<UserMenuProps> = ({
  profileUrl = '/profile',
  onLogout,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { user, profile, clearAuth } = useAuth();

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close menu on escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen]);

  const handleToggle = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const handleLogout = useCallback(async () => {
    setIsLoggingOut(true);
    try {
      await signOutUser();
      clearAuth();
      onLogout?.();
      // Redirect to home
      window.location.href = '/';
    } catch (error) {
      console.error('Logout failed:', error);
      setIsLoggingOut(false);
    }
  }, [clearAuth, onLogout]);

  const handleProfileClick = useCallback(() => {
    setIsOpen(false);
    window.location.href = profileUrl;
  }, [profileUrl]);

  if (!user) {
    return null;
  }

  // Get initials for avatar
  const initials = user.name
    ? user.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : user.email[0].toUpperCase();

  return (
    <div className="user-menu" ref={menuRef}>
      <button
        type="button"
        className="user-menu-trigger"
        onClick={handleToggle}
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="User menu"
      >
        {user.image ? (
          <img src={user.image} alt="" className="user-menu-avatar" />
        ) : (
          <div className="user-menu-avatar user-menu-avatar-initials">{initials}</div>
        )}
        <span className="user-menu-name">{user.name || user.email}</span>
        <svg
          className={`user-menu-chevron ${isOpen ? 'user-menu-chevron-open' : ''}`}
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M7 10l5 5 5-5z" />
        </svg>
      </button>

      {isOpen && (
        <div className="user-menu-dropdown" role="menu">
          <div className="user-menu-header">
            <p className="user-menu-email">{user.email}</p>
            {profile && !profile.profileCompleted && (
              <span className="user-menu-badge">Profile incomplete</span>
            )}
          </div>

          <div className="user-menu-items">
            <button
              type="button"
              className="user-menu-item"
              onClick={handleProfileClick}
              role="menuitem"
            >
              <svg
                viewBox="0 0 24 24"
                width="18"
                height="18"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
              <span>Profile Settings</span>
            </button>

            <div className="user-menu-divider" />

            <button
              type="button"
              className="user-menu-item user-menu-item-danger"
              onClick={handleLogout}
              disabled={isLoggingOut}
              role="menuitem"
            >
              <svg
                viewBox="0 0 24 24"
                width="18"
                height="18"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" />
              </svg>
              <span>{isLoggingOut ? 'Signing out...' : 'Sign Out'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
