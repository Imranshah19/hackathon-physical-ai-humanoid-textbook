# Tasks: User Authentication with Personalized Learning

**Input**: Design documents from `/specs/002-user-auth-personalization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Auth Service**: `auth-service/src/` (Node.js + better-auth)
- **Backend**: `backend/src/` (FastAPI)
- **Frontend**: `frontend/src/` (React)
- **Plugin**: `packages/docusaurus-plugin-rag-chatbot/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization for auth service and dependencies

- [x] T001 Create auth-service directory structure per plan.md in auth-service/
- [x] T002 Initialize Node.js project with package.json in auth-service/package.json
- [x] T003 [P] Configure TypeScript in auth-service/tsconfig.json
- [x] T004 [P] Create environment template in auth-service/.env.example
- [x] T005 [P] Add better-auth and pg dependencies to auth-service/package.json
- [x] T006 [P] Install @better-auth/react in frontend/package.json
- [x] T007 Create .gitignore for auth-service in auth-service/.gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Auth Service Foundation

- [x] T008 Configure better-auth instance with PostgreSQL in auth-service/src/auth.ts
- [x] T009 Create HTTP server with Hono in auth-service/src/index.ts
- [x] T010 [P] Implement CORS middleware in auth-service/src/middleware/cors.ts
- [ ] T011 Run better-auth migrations with `npx @better-auth/cli migrate` (requires DB connection)

### Backend Foundation

- [x] T012 Create UserProfile SQLAlchemy model in backend/src/models/user_profile.py
- [x] T013 Create Alembic migration for user_profile table in backend/alembic/versions/002_user_profile.py
- [x] T014 [P] Implement auth middleware for session validation in backend/src/api/middleware/auth.py
- [x] T015 [P] Create profile enums and constants in backend/src/models/enums.py
- [x] T016 Register auth middleware in backend/src/main.py

### Frontend Foundation

- [x] T017 Create auth client hook with createAuthClient in frontend/src/hooks/useAuth.ts
- [x] T018 [P] Create AuthContext provider in frontend/src/context/AuthContext.tsx
- [x] T019 Export auth types in frontend/src/types/auth.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Registration with Profile (Priority: P1)

**Goal**: Enable new users to register and complete their learner profile

**Independent Test**: Complete signup flow, verify profile data is captured and stored

### Implementation for User Story 1

#### Auth Service (Registration)

- [x] T020 [US1] Configure email/password authentication in auth-service/src/auth.ts
- [x] T021 [P] [US1] Configure email verification settings in auth-service/src/auth.ts
- [x] T022 [P] [US1] Add password validation rules (min 8 chars, mixed case, number) in auth-service/src/auth.ts

#### Backend (Profile)

- [x] T023 [US1] Create ProfileService with create/complete logic in backend/src/services/profile.py
- [x] T024 [US1] Implement POST /api/profile/complete endpoint in backend/src/api/routes/profile.py
- [x] T025 [P] [US1] Implement POST /api/profile/skip endpoint in backend/src/api/routes/profile.py
- [x] T026 [P] [US1] Implement GET /api/profile/options endpoint in backend/src/api/routes/profile.py
- [x] T027 [US1] Register profile routes in backend/src/api/routes/__init__.py

#### Frontend (Registration UI)

- [x] T028 [P] [US1] Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx
- [x] T029 [P] [US1] Create ProfileWizard component (3-step wizard) in frontend/src/components/auth/ProfileWizard.tsx
- [x] T030 [P] [US1] Create SoftwareBackgroundStep component in frontend/src/components/auth/steps/SoftwareBackgroundStep.tsx
- [x] T031 [P] [US1] Create HardwareAccessStep component in frontend/src/components/auth/steps/HardwareAccessStep.tsx
- [x] T032 [P] [US1] Create ExperienceLevelStep component in frontend/src/components/auth/steps/ExperienceLevelStep.tsx
- [x] T033 [US1] Create registration flow page integrating RegisterForm + ProfileWizard in frontend/src/pages/Register.tsx

#### Plugin Integration

- [x] T034 [US1] Create AuthWrapper for Docusaurus in packages/docusaurus-plugin-rag-chatbot/src/theme/AuthWrapper.tsx
- [x] T035 [US1] Create ProfileBanner for incomplete profile prompts in packages/docusaurus-plugin-rag-chatbot/src/theme/ProfileBanner.tsx

**Checkpoint**: Users can register with email/password and complete their profile

---

## Phase 4: User Story 2 - Personalized Chapter Content (Priority: P1)

**Goal**: Deliver chapter content adapted to user's profile (experience level, code language, hardware)

**Independent Test**: User with "Beginner + Python + No Hardware" sees different content than "Advanced + C++ + Robot"

### Implementation for User Story 2

#### Backend (Personalization)

