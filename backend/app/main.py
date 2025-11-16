from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    UploadTextRequest, WikiImportRequest,
    ChatRequest, ChatResponse, FeedbackRequest, StatsResponse,
    RetrievedChunk, ChunkMetadata
)
from . import rag, wiki, store


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

