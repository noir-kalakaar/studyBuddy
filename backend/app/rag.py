import logging
import math
import os
from typing import List, Optional

import httpx  # type: ignore[import-not-found]  # or mistral SDK
import wikipedia  # type: ignore[import-not-found]
from dotenv import load_dotenv  # type: ignore[import-not-found]
from fastapi import HTTPException  # type: ignore[import-not-found]

from .store import add_doc_chunk, get_docs

logger = logging.getLogger(__name__)

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

# You can tweak these if you want different models
EMBEDDING_MODEL = "mistral-embed"
CHAT_MODEL = "mistral-small-latest"
# How many Wikipedia articles to auto-fetch per question.
# Default 0 to avoid hitting Mistral rate limits unless explicitly enabled.
AUTO_WIKI_ARTICLES = int(os.getenv("AUTO_WIKI_ARTICLES", "0"))
# Limit how many chunks we embed per document to avoid rate limits.
MAX_DOC_CHUNKS = int(os.getenv("MAX_DOC_CHUNKS", "10"))


def split_into_chunks(text: str, max_chars: int = 500) -> List[str]:
    # super simple split by paragraphs or fixed size
    chunks = []
    current = []
    current_len = 0

    for paragraph in text.split("\n"):
        if current_len + len(paragraph) > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph)

    if current:
        chunks.append("\n".join(current))
    return chunks


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def _post_embeddings(inputs: List[str]) -> List[List[float]]:
    if not inputs:
        return []

    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": inputs,
    }

    logger.debug("Requesting embeddings for %d chunk(s)", len(inputs))

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{MISTRAL_BASE_URL}/embeddings",
            headers=headers,
            json=payload,
        )

    if resp.status_code == 429:
        logger.warning("Mistral rate limit reached: %s", resp.text)
        raise HTTPException(
            status_code=503,
            detail="Mistral embeddings rate limit reached. Try again later or use a smaller document.",
        )

    resp.raise_for_status()
    data = resp.json()
    return [item["embedding"] for item in data["data"]]


async def get_embedding(text: str) -> List[float]:
    """
    Convenience wrapper to fetch a single embedding.
    """
    embeddings = await _post_embeddings([text])
    return embeddings[0] if embeddings else []


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Fetch embeddings for a batch of texts in one API call.
    """
    return await _post_embeddings(texts)


async def call_mistral_chat(prompt: str) -> str:
    """
    Call Mistral's chat completions endpoint with a single user prompt.
    Returns the assistant's text content.
    """
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful study assistant. "
                "Use only the provided context when answering. "
                "If the answer is not in the context, say you don't know."
            ),
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    payload = {
        "model": CHAT_MODEL,
        "messages": messages,
        # Optional: you can tune these
        "temperature": 0.1,
        "max_tokens": 512,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{MISTRAL_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    # Response shape: {"choices": [{"message": {"role": "assistant", "content": "..."}, ...}], ...}
    content = data["choices"][0]["message"]["content"]
    return content



async def store_text(title: str, text: str, source: str, max_chunks: Optional[int] = None):
    """
    Split text into chunks, embed, and store.
    max_chunks can be used to cap how many chunks are embedded (helps avoid rate limits
    for very long documents).
    """
    chunks = [c for c in split_into_chunks(text) if c.strip()]
    limit = max_chunks if max_chunks is not None else MAX_DOC_CHUNKS
    if limit > 0 and len(chunks) > limit:
        logger.warning(
            "Truncating document '%s' to %d chunks (out of %d) to respect MAX_DOC_CHUNKS",
            title,
            limit,
            len(chunks),
        )
        chunks = chunks[:limit]

    if not chunks:
        return

    embeddings = await get_embeddings(chunks)

    for chunk, emb in zip(chunks, embeddings):
        add_doc_chunk(chunk, emb, source=source, title=title)


async def _ensure_wikipedia_context(question: str, max_new_articles: int = AUTO_WIKI_ARTICLES):
    """
    Fetch and embed Wikipedia content relevant to the question if we do not already
    have enough Wikipedia context stored locally.
    """
    if max_new_articles <= 0:
        return

    existing_titles = {doc.title for doc in get_docs(source="wikipedia")}
    try:
        candidate_titles = wikipedia.search(question, results=max_new_articles * 3)
    except wikipedia.exceptions.WikipediaException:
        return

    added = 0
    for title in candidate_titles:
        if title in existing_titles:
            continue
        try:
            page = wikipedia.page(title, auto_suggest=True)
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
            continue
        await store_text(title=page.title, text=page.content, source="wikipedia", max_chunks=5)
        existing_titles.add(page.title)
        added += 1
        if added >= max_new_articles:
            break


async def rag_answer(question: str, top_k: int = 3, sources: Optional[List[str]] = None):
    # Only auto-fetch Wikipedia if explicitly enabled via AUTO_WIKI_ARTICLES > 0
    include_wikipedia = (AUTO_WIKI_ARTICLES > 0) and (sources is None or "wikipedia" in sources)
    if include_wikipedia:
        await _ensure_wikipedia_context(question)

    q_embedding = await get_embedding(question)

    docs = get_docs()
    if sources:
        docs = [d for d in docs if d.source in sources]

    scored = []
    for d in docs:
        score = cosine_similarity(q_embedding, d.embedding)
        scored.append((score, d))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_scored = scored[:top_k]

    context_text = "\n\n".join(
        f"[{d.source.upper()} - {d.title}] {d.text}" for (_, d) in top_scored
    )

    prompt = f"""
Context:

{context_text}

Question:

{question}
"""

    answer = await call_mistral_chat(prompt)

    return answer, top_scored