- [x] T036 [US2] Create PersonalizationService in backend/src/services/personalization.py
- [x] T037 [US2] Implement content variant selection based on experience level in backend/src/services/personalization.py
- [x] T038 [US2] Implement code language selection based on software background in backend/src/services/personalization.py
- [x] T039 [US2] Implement hardware variant selection in backend/src/services/personalization.py
- [x] T040 [US2] Implement GET /api/content/chapter/{chapterId} endpoint in backend/src/api/routes/content.py
- [x] T041 [P] [US2] Implement GET /api/content/code-example/{exampleId} endpoint in backend/src/api/routes/content.py
- [x] T042 [P] [US2] Implement GET /api/content/exercise/{exerciseId} endpoint in backend/src/api/routes/content.py
- [x] T043 [US2] Register content routes in backend/src/api/routes/__init__.py

#### Frontend (Content Display)

- [x] T044 [P] [US2] Create ContentToggle component for manual variant switching in frontend/src/components/profile/ContentToggle.tsx
- [x] T045 [P] [US2] Create CodeExampleViewer with language tabs in frontend/src/components/content/CodeExampleViewer.tsx
- [x] T046 [P] [US2] Create ExerciseViewer with hardware variants in frontend/src/components/content/ExerciseViewer.tsx
- [x] T047 [US2] Create usePersonalizedContent hook in frontend/src/hooks/usePersonalizedContent.ts

#### Preferences API

- [x] T048 [US2] Implement GET /api/preferences endpoint in backend/src/api/routes/content.py
- [x] T049 [US2] Implement PATCH /api/preferences endpoint in backend/src/api/routes/content.py

**Checkpoint**: Logged-in users see personalized content based on their profile

---

## Phase 5: User Story 3 - User Login and Session Management (Priority: P2)

**Goal**: Enable returning users to log in and manage their sessions

**Independent Test**: User can log in with email/password or social, session persists, can log out

### Implementation for User Story 3

#### Auth Service (Login + Social)

- [x] T050 [US3] Configure Google OAuth provider in auth-service/src/auth.ts
- [x] T051 [P] [US3] Configure GitHub OAuth provider in auth-service/src/auth.ts
- [x] T052 [US3] Configure session settings (7-day expiry, cookie options) in auth-service/src/auth.ts
- [x] T053 [P] [US3] Add rate limiting for login endpoints in auth-service/src/middleware/rateLimit.ts

#### Frontend (Login UI)

- [x] T054 [P] [US3] Create LoginForm component in frontend/src/components/auth/LoginForm.tsx
- [x] T055 [P] [US3] Create SocialLoginButtons component (Google, GitHub) in frontend/src/components/auth/SocialLoginButtons.tsx
- [x] T056 [US3] Create login page integrating LoginForm + SocialLoginButtons in frontend/src/pages/Login.tsx
- [x] T057 [US3] Add logout functionality to auth hook in frontend/src/hooks/useAuth.ts
- [x] T058 [P] [US3] Create UserMenu component with logout button in frontend/src/components/auth/UserMenu.tsx

#### Session Management

- [x] T059 [US3] Implement session persistence check on app load in frontend/src/context/AuthContext.tsx
- [x] T060 [P] [US3] Add revoke-all-sessions support in frontend/src/hooks/useAuth.ts

**Checkpoint**: Users can log in with email or social, session persists across page loads

---

## Phase 6: User Story 4 - Profile Updates (Priority: P3)

**Goal**: Allow users to update their profile settings at any time

**Independent Test**: User changes hardware access, content updates to reflect new selection

### Implementation for User Story 4

#### Backend (Profile Updates)

- [x] T061 [US4] Implement GET /api/profile endpoint in backend/src/api/routes/profile.py
- [x] T062 [US4] Implement PATCH /api/profile endpoint in backend/src/api/routes/profile.py
- [x] T063 [US4] Add profile update validation in backend/src/services/profile.py

#### Frontend (Profile Editor)

- [x] T064 [P] [US4] Create ProfileEditor component in frontend/src/components/profile/ProfileEditor.tsx
- [x] T065 [P] [US4] Create ProfileSettings page in frontend/src/pages/ProfileSettings.tsx
- [x] T066 [US4] Add navigation to profile settings in frontend/src/components/auth/UserMenu.tsx

**Checkpoint**: Users can view and update their profile, content reflects changes

---

## Phase 7: User Story 5 - Password Recovery (Priority: P3)

**Goal**: Enable users to reset forgotten passwords

**Independent Test**: User requests reset, receives email, sets new password, can log in

### Implementation for User Story 5

#### Auth Service (Password Reset)

- [x] T067 [US5] Configure password reset email template in auth-service/src/auth.ts
- [x] T068 [P] [US5] Add rate limiting for password reset (3/hour) in auth-service/src/middleware/rateLimit.ts
- [x] T069 [US5] Configure 24-hour token expiration for reset links in auth-service/src/auth.ts

