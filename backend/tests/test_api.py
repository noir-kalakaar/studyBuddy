from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app, rag


client = TestClient(app)


def test_upload_pdf_success(monkeypatch):
    captured = {}

    async def fake_store_text(title, text, source, max_chunks=None):
        captured["title"] = title
        captured["text"] = text
        captured["source"] = source

    class FakePage:
        def extract_text(self):
            return "Sample PDF text"

    class FakePdfReader:
        def __init__(self, _file_like):
            self.pages = [FakePage()]

    monkeypatch.setattr("app.main.PdfReader", FakePdfReader)
    monkeypatch.setattr(rag, "store_text", fake_store_text)

    response = client.post(
        "/api/upload-pdf",
        data={"title": "Test PDF"},
        files={"file": ("test.pdf", b"%PDF-1.4 data", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert captured["title"] == "Test PDF"
    assert captured["source"] == "user"
    assert "Sample PDF text" in captured["text"]


def test_upload_pdf_rejects_empty(monkeypatch):
    class EmptyPage:
        def extract_text(self):
            return ""

    class FakePdfReader:
        def __init__(self, _file_like):
            self.pages = [EmptyPage()]

    monkeypatch.setattr("app.main.PdfReader", FakePdfReader)

    response = client.post(
        "/api/upload-pdf",
        data={"title": "Empty PDF"},
        files={"file": ("empty.pdf", b"%PDF-1.4 data", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Could not extract text" in response.json()["detail"]


def test_chat_endpoint(monkeypatch):
    async def fake_rag_answer(question, top_k=3, sources=None):
        doc = SimpleNamespace(
            id=uuid4(),
            text="Chunk text",
            source="user",
            title="Doc Title",
            url=None,
        )
        return ("Mock answer for " + question, [(0.92, doc)])

    monkeypatch.setattr(rag, "rag_answer", fake_rag_answer)

    response = client.post(
        "/api/chat",
        json={"question": "What is 2+2?", "top_k": 1, "sources": ["user"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"].startswith("Mock answer")
    assert len(payload["context"]) == 1
    assert payload["context"][0]["meta"]["title"] == "Doc Title"

