/**
 * Profile editor component for updating user profile settings (T064).
 *
 * Allows users to modify their software background, hardware access, and experience level.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import type {
  ProfileOptions,
  ProfileOptionInfo,
  SoftwareOption,
  HardwareOption,
  ExperienceLevel,
  UserProfile,
} from '../../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProfileEditorProps {
  /** Callback when profile is saved successfully */
  onSave?: () => void;
  /** Callback when user cancels editing */
  onCancel?: () => void;
}

type EditSection = 'software' | 'hardware' | 'experience' | null;

export const ProfileEditor: React.FC<ProfileEditorProps> = ({ onSave, onCancel }) => {
  const { profile, refreshProfile } = useAuth();
  const [options, setOptions] = useState<ProfileOptions | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [editingSection, setEditingSection] = useState<EditSection>(null);

  // Local state for editing
  const [softwareBackground, setSoftwareBackground] = useState<SoftwareOption[]>([]);
  const [hardwareAccess, setHardwareAccess] = useState<HardwareOption[]>([]);
  const [experienceLevel, setExperienceLevel] = useState<ExperienceLevel | null>(null);

  // Initialize from profile
  useEffect(() => {
    if (profile) {
      setSoftwareBackground(profile.softwareBackground || []);
      setHardwareAccess(profile.hardwareAccess || []);
      setExperienceLevel(profile.experienceLevel || null);
    }
  }, [profile]);

  // Fetch options on mount
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/profile/options`);
        if (response.ok) {
          const data = await response.json();
          setOptions({
            softwareBackground: data.software_background,
            hardwareAccess: data.hardware_access,
            experienceLevel: data.experience_level,
          });
        }
      } catch (err) {
        console.error('Failed to fetch profile options:', err);
        setError('Failed to load options');
      } finally {
        setIsLoading(false);
      }
    };

    fetchOptions();
  }, []);

  const handleSaveSection = useCallback(
    async (section: EditSection) => {
      if (!section) return;

      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);

      const updateData: Record<string, unknown> = {};
      if (section === 'software') {
        updateData.software_background = softwareBackground;
      } else if (section === 'hardware') {
        updateData.hardware_access = hardwareAccess;
      } else if (section === 'experience') {
        updateData.experience_level = experienceLevel;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/profile`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(updateData),
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to update profile');
        }

        await refreshProfile();
        setEditingSection(null);
        setSuccessMessage('Profile updated successfully');
        onSave?.();

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to save');
      } finally {
        setIsSaving(false);
      }
    },
    [softwareBackground, hardwareAccess, experienceLevel, refreshProfile, onSave]
  );

  const handleCancelEdit = useCallback(() => {
    // Reset to profile values
    if (profile) {
      setSoftwareBackground(profile.softwareBackground || []);
      setHardwareAccess(profile.hardwareAccess || []);
      setExperienceLevel(profile.experienceLevel || null);
    }
    setEditingSection(null);
    setError(null);
  }, [profile]);

  const toggleSoftware = (value: SoftwareOption) => {
    setSoftwareBackground((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const toggleHardware = (value: HardwareOption) => {
    setHardwareAccess((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  };

  const getOptionLabel = (
    optionsList: ProfileOptionInfo[],
    value: string
  ): string => {
    return optionsList.find((o) => o.value === value)?.label || value;
  };

  if (isLoading) {
    return (
      <div className="profile-editor-loading">
        <div className="profile-spinner" />
        <p>Loading profile...</p>
      </div>
    );
  }

  if (!options) {
    return (
      <div className="profile-editor-error">
        <p>Failed to load profile options.</p>
        <button onClick={() => window.location.reload()} className="profile-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="profile-editor">
      {error && <div className="profile-error">{error}</div>}
      {successMessage && <div className="profile-success">{successMessage}</div>}

      {/* Software Background Section */}
      <div className="profile-section">
        <div className="profile-section-header">
          <h3 className="profile-section-title">Software Background</h3>
          {editingSection !== 'software' && (
            <button
              className="profile-edit-btn"
              onClick={() => setEditingSection('software')}
            >
              Edit
            </button>
          )}
        </div>

        {editingSection === 'software' ? (
          <div className="profile-section-edit">
            <div className="profile-options-grid">
              {options.softwareBackground.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`profile-option ${
                    softwareBackground.includes(option.value as SoftwareOption)
                      ? 'profile-option-selected'
                      : ''
                  }`}
                  onClick={() => toggleSoftware(option.value as SoftwareOption)}
                >
                  <span className="profile-option-label">{option.label}</span>
                </button>
              ))}
            </div>
            <div className="profile-section-actions">
              <button
                className="profile-btn profile-btn-secondary"
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                className="profile-btn profile-btn-primary"
                onClick={() => handleSaveSection('software')}
                disabled={isSaving || softwareBackground.length === 0}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ) : (
          <div className="profile-section-display">
            {softwareBackground.length > 0 ? (
              <div className="profile-tags">
                {softwareBackground.map((value) => (
                  <span key={value} className="profile-tag">
                    {getOptionLabel(options.softwareBackground, value)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="profile-empty">No software background selected</p>
            )}
          </div>
        )}
      </div>

      {/* Hardware Access Section */}
      <div className="profile-section">
        <div className="profile-section-header">
          <h3 className="profile-section-title">Hardware Access</h3>
          {editingSection !== 'hardware' && (
            <button
              className="profile-edit-btn"
              onClick={() => setEditingSection('hardware')}
            >
              Edit
            </button>
          )}
        </div>

        {editingSection === 'hardware' ? (
          <div className="profile-section-edit">
            <div className="profile-options-grid">
              {options.hardwareAccess.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`profile-option ${
                    hardwareAccess.includes(option.value as HardwareOption)
                      ? 'profile-option-selected'
                      : ''
                  }`}
                  onClick={() => toggleHardware(option.value as HardwareOption)}
                >
                  <span className="profile-option-label">{option.label}</span>
                </button>
              ))}
            </div>
            <div className="profile-section-actions">
              <button
                className="profile-btn profile-btn-secondary"
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                className="profile-btn profile-btn-primary"
                onClick={() => handleSaveSection('hardware')}
                disabled={isSaving || hardwareAccess.length === 0}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ) : (
          <div className="profile-section-display">
            {hardwareAccess.length > 0 ? (
              <div className="profile-tags">
                {hardwareAccess.map((value) => (
                  <span key={value} className="profile-tag">
                    {getOptionLabel(options.hardwareAccess, value)}
                  </span>
                ))}
              </div>
            ) : (
              <p className="profile-empty">No hardware access selected</p>
            )}
          </div>
        )}
      </div>

      {/* Experience Level Section */}
      <div className="profile-section">
        <div className="profile-section-header">
          <h3 className="profile-section-title">Experience Level</h3>
          {editingSection !== 'experience' && (
            <button
              className="profile-edit-btn"
              onClick={() => setEditingSection('experience')}
            >
              Edit
            </button>
          )}
        </div>

        {editingSection === 'experience' ? (
          <div className="profile-section-edit">
            <div className="profile-options-list">
              {options.experienceLevel.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`profile-option profile-option-full ${
                    experienceLevel === option.value ? 'profile-option-selected' : ''
                  }`}
                  onClick={() => setExperienceLevel(option.value as ExperienceLevel)}
                >
                  <span className="profile-option-label">{option.label}</span>
                  <span className="profile-option-desc">{option.description}</span>
                </button>
              ))}
            </div>
            <div className="profile-section-actions">
              <button
                className="profile-btn profile-btn-secondary"
                onClick={handleCancelEdit}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                className="profile-btn profile-btn-primary"
                onClick={() => handleSaveSection('experience')}
                disabled={isSaving || !experienceLevel}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        ) : (
          <div className="profile-section-display">
            {experienceLevel ? (
              <span className="profile-experience-badge">
                {getOptionLabel(options.experienceLevel, experienceLevel)}
              </span>
            ) : (
              <p className="profile-empty">No experience level selected</p>
            )}
          </div>
        )}
      </div>

      {onCancel && (
        <div className="profile-editor-footer">
          <button className="profile-btn profile-btn-secondary" onClick={onCancel}>
            Close
          </button>
        </div>
      )}
    </div>
  );
};

export default ProfileEditor;
