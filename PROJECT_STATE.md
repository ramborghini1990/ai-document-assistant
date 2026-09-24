# Project State Tracking

## Current Status
- **Current Phase:** Phase 16 & 17 — Multi-Format & Scanned Document Ingestion (Completed)
- **Current Task:** Verification of Vision OCR on images and scanned PDFs via Tier 1 API
- **Next Phase:** Phase 20 — Structured Excel Export (ISO 14001 Compliant)
- **Completed Phases:**
  - Phase 0 to 15: Foundation, Grounded RAG, Persistent Storage, Batch Ingestion
  - Phase 16: Multi-format parsing (PDF, DOCX with tables, standalone Images)
  - Phase 17: Automatic Scanned PDF detection and PyMuPDF page-to-image rasterization with Gemini Vision
  - Phase 18: Schema-driven extraction engine (Scadenziario, Vehicle/Fuel) with Italian normalizers
  - Phase 19: Interactive Human-in-the-Loop review UI (`st.data_editor`)
  - Billing & Capacity: Google AI Studio Tier 1 (1,000 RPM / 2M TPM) active

## Architecture Decisions
- Hybrid PDF Ingestion: Digital text extracted directly via pypdf; Scanned pages detected (<30 chars) and rasterized via PyMuPDF for Gemini Vision OCR.
- Image Processing: Dynamic downsampling to 1600px RGB JPEG for rapid, cost-effective multimodal transcription.