---
id: "003"
title: "Bug Fixes Tests Datetime Pydantic"
stage: general
date: "2026-02-27"
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 002-user-auth-personalization
user: Aksystems
command: "check and clear bugs"
labels: ["bug-fix", "tests", "datetime", "pydantic", "vite", "frontend", "backend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/services/api.ts
  - frontend/vite.config.ts
  - backend/src/api/routes/profile.py
  - backend/src/api/routes/health.py
  - backend/src/models/user_profile.py
  - backend/src/services/profile.py
  - backend/tests/test_models_user_profile.py
tests:
  - backend: 161 passed (was 161 passed with 18 warnings, now 0 warnings)
  - frontend: 62 passed (was 40 passed, 1 failed, 1 suite crashed)
---

## Prompt

check and clear bugs if missing somethings add it if more remove it

## Response

Ran full test suites (backend pytest + frontend vitest) and fixed all failures and deprecations:

**Frontend bugs fixed:**
1. `api.ts` — catch fallback `{ error: 'Unknown error' }` → `{}` so `'API request failed'` fallback works
2. `vite.config.ts` — added `resolve.extensions` putting `.ts` before `.js` to prevent CJS `api.js` being loaded in useChat tests

**Backend deprecations (breaking in Python 3.13) fixed:**
3. `profile.py` — Pydantic v2 `class Config` → `ConfigDict(from_attributes=True)`
4. `health.py`, `user_profile.py`, `services/profile.py`, `tests/test_models_user_profile.py` — `datetime.utcnow()` → `datetime.now(timezone.utc)` (offset-naive was causing TypeError in comparison test)

## Outcome

- Backend: 161/161 passed, 0 warnings
- Frontend: 62/62 passed, all 3 test files green
