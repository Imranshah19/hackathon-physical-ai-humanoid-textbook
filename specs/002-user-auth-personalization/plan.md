# Implementation Plan: User Authentication with Personalized Learning

**Branch**: `002-user-auth-personalization` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-user-auth-personalization/spec.md`

## Summary

Implement user authentication using better-auth.com (TypeScript) with a dedicated auth microservice, integrated with the existing FastAPI backend and React frontend. Collect user profile data (software background, hardware access, experience level) at signup to deliver personalized textbook chapter content with appropriate code examples and hardware instructions.

## Technical Context

**Language/Version**: TypeScript 5.x (auth service), Python 3.11+ (backend), React 18 (frontend)
**Primary Dependencies**: better-auth, pg, FastAPI, SQLAlchemy, @better-auth/react
**Storage**: Neon PostgreSQL (shared between auth service and backend)
**Testing**: Vitest (frontend), pytest (backend), manual integration tests
**Target Platform**: Web application (Docusaurus + embedded widgets)
**Project Type**: Web (microservices architecture)
**Performance Goals**: Login < 5s (SC-003), 1000 concurrent users (SC-007)
**Constraints**: Registration < 3 min (SC-001), 80% profile completion (SC-002)
**Scale/Scope**: Educational platform, single-tenant, moderate traffic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. ROS 2 Mandatory | N/A | Auth feature doesn't involve robotics code |
| II. Simulation-First | N/A | Auth feature doesn't involve robot behaviors |
| III. Physical AI Focus | PASS | Enables personalized content for robotics learners |
| IV. No Hallucinations | PASS | All APIs verified against better-auth docs |
| V. Clear Communication | PASS | Profile options have clear descriptions |
| VI. RAG Constraint | PASS | Personalization complements RAG, doesn't replace |
| Content Personalization | PASS | Core feature - profile enables adaptive content |
| Code Standards | PASS | Python 3.11+, TypeScript, type hints required |

**Pre-Phase 0 Gate**: PASS - No violations, auth feature aligned with constitution.

## Project Structure

### Documentation (this feature)

```text
specs/002-user-auth-personalization/
├── plan.md              # This file
├── research.md          # Technology decisions (better-auth, architecture)
├── data-model.md        # Entity definitions (User, Session, Profile)
├── quickstart.md        # Local development setup
├── contracts/           # API specifications
│   ├── auth-api.yaml    # better-auth endpoints
│   ├── profile-api.yaml # Profile management
│   └── personalization-api.yaml # Content personalization
└── checklists/
    └── requirements.md  # Spec quality validation
```

### Source Code (repository root)

```text
# Auth Service (new - better-auth microservice)
auth-service/
├── src/
│   ├── auth.ts          # better-auth configuration
│   ├── index.ts         # HTTP server (Hono or Express)
│   └── middleware/
│       └── cors.ts      # CORS configuration
├── package.json
├── tsconfig.json
└── .env

# Backend (existing - FastAPI extensions)
backend/
├── src/
│   ├── models/
│   │   └── user_profile.py    # UserProfile SQLAlchemy model
│   ├── services/
│   │   ├── profile.py         # Profile business logic
│   │   └── personalization.py # Content variant selection
│   ├── api/
│   │   ├── middleware/
│   │   │   └── auth.py        # Session validation middleware
│   │   └── routes/
│   │       ├── profile.py     # Profile CRUD endpoints
│   │       └── content.py     # Personalized content endpoints
│   └── db/
│       └── migrations/
│           └── 002_user_profile.py
└── tests/
    ├── unit/
    │   └── test_profile.py
    └── integration/
        └── test_auth_flow.py

# Frontend (existing - React extensions)
frontend/
├── src/
│   ├── hooks/
│   │   └── useAuth.ts         # better-auth React client
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   ├── ProfileWizard.tsx
│   │   │   ├── SocialLoginButtons.tsx
│   │   │   └── PasswordReset.tsx
│   │   └── profile/
│   │       ├── ProfileEditor.tsx
│   │       └── ContentToggle.tsx
│   ├── context/
│   │   └── AuthContext.tsx    # Auth state provider
│   └── pages/
│       └── (Docusaurus integration)
└── tests/
    └── components/
        └── auth.test.tsx