#### Frontend (Password Reset UI)

- [x] T070 [P] [US5] Create ForgotPasswordForm component in frontend/src/components/auth/ForgotPasswordForm.tsx
- [x] T071 [P] [US5] Create ResetPasswordForm component in frontend/src/components/auth/ResetPasswordForm.tsx
- [x] T072 [US5] Create forgot-password page in frontend/src/pages/ForgotPassword.tsx
- [x] T073 [US5] Create reset-password page (with token param) in frontend/src/pages/ResetPassword.tsx
- [x] T074 [US5] Add "Forgot Password" link to LoginForm in frontend/src/components/auth/LoginForm.tsx

**Checkpoint**: Users can reset their password via email link

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Security hardening, logging, and final validation

- [x] T075 [P] Add authentication event logging in auth-service/src/auth.ts
- [x] T076 [P] Configure rate limiting on all auth endpoints in auth-service/src/middleware/rateLimit.ts
- [x] T077 [P] Add HTTPS redirect and security headers in auth-service/src/index.ts
- [x] T078 Update backend .env.example with auth service URL in backend/.env.example
- [x] T079 Update frontend environment config for auth URL in frontend/src/config.ts
- [x] T080 [P] Add loading states to all auth forms in frontend/src/components/auth/
- [x] T081 [P] Add error handling and user feedback in frontend/src/components/auth/
- [x] T082 Run quickstart.md validation scenarios
- [x] T083 Update main README with auth setup instructions in README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational - MVP core
- **US2 (Phase 4)**: Depends on Foundational + benefits from US1 (profile data)
- **US3 (Phase 5)**: Depends on Foundational - can run parallel with US1/US2
- **US4 (Phase 6)**: Depends on US1 (profile must exist)
- **US5 (Phase 7)**: Depends on Foundational - can run parallel with others
- **Polish (Phase 8)**: Depends on all user stories

### User Story Dependencies

```text
Foundational (Phase 2)
        │
        ├──► US1: Registration (P1) ──► US4: Profile Updates (P3)
        │                           │
        │                           ▼
        ├──► US2: Personalization (P1) [benefits from US1 profile]
        │
        ├──► US3: Login (P2) [parallel with US1/US2]
        │
        └──► US5: Password Reset (P3) [parallel with others]
```

### Parallel Opportunities by Phase

**Phase 1 Setup**: T003, T004, T005, T006 can run in parallel

**Phase 2 Foundational**: T010, T014, T015, T018 can run in parallel

**Phase 3 US1**:
- T021, T022 parallel (auth config)
- T025, T026 parallel (backend endpoints)
- T028-T032 parallel (frontend components)

**Phase 4 US2**:
- T041, T042 parallel (backend endpoints)
- T044, T045, T046 parallel (frontend components)

**Phase 5 US3**:
- T050, T051 parallel (OAuth providers)
- T054, T055 parallel (frontend components)

---

## Parallel Example: Phase 3 (US1)

```bash
# Launch frontend components in parallel:
Task: "Create RegisterForm component in frontend/src/components/auth/RegisterForm.tsx"
Task: "Create ProfileWizard component in frontend/src/components/auth/ProfileWizard.tsx"
Task: "Create SoftwareBackgroundStep in frontend/src/components/auth/steps/SoftwareBackgroundStep.tsx"
Task: "Create HardwareAccessStep in frontend/src/components/auth/steps/HardwareAccessStep.tsx"
Task: "Create ExperienceLevelStep in frontend/src/components/auth/steps/ExperienceLevelStep.tsx"
```

---

## Implementation Strategy

### MVP First (US1 + US3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Registration)
4. Complete Phase 5: US3 (Login) - minimal viable auth
5. **STOP and VALIDATE**: Users can register and log in

### Full MVP (US1 + US2 + US3)

1. Setup + Foundational
2. US1: Registration with Profile
3. US2: Personalized Content
4. US3: Login + Sessions
5. **Deploy**: Core personalization working

### Complete Feature

1. MVP phases above
2. US4: Profile Updates
3. US5: Password Recovery
4. Phase 8: Polish

---

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 7 |
| Phase 2 | Foundational | 12 |
| Phase 3 | US1: Registration | 16 |
| Phase 4 | US2: Personalization | 14 |
| Phase 5 | US3: Login | 11 |
| Phase 6 | US4: Profile Updates | 6 |
| Phase 7 | US5: Password Reset | 8 |
| Phase 8 | Polish | 9 |
| **Total** | | **83** |

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [USn] label maps task to specific user story
- Each user story is independently testable after completion
- Commit after each task or logical group
- Auth service runs on port 3001, backend on port 8000
- All endpoints use HTTP-only cookies for session management
