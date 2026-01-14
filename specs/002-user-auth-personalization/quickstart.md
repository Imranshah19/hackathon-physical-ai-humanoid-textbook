# Quickstart: User Authentication with Personalized Learning

**Feature**: 002-user-auth-personalization
**Date**: 2026-01-08

## Prerequisites

- Node.js 20 LTS
- Python 3.11+
- PostgreSQL (Neon account or local)
- Google OAuth credentials (optional)
- GitHub OAuth credentials (optional)

## Local Development Setup

### 1. Auth Service Setup

```bash
# Create auth service directory
mkdir -p auth-service
cd auth-service

# Initialize Node.js project
npm init -y

# Install better-auth and dependencies
npm install better-auth pg dotenv

# Install dev dependencies
npm install -D typescript @types/node tsx
```

### 2. Configure Environment Variables

Create `auth-service/.env`:

```env
# Required
BETTER_AUTH_SECRET=your-32-char-secret-key-here-min
BETTER_AUTH_URL=http://localhost:3001

# Database (same as backend)
DATABASE_URL=postgresql://user:password@localhost:5432/textbook

# OAuth Providers (optional for initial setup)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Create Auth Configuration

Create `auth-service/src/auth.ts`:

```typescript
import { betterAuth } from "better-auth";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
    minPasswordLength: 8,
  },
  socialProviders: {
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
});
```

### 4. Run Database Migrations

```bash
cd auth-service

# Generate migrations
npx @better-auth/cli generate

# Apply migrations
npx @better-auth/cli migrate
```

### 5. Create User Profile Migration

Create migration file in `backend/alembic/versions/`:

```python
"""Add user_profile table

Revision ID: 002_user_profile
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'user_profile',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('software_background', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('hardware_access', postgresql.ARRAY(sa.String(50)), default=[]),
        sa.Column('experience_level', sa.String(20), nullable=True),
        sa.Column('profile_completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_reminded_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('idx_profile_user', 'user_profile', ['user_id'])
    op.create_index('idx_profile_experience', 'user_profile', ['experience_level'])

def downgrade():
    op.drop_table('user_profile')
```

### 6. Start Services

Terminal 1 - Auth Service:
```bash
cd auth-service
npm run dev
# Runs on http://localhost:3001
```

Terminal 2 - FastAPI Backend:
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn src.main:app --reload --port 8000
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

## Integration Test Scenarios

### Test 1: Email Registration (US1)

```bash
# Register new user
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'

# Expected: 200 OK with user and session
```

### Test 2: Complete Profile (US1)

```bash
# With session cookie from registration
curl -X POST http://localhost:8000/api/profile/complete \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=<token>" \
  -d '{
    "softwareBackground": ["python", "ros_ros2"],
    "hardwareAccess": ["simulation_only", "raspberry_pi"],
    "experienceLevel": "intermediate"
  }'

# Expected: 200 OK with completed profile
```

### Test 3: Get Personalized Content (US2)

```bash
# With session cookie
curl http://localhost:8000/api/content/chapter/01-introduction \
  -H "Cookie: better-auth.session_token=<token>"

# Expected: Content with variant=intermediate, codeLanguage=python
```

### Test 4: Login (US3)

```bash
curl -X POST http://localhost:3001/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Expected: 200 OK with Set-Cookie header
```

### Test 5: Social Login (US3)

```bash
# Initiate GitHub login
open "http://localhost:3001/api/auth/sign-in/social?provider=github"

# Expected: Redirect to GitHub, then back with session
```

### Test 6: Update Profile (US4)

```bash
curl -X PATCH http://localhost:8000/api/profile \
  -H "Content-Type: application/json" \
  -H "Cookie: better-auth.session_token=<token>" \
  -d '{
    "hardwareAccess": ["simulation_only", "raspberry_pi", "nvidia_jetson"]
  }'

# Expected: 200 OK with updated profile
```

### Test 7: Password Reset (US5)

```bash
# Request reset
curl -X POST http://localhost:3001/api/auth/forget-password \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Expected: 200 OK (always returns success)

# Complete reset (with token from email)
curl -X POST http://localhost:3001/api/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<reset-token>",
    "newPassword": "NewSecurePass456"
  }'

# Expected: 200 OK
```

## Frontend Integration

### Install Auth Client

```bash
cd frontend
npm install @better-auth/react
```

### Create Auth Hook

```typescript
// frontend/src/hooks/useAuth.ts
import { createAuthClient } from "@better-auth/react";

export const authClient = createAuthClient({
  baseURL: "http://localhost:3001",
});

export const { useSession, signIn, signUp, signOut } = authClient;
```

### Auth Provider Setup

```typescript
// frontend/src/index.tsx
import { AuthProvider } from "@better-auth/react";
import { authClient } from "./hooks/useAuth";

export function App() {
  return (
    <AuthProvider client={authClient}>
      {/* app content */}
    </AuthProvider>
  );
}
```

## Troubleshooting

### Common Issues

1. **"BETTER_AUTH_SECRET too short"**
   - Ensure secret is at least 32 characters

2. **"Database connection refused"**
   - Check DATABASE_URL in .env
   - Ensure PostgreSQL is running

3. **"OAuth callback error"**
   - Verify redirect URIs in Google/GitHub console
   - Check client ID and secret

4. **"CORS error on auth requests"**
   - Ensure CORS_ORIGINS includes frontend URL
   - Check auth service CORS middleware

### Debug Mode

Set in auth-service/.env:
```env
DEBUG=better-auth:*
```
