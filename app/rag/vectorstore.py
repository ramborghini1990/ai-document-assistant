import os
from typing import List, Dict, Any
import chromadb

# مسیر ذخیره‌سازی داده‌های وکتور دیتابیس در ریشه پروژه
CHROMA_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_data")


def get_chroma_client() -> chromadb.PersistentClient:
    """ایجاد یا فراخوانی کلاینت محلی و پایدار ChromaDB با مسیر مطلق."""
    os.makedirs(CHROMA_DATA_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DATA_PATH)


def get_or_create_collection(collection_name: str = "document_chunks"):
    """دریافت یا ساخت کالکشن برای ذخیره چانک‌ها و بردارها با معیار شباهت کسینوسی."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )


# معادل‌سازی برای حفظ ۱۰۰٪ سازگاری رو به عقب و جلوگیری از بروز هرگونه ImportError
get_chroma_collection = get_or_create_collection


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


def remove_document_from_chromadb(document_name: str, collection_name: str = "document_chunks") -> None:
    """حذف خودکار تمامی چانک‌های متعلق به یک سند مشخص از ChromaDB."""
    try:
        collection = get_or_create_collection(collection_name)
        collection.delete(where={"document_name": document_name})
    except Exception as e:
        print(f"Warning: Failed to delete chunks for {document_name}: {e}")


def clear_chroma_collection(collection_name: str = "document_chunks") -> None:
    """پاک‌سازی کامل کالکشن برداری با کلاینت اصلی در صورت خالی شدن تمامی اسناد."""
    try:
        client = get_chroma_client()
        client.delete_collection(name=collection_name)
    except Exception:
        pass