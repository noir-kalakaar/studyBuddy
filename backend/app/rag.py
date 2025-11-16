import math
import os
from typing import List, Optional
import httpx  # or mistral SDK

from .store import add_doc_chunk, get_docs


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


async def get_embedding(text: str) -> List[float]:
    # PSEUDOCODE – replace with actual Mistral embed call
    api_key = os.environ["MISTRAL_API_KEY"]
    # Example with httpx; adjust to real endpoint
    # resp = await httpx.post("https://api.mistral.ai/embeddings", json={...}, headers={...})
    # return resp.json()["data"][0]["embedding"]
    raise NotImplementedError


async def call_mistral_chat(prompt: str) -> str:
    api_key = os.environ["MISTRAL_API_KEY"]
    # resp = await httpx.post("https://api.mistral.ai/chat/completions", json={...}, headers={...})
    # return resp.json()["choices"][0]["message"]["content"]
    raise NotImplementedError


async def store_text(title: str, text: str, source: str):
    chunks = split_into_chunks(text)
    for chunk in chunks:
        emb = await get_embedding(chunk)
        add_doc_chunk(chunk, emb, source=source, title=title)


async def rag_answer(question: str, top_k: int = 3, sources: Optional[List[str]] = None):
    """
    RAG answer generation using embeddings and Mistral chat.
    Returns (answer, list of (score, doc) tuples).
    """
    q_embedding = await get_embedding(question)

    # filter docs if sources provided
    docs = get_docs()
    if sources:
        docs = [d for d in docs if d.source in sources]

    # compute similarities
    scored = []
    for doc in docs:
        score = cosine_similarity(q_embedding, doc.embedding)
        scored.append((score, doc))

    scored.sort(reverse=True, key=lambda x: x[0])
    top_docs = [d for (s, d) in scored[:top_k]]

    context_text = "\n\n".join(
        f"[{d.source.upper()}:{d.title}] {d.text}" for d in top_docs
    )

    prompt = f"""
You are a helpful assistant. Use ONLY the context below to answer the user's question.
If the answer is not in the context, say you don't know.

Context:
{context_text}

Question:
{question}
"""

    llm_answer = await call_mistral_chat(prompt)

    # Return answer and list of (score, doc) tuples
    top_scored = scored[:top_k]
    return llm_answer, top_scored

