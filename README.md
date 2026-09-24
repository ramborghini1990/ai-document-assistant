
# Project State Tracking

## Current Status
- **Current Phase:** Phase 22 — Final Quality Assurance, Documentation & Production Release (Completed)
- **Status:** All core and advanced milestones fully verified and operational.
- **Completed Phases:**
  - **Phase 0 to 12:** Core RAG pipeline, persistent ChromaDB, SQLite storage, conversation memory, edge-case testing, and initial MVP release.
  - **Phase 13 to 15:** Multi-document batch upload, fault-tolerant ingestion boundaries, and cross-document grounded synthesis.
  - **Phase 16 & 17:** Multimodal ingestion pipeline:
    - Digital PDF via `pypdf`.
    - DOCX tables & paragraphs via `python-docx`.
    - Standalone image OCR and scanned PDF page rasterization via `pymupdf` and Gemini Vision.
  - **Phase 18:** Schema-driven extraction engine (`SCADENZIARIO`, `VEHICLE_FUEL`, `GENERAL`) with strict anti-hallucination guarantees and Italian date/number normalizers.
  - **Phase 19:** Interactive Human-in-the-Loop review UI (`st.data_editor`) for real-time verification and editing.
  - **Phase 20:** Enterprise Excel export (`.xlsx`) with ISO 14001 olive-green corporate styling, audit summary sheets, and auto-adjusted columns.
  - **Phase 21:** Formal Word export (`.docx`) with audit metadata, source page traceability, and management sign-off blocks.
  - **Infrastructure:** Upgraded to Google AI Studio Tier-1 (Pay-as-you-go) with 1,000 RPM capacity.

## Architectural Highlights
- **Framework-Free RAG:** Direct integration of ChromaDB, SQLite, and Google GenAI SDK without heavy abstractions.
- **Multimodal & Scanned Doc Intelligence:** Automated fallback from digital text extraction to PyMuPDF image rasterization for scanned pages.
- **Dual Enterprise Reporting:** Immediate export to structured Excel workbooks for data analytics and signed Word reports for audit archives.
گام ۳: به‌روزرسانی مستندات فنی و پرتفولیو (README.md)
فایل README.md را باز کنید:

DOS
notepad README.md
کل محتوا را با این سند رسمی و مدیریتی جایگزین و ذخیره کنید:

Markdown
# AI Document Intelligence & Enterprise Reporting System
### Production-Grade Multimodal RAG & ISO 14001 Structured Extraction Engine

An enterprise-ready Document Intelligence platform built with Python, Google Gemini, ChromaDB, and SQLite. The system processes complex corporate documentation (digital PDFs, scanned contracts, Word files, and images), provides grounded cross-document Q&A, performs schema-driven compliance extraction with zero hallucination, and generates audit-ready Excel and Word deliverables.

---

## Key Features

1. **Multimodal & Scanned Document Ingestion**
   - **Unified Ingestion:** Batch upload supporting PDF, DOCX, PNG, JPG, and WEBP.
   - **Hybrid PDF Parsing:** Automatically extracts digital text via `pypdf`; detects scanned pages (<30 chars) and rasterizes them via `PyMuPDF` for Gemini Vision transcription.
   - **Fault-Tolerant Processing:** Document-level error isolation ensures invalid files do not break batch indexing.

2. **Grounded Cross-Document RAG**
   - **Vector Persistence:** ChromaDB embeddings (`gemini-embedding-001`) with cosine similarity ranking.
   - **Session & History:** Relational tracking of users, sessions, and messages via SQLite.
   - **Strict Grounding:** Prompts engineered to synthesize responses exclusively from cited document context.

3. **Schema-Driven Extraction & Anti-Hallucination**
   - **Predefined Schemas:** Aligned with ISO 14001 environmental compliance (`SCADENZIARIO`, `VEHICLE_FUEL`, and general administrative documents).
   - **Italian Locale Normalizers:** Normalizes dates (`DD/MM/YYYY` to `YYYY-MM-DD`) and numbers (comma-to-dot decimals, thousand separators).
   - **Derived Fields:** Automatic deterministic calculations (e.g., fuel consumption $L/100km$) with explicit `CALCULATED` status tags.
   - **Source Traceability:** Every extracted record references its exact source page.

4. **Human-in-the-Loop Review & Export**
   - **Interactive Grid:** Review and edit extracted rows directly inside Streamlit using `st.data_editor`.
   - **Corporate Excel Deliverables (`.xlsx`):** Multi-sheet workbooks with ISO olive-green styling, metadata summary sheets, auto-fit columns, and frozen headers via `openpyxl`.
   - **Formal Audit Reports (`.docx`):** Executive Word reports with document provenance, formatted tables, and management sign-off blocks for RSGA and Technical Directors.

---

## Tech Stack

- **Core:** Python 3.12, Streamlit
- **AI Models:** Google Gemini 3.6 Flash (Vision & Language), Gemini Embedding 001
- **Storage:** ChromaDB (Vector Store), SQLite (Relational Store)
- **Document Parsers:** `pymupdf` (Fitz), `pypdf`, `python-docx`, `Pillow`
- **Reporting Engines:** `openpyxl`, `python-docx`, `pandas`

---

## Quickstart

### 1. Clone & Set Up Environment
```bash
git clone [https://github.com/YOUR_USERNAME/ai-document-assistant.git](https://github.com/YOUR_USERNAME/ai-document-assistant.git)
cd ai-document-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
2. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
GEMINI_API_KEYS=your_api_key_here
3. Run Application
Bash
streamlit run app/main.py