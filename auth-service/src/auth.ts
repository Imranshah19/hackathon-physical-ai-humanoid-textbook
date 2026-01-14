import { betterAuth } from 'better-auth';
import { Pool } from 'pg';

// Database connection pool (shared with backend via same Neon PostgreSQL)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

/**
 * Authentication event logger (T075)
 *
 * Logs authentication events for security monitoring and debugging.
 */
interface AuthEvent {
  type: string;
  userId?: string;
  email?: string;
  ip?: string;
  userAgent?: string;
  success: boolean;
  error?: string;
  timestamp: string;
}

function logAuthEvent(event: AuthEvent): void {
  const logLevel = event.success ? 'INFO' : 'WARN';
  const logEntry = {
    level: logLevel,
    service: 'auth-service',
    ...event,
  };

  // Structured JSON logging for production log aggregation
  if (process.env.NODE_ENV === 'production') {
    console.log(JSON.stringify(logEntry));
  } else {
    // Human-readable format for development
    const status = event.success ? '✓' : '✗';
    const userInfo = event.email || event.userId || 'unknown';
    console.log(
      `[AUTH ${status}] ${event.type} | user: ${userInfo} | ${event.timestamp}${event.error ? ` | error: ${event.error}` : ''}`
    );
  }
}

/**
 * better-auth configuration for Physical AI Textbook
 * Handles: email/password auth, social login, session management
 */
export const auth = betterAuth({
  database: pool,

  // Email/password authentication (FR-001, FR-003, FR-004)
  emailAndPassword: {
    enabled: true,
    // FR-003: Require email verification
    requireEmailVerification: true,
    // FR-004: Password strength requirements (min 8 chars)
    // Note: Additional validation (mixed case, number) handled client-side
    minPasswordLength: 8,
    // Password reset configuration (T067, T069)
    resetPasswordTokenExpiresIn: 60 * 60 * 24, // 24 hours (T069)
    // Send password reset email (T067)
    sendResetPassword: async ({ user, url, token }) => {
      // Email template for password reset
      const emailContent = {
        to: user.email,
        subject: 'Reset Your Password - Physical AI Textbook',
        html: `
          <div style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #1e293b;">Reset Your Password</h1>
            <p style="color: #475569;">Hi ${user.name || 'there'},</p>
            <p style="color: #475569;">
              We received a request to reset the password for your Physical AI & Humanoid Robotics Textbook account.
            </p>
            <p style="color: #475569;">
              Click the button below to set a new password. This link will expire in 24 hours.
            </p>
            <div style="margin: 32px 0;">
              <a href="${url}"
                 style="background: #2563eb; color: white; padding: 12px 24px;
                        border-radius: 8px; text-decoration: none; font-weight: 500;">
                Reset Password
              </a>
            </div>
            <p style="color: #64748b; font-size: 14px;">
              If you didn't request this, you can safely ignore this email.
            </p>
            <p style="color: #64748b; font-size: 14px;">
              Or copy this link: ${url}
            </p>
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 32px 0;" />
            <p style="color: #94a3b8; font-size: 12px;">
              Physical AI & Humanoid Robotics Textbook
            </p>
          </div>
        `,
        text: `
          Reset Your Password

          Hi ${user.name || 'there'},

          We received a request to reset the password for your Physical AI & Humanoid Robotics Textbook account.

          Click this link to set a new password (expires in 24 hours):
          ${url}

          If you didn't request this, you can safely ignore this email.
        `,
      };

      // TODO: Replace with actual email service (Resend, SendGrid, SMTP)
      // For now, log to console for development
      console.log('=== PASSWORD RESET EMAIL ===');
      console.log(`To: ${emailContent.to}`);
      console.log(`Subject: ${emailContent.subject}`);
      console.log(`Reset URL: ${url}`);
      console.log(`Token: ${token}`);
      console.log('============================');

      // Example integration with Resend:
      // import { Resend } from 'resend';
      // const resend = new Resend(process.env.RESEND_API_KEY);
      // await resend.emails.send({
      //   from: 'Physical AI Textbook <noreply@yourdomain.com>',
      //   ...emailContent,
      // });
    },
    // Send email verification
    sendVerificationEmail: async ({ user, url, token }) => {
      console.log('=== VERIFICATION EMAIL ===');
      console.log(`To: ${user.email}`);
      console.log(`Verification URL: ${url}`);
      console.log('==========================');
    },
  },

  // Session configuration (FR-005) - T052
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session age daily
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  // Social login providers (FR-002) - T050, T051
  socialProviders: {
    // Google OAuth (T050)
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
      // Request profile and email scopes
      scope: ['openid', 'email', 'profile'],
    },
    // GitHub OAuth (T051)
    github: {
      clientId: process.env.GITHUB_CLIENT_ID || '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
      // Request user email scope
      scope: ['user:email'],
    },
  },

  // Advanced options
  advanced: {
    cookiePrefix: 'textbook-auth',
    generateId: () => crypto.randomUUID(),
    // Secure cookie settings for production
    cookies: {
      sessionToken: {
        name: 'textbook-auth.session_token',
        options: {
          httpOnly: true,
          sameSite: 'lax',
          secure: process.env.NODE_ENV === 'production',
          path: '/',
          maxAge: 60 * 60 * 24 * 7, // 7 days
        },
      },
    },
  },

  // Account linking: allow linking social accounts to existing email
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ['google', 'github'],
    },
  },

  // Authentication event hooks for logging (T075)
  hooks: {
    after: [
      {
        matcher: (ctx) => ctx.path.startsWith('/sign-in'),
        handler: async (ctx) => {
          const response = ctx.response;
          const success = response?.status === 200;
          logAuthEvent({
            type: 'SIGN_IN',
            email: ctx.body?.email,
            success,
            error: !success ? 'Authentication failed' : undefined,
            timestamp: new Date().toISOString(),
          });
        },
      },
      {
        matcher: (ctx) => ctx.path.startsWith('/sign-up'),
        handler: async (ctx) => {
          const response = ctx.response;
          const success = response?.status === 200;
          logAuthEvent({
            type: 'SIGN_UP',
            email: ctx.body?.email,
            success,
            error: !success ? 'Registration failed' : undefined,
            timestamp: new Date().toISOString(),
          });
        },
      },
      {
        matcher: (ctx) => ctx.path.startsWith('/sign-out'),
        handler: async (ctx) => {
          logAuthEvent({
            type: 'SIGN_OUT',
            success: true,
            timestamp: new Date().toISOString(),
          });
        },
      },
      {
        matcher: (ctx) => ctx.path.startsWith('/forget-password'),
        handler: async (ctx) => {
          logAuthEvent({
            type: 'PASSWORD_RESET_REQUEST',
            email: ctx.body?.email,
            success: true,
            timestamp: new Date().toISOString(),
          });
        },
      },
      {
        matcher: (ctx) => ctx.path.startsWith('/reset-password'),
        handler: async (ctx) => {
          const response = ctx.response;
          const success = response?.status === 200;
          logAuthEvent({
            type: 'PASSWORD_RESET',
            success,
            error: !success ? 'Password reset failed' : undefined,
            timestamp: new Date().toISOString(),
          });
        },
      },
    ],
  },
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.User;
