import io
import os
from typing import List, Dict, Any
from pypdf import PdfReader
from docx import Document as DocxDocument
from PIL import Image
from app.ai.gemini import transcribe_image_with_vision

try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


def _transcribe_page_image(pil_img: Image.Image, page_num: int, filename: str) -> str:
    """ارسال تصویر صفحه اسکن‌شده به هوش مصنوعی جهت بازخوانی متن و جداول."""
    # بهینه‌سازی ابعاد تصویر جهت سرعت و کیفیت ایده‌آل
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")

    max_dim = 1600
    if max(pil_img.size) > max_dim:
        pil_img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    vision_prompt = (
        "You are an expert document OCR and transcription assistant. "
        "Transcribe all readable text, labels, numbers, dates, tables, and document stamps from this document page verbatim. "
        "Preserve tabular layouts using plain text or markdown tables. Do not summarize; extract the complete content."
    )

    try:
        text = transcribe_image_with_vision(pil_img, vision_prompt)
        return text.strip() if text else ""
    except Exception as e:
        print(f"Warning: OCR failed for {filename} (Page {page_num}): {str(e)}")
        return ""


def extract_text_from_pdf(file_stream, filename: str) -> List[Dict[str, Any]]:
    """
    استخراج هوشمند متن از PDF:
    اگر صفحه دارای متن دیجیتال باشد، مستقیماً استخراج می‌شود.
    اگر صفحه اسکن‌شده باشد، خودکار به تصویر تبدیل شده و با بینایی ماشین بازخوانی می‌شود.
    """
    if not file_stream:
        raise ValueError(f"File stream for '{filename}' is empty or invalid.")

    file_stream.seek(0)
    pdf_bytes = file_stream.read()

    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
    except Exception as e:
        raise ValueError(f"Failed to read PDF file '{filename}': {str(e)}")

    if not reader.pages:
        raise ValueError(f"The PDF file '{filename}' contains no pages.")

    # باز کردن با PyMuPDF برای رندر صفحات در صورت اسکن بودن
    fitz_doc = None
    if PYMUPDF_AVAILABLE:
        try:
            fitz_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception:
            fitz_doc = None

    pages_data = []

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        text = ""
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""

        cleaned_text = " ".join(text.split())

        # بررسی آیا صفحه اسکن‌شده است؟ (کمتر از ۳۰ کاراکتر متن قابل استخراج)
        if len(cleaned_text) < 30:
            scanned_text = ""
            # روش ۱: رندر با PyMuPDF
            if fitz_doc and idx < len(fitz_doc):
                fitz_page = fitz_doc[idx]
                pix = fitz_page.get_pixmap(dpi=150)
                page_img = Image.open(io.BytesIO(pix.tobytes("png")))
                scanned_text = _transcribe_page_image(page_img, page_num, filename)

            # روش ۲: استخراج عکس داخلی صفحه با pypdf در صورت عدم وجود PyMuPDF
            elif page.images:
                try:
                    first_img = page.images[0]
                    page_img = Image.open(io.BytesIO(first_img.data))
                    scanned_text = _transcribe_page_image(page_img, page_num, filename)
                except Exception:
                    pass

            if scanned_text:
                pages_data.append({
                    "page_number": page_num,
                    "text": scanned_text,
                    "is_scanned": True
                })
        else:
            pages_data.append({
                "page_number": page_num,
                "text": cleaned_text,
                "is_scanned": False
            })

    if fitz_doc:
        fitz_doc.close()

    return pages_data


def extract_text_from_docx(file_stream, filename: str) -> List[Dict[str, Any]]:
    """استخراج ساختاریافته متن و جداول از فایل Word (.docx)."""
    if not file_stream:
        raise ValueError(f"File stream for '{filename}' is empty or invalid.")

    try:
        file_stream.seek(0)
        doc = DocxDocument(file_stream)
    except Exception as e:
        raise ValueError(f"Failed to read Word document '{filename}': {str(e)}")

    content_blocks = []

    # استخراج پاراگراف‌ها
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content_blocks.append(text)

    # استخراج جداول
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                unique_cells = []
                for c in row_cells:
                    if not unique_cells or c != unique_cells[-1]:
                        unique_cells.append(c)
                content_blocks.append(" | ".join(unique_cells))

    full_text = "\n".join(content_blocks).strip()
    if not full_text:
        return []

    return [{"page_number": 1, "text": full_text, "is_scanned": False}]


def extract_text_from_image(file_stream, filename: str) -> List[Dict[str, Any]]:
    """استخراج متن، جداول و برچسب‌های موجود در تصاویر (JPG, PNG)."""
    if not file_stream:
        raise ValueError(f"File stream for '{filename}' is empty or invalid.")

    try:
        file_stream.seek(0)
        file_bytes = file_stream.read()
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as e:
        raise ValueError(f"Failed to decode image '{filename}': {str(e)}")

    text = _transcribe_page_image(image, 1, filename)
    if not text:
        return []

    return [{"page_number": 1, "text": text, "is_scanned": True}]


def load_document_content(file, filename: str) -> List[Dict[str, Any]]:
    """توزیع‌کننده یکپارچه ورود اسناد بر اساس پسوند."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file, filename)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file, filename)
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return extract_text_from_image(file, filename)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported: PDF, DOCX, JPG, PNG, WEBP.")