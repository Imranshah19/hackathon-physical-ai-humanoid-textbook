import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { secureHeaders } from 'hono/secure-headers';
import { auth } from './auth';
import { rateLimitMiddleware } from './middleware/rateLimit';
import 'dotenv/config';

const app = new Hono();

// Security headers middleware (T077)
app.use(
  '*',
  secureHeaders({
    // Content Security Policy
    contentSecurityPolicy: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", 'data:', 'https:'],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      frameAncestors: ["'self'"],
    },
    // Prevent clickjacking
    xFrameOptions: 'DENY',
    // Prevent MIME type sniffing
    xContentTypeOptions: 'nosniff',
    // Referrer policy
    referrerPolicy: 'strict-origin-when-cross-origin',
    // Permissions policy (disable unnecessary APIs)
    permissionsPolicy: {
      camera: [],
      microphone: [],
      geolocation: [],
    },
  })
);

// HTTPS redirect in production (T077)
app.use('*', async (c, next) => {
  if (process.env.NODE_ENV === 'production') {
    const proto = c.req.header('x-forwarded-proto');
    if (proto && proto !== 'https') {
      const url = new URL(c.req.url);
      url.protocol = 'https:';
      return c.redirect(url.toString(), 301);
    }
  }
  await next();
});

// Request logging
app.use('*', logger());

// Rate limiting for auth endpoints (T053, T076)
app.use('/api/auth/*', rateLimitMiddleware);

// CORS configuration
const corsOrigins = process.env.CORS_ORIGINS?.split(',') || [
  'http://localhost:3000',
  'http://localhost:5173',
];

app.use(
  '*',
  cors({
    origin: corsOrigins,
    credentials: true,
    allowMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowHeaders: ['Content-Type', 'Authorization'],
    exposeHeaders: ['Set-Cookie'],
  })
);

// Health check endpoint
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    service: 'auth-service',
    timestamp: new Date().toISOString(),
  });
});

// Mount better-auth handler on /api/auth/*
app.on(['GET', 'POST'], '/api/auth/**', (c) => {
  return auth.handler(c.req.raw);
});

// Start server
const port = parseInt(process.env.PORT || '3001', 10);

console.log(`Auth service starting on port ${port}...`);

serve({
  fetch: app.fetch,
  port,
});

console.log(`Auth service running at http://localhost:${port}`);
console.log(`Auth endpoints available at http://localhost:${port}/api/auth/*`);
