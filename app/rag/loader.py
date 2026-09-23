import io
from typing import List, Dict, Any
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: io.BytesIO, filename: str = "document.pdf") -> List[Dict[str, Any]]:
    """
    استخراج متن از یک فایل PDF همراه با متادیتای شماره صفحه.
    خروجی: لیستی از دیکشنری‌ها حاوی متن هر صفحه و شماره صفحه.
    """
    try:
        reader = PdfReader(file_bytes)
    except Exception as e:
        raise ValueError(f"Failed to read PDF file '{filename}': {str(e)}")

    if len(reader.pages) == 0:
        raise ValueError(f"The PDF file '{filename}' contains no pages.")

    pages_data = []
    total_characters = 0

    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        cleaned_text = text.strip()
        total_characters += len(cleaned_text)

        pages_data.append({
            "page_number": idx + 1,
            "text": cleaned_text
        })

    if total_characters == 0:
        raise ValueError(f"The PDF file '{filename}' contains no extractable text (it might be scanned or image-only).")

    return pages_data