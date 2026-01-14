/**
 * Authentication types for better-auth integration.
 */

/**
 * Authenticated user from better-auth
 */
export interface AuthUser {
  id: string;
  email: string;
  emailVerified: boolean;
  name: string | null;
  image: string | null;
  createdAt: string;
  updatedAt: string;
}

/**
 * Session from better-auth
 */
export interface AuthSession {
  id: string;
  userId: string;
  expiresAt: string;
  ipAddress: string | null;
  userAgent: string | null;
}

/**
 * Combined session response
 */
export interface SessionResponse {
  user: AuthUser | null;
  session: AuthSession | null;
}

/**
 * User profile for personalization (FR-007, FR-008, FR-009)
 */
export interface UserProfile {
  id: string;
  userId: string;
  softwareBackground: SoftwareOption[];
  hardwareAccess: HardwareOption[];
  experienceLevel: ExperienceLevel | null;
  profileCompleted: boolean;
  completedAt: string | null;
  needsReminder: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * Software background options (FR-007)
 */
export type SoftwareOption =
  | 'python'
  | 'cpp'
  | 'javascript_typescript'
  | 'ros_ros2'
  | 'matlab'
  | 'none_learning';

/**
 * Hardware access options (FR-008)
 */
export type HardwareOption =
  | 'simulation_only'
  | 'arduino_microcontrollers'
  | 'raspberry_pi'
  | 'nvidia_jetson'
  | 'robot_arm'
  | 'humanoid_robot'
  | 'drone_uav'
  | 'custom_other';

/**
 * Experience level options (FR-009)
 */
export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced';

/**
 * Profile option with label and description for UI
 */
export interface ProfileOptionInfo {
  value: string;
  label: string;
  description: string;
}

/**
 * All profile options for the wizard
 */
export interface ProfileOptions {
  softwareBackground: ProfileOptionInfo[];
  hardwareAccess: ProfileOptionInfo[];
  experienceLevel: ProfileOptionInfo[];
}

/**
 * Profile completion request
 */
export interface ProfileCompleteRequest {
  softwareBackground: SoftwareOption[];
  hardwareAccess: HardwareOption[];
  experienceLevel: ExperienceLevel;
}

/**
 * Profile update request (partial)
 */
export interface ProfileUpdateRequest {
  softwareBackground?: SoftwareOption[];
  hardwareAccess?: HardwareOption[];
  experienceLevel?: ExperienceLevel;
}

/**
 * Auth error response
 */
export interface AuthError {
  error: {
    message: string;
    code: string;
  };
}

/**
 * Auth state for context
 */
export interface AuthState {
  user: AuthUser | null;
  session: AuthSession | null;
  profile: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  profileComplete: boolean;
}
