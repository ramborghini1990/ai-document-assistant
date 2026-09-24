# Project State Tracking

## Current Status
- **Current Phase:** Phase 18 — Schema-Driven Structured Information Extraction
- **Current Task:** Verification of extraction engine, normalizers, and anti-hallucination guarantees
- **Next Phase:** Phase 19 — Extraction Review UI (Interactive table display & field validation in Streamlit)
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
  - Phase 16: Multi-format support verified for PDF and DOCX
  - Phase 18: Extraction schemas (Scadenziario, Vehicle/Fuel), normalizers, and strict anti-hallucination engine implemented.

## Architecture Decisions
- Schema-Driven Extraction: Dedicated schemas aligned with client ISO 14001 workbook (`SCADENZIARIO`, `CONSUMI_CARBURANTE`).
- Anti-Hallucination & Provenance: Explicit `EXTRACTED`, `CALCULATED`, and `MISSING` statuses with source page tracking.
- Normalization: Independent Italian date parsing (`YYYY-MM-DD`) and numeric cleaning (comma-to-dot floats).