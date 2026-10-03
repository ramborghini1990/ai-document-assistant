# Project State Tracking — Modular Platform Architecture (v2.1)

## Current Status
- **Current Milestone:** Step 2 Completed → Moving to Step 3 (Scoped Exporters)
- **System Architecture:** Modular Multi-Tenant Document Intelligence Platform
- **Stability Status:** 100% Operational, Zero-Hallucination Verified, Fully Backward Compatible.

## Completed Milestones (v2.1 Platform Evolution):
- **Phase 0–27 (Baseline MVP):** Framework-free Multimodal RAG, PyMuPDF Vision OCR, Tier-1 Gemini, SQLite Profiles, Dual ISO 14001 Excel/Word Reporting.
- **Step 1 — Modular Schema Registry:**
  - Externalized domain schemas into `/schemas/*.json` (`iso_14001.json`, `fleet_fuel_expenses.json`, `general_documents.json`).
  - Implemented `registry.py` and whitelist deterministic `calculators.py`.
  - Converted `schemas.py` into a backward-compatible shim (legacy tests pass 100%).
  - Resolved latent substring bug on field types (`ente_formatore` / `fornitore`).
- **Step 2 — UI Module Switcher & Review Roundtrip:**
  - Added operational domain selector (`🧩 Modulo / Standard Operativo`) in sidebar.
  - Resolved Bug A via `app/extraction/review.py` (st.data_editor changes now persist and trigger deterministic recalculations like L/100km).
  - Resolved ChromaDB scope leakage: `retrieve_relevant_chunks` now strictly filters by active session document names.
  - Implemented reactive auto-garbage collection for ChromaDB vectors when files are removed or updated.

## Next Milestone:
- **Step 3 — Scoped Exporters (Excel & Word):** Ensure report deliverables only contain sheets and tables belonging to the active module/standard, eliminating cross-schema document pollution.