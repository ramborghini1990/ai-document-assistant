"""
Pytest global configuration and fixtures.
Ensures clean database isolation and project root path injection.
"""
import os
import sys
import tempfile
from pathlib import Path
import pytest

# تضمین قرارگیری ریشه پروژه در sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database.database import init_db
from app.alerts.store import ensure_alert_tables


@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    """
    فیکسچر خودکار: برای تمام تست‌ها یک پایگاه داده موقت و ایزوله در حافظه/تمپ می‌سازد
    تا دیتابیس اصلی پروژه (assistant.db) هرگز دستکاری یا آلوده نشود.
    """
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db.close()

    monkeypatch.setenv("ASSISTANT_DB_PATH", temp_db.name)
    init_db()
    ensure_alert_tables()

    yield temp_db.name

    if os.path.exists(temp_db.name):
        try:
            os.remove(temp_db.name)
        except PermissionError:
            pass