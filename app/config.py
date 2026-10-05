"""
Centralized Configuration Module.
Loads environment variables and exposes unified settings with production defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# بارگذاری خودکار متغیرهای محیطی از فایل .env در ریشه پروژه
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# --- تنظیمات مدل‌های هوش مصنوعی (Google Gemini) ---
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# --- تنظیمات خط لوله RAG و چانکینگ ---
RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))
CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "document_chunks")

# --- تنظیمات پایش و هشدارهای سررسید ---
ALERT_MAX_OVERDUE_DAYS: int = int(os.getenv("ALERT_MAX_OVERDUE_DAYS", "30"))

# --- مسیر پایگاه داده SQLite با ارزیابی پویا جهت ایزوله‌سازی آزمون‌ها ---
def get_db_path() -> str:
    """دریافت پویای مسیر فایل دیتابیس با اولویت متغیر محیطی ASSISTANT_DB_PATH."""
    return os.getenv("ASSISTANT_DB_PATH", "assistant.db")