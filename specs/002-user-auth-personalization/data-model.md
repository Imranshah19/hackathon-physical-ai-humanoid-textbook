# Data Model: User Authentication with Personalized Learning

**Feature**: 002-user-auth-personalization
**Date**: 2026-01-08

## Entity Overview

```text
┌──────────────────────────────────────────────────────────────────┐
│                        better-auth managed                        │
├──────────────┬──────────────┬───────────────┬───────────────────┤
│     user     │   session    │    account    │   verification    │
│  (core auth) │  (sessions)  │ (social links)│  (email verify)   │
└──────┬───────┴──────────────┴───────────────┴───────────────────┘
       │
       │ 1:1
       ▼
┌──────────────┐
│ user_profile │  (custom - personalization)
└──────────────┘
```

## Entities

### 1. User (better-auth managed)

**Description**: Core user identity managed by better-auth

**Source**: FR-001, FR-002, FR-003

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| emailVerified | BOOLEAN | DEFAULT false | Email verification status (FR-003) |
| name | VARCHAR(255) | NULL | Display name |
| image | VARCHAR(500) | NULL | Profile image URL |
| createdAt | TIMESTAMP | NOT NULL | Account creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last update time |

**Relationships**:
- Has many `session` (1:N)
- Has many `account` (1:N for social logins)
- Has one `user_profile` (1:1)

**Validation Rules**:
- Email must be valid format
- Email must be unique across all users

---

### 2. Session (better-auth managed)

**Description**: Active login sessions

**Source**: FR-005, FR-006

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Session identifier |
| userId | UUID | FK → user.id, NOT NULL | Associated user |
| token | VARCHAR(255) | UNIQUE, NOT NULL | Session token (hashed) |
| expiresAt | TIMESTAMP | NOT NULL | Session expiration |
| ipAddress | VARCHAR(45) | NULL | Client IP (IPv6 compatible) |
| userAgent | TEXT | NULL | Browser/device info |
| createdAt | TIMESTAMP | NOT NULL | Session start time |
| updatedAt | TIMESTAMP | NOT NULL | Last activity time |

**State Transitions**:
```text
Created → Active → [Expired | Revoked]
```

**Validation Rules**:
- Token must be cryptographically secure
- ExpiresAt must be in future when created
- Default expiration: 7 days

---

### 3. Account (better-auth managed)

**Description**: OAuth/social login connections

**Source**: FR-002

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Account link identifier |
| userId | UUID | FK → user.id, NOT NULL | Associated user |
| accountId | VARCHAR(255) | NOT NULL | Provider's user ID |
| providerId | VARCHAR(50) | NOT NULL | Provider name (google, github) |
| accessToken | TEXT | NULL | OAuth access token (encrypted) |
| refreshToken | TEXT | NULL | OAuth refresh token (encrypted) |
| accessTokenExpiresAt | TIMESTAMP | NULL | Token expiration |
| scope | TEXT | NULL | Granted OAuth scopes |
| createdAt | TIMESTAMP | NOT NULL | Link creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last update time |

**Unique Constraint**: (providerId, accountId)

---

### 4. Verification (better-auth managed)

**Description**: Email verification and password reset tokens

**Source**: FR-003, FR-020, FR-021

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Verification identifier |
| identifier | VARCHAR(255) | NOT NULL | Email address |
| value | VARCHAR(255) | NOT NULL | Verification token |
| expiresAt | TIMESTAMP | NOT NULL | Token expiration (24h for reset) |
| createdAt | TIMESTAMP | NOT NULL | Token creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last update |

**Types**:
- Email verification
- Password reset (FR-021: 24-hour expiration)

---

### 5. UserProfile (custom)

**Description**: Learner profile for content personalization

**Source**: FR-007, FR-008, FR-009, FR-010, FR-011, FR-012

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Profile identifier |
| userId | UUID | FK → user.id, UNIQUE, NOT NULL | Associated user |
| softwareBackground | VARCHAR[] | DEFAULT '{}' | Selected languages (FR-007) |
| hardwareAccess | VARCHAR[] | DEFAULT '{}' | Selected platforms (FR-008) |
| experienceLevel | VARCHAR(20) | NULL | Skill level (FR-009) |
| profileCompleted | BOOLEAN | DEFAULT false | Completion status |
| completedAt | TIMESTAMP | NULL | When profile was completed |
| lastRemindedAt | TIMESTAMP | NULL | Last skip reminder shown |
| createdAt | TIMESTAMP | NOT NULL | Profile creation time |
| updatedAt | TIMESTAMP | NOT NULL | Last update time |

**Enum Values**:

**softwareBackground** (FR-007 multi-select):
- `python`
- `cpp`
- `javascript_typescript`
- `ros_ros2`
- `matlab`
- `none_learning`

**hardwareAccess** (FR-008 multi-select):
- `simulation_only`
- `arduino_microcontrollers`
- `raspberry_pi`
- `nvidia_jetson`
- `robot_arm`
- `humanoid_robot`
- `drone_uav`
- `custom_other`

**experienceLevel** (FR-009 single-select):
- `beginner` - New to robotics
- `intermediate` - Some projects completed
- `advanced` - Professional/research experience

**Validation Rules**:
- softwareBackground: array of valid enum values
- hardwareAccess: array of valid enum values
- experienceLevel: single valid enum value or NULL
- profileCompleted: true only if all three fields have values

**State Transitions**:
```text
Created (empty) → Partial (some fields) → Completed (all fields)
                      ↓                          ↓
               [Skip reminder]           [Can update anytime]
```

---

## Indexes

```sql
-- better-auth standard indexes
CREATE INDEX idx_session_user ON session(userId);
CREATE INDEX idx_session_token ON session(token);
CREATE INDEX idx_account_user ON account(userId);
CREATE INDEX idx_account_provider ON account(providerId, accountId);
CREATE INDEX idx_verification_identifier ON verification(identifier);

-- Custom profile indexes
CREATE UNIQUE INDEX idx_profile_user ON user_profile(userId);
CREATE INDEX idx_profile_experience ON user_profile(experienceLevel);
CREATE INDEX idx_profile_completed ON user_profile(profileCompleted);
```

## Database Migrations

**Migration Strategy**:
1. Run `npx @better-auth/cli migrate` for core auth tables
2. Custom migration for `user_profile` table
3. Create trigger to auto-create profile on user registration

**Trigger (PostgreSQL)**:
```sql
CREATE OR REPLACE FUNCTION create_user_profile()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO user_profile (id, userId, createdAt, updatedAt)
  VALUES (gen_random_uuid(), NEW.id, NOW(), NOW());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_user_insert
AFTER INSERT ON "user"
FOR EACH ROW EXECUTE FUNCTION create_user_profile();
```

## API Mappings

| Entity | Create | Read | Update | Delete |
|--------|--------|------|--------|--------|
| User | POST /auth/sign-up | GET /auth/session | PATCH /auth/update-user | - |
| Session | POST /auth/sign-in | GET /auth/session | - | POST /auth/sign-out |
| Account | OAuth callback | GET /auth/session | - | - |
| UserProfile | Auto on registration | GET /api/profile | PATCH /api/profile | - |
