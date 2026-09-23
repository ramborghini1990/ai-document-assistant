import sqlite3
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# مسیر فایل دیتابیس در ریشه پروژه
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app_database.db")


def get_connection() -> sqlite3.Connection:
    """ایجاد اتصال به پایگاه داده و فعال‌سازی کلیدهای خارجی."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """ایجاد جداول ساختاریافته در صورت عدم وجود."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # جدول کاربران
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            );
        """)

        # جدول اسناد بارگذاری‌شده
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # جدول جلسات گفتگو (Sessions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                document_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
            );
        """)

        # جدول پیام‌ها و تاریخچه گفتگو
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
        """)
        conn.commit()


# توابع کمکی کار با داده‌ها (CRUD)

def create_user() -> str:
    """ایجاد کاربر جدید با شناسه UUID."""
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute("INSERT INTO users (id, created_at) VALUES (?, ?);", (user_id, now))
    return user_id


def create_document(user_id: str, filename: str) -> str:
    """ثبت سند برای کاربر مشخص."""
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, user_id, filename, created_at) VALUES (?, ?, ?, ?);",
            (doc_id, user_id, filename, now)
        )
    return doc_id


def create_conversation(user_id: str, document_id: Optional[str] = None) -> str:
    """ایجاد یک نشست گفتگوی جدید."""
    conv_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (id, user_id, document_id, created_at) VALUES (?, ?, ?, ?);",
            (conv_id, user_id, document_id, now)
        )
    return conv_id


def save_message(conversation_id: str, role: str, content: str) -> str:
    """ثبت یک پیام کاربر یا دستیار هوش مصنوعی."""
    message_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?);",
            (message_id, conversation_id, role, content, now)
        )
    return message_id


def get_conversation_history(conversation_id: str) -> List[Dict[str, Any]]:
    """بازیابی پیام‌های یک مکالمه به ترتیب زمانی."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC;",
            (conversation_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]