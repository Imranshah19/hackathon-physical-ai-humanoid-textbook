# Implementation Plan: RAG Documentation Chatbot

**Branch**: `001-rag-chatbot` | **Date**: 2026-01-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot/spec.md`

## Summary

Build an intelligent documentation assistant embedded in Docusaurus that enables users to select text passages and ask context-aware questions. The system uses RAG (Retrieval-Augmented Generation) with Qdrant Cloud for vector search, Neon Postgres for conversation persistence, and OpenAI Agents/ChatKit for AI orchestration. Responses are grounded solely in selected text and related documentation with inline citations.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend widget)
**Primary Dependencies**: FastAPI 0.109+, OpenAI Agents SDK, Qdrant Client, asyncpg, React 18
**Storage**: Qdrant Cloud (vectors), Neon Postgres (conversations, sessions, analytics)
**Testing**: pytest (backend), Vitest (frontend), Playwright (E2E)
**Target Platform**: Web (Docusaurus 2.x/3.x sites), Cloud deployment (Docker/Kubernetes)
**Project Type**: Web application (backend API + frontend widget)
**Performance Goals**: <3s response time, <2s widget load, 500 concurrent sessions
**Constraints**: No PII storage without consent, answers grounded only in documentation
**Scale/Scope**: Single documentation site, ~10k pages max, 50k monthly users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. ROS 2 Mandatory | N/A | Not robotics control code - documentation chatbot |
| II. Simulation-First | N/A | No robot behaviors - web application |
| III. Physical AI Focus | N/A | Supporting tool for robotics education |
| IV. No Hallucinations | ✅ PASS | RAG grounds all answers in source documentation |
| V. Clear Communication | ✅ PASS | UI provides citations and context visibility |
| VI. RAG Constraint | ✅ PASS | Core feature - answers from selected text only |
| Code Standards | ✅ PASS | Python 3.11+, type hints, docstrings, tests |
| Safety Requirements | N/A | No robot control code |

**Gate Status**: PASSED - Feature aligns with constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── history.py       # Conversation history
│   │   │   └── health.py        # Health checks
│   │   └── middleware/
│   │       ├── cors.py
│   │       └── rate_limit.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py      # Conversation, Message
│   │   ├── document.py          # DocumentChunk, Citation
│   │   └── session.py           # UserSession
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag/
│   │   │   ├── embeddings.py    # Text embedding generation
│   │   │   ├── retriever.py     # Qdrant vector search
│   │   │   └── reranker.py      # Relevance reranking
│   │   ├── chat/
│   │   │   ├── agent.py         # OpenAI Agents orchestration
│   │   │   └── context.py       # Context window management
│   │   └── indexer/
│   │       ├── crawler.py       # Documentation crawler
│   │       └── chunker.py       # Text chunking
│   ├── db/
│   │   ├── __init__.py
│   │   ├── postgres.py          # Neon Postgres connection
│   │   └── qdrant.py            # Qdrant Cloud connection
│   └── config.py                # Settings and env vars
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.tsx       # Main floating widget
│   │   ├── ChatPanel.tsx        # Chat interface
│   │   ├── MessageList.tsx      # Message display
│   │   ├── ContextDisplay.tsx   # Selected text display
│   │   └── CitationLink.tsx     # Citation components
│   ├── hooks/
│   │   ├── useChat.ts           # Chat API hook
│   │   ├── useSelection.ts      # Text selection hook
│   │   └── useHistory.ts        # History management
│   ├── services/
│   │   └── api.ts               # Backend API client
│   ├── styles/
│   │   └── widget.css           # Theme-aware styles
│   └── index.tsx                # Entry point
├── tests/
│   └── components/
├── package.json
└── tsconfig.json

docusaurus-plugin/
├── src/
│   ├── index.ts                 # Plugin entry
│   └── theme/
│       └── ChatWidgetWrapper.tsx
├── package.json
└── README.md
```

**Structure Decision**: Web application structure with separate backend (FastAPI) and frontend (React widget). The Docusaurus plugin wraps the frontend widget for easy integration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Docusaurus Site                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  Chat Widget (React)                      │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │    │
│  │  │Selection │  │  Chat    │  │    History Panel     │   │    │
│  │  │ Capture  │  │  Panel   │  │                      │   │    │
│  │  └────┬─────┘  └────┬─────┘  └──────────────────────┘   │    │
│  └───────┼─────────────┼────────────────────────────────────┘    │
└──────────┼─────────────┼────────────────────────────────────────┘
           │             │
           ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  /chat      │  │  /history   │  │   /index (webhook)      │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│  ┌──────▼──────────────────────────────────────▼─────────────┐  │
│  │                    Services Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │
│  │  │ RAG      │  │ Chat     │  │ Indexer  │  │ Session  │   │  │
│  │  │ Pipeline │  │ Agent    │  │ Service  │  │ Manager  │   │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │  │
│  └───────┼─────────────┼─────────────┼─────────────┼─────────┘  │
└──────────┼─────────────┼─────────────┼─────────────┼────────────┘
           │             │             │             │
     ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
     │  Qdrant   │ │  OpenAI   │ │  Qdrant   │ │   Neon    │
     │  Cloud    │ │  Agents   │ │  Cloud    │ │ Postgres  │
     │ (vectors) │ │  (LLM)    │ │ (vectors) │ │ (data)    │
     └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

## Complexity Tracking

> No violations requiring justification.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |
