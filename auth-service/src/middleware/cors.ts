import { cors } from 'hono/cors';

/**
 * CORS configuration for auth service
 * Allows frontend origins to make authenticated requests
 */
export function createCorsMiddleware() {
  const corsOrigins = process.env.CORS_ORIGINS?.split(',').map((o) => o.trim()) || [
    'http://localhost:3000',
    'http://localhost:5173',
  ];

  return cors({
    origin: (origin) => {
      // Allow requests from configured origins
      if (!origin) return corsOrigins[0]; // Default for non-browser requests
      if (corsOrigins.includes(origin)) return origin;
      return null; // Reject unknown origins
    },
    credentials: true,
    allowMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowHeaders: [
      'Content-Type',
      'Authorization',
      'X-Requested-With',
      'Accept',
      'Origin',
    ],
    exposeHeaders: ['Set-Cookie'],
    maxAge: 86400, // 24 hours preflight cache
  });
}

/**
 * Get allowed origins for validation
 */
export function getAllowedOrigins(): string[] {
  return process.env.CORS_ORIGINS?.split(',').map((o) => o.trim()) || [
    'http://localhost:3000',
    'http://localhost:5173',
  ];
}
