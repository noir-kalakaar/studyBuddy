# StudyBuddy

Personal RAG assistant that lets you upload your class notes (text or PDF), pull in Wikipedia context, and chat with a Mistral LLM about the combined knowledge base.

## Features

- FastAPI backend with persisted document store (JSON on disk by default).
- Text and PDF ingestion (PDFs are parsed server-side via `pypdf`).
- Optional Wikipedia import (metadata only by default to preserve API quota).
- Retrieval-augmented chat powered by Mistral (`mistral-embed` + `mistral-small-latest`).
- Feedback + stats endpoints to track usage quality.
- React/Vite frontend with Upload, Chat, and Feedback controls.

## Architecture Blueprint

```
┌─────────────┐        POST /api/upload-text|pdf        ┌──────────────┐
│ React/Vite  │ ───────────────────────────────────────▶ │ FastAPI app  │
│ (Upload UI) │◀───────────────────────────────────────┐ │  app/main.py │
└─────┬───────┘                                        │ └─────┬────────┘
      │                                                │       │
      │  POST /api/chat                                │       │
      │                                                ▼       ▼
┌─────┴───────┐                                ┌─────────────────────┐
│ React Chat  │                                │ RAG engine (rag.py) │
│ (Chat.jsx)  │                                │ - chunking          │
└─────────────┘                                │ - embeddings (batch)│
                                               │ - Wikipedia helper  │
                                               └────────┬────────────┘
                                                        │
                                                        ▼
                                               ┌────────────────────┐
                                               │ Mistral API        │
                                               │ (embed + chat)     │
                                               └────────────────────┘
                                                        │
                                                        ▼
                                               ┌────────────────────┐
                                               │ store.py (JSON DB) │
                                               └────────────────────┘
```

## Requirements

- Python 3.11+
- Node.js 18+ / npm 9+
- Mistral API key with access to `mistral-embed` and `mistral-small-latest`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MISTRAL_API_KEY` | **Required.** Secret key issued by Mistral. |
| `AUTO_WIKI_ARTICLES` | Optional. Number of Wikipedia articles to auto-fetch per chat question (defaults to `0`, i.e. disabled). |
| `MAX_DOC_CHUNKS` | Optional. Cap on the number of chunks embedded per document (defaults to `10`). |
| `STUDYBUDDY_STORE_PATH` | Optional. Custom path for the JSON store (defaults to `backend/app/data/store.json`). |

Create `backend/.env` (ignored by Git) and add:

```
MISTRAL_API_KEY=your-key-here
AUTO_WIKI_ARTICLES=0
MAX_DOC_CHUNKS=10
```

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt  # Windows
source .venv/bin/activate && pip install -r requirements.txt  # macOS/Linux
```

Run the server:

```bash
# Windows PowerShell
$env:MISTRAL_API_KEY="your-key"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/docs` for the auto-generated API reference.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```

The Vite dev server prints the local URL (defaults to `http://localhost:3000`). The frontend proxies `/api` calls to the backend automatically.

## Using the App

1. **Upload Text:** Enter a title, choose the source (`user` vs `wikipedia` tag), and paste raw text. Click *Upload Text*.
2. **Upload PDF:** In the second section, pick a title and select a `.pdf` file. The backend extracts text (up to `MAX_DOC_CHUNKS` chunks) and stores embeddings. Error messages (e.g., Mistral rate limits) surface directly in the UI.
3. **Import from Wikipedia:** Provide an article name. By default only the metadata (title + URL) is stored to avoid extra embeddings, but you can re-enable auto-ingest via env vars.
4. **Chat:** On the Chat page, ask questions. The backend retrieves the most relevant chunks, formats a context prompt, and calls `mistral-small-latest` for the answer. You can filter by source (`user`, `wikipedia`) and tweak `top_k`.

## Rate Limits & Resiliency

- Embeddings are **batched** to minimize API calls.
- Each document is truncated to `MAX_DOC_CHUNKS` to avoid draining free quotas on large PDFs.
- When Mistral returns `429 Too Many Requests`, the backend raises a `503` with a human-readable detail; the frontend now surfaces that message directly.
- You can dial `MAX_DOC_CHUNKS` and `AUTO_WIKI_ARTICLES` up/down depending on your plan.

## Testing

```bash
cd backend
.venv\Scripts\python.exe -m pytest
```

The suite covers chunking utilities, persistence logic, and new API endpoints (PDF upload + chat). Add more tests as you extend the RAG engine or introduce new ingestion sources.

## Deployment Notes

- Add production config (e.g., `uvicorn` behind `gunicorn`/`nginx` or Azure App Service) and a build step for the React frontend (`npm run build`). Serve the compiled assets via a static host or behind the same domain as the API.
- Consider Dockerizing (`frontend` + `backend` multi-stage) for smoother deployment.
- For multi-user scenarios, replace the JSON store with a real database (Postgres, Redis, or a vector DB) and add authentication.

## Future Enhancements

- Streaming chat responses and progress indicators for long-running uploads.
- Background job queue for heavy ingestion tasks.
- Multi-tenant storage with per-user namespaces.
- Observability: structured logs, OpenTelemetry traces, and better analytics on retrieved sources.


