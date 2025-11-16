from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from uuid import uuid4, UUID


@dataclass
class DocChunk:
    id: UUID
    text: str
    embedding: List[float]
    source: str  # "user" | "wikipedia"
    title: str
    url: Optional[str] = None


# In-memory storage
_doc_chunks: List[DocChunk] = []
_questions_count: int = 0
_feedback_list: List[Dict[str, Any]] = []


def add_doc_chunk(
    text: str,
    embedding: List[float],
    source: str,
    title: str,
    url: Optional[str] = None,
    chunk_id: Optional[UUID] = None
) -> DocChunk:
    """Add a new document chunk to the store."""
    if chunk_id is None:
        chunk_id = uuid4()
    
    chunk = DocChunk(
        id=chunk_id,
        text=text,
        embedding=embedding,
        source=source,
        title=title,
        url=url
    )
    _doc_chunks.append(chunk)
    return chunk


def get_docs(source: Optional[str] = None) -> List[DocChunk]:
    """Get document chunks, optionally filtered by source."""
    if source is None:
        return _doc_chunks.copy()
    return [chunk for chunk in _doc_chunks if chunk.source == source]


def increment_questions_count() -> None:
    """Increment the questions count."""
    global _questions_count
    _questions_count += 1


def add_feedback(
    question: str,
    answer: str,
    rating: int,
    comment: Optional[str] = None
) -> None:
    """Add feedback to the feedback list."""
    _feedback_list.append({
        "question": question,
        "answer": answer,
        "rating": rating,
        "comment": comment
    })


def get_stats() -> Dict[str, int]:
    """Get statistics about questions and feedback."""
    positive_feedback = sum(1 for fb in _feedback_list if fb["rating"] == 1)
    negative_feedback = sum(1 for fb in _feedback_list if fb["rating"] == -1)
    
    return {
        "total_questions": _questions_count,
        "total_feedback": len(_feedback_list),
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback
    }

