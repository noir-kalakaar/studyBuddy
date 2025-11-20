import io
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from pypdf import PdfReader  # type: ignore[import-not-found]

from .models import (
    UploadTextRequest, WikiImportRequest,
    ChatRequest, ChatResponse, FeedbackRequest, StatsResponse,
    RetrievedChunk, ChunkMetadata
)
from . import rag, wiki, store


logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload-text")
async def upload_text(req: UploadTextRequest):
    await rag.store_text(req.title, req.text, req.source)
    return {"status": "ok"}


@app.post("/api/upload-pdf")
async def upload_pdf(title: str = Form(...), file: UploadFile = File(...)):
    """
    Accept a PDF file upload, extract text, and store it as a 'user' document.
    """
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    raw_bytes = await file.read()
    reader = PdfReader(io.BytesIO(raw_bytes))
    pages_text = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            continue
    full_text = "\n\n".join(pages_text)

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    logger.info(
        "Storing PDF '%s' with %d extracted characters",
        title,
        len(full_text),
    )
    await rag.store_text(title=title, text=full_text, source="user")
    return {"status": "ok"}


@app.post("/api/import-wiki")
async def import_wiki(req: WikiImportRequest):
    info = await wiki.import_wiki_article(req.query)
    return info


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    store.increment_questions_count()
    answer, top_scored = await rag.rag_answer(
        question=req.question,
        top_k=req.top_k,
        sources=req.sources,
    )
    context = [
        RetrievedChunk(
            id=d.id,
            text=d.text,
            source=d.source,
            score=score,
            meta=ChunkMetadata(title=d.title, url=d.url),
        )
        for score, d in top_scored
    ]
    return ChatResponse(answer=answer, context=context)


@app.post("/api/feedback")
async def feedback(req: FeedbackRequest):
    store.add_feedback(
        question=req.question,
        answer=req.answer,
        rating=req.rating,
        comment=req.comment
    )
    return {"status": "ok"}


@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    stats_dict = store.get_stats()
    return StatsResponse(**stats_dict)

