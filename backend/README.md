# RAG Documentation Chatbot Backend

FastAPI backend for the RAG documentation chatbot.

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -e ".[dev]"
```

## Run

```bash
uvicorn src.main:app --reload
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.
