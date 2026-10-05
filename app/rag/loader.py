import io
import os
from typing import List, Dict, Any
import pandas as pd
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
    """استخراج هوشمند متن از PDF (دیجیتال مستقیم + اسکن با Vision)."""
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

        if len(cleaned_text) < 30:
            scanned_text = ""
            if fitz_doc and idx < len(fitz_doc):
                fitz_page = fitz_doc[idx]
                pix = fitz_page.get_pixmap(dpi=150)
                page_img = Image.open(io.BytesIO(pix.tobytes("png")))
                scanned_text = _transcribe_page_image(page_img, page_num, filename)
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

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            content_blocks.append(text)

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


def _clean_excel_dataframe(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    تشخیص هوشمند سطر سربرگ (Header) در فایل‌های اکسل و حذف ستون‌های Unnamed یا ناشناخته.
    """
    df_raw = df_raw.dropna(how="all").dropna(axis=1, how="all")
    if df_raw.empty:
        return df_raw

    # در صورتی که فایل فقط ۱ سطر داشته باشد
    if len(df_raw) == 1:
        cols = [
            f"Colonna_{i+1}" if (pd.isna(v) or not str(v).strip() or str(v).lower().startswith("unnamed")) 
            else str(v).strip() 
            for i, v in enumerate(df_raw.iloc[0])
        ]
        return pd.DataFrame(columns=cols)

    # پیمایش ۱۰ سطر اول برای پیدا کردن سطری که حاوی اسامی واقعی ستون‌هاست
    best_header_idx = 0
    max_string_count = -1

    for r_idx in range(min(10, len(df_raw))):
        row_vals = df_raw.iloc[r_idx]
        non_nulls = row_vals.dropna()
        if non_nulls.empty:
            continue

        # شمارش خانه‌هایی که رشته متنی معنادار هستند (نه صرفاً ارقام عددی)
        string_cells = [
            str(v).strip() for v in non_nulls 
            if isinstance(v, str) and not v.strip().replace(".", "").replace(",", "").isdigit()
        ]
        score = len(string_cells)

        if score > max_string_count and len(non_nulls) >= 2:
            max_string_count = score
            best_header_idx = r_idx

    raw_headers = df_raw.iloc[best_header_idx]
    data_rows = df_raw.iloc[best_header_idx + 1:].copy()

    clean_columns = []
    for i, val in enumerate(raw_headers):
        val_str = str(val).strip() if pd.notna(val) else ""
        if not val_str or val_str.lower().startswith("unnamed") or val_str.lower() == "nan":
            clean_columns.append(f"Colonna_{i+1}")
        else:
            clean_columns.append(val_str)

    data_rows.columns = clean_columns
    return data_rows.dropna(how="all")


def extract_text_from_excel(file_stream, filename: str) -> List[Dict[str, Any]]:
    """
    استخراج ساختاریافته داده‌های شیت‌ها با تشخیص خودکار سربرگ واقعی و جلوگیری از ایجاد ستون‌های Unnamed.
    """
    if not file_stream:
        raise ValueError(f"File stream for '{filename}' is empty or invalid.")

    try:
        file_stream.seek(0)
        xls = pd.ExcelFile(file_stream)
    except Exception as e:
        raise ValueError(f"Failed to read Excel workbook '{filename}': {str(e)}")

    pages_data = []

    for idx, sheet_name in enumerate(xls.sheet_names):
        page_num = idx + 1
        try:
            # بارگذاری به صورت خام و تشخیص هوشمند هدر
            df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            df = _clean_excel_dataframe(df_raw)
        except Exception:
            continue

        if df.empty or len(df.columns) == 0:
            continue

        lines = [f"=== FOGLIO EXCEL: {sheet_name} (Pagina {page_num}) ==="]
        columns = [str(c).strip() for c in df.columns]
        lines.append(f"Colonne: {' | '.join(columns)}")

        for r_idx, (_, row) in enumerate(df.iterrows()):
            row_items = []
            for col in df.columns:
                val = row[col]
                if pd.notna(val) and str(val).strip():
                    if isinstance(val, pd.Timestamp):
                        val_str = val.strftime('%Y-%m-%d')
                    elif isinstance(val, float) and val.is_integer():
                        val_str = str(int(val))
                    else:
                        val_str = str(val).strip()
                    row_items.append(f"{col}: {val_str}")
            if row_items:
                lines.append(f"Riga {r_idx + 1}: " + " | ".join(row_items))

        sheet_text = "\n".join(lines).strip()
        if sheet_text:
            pages_data.append({
                "page_number": page_num,
                "text": sheet_text,
                "is_scanned": False
            })

    return pages_data


def load_document_content(file, filename: str) -> List[Dict[str, Any]]:
    """توزیع‌کننده یکپارچه ورود اسناد بر اساس پسوند."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file, filename)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file, filename)
    elif ext in [".xlsx", ".xls"]:
        return extract_text_from_excel(file, filename)
    elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
        return extract_text_from_image(file, filename)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Supported: PDF, DOCX, XLSX, XLS, JPG, PNG, WEBP.")