from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class UploadTextRequest(BaseModel):
    title: str
    text: str
    source: str = "user"  # "user" or "wikipedia"


class WikiImportRequest(BaseModel):
    query: str


class ChatRequest(BaseModel):
    question: str
    top_k: int = 3
    sources: Optional[List[str]] = None  # ["user", "wikipedia"]


class ChunkMetadata(BaseModel):
    title: str
    url: Optional[str] = None


class RetrievedChunk(BaseModel):
    id: UUID
    text: str
    source: str
    score: float
    meta: ChunkMetadata


class ChatResponse(BaseModel):
    answer: str
    context: List[RetrievedChunk]


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: int  # +1 or -1
    comment: Optional[str] = None


class StatsResponse(BaseModel):
    total_questions: int
    total_feedback: int
    positive_feedback: int
    negative_feedback: int

