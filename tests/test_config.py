import os
import pytest
from app.config import (
    GEMINI_MODEL,
    GEMINI_EMBEDDING_MODEL,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    RAG_TOP_K,
    ALERT_MAX_OVERDUE_DAYS,
    get_db_path
)
from app.rag.chunker import split_text_into_chunks


@pytest.mark.offline
def test_default_config_values():
    assert GEMINI_MODEL == "gemini-3.6-flash"
    assert GEMINI_EMBEDDING_MODEL == "gemini-embedding-001"
    assert RAG_CHUNK_SIZE == 1000
    assert RAG_CHUNK_OVERLAP == 200
    assert RAG_TOP_K == 4
    assert ALERT_MAX_OVERDUE_DAYS == 30


@pytest.mark.offline
def test_dynamic_db_path(monkeypatch):
    monkeypatch.setenv("ASSISTANT_DB_PATH", "custom_test.db")
    assert get_db_path() == "custom_test.db"


@pytest.mark.offline
def test_chunker_uses_config():
    pages = [{"page_number": 1, "text": "A" * 1500}]
    chunks = split_text_into_chunks(pages, "test.pdf")
    assert len(chunks) >= 2