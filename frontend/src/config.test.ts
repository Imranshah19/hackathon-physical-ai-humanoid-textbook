/**
 * Tests for config.ts — URL helpers and default values.
 *
 * import.meta.env variables are not set in the test environment,
 * so all tests use the default fallback values.
 */

import { describe, it, expect } from 'vitest';
import { config, apiUrl, authUrl } from './config';

// ---------------------------------------------------------------------------
// config defaults
// ---------------------------------------------------------------------------

describe('config defaults', () => {
  it('has a backendApiUrl', () => {
    expect(config.backendApiUrl).toBeTruthy();
    expect(typeof config.backendApiUrl).toBe('string');
  });

  it('has an authServiceUrl', () => {
    expect(config.authServiceUrl).toBeTruthy();
    expect(typeof config.authServiceUrl).toBe('string');
  });

  it('backendApiUrl defaults to localhost:8000', () => {
    expect(config.backendApiUrl).toBe('http://localhost:8000');
  });

  it('authServiceUrl defaults to localhost:3001', () => {
    expect(config.authServiceUrl).toBe('http://localhost:3001');
  });

  it('enableAnalytics defaults to false', () => {
    expect(config.enableAnalytics).toBe(false);
  });

  it('enableDebugMode defaults to false', () => {
    expect(config.enableDebugMode).toBe(false);
  });

  it('environment defaults to development', () => {
    expect(config.environment).toBe('development');
  });

  it('isDevelopment is true in test environment', () => {
    expect(config.isDevelopment).toBe(true);
  });

  it('isProduction is false in test environment', () => {
    expect(config.isProduction).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// apiUrl()
// ---------------------------------------------------------------------------

describe('apiUrl', () => {
  it('prepends the backend base URL', () => {
    const url = apiUrl('/health');
    expect(url).toBe('http://localhost:8000/health');
  });

  it('adds a leading slash when path has none', () => {
    const url = apiUrl('health');
    expect(url).toBe('http://localhost:8000/health');
  });

  it('handles nested paths', () => {
    const url = apiUrl('/api/v1/chat');
    expect(url).toBe('http://localhost:8000/api/v1/chat');
  });

  it('does not double-slash when path starts with /', () => {
    const url = apiUrl('/test');
    expect(url).not.toContain('//test');
  });

  it('strips trailing slash from base URL', () => {
    // The function uses replace(/\/$/, '') so a trailing slash on
    // config.backendApiUrl would not produce a double slash.
    const url = apiUrl('/test');
    expect(url).not.toMatch(/localhost:8000\/\//);
  });

  it('returns a valid URL string', () => {
    const url = apiUrl('/api/v1/health');
    expect(() => new URL(url)).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// authUrl()
// ---------------------------------------------------------------------------

describe('authUrl', () => {
  it('prepends the auth service base URL', () => {
    const url = authUrl('/api/auth/session');
    expect(url).toBe('http://localhost:3001/api/auth/session');
  });

  it('adds a leading slash when path has none', () => {
    const url = authUrl('health');
    expect(url).toBe('http://localhost:3001/health');
  });

  it('handles nested paths', () => {
    const url = authUrl('/api/auth/sign-in/email');
    expect(url).toBe('http://localhost:3001/api/auth/sign-in/email');
  });

  it('does not double-slash', () => {
    const url = authUrl('/test');
    expect(url).not.toContain('//test');
  });

  it('returns a valid URL string', () => {
    const url = authUrl('/health');
    expect(() => new URL(url)).not.toThrow();
  });

  it('is distinct from apiUrl for same path', () => {
    expect(apiUrl('/health')).not.toBe(authUrl('/health'));
  });
});
