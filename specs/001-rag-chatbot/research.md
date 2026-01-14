# Research: RAG Documentation Chatbot

**Feature**: 001-rag-chatbot
**Date**: 2026-01-08
**Status**: Complete

## Overview

This document captures research findings and technology decisions for the RAG Documentation Chatbot implementation.

---

## 1. OpenAI Agents / ChatKit Integration

### Decision
Use **OpenAI Agents SDK** with tool-calling for RAG orchestration.

### Rationale
- Native support for multi-turn conversations with context management
- Built-in tool-calling enables RAG retrieval as a tool
- Streaming responses for better UX (<3s perceived latency)
- Function calling for structured citation extraction
- ChatKit provides React components that can be adapted for Docusaurus

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| LangChain | Heavier abstraction layer, more complexity than needed |
| LlamaIndex | Good for RAG but less flexible for agent orchestration |
| Raw OpenAI API | Would require building conversation management from scratch |
| Anthropic Claude | Good alternative but OpenAI Agents specified in requirements |

### Implementation Notes
```python
# Agent configuration pattern
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_documentation",
            "description": "Search related documentation sections",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 5}
                }
            }
        }
    }
]
```

---

## 2. Qdrant Cloud Vector Database

### Decision
Use **Qdrant Cloud** with `text-embedding-3-small` embeddings (1536 dimensions).

### Rationale
- Managed service reduces operational burden
- Excellent Python client with async support
- Hybrid search (dense + sparse) for better retrieval
- Built-in filtering for document source/section
- Cost-effective for documentation scale (~10k pages)

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Pinecone | Higher cost, less flexible filtering |
| Weaviate | Self-hosted complexity not justified |
| pgvector | Good but Qdrant's hybrid search superior for RAG |
| ChromaDB | Not production-ready for cloud deployment |

### Configuration
```python
# Qdrant collection schema
{
    "name": "documentation",
    "vectors": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "source_url": "keyword",
        "section_title": "text",
        "content_hash": "keyword",
        "updated_at": "datetime"
    }
}
```

### Chunking Strategy
- **Chunk size**: 512 tokens with 50 token overlap
- **Metadata**: source URL, section hierarchy, content hash
- **Update strategy**: Content hash comparison for incremental updates

---

## 3. Neon Postgres Database

### Decision
Use **Neon Postgres** (serverless) for conversation and session data.

### Rationale
- Serverless scales to zero when not in use (cost-efficient)
- Standard Postgres compatibility with asyncpg
- Branching for dev/staging environments
- Connection pooling built-in
- JSONB for flexible message metadata

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Supabase | More features than needed, higher cost |
| PlanetScale | MySQL-based, prefer Postgres ecosystem |
| CockroachDB | Overkill for single-region deployment |
| SQLite | Not suitable for multi-instance deployment |

### Schema Approach
- Use SQLAlchemy 2.0 with async support
- Migrations via Alembic
- JSONB for citations and metadata storage
- UUID primary keys for distributed safety

---

## 4. Docusaurus Integration

### Decision
Build a **standalone React widget** distributed as an **npm package** with a thin Docusaurus plugin wrapper.

### Rationale
- Widget can work on any site, not just Docusaurus
- Docusaurus plugin provides seamless theme integration
- Shadow DOM isolation prevents CSS conflicts
- Dynamic loading keeps initial bundle small

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| Docusaurus theme component | Tightly coupled, harder to maintain |
| iframe embed | Poor UX, cross-origin issues |
| Web Component | Browser support concerns, React ecosystem preferred |

### Integration Pattern
```typescript
// docusaurus.config.js
plugins: [
  ['@your-org/docusaurus-plugin-rag-chat', {
    apiEndpoint: 'https://api.yoursite.com',
    position: 'bottom-right',
    theme: 'auto' // follows Docusaurus light/dark
  }]
]
```

---

## 5. Text Selection Capture

### Decision
Use **Selection API** with debounced capture and floating action button.

### Rationale
- Native browser API, no dependencies
- Works across all modern browsers
- Can capture selection range for scroll-to-source
- Floating button appears only on valid selection

