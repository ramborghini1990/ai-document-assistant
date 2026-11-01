---
name: extract-to-service
description: Phase 2 prep. Move one piece of orchestration out of app/ui/streamlit_app.py into a pure function in app/services/ without changing behaviour. Use when the user asks to decouple a UI feature, or before exposing a feature through FastAPI.
---

# Extract UI orchestration into a service

1. Locate the block in `app/ui/streamlit_app.py`. List every `st.session_state` key it reads/writes
   and every side effect (DB, Chroma, model, file).
2. Write a characterization test in `tests/services/` that drives the current behaviour through the
   new service signature with fakes (providers, repositories, `isolated_database`). It fails first.
3. Create `app/services/<area>.py` with a function that:
   - takes plain values + injected dependencies (`repos`, `providers`, `today`), never Streamlit objects;
   - returns a frozen dataclass from `app/domain/models.py` (or a new one there);
   - raises domain exceptions, never `st.error`.
4. Replace the UI block with: read widgets → call the service → render the result. Session state may
   cache the result for display, but the source of truth is the repository.
5. Run `python check_health.py`. Then `/review-invariants`.
6. Note the extracted function in `docs/adr/0001-phase2-service-layer.md` → "Service inventory".
