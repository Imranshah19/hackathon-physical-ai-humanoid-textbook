/**
 * Frontend configuration (T079)
 *
 * Centralizes environment configuration for the frontend application.
 */

interface AppConfig {
  // API endpoints
  authServiceUrl: string;
  backendApiUrl: string;

  // Feature flags
  enableAnalytics: boolean;
  enableDebugMode: boolean;

  // Environment
  environment: 'development' | 'staging' | 'production';
  isDevelopment: boolean;
  isProduction: boolean;
}

// Get environment variables with fallbacks
const getEnvVar = (key: string, defaultValue: string): string => {
  // Vite uses import.meta.env
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return (import.meta.env[key] as string) || defaultValue;
  }
  // Fallback for other environments
  return defaultValue;
};

const environment = getEnvVar('VITE_ENVIRONMENT', 'development') as AppConfig['environment'];

export const config: AppConfig = {
  // API endpoints
  authServiceUrl: getEnvVar('VITE_AUTH_URL', 'http://localhost:3001'),
  backendApiUrl: getEnvVar('VITE_API_URL', 'http://localhost:8000'),

  // Feature flags
  enableAnalytics: getEnvVar('VITE_ENABLE_ANALYTICS', 'false') === 'true',
  enableDebugMode: getEnvVar('VITE_DEBUG', 'false') === 'true',

  // Environment
  environment,
  isDevelopment: environment === 'development',
  isProduction: environment === 'production',
};

// API URL helpers
export const apiUrl = (path: string): string => {
  const base = config.backendApiUrl.replace(/\/$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${cleanPath}`;
};

export const authUrl = (path: string): string => {
  const base = config.authServiceUrl.replace(/\/$/, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${cleanPath}`;
};

export default config;
