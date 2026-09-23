import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به مسیر جستجوی پایتون
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui.streamlit_app import render_ui

if __name__ == "__main__":
    render_ui()