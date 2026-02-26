# Physical AI & Humanoid Robotics Textbook

An interactive, AI-powered textbook for learning physical AI and humanoid robotics, featuring an embedded RAG chatbot that answers questions about book content.

## Hackathon Deliverables

| Deliverable | Status | Description |
|------------|--------|-------------|
| **Textbook** | ✅ Complete | 4 modules in Docusaurus |
| **RAG Chatbot** | ✅ Complete | Embedded in book with context-aware QA |
| **Backend** | ✅ Complete | FastAPI with embeddings, retrieval, inference |
| **Vector DB** | ✅ Ready | Qdrant Cloud integration |
| **Postgres** | ✅ Ready | Neon serverless for metadata |
| **Deployment** | ✅ Ready | GitHub Pages + Railway/Render |

## Tech Stack

- **Frontend**: Docusaurus 3.0 + React Chat Widget
- **Backend**: FastAPI + SQLAlchemy (async)
- **RAG**: OpenAI Embeddings + Qdrant Vector Search
- **Database**: Neon Postgres (metadata) + Qdrant Cloud (vectors)
- **Inference**: OpenAI GPT-4o-mini

## Quick Start

### Prerequisites

- Node.js 20 LTS
- Python 3.11+
- Accounts: OpenAI, Qdrant Cloud, Neon

### 1. Clone and Configure

```bash
git clone <repository-url>
cd hackathon-physical-ai-humanoid-textbook

# Copy environment template
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Copy backend env
cp .env.example .env
# Edit with your credentials

# Run database migrations
alembic upgrade head

# Start backend
uvicorn src.main:app --reload --port 8000
```

### 3. Ingest Book Content

```bash
# With backend venv active
python -m src.scripts.ingest_book --book-path ../book

# Force re-ingest all content
python -m src.scripts.ingest_book --force
```

### 4. Website Setup

```bash
cd website
npm install

# Build the plugin
cd ../docusaurus-plugin
npm install
npm run build

# Start website
cd ../website
npm run start
```

Open http://localhost:3000 to view the textbook with embedded chatbot.

## Configuration

### Required Environment Variables

Create `.env` in the project root:

```bash
# OpenAI (get from platform.openai.com)
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud (get from cloud.qdrant.io)
QDRANT_URL=https://your-cluster.region.aws.qdrant.io
QDRANT_API_KEY=your-api-key

# Neon Postgres (get from neon.tech)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
```

### Setting Up Cloud Services

#### Qdrant Cloud (Free Tier)
1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free cluster
3. Copy the URL and API key from dashboard

#### Neon Postgres (Free Tier)
1. Go to [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string (use asyncpg format)

#### OpenAI API
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Ensure you have credits (embeddings are cheap)

## Project Structure

```
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── api/routes/    # API endpoints (chat, health)
│   │   ├── services/chat/ # RAG agent, retrieval, context
│   │   ├── db/            # Postgres & Qdrant connections
│   │   └── scripts/       # Book ingestion script
│   └── alembic/           # Database migrations
├── book/                  # Textbook content (4 modules)
│   ├── module-1/          # ROS 2 Foundations
│   ├── module-2/          # Digital Twins
│   ├── module-3/          # Isaac & RL
│   └── module-4/          # VLA Models
├── website/               # Docusaurus site
├── docusaurus-plugin/     # RAG chatbot plugin
├── frontend/              # Chat widget component
└── specs/                 # Feature specifications
```

## RAG Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│   ┌─────────────┐    ┌─────────────────────────────────┐   │
│   │  Docusaurus │───▶│   Chat Widget (React)           │   │
│   │  Textbook   │    │   - Text selection context      │   │
│   └─────────────┘    │   - Streaming responses         │   │
│                      └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  /api/chat  │───▶│  Retrieval  │───▶│  Chat Agent │    │
│   │  endpoint   │    │  Service    │    │  (OpenAI)   │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│                              │                              │
│                              ▼                              │
│   ┌─────────────────────────────────────────────────────┐  │
│   │            Context Builder                           │  │
│   │   RAG Context + Selected Text + History             │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASES                              │
│   ┌─────────────────┐        ┌─────────────────┐           │
│   │  Qdrant Cloud   │        │  Neon Postgres  │           │
│   │  (Vectors)      │        │  (Metadata)     │           │
│   │  - Embeddings   │        │  - Conversations│           │
│   │  - Similarity   │        │  - Sessions     │           │
│   └─────────────────┘        └─────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Textbook Modules

### Module 1: ROS 2 Nervous System (2 weeks)
- ROS 2 architecture and DDS
- Nodes, topics, messages
- Services and actions
- URDF/XACRO robot descriptions
- Launch files and parameters
- Lifecycle nodes

### Module 2: Digital Twin Development (2 weeks)
- Gazebo world setup
- Robot spawning and simulation
- Sensor simulation (LiDAR, RGB-D, IMU)
- Unity integration
- Domain randomization

### Module 3: Isaac Brain (3 weeks)
- NVIDIA Isaac Sim setup
- Isaac Gym fundamentals
- Reinforcement learning for locomotion
- PPO training
- Sim-to-real transfer

### Module 4: Vision-Language-Action (2 weeks)
- VLM foundations
- Action tokenization
- Language grounding
- VLA pipeline integration
- ROS 2 deployment

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message, get RAG response |
| `/api/v1/chat/stream` | POST | Streaming chat response (SSE) |
| `/api/v1/messages/{id}/feedback` | POST | Submit message feedback |
| `/api/v1/health` | GET | Health check |

## Deployment

### GitHub Pages (Textbook)

The website auto-deploys via GitHub Actions:

```bash
git push origin main  # Triggers deploy-docs.yml
```

### Backend (Railway/Render)

```bash
# Railway
railway up

# Or Render - connect via dashboard
```

Set environment variables in your deployment platform.

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Quality

```bash
# Backend
cd backend
black src/
ruff check src/
mypy src/

# Frontend
cd frontend
npm run lint
npm run format
```

## Capstone Project

The textbook culminates in building a humanoid robot that can:

1. **Receive** a voice command ("Pick up the red cup")
2. **Plan** the task sequence
3. **Navigate** to the target location
4. **Perceive** and localize the object
5. **Execute** the manipulation

## Hardware References

| Component | Purpose |
|-----------|---------|
| Jetson Orin Nano/NX | Edge AI inference |
| Intel RealSense D435i | RGB-D perception |
| USB IMU | Inertial measurement |
| RTX GPU Workstation | Training and simulation |
| Unitree Go2/G1 | Optional physical robot |

## License

MIT License