# Docusaurus Plugin (existing - auth integration)
packages/docusaurus-plugin-rag-chatbot/
├── src/
│   └── theme/
│       ├── AuthWrapper.tsx    # Auth state wrapper
│       └── ProfileBanner.tsx  # Profile completion prompt
└── ...
```

**Structure Decision**: Microservices architecture with dedicated auth service. better-auth requires Node.js runtime, separate from Python FastAPI backend. Shared PostgreSQL database enables seamless data access.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           Docusaurus Site                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   Login     │  │  Register   │  │  Profile    │  │  RAG Chatbot    │ │
│  │   Page      │  │   Page      │  │   Wizard    │  │  Widget         │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘ │
│         │                │                │                   │          │
│         └────────────────┼────────────────┼───────────────────┘          │
│                          │                │                              │
│                    ┌─────▼────────────────▼─────┐                        │
│                    │   @better-auth/react       │                        │
│                    │   (Frontend Auth Client)   │                        │
│                    └─────────────┬──────────────┘                        │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
                    ▼              │              ▼
         ┌──────────────────┐     │    ┌──────────────────┐
         │   Auth Service   │     │    │  FastAPI Backend │
         │  (better-auth)   │     │    │  (Profile + RAG) │
         │  :3001           │     │    │  :8000           │
         └────────┬─────────┘     │    └────────┬─────────┘
                  │               │             │
                  │  Session      │  Profile    │
                  │  Validation   │  + Content  │
                  │               │             │
                  └───────────────┼─────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │    Neon PostgreSQL       │
                    │  ┌────────┐ ┌──────────┐ │
                    │  │ user   │ │ user_    │ │
                    │  │session │ │ profile  │ │
                    │  │account │ │          │ │
                    │  └────────┘ └──────────┘ │
                    └──────────────────────────┘
```

## Key Implementation Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth Framework | better-auth | User-specified, TypeScript-native, PostgreSQL support |
| Architecture | Microservice | better-auth needs Node.js, separate from Python backend |
| Session Strategy | HTTP-only cookies | Secure by default, CSRF protection |
| Profile Storage | Same PostgreSQL | Enables JOINs for personalized queries |
| Content Personalization | Server-side variants | Profile lookup on each request, cacheable |

## Security Considerations

- **FR-018**: Rate limiting on auth endpoints (5/min login, 3/hr reset)
- **FR-019**: Authentication events logged for monitoring
- **FR-021**: Reset tokens expire after 24 hours, single-use
- **Cookies**: HttpOnly, Secure, SameSite=Strict
- **Passwords**: bcrypt hashing (better-auth default)
- **OAuth tokens**: Encrypted at rest in database

## Dependencies Map

```text
Phase 1 (Setup)
├── Auth service initialization
├── Database migrations
└── Environment configuration

Phase 2 (Foundational) ─── depends on Phase 1
├── better-auth configuration
├── FastAPI auth middleware
└── Frontend auth client

Phase 3 (US1: Registration) ─── depends on Phase 2
├── Registration endpoints (better-auth)
├── Profile wizard component
└── Profile completion API

Phase 4 (US2: Personalization) ─── depends on Phase 3
├── Content variant selection
├── Code example switching
└── Hardware-specific instructions

Phase 5 (US3: Login) ─── depends on Phase 2
├── Login endpoints (better-auth)
├── Session management
└── Social login integration

Phase 6 (US4: Profile Updates) ─── depends on Phase 3
├── Profile editor component
└── Update API

Phase 7 (US5: Password Reset) ─── depends on Phase 2
├── Reset request endpoint
├── Email sending
└── Reset completion
```

## Complexity Tracking

No constitution violations requiring justification. Architecture uses minimum necessary complexity:
- Microservice split is required (different runtimes)
- Shared database avoids data sync complexity
- better-auth handles auth complexity internally

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| better-auth version changes | Pin version, review changelogs before updates |
| OAuth provider outages | Email/password always available as fallback |
| Profile completion rate < 80% | Implement gentle reminders, track metrics |

## Next Steps

1. Generate tasks.md with `/sp.tasks`
2. Implement in priority order (US1 → US2 → US3 → US4 → US5)
3. Integration testing with existing RAG chatbot
4. Documentation for Docusaurus theme integration
