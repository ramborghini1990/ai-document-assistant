# Project State Tracking

## Current Status
- **Current Phase:** Phase 16 — Document Format Abstraction & Fault-Tolerant Ingestion (Completed)
- **Current Task:** Ready for Phase 18 — Schema-Driven Structured Information Extraction
- **Next Phase:** Phase 18 — Structured Extraction Engine (Vehicles, Fuel, Deadlines/Scadenziario)
- **Completed Phases:**
  - Phase 0: Project setup, git repo, venv, requirements, environment configuration
  - Phase 1: Standalone Gemini API integration verified (`gemini-3.6-flash`)
  - Phase 2: Basic Streamlit UI connected to Gemini
  - Phase 3: PDF text extraction with page tracking verified (`pypdf`)
  - Phase 4: Text chunking with overlap, metadata tracking, and UUIDs verified
  - Phase 5: Embeddings generation verified with `gemini-embedding-001`
  - Phase 6: ChromaDB local persistent storage and upsert verified
  - Phase 7: Semantic retrieval and distance ranking verified
  - Phase 8: End-to-end RAG grounded prompting verified
  - Phase 9: SQLite relational schema with UUIDs verified
  - Phase 10: Interactive chat UI with conversation history verified
  - Phase 11: Automated edge-case and error boundary testing verified
  - Phase 12: Comprehensive portfolio README and clean git hygiene verified
  - Phase 13: Official MVP Acceptance Report issued
  - Phase 14: Inspection of current architecture and reference ISO 14001 workbook verified
  - Phase 15: Multi-file batch upload and cross-document RAG verified
  - Phase 16: Multi-format support verified for PDF and DOCX (with table parsing); Fault tolerance verified (failed files do not halt batch ingestion); Image ingestion via Cloud Vision marked for on-prem GPU migration.

## Architecture Decisions
- Stack: Python, Streamlit, Google Gemini API, ChromaDB, SQLite, python-docx, Pillow.
- Multi-Format Parsing: Unified dispatcher routing `.pdf` to pypdf and `.docx` to python-docx (paragraphs + tables).
- Fault Tolerance: Individual document failure boundaries prevent batch crashing; dynamic error dismissals in UI.
- Local Infrastructure Roadmap: Heavy image OCR and scanned PDF workloads scheduled for local execution via on-premises GPU infrastructure to bypass cloud API rate-limits.

## Known Issues / Technical Debt
- Cloud Vision API on Google Free-Tier enforces a strict 20 RPM limit causing occasional 429/503 errors on image files. Decoupled and scheduled for offline OCR engine migration on enterprise GPU.