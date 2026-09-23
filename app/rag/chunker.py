import uuid
from typing import List, Dict, Any


def split_text_into_chunks(
    pages_data: List[Dict[str, Any]],
    document_name: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Dict[str, Any]]:
    """
    تقسیم صفحات سند به قطعات کوچک‌تر (Chunks) با قابلیت همپوشانی و حفظ متادیتا.
    
    پارامترها:
    - pages_data: خروجی استخراج فاز ۳ شامل شماره صفحه و متن
    - document_name: نام فایل PDF
    - chunk_size: حداکثر تعداد کاراکتر در هر تکه (پیش‌فرض: ۱۰۰۰)
    - chunk_overlap: میزان اشتراک کاراکتر میان دو تکه مجاور (پیش‌فرض: ۲۰۰)
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

        # اگر متن صفحه از حداقل سایز کمتر باشد، مستقیماً یک تکه می‌شود
        if len(text) <= chunk_size:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_name": document_name,
                "page_number": page_num,
                "text": text,
                "char_length": len(text)
            })
            continue

        # تقسیم پنجره‌ای با همپوشانی
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