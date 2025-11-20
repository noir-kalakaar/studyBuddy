import json
import os
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4


DATA_PATH = Path(
    os.getenv(
        "STUDYBUDDY_STORE_PATH",
        Path(__file__).resolve().parent / "data" / "store.json",
    )
)
_STATE_LOCK = Lock()


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


def _ensure_data_dir() -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def _serialize_chunk(chunk: DocChunk) -> Dict[str, Any]:
    return {
        "id": str(chunk.id),
        "text": chunk.text,
        "embedding": chunk.embedding,
        "source": chunk.source,
        "title": chunk.title,
        "url": chunk.url,
    }


def _save_state() -> None:
    payload = {
        "doc_chunks": [_serialize_chunk(chunk) for chunk in _doc_chunks],
        "questions_count": _questions_count,
        "feedback": _feedback_list,
    }
    with _STATE_LOCK:
        _ensure_data_dir()
        with DATA_PATH.open("w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)


def _load_state() -> None:
    global _doc_chunks, _questions_count, _feedback_list
    if not DATA_PATH.exists():
        return
    try:
        with DATA_PATH.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except (json.JSONDecodeError, OSError):
        return

    doc_chunks = []
    for raw in data.get("doc_chunks", []):
        try:
            chunk = DocChunk(
                id=UUID(raw["id"]),
                text=raw.get("text", ""),
                embedding=raw.get("embedding", []),
                source=raw.get("source", "user"),
                title=raw.get("title", ""),
                url=raw.get("url"),
            )
            doc_chunks.append(chunk)
        except (KeyError, ValueError):
            continue

    _doc_chunks = doc_chunks
    _questions_count = data.get("questions_count", 0)
    _feedback_list = data.get("feedback", [])


def add_doc_chunk(
    text: str,
    embedding: List[float],
    source: str,
    title: str,
    url: Optional[str] = None,
    chunk_id: Optional[UUID] = None,
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
        url=url,
    )
    _doc_chunks.append(chunk)
    _save_state()
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
    _save_state()


def add_feedback(
    question: str,
    answer: str,
    rating: int,
    comment: Optional[str] = None,
) -> None:
    """Add feedback to the feedback list."""
    _feedback_list.append(
        {
            "question": question,
            "answer": answer,
            "rating": rating,
            "comment": comment,
        }
    )
    _save_state()


def get_stats() -> Dict[str, int]:
    """Get statistics about questions and feedback."""
    positive_feedback = sum(1 for fb in _feedback_list if fb["rating"] == 1)
    negative_feedback = sum(1 for fb in _feedback_list if fb["rating"] == -1)

    return {
        "total_questions": _questions_count,
        "total_feedback": len(_feedback_list),
        "positive_feedback": positive_feedback,
        "negative_feedback": negative_feedback,
    }


_load_state()

