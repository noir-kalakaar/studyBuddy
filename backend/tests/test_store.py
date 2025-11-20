import importlib
import json
import sys
from pathlib import Path
from typing import Tuple

import pytest


def _fresh_store(tmp_path: Path, monkeypatch) -> Tuple[object, Path]:
    store_file = tmp_path / "store.json"
    monkeypatch.setenv("STUDYBUDDY_STORE_PATH", str(store_file))
    if "app.store" in sys.modules:
        store_module = importlib.reload(sys.modules["app.store"])
    else:
        store_module = importlib.import_module("app.store")
    return store_module, store_file


def test_add_doc_chunk_persists_to_disk(tmp_path, monkeypatch):
    store, store_file = _fresh_store(tmp_path, monkeypatch)

    chunk = store.add_doc_chunk(
        text="Example text",
        embedding=[0.1, 0.2, 0.3],
        source="user",
        title="Unit Test",
    )

    assert chunk.text == "Example text"
    assert store_file.exists()

    data = json.loads(store_file.read_text(encoding="utf-8"))
    assert data["doc_chunks"][0]["title"] == "Unit Test"
    assert data["doc_chunks"][0]["source"] == "user"


def test_question_count_survives_reload(tmp_path, monkeypatch):
    store, store_file = _fresh_store(tmp_path, monkeypatch)
    assert not store_file.exists()

    store.increment_questions_count()
    store.increment_questions_count()

    # Reload module to force disk read
    reloaded_store, _ = _fresh_store(tmp_path, monkeypatch)
    stats = reloaded_store.get_stats()

    assert stats["total_questions"] == 2

