# Quickstart: RAG Documentation Chatbot

**Feature**: 001-rag-chatbot
**Date**: 2026-01-08

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for local development)
- Accounts: OpenAI, Qdrant Cloud, Neon Postgres

## Environment Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <repo-url>
cd rag-chatbot

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Frontend setup
cd ../frontend
npm install

# Docusaurus plugin
cd ../docusaurus-plugin
npm install
npm link
```

### 2. Environment Variables

Create `.env` file in `backend/`:

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant Cloud
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=...

# Neon Postgres
DATABASE_URL=postgresql://user:pass@xxx.neon.tech/dbname?sslmode=require

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### 3. Database Setup

```bash
# Run migrations
cd backend
alembic upgrade head
```

### 4. Initial Indexing

```bash
# Index sample documentation
python -m src.cli index --url https://your-docs-site.com
```

## Running Locally

### Start Backend

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

### Start Frontend (Standalone)

```bash
cd frontend
npm run dev
```

Widget preview at: http://localhost:5173

### Docusaurus Integration

```bash
# In your Docusaurus project
npm link @your-org/docusaurus-plugin-rag-chat

# Add to docusaurus.config.js
plugins: [
  ['@your-org/docusaurus-plugin-rag-chat', {
    apiEndpoint: 'http://localhost:8000/v1'
  }]
]

# Start Docusaurus
npm start
```

## Quick Test

### Test Chat API

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: $(openssl rand -hex 32)" \
  -d '{
    "message": "What is ROS 2?",
    "selected_text": "ROS 2 is the second generation of the Robot Operating System...",
    "page_url": "/docs/module-1/chapter-1"
  }'
```

### Test Streaming

```bash
curl -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-Session-Token: $(openssl rand -hex 32)" \
  -d '{
    "message": "Explain this in simpler terms",
    "selected_text": "The DDS middleware provides..."
  }'
```

## Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── api/          # FastAPI routes
│   │   ├── models/       # Pydantic models
│   │   ├── services/     # Business logic
│   │   ├── db/           # Database clients
│   │   └── config.py     # Settings
│   ├── tests/
│   ├── alembic/          # Migrations
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API client
│   └── package.json
└── docusaurus-plugin/
    └── src/              # Plugin source
```

## Key Commands

| Command | Description |
|---------|-------------|
| `uvicorn src.main:app --reload` | Start backend dev server |
| `npm run dev` | Start frontend dev server |
| `pytest` | Run backend tests |
| `npm test` | Run frontend tests |
| `alembic upgrade head` | Apply migrations |
| `python -m src.cli index` | Reindex documentation |

## Configuration Options

### Backend (`config.py`)

```python
class Settings(BaseSettings):
    # API
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_window: int = 60

    # RAG
    embedding_model: str = "text-embedding-3-small"
    retrieval_top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 50
```

### Frontend Widget

```typescript
interface WidgetConfig {
  apiEndpoint: string;
  position: 'bottom-right' | 'bottom-left';
  theme: 'auto' | 'light' | 'dark';
  placeholder: string;
  welcomeMessage: string;
}
```

## Deployment

### Docker

```bash
# Build images
docker build -t rag-chatbot-backend ./backend
docker build -t rag-chatbot-frontend ./frontend

# Run with compose
docker-compose up -d
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable HTTPS
- [ ] Configure monitoring (OpenTelemetry)
- [ ] Set up backup for Postgres
- [ ] Configure CDN for frontend assets

## Troubleshooting

### Common Issues

**"Connection refused" to Qdrant**
- Check QDRANT_URL and QDRANT_API_KEY
- Verify collection exists: `python -m src.cli check-qdrant`

**"Rate limit exceeded"**
- Increase rate limits in config
- Check OpenAI API quota

**Widget not appearing**
- Check browser console for errors
- Verify apiEndpoint is correct
- Check CORS configuration

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=DEBUG uvicorn src.main:app --reload
```

## Next Steps

1. Index your documentation: `python -m src.cli index --url <docs-url>`
2. Customize widget styling in `frontend/src/styles/widget.css`
3. Set up CI/CD webhooks for automatic reindexing
4. Configure analytics dashboard
