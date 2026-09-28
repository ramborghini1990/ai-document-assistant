# Project State Tracking

## Current Status
- **Current Phase:** Phase 26 — Configurable Export Engine (Completed)
- **Current Task:** Verification of dynamic user-driven column selection and enriched schema definitions
- **Next Phase:** Phase 27 — Comprehensive Verification, Edge-Case Auditing & Git Release
- **Completed Phases:**
  - Phase 0 to 22: Multimodal RAG, Tier-1 API, Scanned OCR, Review UI, ISO Excel & Word Exporters.
  - Phase 23: Company Profile persistence in SQLite and dynamic injection into deliverables.
  - Phase 24: Direct Excel workbook ingestion (`.xlsx`, `.xls`) with sheet-as-page preservation.
  - Phase 25: Domain-specific schemas for Energy utilities, Personnel Training (with Codice Fiscale & D.Lgs 81/08), and Waste Permitting.
  - Phase 26: Configurable export engine allowing users to select/deselect report columns via `st.multiselect` prior to generating Excel and Word deliverables.

## Architecture Decisions
- Configurable Reporting: Exporters dynamically adapt column headers and table structures based on user multiselect state while preserving zero hallucination and source page provenance.