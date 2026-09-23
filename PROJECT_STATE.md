# Project State Tracking

## Current Status
- **Current Phase:** Phase 3 — PDF processing
- **Current Task:** Implementing PDF upload and text extraction (pypdf)
- **Next Phase:** Phase 4 — Chunking
- **Completed Phases:**
  - Phase 0: Project setup, git repo, venv, requirements, environment configuration
  - Phase 1: Standalone Gemini API integration verified (`gemini-3.6-flash`)
  - Phase 2: Basic Streamlit UI connected to Gemini

## Architecture Decisions
- Stack: Python, Streamlit, Google Gemini API, ChromaDB, SQLite.
- PDF Parser: `pypdf` (pure Python, lightweight, standard for text extraction).
- Modular architecture with package root handling in `main.py`.

## Known Issues / Blockers
- None.
