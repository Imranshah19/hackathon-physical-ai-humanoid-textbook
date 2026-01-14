/**
 * Rate limiting middleware for auth endpoints (T053).
 *
 * Protects against brute-force attacks on login/registration.
 */

import type { Context, Next } from 'hono';

interface RateLimitEntry {
  count: number;
  resetAt: number;
}

// In-memory store (use Redis in production)
const rateLimitStore = new Map<string, RateLimitEntry>();

// Configuration
const RATE_LIMITS = {
  // Login: 5 attempts per minute
  login: { maxRequests: 5, windowMs: 60 * 1000 },
  // Registration: 3 attempts per minute
  register: { maxRequests: 3, windowMs: 60 * 1000 },
  // Password reset: 3 attempts per hour
  passwordReset: { maxRequests: 3, windowMs: 60 * 60 * 1000 },
  // Default: 100 requests per minute
  default: { maxRequests: 100, windowMs: 60 * 1000 },
};

type RateLimitType = keyof typeof RATE_LIMITS;

/**
 * Get client identifier from request
 */
function getClientId(c: Context): string {
  // Prefer X-Forwarded-For for proxied requests
  const forwarded = c.req.header('x-forwarded-for');
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  // Fall back to direct IP
  return c.req.header('x-real-ip') || 'unknown';
}

/**
 * Determine rate limit type from request path
 */
function getRateLimitType(path: string): RateLimitType {
  if (path.includes('/sign-in') || path.includes('/login')) {
    return 'login';
  }
  if (path.includes('/sign-up') || path.includes('/register')) {
    return 'register';
  }
  if (path.includes('/forget-password') || path.includes('/reset-password')) {
    return 'passwordReset';
  }
  return 'default';
}

/**
 * Clean up expired entries periodically
 */
function cleanupExpired() {
  const now = Date.now();
  for (const [key, entry] of rateLimitStore.entries()) {
    if (entry.resetAt < now) {
      rateLimitStore.delete(key);
    }
  }
}

// Run cleanup every minute
setInterval(cleanupExpired, 60 * 1000);

/**
 * Rate limiting middleware
 */
export async function rateLimitMiddleware(c: Context, next: Next) {
  const clientId = getClientId(c);
  const path = c.req.path;
  const limitType = getRateLimitType(path);
  const { maxRequests, windowMs } = RATE_LIMITS[limitType];

  const key = `${clientId}:${limitType}`;
  const now = Date.now();

  let entry = rateLimitStore.get(key);

  // Create new entry if doesn't exist or window expired
  if (!entry || entry.resetAt < now) {
    entry = {
      count: 0,
      resetAt: now + windowMs,
    };
  }

  entry.count++;
  rateLimitStore.set(key, entry);

  // Calculate remaining time and requests
  const remaining = Math.max(0, maxRequests - entry.count);
  const resetIn = Math.ceil((entry.resetAt - now) / 1000);

  // Set rate limit headers
  c.header('X-RateLimit-Limit', String(maxRequests));
  c.header('X-RateLimit-Remaining', String(remaining));
  c.header('X-RateLimit-Reset', String(resetIn));

  // Check if rate limited
  if (entry.count > maxRequests) {
    c.header('Retry-After', String(resetIn));
    return c.json(
      {
        error: 'Too many requests',
        message: `Rate limit exceeded. Try again in ${resetIn} seconds.`,
        retryAfter: resetIn,
      },
      429
    );
  }

  await next();
}

/**
 * Create rate limiter for specific endpoint type
 */
export function createRateLimiter(type: RateLimitType) {
  return async (c: Context, next: Next) => {
    const clientId = getClientId(c);
    const { maxRequests, windowMs } = RATE_LIMITS[type];

    const key = `${clientId}:${type}`;
    const now = Date.now();

    let entry = rateLimitStore.get(key);

    if (!entry || entry.resetAt < now) {
      entry = { count: 0, resetAt: now + windowMs };
    }

    entry.count++;
    rateLimitStore.set(key, entry);

    const remaining = Math.max(0, maxRequests - entry.count);
    const resetIn = Math.ceil((entry.resetAt - now) / 1000);

    c.header('X-RateLimit-Limit', String(maxRequests));
    c.header('X-RateLimit-Remaining', String(remaining));
    c.header('X-RateLimit-Reset', String(resetIn));

    if (entry.count > maxRequests) {
      c.header('Retry-After', String(resetIn));
      return c.json(
        {
          error: 'Too many requests',
          message: `Rate limit exceeded. Try again in ${resetIn} seconds.`,
          retryAfter: resetIn,
        },
        429
      );
    }

    await next();
  };
}

export default rateLimitMiddleware;