### Implementation Pattern
```typescript
// Selection hook
const useSelection = () => {
  const [selection, setSelection] = useState<SelectionData | null>(null);

  useEffect(() => {
    const handler = debounce(() => {
      const sel = window.getSelection();
      if (sel && sel.toString().trim().length >= 10) {
        setSelection({
          text: sel.toString().slice(0, 5000),
          range: sel.getRangeAt(0),
          sourceUrl: window.location.pathname
        });
      }
    }, 200);

    document.addEventListener('selectionchange', handler);
    return () => document.removeEventListener('selectionchange', handler);
  }, []);

  return selection;
};
```

---

## 6. Citation Generation

### Decision
Use **structured output** from OpenAI to extract citations with source URLs.

### Rationale
- Guaranteed JSON structure for citations
- Can include relevance scores
- Links back to exact documentation sections
- Enables citation verification

### Output Schema
```json
{
  "answer": "The robot uses...",
  "citations": [
    {
      "text": "quoted passage",
      "source_url": "/docs/chapter-3/section-2",
      "section_title": "Motor Control",
      "relevance": 0.92
    }
  ],
  "confidence": 0.85
}
```

---

## 7. Streaming Response Strategy

### Decision
Use **Server-Sent Events (SSE)** for streaming responses.

### Rationale
- Native browser support, no WebSocket complexity
- Works through CDNs and proxies
- FastAPI has built-in SSE support
- Can stream tokens as they're generated

### Alternatives Considered
| Alternative | Reason Rejected |
|-------------|-----------------|
| WebSocket | Overkill for one-way streaming |
| Long polling | Higher latency, more connections |
| HTTP/2 streaming | Less browser support |

### Implementation
```python
# FastAPI SSE endpoint
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        async for chunk in agent.stream_response(request):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

## 8. Session Management

### Decision
Use **anonymous sessions** with optional browser storage persistence.

### Rationale
- No authentication barrier for documentation users
- LocalStorage for conversation history
- Session ID in cookie for server-side tracking
- GDPR-compliant (no PII stored)

### Session Flow
1. First visit: Generate UUID session ID, store in cookie
2. Conversation: Associate messages with session ID
3. History: Query by session ID from Postgres
4. Privacy: User can clear history (deletes from DB)

---

## 9. Documentation Indexing

### Decision
**Webhook-triggered** indexing with incremental updates.

### Rationale
- CI/CD can trigger reindex on doc changes
- Content hashing avoids reprocessing unchanged content
- Batch processing for efficiency
- Queue-based for reliability

### Indexing Pipeline
1. **Crawl**: Fetch updated documentation pages
2. **Parse**: Extract text, code blocks, headers
3. **Chunk**: Split into 512-token segments
4. **Hash**: Compare with existing chunks
5. **Embed**: Generate vectors for new/changed chunks
6. **Upsert**: Update Qdrant collection

---

## 10. Rate Limiting & Cost Control

### Decision
**Token bucket** rate limiting per session with daily quotas.

### Rationale
- Prevents abuse without blocking legitimate users
- Per-session limits (not IP) for shared networks
- Daily quota controls OpenAI API costs
- Graceful degradation with queue

### Limits
| Tier | Requests/min | Tokens/day |
|------|--------------|------------|
| Anonymous | 10 | 50,000 |
| Authenticated | 30 | 200,000 |

---

## Summary of Key Decisions

| Component | Technology | Key Reason |
|-----------|------------|------------|
| AI Orchestration | OpenAI Agents SDK | Native tool-calling, streaming |
| Vector DB | Qdrant Cloud | Hybrid search, managed service |
| Relational DB | Neon Postgres | Serverless, Postgres compatibility |
| Frontend | React Widget | Portable, theme-aware |
| Integration | Docusaurus Plugin | Seamless DX |
| Streaming | SSE | Simple, native support |
| Embeddings | text-embedding-3-small | Cost-effective, good quality |
| Sessions | Anonymous + Cookie | No auth barrier |

---

## Open Questions (Resolved)

All initial unknowns have been resolved through this research phase.

| Question | Resolution |
|----------|------------|
| Which embedding model? | text-embedding-3-small (1536d) |
| How to handle multi-turn context? | OpenAI Agents with conversation history |
| Widget isolation? | Shadow DOM in React component |
| Incremental indexing? | Content hash comparison |
