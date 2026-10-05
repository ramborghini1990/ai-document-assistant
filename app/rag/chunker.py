import uuid
from typing import List, Dict, Any
from app.config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP


def split_text_into_chunks(
    pages_data: List[Dict[str, Any]],
    document_name: str,
    chunk_size: int = RAG_CHUNK_SIZE,
    chunk_overlap: int = RAG_CHUNK_OVERLAP,
) -> List[Dict[str, Any]]:
    """
    تقسیم صفحات سند به قطعات کوچک‌تر (Chunks) بر اساس تنظیمات مرکزی.
    """
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be strictly greater than chunk_overlap.")

    chunks = []
    step = chunk_size - chunk_overlap

    for page in pages_data:
        page_num = page["page_number"]
        text = page["text"]

        if not text:
            continue

        if len(text) <= chunk_size:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_name": document_name,
                "page_number": page_num,
                "text": text,
                "char_length": len(text)
            })
            continue

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end].strip()

            if chunk_content:
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "document_name": document_name,
                    "page_number": page_num,
                    "text": chunk_content,
                    "char_length": len(chunk_content)
                })

            start += step

    return chunks