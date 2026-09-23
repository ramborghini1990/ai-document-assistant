# Project State Tracking

## Current Status
- **Current Phase:** Phase 2 — Basic Streamlit UI
- **Current Task:** Adding Streamlit, building minimal UI connected directly to Gemini
- **Next Phase:** Phase 3 — PDF processing
- **Completed Phases:**
  - Phase 0: Project setup, git repo, venv, requirements, environment configuration
  - Phase 1: Gemini API integration verified (`gemini-3.6-flash`)

## Architecture Decisions
- Stack: Python, Streamlit, Google Gemini API, ChromaDB, SQLite.
- SDK: Official `google-genai` with model `gemini-3.6-flash`.
- Direct implementation (No LangChain).

## Known Issues / Blockers
- None.
