# Data Model: RAG Documentation Chatbot

**Feature**: 001-rag-chatbot
**Date**: 2026-01-08
**Storage**: Neon Postgres (relational) + Qdrant Cloud (vectors)

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   UserSession   │       │ DocumentChunk   │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ session_token   │       │ source_url      │
│ created_at      │       │ section_title   │
│ last_active_at  │       │ content         │
│ preferences     │       │ content_hash    │
└────────┬────────┘       │ chunk_index     │
         │                │ updated_at      │
         │ 1:N            └─────────────────┘
         │                        │
         ▼                        │ (Qdrant)
┌─────────────────┐               ▼
│  Conversation   │       ┌─────────────────┐
├─────────────────┤       │ Vector Index    │
│ id (PK)         │       ├─────────────────┤
│ session_id (FK) │       │ chunk_id        │
│ page_url        │       │ embedding[1536] │
│ selected_text   │       │ metadata        │
│ created_at      │       └─────────────────┘
│ updated_at      │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│    Message      │
├─────────────────┤
│ id (PK)         │
│ conversation_id │
│ role            │
│ content         │
│ citations       │
│ feedback        │
│ created_at      │
└─────────────────┘
```

---

## Postgres Entities

### 1. UserSession

Tracks anonymous user sessions for history and preferences.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Unique session identifier |
| session_token | VARCHAR(64) | UNIQUE, NOT NULL | Browser cookie token |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Session creation time |
| last_active_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last activity timestamp |
| preferences | JSONB | DEFAULT '{}' | User preferences (theme, language) |

**Indexes**:
- `idx_session_token` ON session_token
- `idx_session_last_active` ON last_active_at

**Validation Rules**:
- session_token must be 64 character hex string
- Session expires after 30 days of inactivity

---

### 2. Conversation

A chat session about selected documentation text.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Unique conversation identifier |
| session_id | UUID | FK → UserSession.id, NOT NULL | Owning session |
| page_url | VARCHAR(512) | NOT NULL | Documentation page URL |
| page_title | VARCHAR(256) | | Page title for display |
| selected_text | TEXT | | User-selected context (max 5000 chars) |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Conversation start time |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last message time |

**Indexes**:
- `idx_conversation_session` ON session_id
- `idx_conversation_created` ON created_at DESC

**Validation Rules**:
- selected_text truncated to 5000 characters
- page_url must be valid URL path

**State Transitions**:
- ACTIVE → ARCHIVED (after 24h inactivity or manual archive)

---

### 3. Message

Individual messages within a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Unique message identifier |
| conversation_id | UUID | FK → Conversation.id, NOT NULL | Parent conversation |
| role | VARCHAR(16) | NOT NULL, CHECK IN ('user', 'assistant') | Message author |
| content | TEXT | NOT NULL | Message text content |
| citations | JSONB | DEFAULT '[]' | Array of citation objects |
| tokens_used | INTEGER | | Token count for cost tracking |
| latency_ms | INTEGER | | Response generation time |
| feedback | VARCHAR(16) | CHECK IN ('up', 'down', NULL) | User feedback |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- `idx_message_conversation` ON conversation_id
- `idx_message_created` ON created_at

**Citation Object Schema**:
```json
{
  "text": "quoted passage from documentation",
  "source_url": "/docs/module-1/chapter-2",
  "section_title": "ROS 2 Nodes",
  "relevance": 0.92
}
```

---

### 4. DocumentChunk (Metadata)

Postgres metadata for indexed documentation chunks.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Unique chunk identifier |
| source_url | VARCHAR(512) | NOT NULL | Source documentation URL |
| section_title | VARCHAR(256) | | Section heading |
| content | TEXT | NOT NULL | Chunk text content |
| content_hash | VARCHAR(64) | NOT NULL | SHA-256 hash for change detection |
| chunk_index | INTEGER | NOT NULL | Position within document |
| metadata | JSONB | DEFAULT '{}' | Additional metadata |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Index time |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update time |

**Indexes**:
- `idx_chunk_source` ON source_url
- `idx_chunk_hash` ON content_hash
- `idx_chunk_updated` ON updated_at

**Unique Constraint**: (source_url, chunk_index)

---

### 5. AnalyticsEvent

Anonymized analytics for improving responses.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() | Event identifier |
| event_type | VARCHAR(32) | NOT NULL | Event type (query, feedback, etc.) |
| page_url | VARCHAR(512) | | Documentation page |
| query_hash | VARCHAR(64) | | Hashed query for privacy |
| response_quality | VARCHAR(16) | | Feedback if provided |
| latency_ms | INTEGER | | Response time |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Event timestamp |

**Indexes**:
- `idx_analytics_type` ON event_type
- `idx_analytics_created` ON created_at

---

## Qdrant Vector Collection

### Collection: `documentation`

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Matches DocumentChunk.id |
| vector | float[1536] | text-embedding-3-small embedding |
| payload.source_url | keyword | Documentation URL |
| payload.section_title | text | Section heading |
| payload.content_preview | text | First 200 chars |
| payload.chunk_index | integer | Position in document |
| payload.updated_at | datetime | Last indexed time |

**Configuration**:
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "optimizers_config": {
    "indexing_threshold": 10000
  },
  "hnsw_config": {
    "m": 16,
    "ef_construct": 100
  }
}
```

---

## Database Migrations

### Migration 001: Initial Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- UserSession table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_token VARCHAR(64) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    preferences JSONB DEFAULT '{}'
);

-- Conversation table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES user_sessions(id) ON DELETE CASCADE,
    page_url VARCHAR(512) NOT NULL,
    page_title VARCHAR(256),
    selected_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Message table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    citations JSONB DEFAULT '[]',
    tokens_used INTEGER,
    latency_ms INTEGER,
    feedback VARCHAR(16) CHECK (feedback IN ('up', 'down')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- DocumentChunk table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_url VARCHAR(512) NOT NULL,
    section_title VARCHAR(256),
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    chunk_index INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_url, chunk_index)
);

-- AnalyticsEvent table
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(32) NOT NULL,
    page_url VARCHAR(512),
    query_hash VARCHAR(64),
    response_quality VARCHAR(16),
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_session_token ON user_sessions(session_token);
CREATE INDEX idx_session_last_active ON user_sessions(last_active_at);
CREATE INDEX idx_conversation_session ON conversations(session_id);
CREATE INDEX idx_conversation_created ON conversations(created_at DESC);
CREATE INDEX idx_message_conversation ON messages(conversation_id);
CREATE INDEX idx_message_created ON messages(created_at);
CREATE INDEX idx_chunk_source ON document_chunks(source_url);
CREATE INDEX idx_chunk_hash ON document_chunks(content_hash);
CREATE INDEX idx_analytics_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_created ON analytics_events(created_at);
```

---

## Data Retention Policy

| Entity | Retention | Action |
|--------|-----------|--------|
| UserSession | 30 days inactive | Delete session + cascade |
| Conversation | 90 days | Archive to cold storage |
| Message | With conversation | Cascade delete |
| DocumentChunk | Until doc deleted | Update on reindex |
| AnalyticsEvent | 1 year | Aggregate then delete |
