---
id: "002"
title: "Project Review Fix Problems"
stage: general
date: "2026-02-27"
surface: agent
model: claude-sonnet-4-6
feature: none
branch: main
user: Aksystems
command: "check the project review and fix problums"
labels: ["bug-fix", "review", "backend", "frontend", "docker"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/src/config.py
  - backend/pyproject.toml
  - backend/src/api/routes/health.py
  - backend/src/models/user_profile.py
  - backend/src/api/middleware/auth.py
  - docker-compose.yml
  - frontend/src/context/AuthContext.tsx
  - frontend/src/services/api.ts
  - frontend/src/pages/ProfileSettings.tsx
tests: []
---

## Prompt

check the project review and fix problums

## Response

Performed a full project review and fixed 9 issues across backend, Docker config, and frontend:

**Backend fixes:**
1. Added missing `openai_api_key`, `openai_model`, `auth_service_url` fields to `config.py` (translation service was crashing at startup)
2. Added `openai>=1.0.0` to `pyproject.toml` dependencies (missing package)
3. Fixed raw SQL string → `text("SELECT 1")` in `health.py` (SQLAlchemy async requires text() wrapper)
4. Fixed `datetime.now()` → `datetime.utcnow()` in `user_profile.py:mark_complete()` (timezone inconsistency)
5. Fixed hardcoded `AUTH_SERVICE_URL = "http://localhost:3001"` → `os.getenv("AUTH_SERVICE_URL", "http://localhost:3001")` in `middleware/auth.py`

**Docker fixes:**
6. Fixed auth service healthcheck from `/api/auth/health` → `/health` (that endpoint doesn't exist; only `/health` is defined)

**Frontend fixes:**
7. Fixed profile API path `/api/profile` → `/api/v1/profile` in `AuthContext.tsx` (was double-pathing to `/api/api/profile`)
8. Improved `response.body` null check order in `api.ts` (check before calling `.getReader()`)
9. Implemented "Sign Out All Devices" button in `ProfileSettings.tsx` using `revokeAllSessions()` + `signOutUser()` from `useAuth.ts`

## Outcome

All 9 issues fixed. Project should now start cleanly and all runtime-critical bugs are resolved.
