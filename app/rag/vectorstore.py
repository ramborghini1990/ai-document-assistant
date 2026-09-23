import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings

# مسیر ذخیره‌سازی داده‌های وکتور دیتابیس در ریشه پروژه
CHROMA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_data")


def get_chroma_client() -> chromadb.PersistentClient:
    """ایجاد یا فراخوانی کلاینت محلی و پایدار ChromaDB."""
    os.makedirs(CHROMA_DATA_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DATA_PATH)


def get_or_create_collection(collection_name: str = "document_chunks"):
    """دریافت یا ساخت کالکشن برای ذخیره چانک‌ها و بردارها با معیار شباهت کسینوسی."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


def store_chunks_in_chromadb(
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    collection_name: str = "document_chunks"
) -> int:
    """
    ذخیره قطعات متنی، متادیتا، شناسه و بردارهای امبدینگ در ChromaDB.
    خروجی: تعداد رکوردهای ذخیره شده.
    """
    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks and embeddings must match exactly.")

    if not chunks:
        return 0

    collection = get_or_create_collection(collection_name)

    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "document_name": chunk.get("document_name", "unknown"),
            "page_number": int(chunk.get("page_number", 0)),
            "char_length": int(chunk.get("char_length", len(chunk["text"])))
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)