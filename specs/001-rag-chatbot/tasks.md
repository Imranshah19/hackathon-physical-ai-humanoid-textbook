# Tasks: RAG Documentation Chatbot

**Input**: Design documents from `/specs/001-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Not explicitly requested - tests omitted (add with TDD approach if needed)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1, US2, US3, US4)
- Exact file paths included

## Path Conventions

- **Backend**: `backend/src/` (FastAPI)
- **Frontend**: `frontend/src/` (React widget)
- **Plugin**: `docusaurus-plugin/src/` (Docusaurus integration)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure per plan.md (backend/, frontend/, docusaurus-plugin/)
- [x] T002 [P] Initialize backend Python project with pyproject.toml (FastAPI 0.109+, asyncpg, qdrant-client, openai)
- [x] T003 [P] Initialize frontend React project with package.json (React 18, TypeScript 5.x)
- [x] T004 [P] Initialize docusaurus-plugin with package.json
- [x] T005 [P] Configure backend linting (ruff) and formatting (black) in pyproject.toml
- [x] T006 [P] Configure frontend linting (eslint) and formatting (prettier) in package.json
- [x] T007 Create backend/.env.example with all required environment variables
- [x] T008 [P] Create backend Dockerfile for containerized deployment
- [x] T009 [P] Create docker-compose.yml for local development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Connections

- [x] T010 Create database connection module in backend/src/db/postgres.py (Neon Postgres async pool)
- [x] T011 [P] Create vector database connection in backend/src/db/qdrant.py (Qdrant Cloud client)
- [x] T012 Create Alembic migrations directory and initial migration from data-model.md in backend/alembic/

### Configuration

- [x] T013 Implement settings management in backend/src/config.py (pydantic-settings, env vars)

### Base Models

- [x] T014 Create UserSession model in backend/src/models/session.py (session_token, preferences)
- [x] T015 [P] Create base Pydantic schemas in backend/src/models/__init__.py (request/response base classes)

### API Infrastructure

- [x] T016 Create FastAPI application entry point in backend/src/main.py (lifespan, exception handlers)
- [x] T017 [P] Implement CORS middleware in backend/src/api/middleware/cors.py
- [x] T018 [P] Implement rate limiting middleware in backend/src/api/middleware/rate_limit.py (token bucket per session)
- [x] T019 Create health check endpoint in backend/src/api/routes/health.py (database connectivity checks)
- [x] T020 Create session management service in backend/src/services/session.py (create/get/update session)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Ask About Selected Text (Priority: P1) 🎯 MVP

**Goal**: User selects text, asks question, receives grounded AI response with citations

**Independent Test**: Select documentation text, ask "Explain this", verify response includes citations to selected text

### Backend Implementation for US1

- [x] T021 [P] [US1] Create Conversation model in backend/src/models/conversation.py (session_id, page_url, selected_text)
- [x] T022 [P] [US1] Create Message model in backend/src/models/conversation.py (role, content, citations JSONB)
- [x] T023 [P] [US1] Create Citation schema in backend/src/models/document.py (text, source_url, relevance)
- [x] T024 [US1] Create ChatRequest/ChatResponse schemas in backend/src/models/conversation.py
- [x] T025 [US1] Implement context window management in backend/src/services/chat/context.py (selected text + message history)
- [x] T026 [US1] Implement OpenAI Agents chat service in backend/src/services/chat/agent.py (tool calling, structured output)
- [x] T027 [US1] Implement POST /chat endpoint in backend/src/api/routes/chat.py (sync response)
- [x] T028 [US1] Implement POST /chat/stream endpoint in backend/src/api/routes/chat.py (SSE streaming)
- [x] T029 [US1] Add citation extraction from agent response in backend/src/services/chat/agent.py

### Frontend Implementation for US1

- [x] T030 [P] [US1] Create API client service in frontend/src/services/api.ts (fetch wrapper, SSE handling)
- [x] T031 [P] [US1] Implement useSelection hook in frontend/src/hooks/useSelection.ts (Selection API, debounce)
- [x] T032 [P] [US1] Implement useChat hook in frontend/src/hooks/useChat.ts (send message, handle stream)
- [x] T033 [US1] Create ContextDisplay component in frontend/src/components/ContextDisplay.tsx (show selected text)
- [x] T034 [US1] Create MessageList component in frontend/src/components/MessageList.tsx (render messages)
- [x] T035 [US1] Create CitationLink component in frontend/src/components/CitationLink.tsx (clickable source links)
- [x] T036 [US1] Create ChatPanel component in frontend/src/components/ChatPanel.tsx (input, messages, context)
- [x] T037 [US1] Create ChatWidget component in frontend/src/components/ChatWidget.tsx (floating button, panel toggle)
- [x] T038 [US1] Create widget entry point in frontend/src/index.tsx (Shadow DOM mount)
- [x] T039 [US1] Create theme-aware styles in frontend/src/styles/widget.css (light/dark mode)

### Docusaurus Plugin for US1

- [x] T040 [US1] Create plugin entry in docusaurus-plugin/src/index.ts (lifecycle hooks)
- [x] T041 [US1] Create ChatWidgetWrapper in docusaurus-plugin/src/theme/ChatWidgetWrapper.tsx (inject widget)
- [x] T042 [US1] Add plugin README with installation instructions in docusaurus-plugin/README.md

**Checkpoint**: User Story 1 complete - can select text, ask questions, receive cited responses

---

## Phase 4: User Story 2 - Follow-up Conversation (Priority: P2)

**Goal**: User can ask follow-up questions with maintained conversation context

**Independent Test**: Ask initial question, then 2-3 follow-ups, verify context maintained

### Backend Implementation for US2

- [ ] T043 [US2] Extend context service for multi-turn history in backend/src/services/chat/context.py (20 turn limit)
- [ ] T044 [US2] Add conversation_id tracking in chat endpoints in backend/src/api/routes/chat.py
- [ ] T045 [US2] Implement conversation state persistence in backend/src/services/chat/agent.py
- [ ] T046 [US2] Add tokens_used and latency_ms tracking to Message in backend/src/models/conversation.py
- [ ] T047 [P] [US2] Implement feedback endpoint POST /messages/{id}/feedback in backend/src/api/routes/chat.py

### Frontend Implementation for US2

- [ ] T048 [US2] Update useChat hook for conversation continuity in frontend/src/hooks/useChat.ts
- [ ] T049 [US2] Add "New Conversation" button to ChatPanel in frontend/src/components/ChatPanel.tsx
- [ ] T050 [US2] Add feedback buttons (thumbs up/down) to MessageList in frontend/src/components/MessageList.tsx

**Checkpoint**: User Story 2 complete - multi-turn conversations work with context

---

## Phase 5: User Story 3 - Expand Search Beyond Selection (Priority: P3)

**Goal**: AI retrieves related documentation via vector search when question requires broader context

**Independent Test**: Select narrow snippet, ask broad question, verify additional sources cited

### Backend Implementation for US3

- [ ] T051 [P] [US3] Create DocumentChunk model in backend/src/models/document.py (source_url, content_hash, embedding)
- [ ] T052 [US3] Implement text chunking service in backend/src/services/indexer/chunker.py (512 tokens, 50 overlap)
- [ ] T053 [US3] Implement documentation crawler in backend/src/services/indexer/crawler.py (fetch pages, extract text)
- [ ] T054 [US3] Implement embedding generation in backend/src/services/rag/embeddings.py (text-embedding-3-small)
- [ ] T055 [US3] Implement Qdrant vector upsert/search in backend/src/services/rag/retriever.py (top-k retrieval)
- [ ] T056 [US3] Implement relevance reranking in backend/src/services/rag/reranker.py (cross-encoder or heuristic)
- [ ] T057 [US3] Create indexing orchestration service in backend/src/services/indexer/__init__.py (crawl, chunk, embed, store)
- [ ] T058 [US3] Implement POST /index/webhook endpoint in backend/src/api/routes/index.py (trigger reindex)
- [ ] T059 [US3] Integrate RAG retrieval into chat agent in backend/src/services/chat/agent.py (search_documentation tool)
- [ ] T060 [US3] Add CLI command for manual indexing in backend/src/cli.py

### Frontend Implementation for US3

- [ ] T061 [US3] Update CitationLink to distinguish primary vs expanded sources in frontend/src/components/CitationLink.tsx
- [ ] T062 [US3] Add "Sources" section to message display in frontend/src/components/MessageList.tsx

**Checkpoint**: User Story 3 complete - RAG retrieval expands answers beyond selected text

---

## Phase 6: User Story 4 - Chat History Persistence (Priority: P4)

**Goal**: Users can view and resume past conversations

**Independent Test**: Have conversation, close browser, return, verify history accessible and resumable

### Backend Implementation for US4

- [ ] T063 [US4] Implement GET /conversations endpoint in backend/src/api/routes/history.py (list by session)
- [ ] T064 [US4] Implement GET /conversations/{id} endpoint in backend/src/api/routes/history.py (with messages)
- [ ] T065 [US4] Implement DELETE /conversations/{id} endpoint in backend/src/api/routes/history.py
- [ ] T066 [US4] Implement GET /conversations/{id}/export endpoint in backend/src/api/routes/history.py (markdown)
- [ ] T067 [US4] Add conversation archival logic in backend/src/services/session.py (24h inactivity)

### Frontend Implementation for US4

- [ ] T068 [P] [US4] Implement useHistory hook in frontend/src/hooks/useHistory.ts (fetch, delete, export)
- [ ] T069 [US4] Create HistoryPanel component in frontend/src/components/HistoryPanel.tsx (list conversations)
- [ ] T070 [US4] Create HistoryItem component in frontend/src/components/HistoryItem.tsx (title, date, actions)
- [ ] T071 [US4] Add history toggle to ChatWidget in frontend/src/components/ChatWidget.tsx
- [ ] T072 [US4] Implement "Continue conversation" flow in frontend/src/hooks/useChat.ts
- [ ] T073 [US4] Add localStorage session persistence in frontend/src/services/api.ts

**Checkpoint**: User Story 4 complete - full history management works

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Analytics & Monitoring

- [ ] T074 [P] Create AnalyticsEvent model in backend/src/models/analytics.py
- [ ] T075 Implement analytics logging service in backend/src/services/analytics.py (anonymized events)
- [ ] T076 Add analytics event emission to chat endpoints in backend/src/api/routes/chat.py

### Performance & Reliability

- [ ] T077 Add response caching for repeated queries in backend/src/services/chat/agent.py
- [ ] T078 Implement graceful degradation when Qdrant unavailable in backend/src/services/rag/retriever.py
- [ ] T079 Add connection pooling configuration in backend/src/db/postgres.py
- [ ] T080 Optimize frontend bundle size in frontend/package.json (tree shaking, code splitting)

### Documentation & DevEx

- [ ] T081 [P] Update quickstart.md with final setup instructions in specs/001-rag-chatbot/quickstart.md
- [ ] T082 [P] Create API documentation with examples in backend/docs/api.md
- [ ] T083 Run quickstart.md validation (full local setup test)

### Security

- [ ] T084 Add input sanitization for selected_text in backend/src/api/routes/chat.py
- [ ] T085 Implement session token rotation in backend/src/services/session.py
- [ ] T086 Add rate limit headers to API responses in backend/src/api/middleware/rate_limit.py

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───────────────────────────────────────────────┐
│  User Stories can proceed in parallel         │
│  or sequentially by priority                  │
│                                               │
│  US1 (P1) ─┐                                  │
│  US2 (P2) ─┼── All depend on Phase 2 only    │
│  US3 (P3) ─┤                                  │
│  US4 (P4) ─┘                                  │
└───────────────────────────────────────────────┘
    ↓
Phase 7 (Polish) ← After desired stories complete
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (P1) | Phase 2 only | T020 complete |
| US2 (P2) | Phase 2 only | T020 complete (can parallel with US1) |
| US3 (P3) | Phase 2 only | T020 complete (can parallel with US1/US2) |
| US4 (P4) | Phase 2 only | T020 complete (can parallel with others) |

### Within Each Phase

- Tasks marked [P] can run in parallel
- Models before services
- Services before endpoints
- Backend before frontend (for API contracts)

---

## Parallel Execution Examples

### Phase 1 Parallel (5 tasks simultaneously)

```
T002: Initialize backend pyproject.toml
T003: Initialize frontend package.json
T004: Initialize docusaurus-plugin package.json
T005: Configure backend linting
T006: Configure frontend linting
```

### Phase 2 Parallel (after T010)

```
T011: Qdrant connection
T017: CORS middleware
T018: Rate limit middleware
```

### US1 Backend Models Parallel

```
T021: Conversation model
T022: Message model
T023: Citation schema
```

### US1 Frontend Parallel

```
T030: API client service
T031: useSelection hook
T032: useChat hook
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (T001-T009)
2. ✅ Complete Phase 2: Foundational (T010-T020)
3. ✅ Complete Phase 3: User Story 1 (T021-T042)
4. **STOP and VALIDATE**: Test US1 independently
5. Deploy/demo MVP with core Q&A functionality

### Incremental Delivery

| Increment | Stories | Value Delivered |
|-----------|---------|-----------------|
| MVP | US1 | Basic Q&A on selected text |
| v1.1 | US1 + US2 | Multi-turn conversations |
| v1.2 | US1 + US2 + US3 | RAG-expanded answers |
| v1.3 | All stories | Full history persistence |

### Estimated Task Counts

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Setup | 9 | 6 |
| Foundational | 11 | 4 |
| US1 | 22 | 10 |
| US2 | 8 | 1 |
| US3 | 12 | 2 |
| US4 | 11 | 1 |
| Polish | 13 | 3 |
| **Total** | **86** | **27** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story
- Each user story independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
