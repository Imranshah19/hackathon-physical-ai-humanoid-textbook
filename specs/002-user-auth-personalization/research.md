# Research: User Authentication with Personalized Learning

**Feature**: 002-user-auth-personalization
**Date**: 2026-01-08

## Research Tasks Completed

### 1. better-auth.com Integration

**Decision**: Use better-auth as a dedicated TypeScript auth service

**Rationale**:
- better-auth is a TypeScript-first framework - integrates natively with our React frontend
- Supports PostgreSQL adapter (matches our Neon Postgres database)
- Built-in email/password and social login (Google, GitHub) per FR-001, FR-002
- Session management with configurable timeout (FR-005)
- Plugin ecosystem for extensibility

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| Auth.js/NextAuth | Popular, well-documented | Next.js focused, overkill for Docusaurus | Not framework-agnostic |
| Passport.js | Flexible strategies | Node.js only, more manual setup | More boilerplate |
| Custom Python auth | Stays in FastAPI | Rebuilding the wheel | better-auth specified by user |
| Supabase Auth | Managed service | External dependency, cost | User specified better-auth |

### 2. Architecture Decision: Auth Service Placement

**Decision**: Create a dedicated auth microservice (`/auth-service`) using Node.js + better-auth

**Rationale**:
- Separation of concerns - auth is independent from RAG chatbot
- better-auth requires Node.js/TypeScript runtime
- FastAPI backend remains focused on RAG functionality
- Auth service handles `/api/auth/*` routes
- Shared PostgreSQL database (Neon) for both services

**Architecture**:
```text
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Docusaurus    │────▶│   Auth Service   │────▶│  Neon Postgres  │
│   (Frontend)    │     │  (better-auth)   │     │   (Shared DB)   │
└────────┬────────┘     └──────────────────┘     └────────┬────────┘
         │                                                 │
         │              ┌──────────────────┐              │
         └─────────────▶│  FastAPI Backend │◀─────────────┘
                        │  (RAG Chatbot)   │
                        └──────────────────┘
```

### 3. Database Schema Strategy

**Decision**: Extend existing Neon PostgreSQL with auth tables

**Rationale**:
- Reuse existing database infrastructure
- better-auth CLI generates schema via `npx @better-auth/cli migrate`
- Custom `user_profile` table for personalization data (software background, hardware access, experience level)
- Foreign key from profile to better-auth user table

**Tables Required**:
- `user` (better-auth managed)
- `session` (better-auth managed)
- `account` (better-auth managed for social logins)
- `verification` (better-auth managed for email verification)
- `user_profile` (custom - for personalization)

### 4. Social Login Providers

**Decision**: Google and GitHub OAuth per FR-002

**Rationale**:
- GitHub: Primary audience is developers/robotics engineers
- Google: Universal access for students globally
- Both supported natively by better-auth

**Configuration Required**:
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `BETTER_AUTH_SECRET` (32+ characters)
- `BETTER_AUTH_URL` (base URL for auth callbacks)

### 5. Profile Collection UX

**Decision**: Post-registration wizard with skip option

**Rationale**:
- FR-010 requires skip option with reminders
- Multi-step wizard reduces cognitive load
- Profile completion rate target: 80% (SC-002)

**Flow**:
1. User completes registration (email/password or social)
2. Redirect to profile wizard (3 steps)
3. Step 1: Software Background (multi-select checkboxes)
4. Step 2: Hardware Access (multi-select checkboxes)
5. Step 3: Experience Level (single-select radio)
6. Optional skip at any step → reminder on next login

### 6. Content Personalization Strategy

**Decision**: Server-side content variants with client preference header

**Rationale**:
- Profile stored in database, retrieved on session validation
- FastAPI middleware adds user profile to request context
- Content API returns variant based on profile
- Client can override via toggle (FR-017)

**Implementation Pattern**:
```text
Request → Auth Middleware → Profile Lookup → Content Variant Selection → Response
```

### 7. Session Management

**Decision**: HTTP-only secure cookies with 7-day expiration

**Rationale**:
- better-auth default session strategy
- HTTP-only prevents XSS token theft (FR-019)
- SameSite=Strict for CSRF protection
- Configurable timeout per FR-005

### 8. Rate Limiting Strategy

**Decision**: Extend existing FastAPI rate limiter for auth endpoints

**Rationale**:
- FR-018 requires rate limiting on auth endpoints
- Existing `rate_limit.py` middleware in backend
- Apply stricter limits to login/register (5 attempts/minute)
- Password reset: 3 attempts/hour per email

## Unresolved Items

None - all clarifications resolved through research.

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Auth Framework | better-auth | latest |
| Auth Runtime | Node.js | 20 LTS |
| Auth Database Adapter | pg (PostgreSQL) | latest |
| Frontend Auth Client | @better-auth/react | latest |
| Backend Integration | FastAPI middleware | existing |
| Database | Neon PostgreSQL | existing |
| Social Providers | Google, GitHub | OAuth 2.0 |

## Next Steps

1. Create data-model.md with entity definitions
2. Create API contracts for auth endpoints
3. Define content personalization API
4. Create quickstart.md for local development
