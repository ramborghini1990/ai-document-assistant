# ADR 0001: Service and storage layers before FastAPI

- Date: 2026-11-01
- Status: proposed

## Context
Phase 1 domain code (`app/extraction`, `app/alerts`, `app/reporting/analytics.py`) is pure and well
tested. Working state lives in `st.session_state` (`app/ui/streamlit_app.py` `initialize_session`),
documents are keyed by filename (`app/rag/vectorstore.py:47-53`, `app/alerts/deadlines.py:9-12`), and
part of the orchestration is still in the UI (`process_single_document`, the chat flow, KPI day counts).

## Decision
Before any FastAPI code, introduce `app/domain/models.py` (frozen dataclasses mirroring today's dicts),
`app/storage/` (repository Protocols, SQLite implementation) and `app/services/` (use-cases). Streamlit
calls services. FastAPI routers and Celery tasks will later call the same services. Documents are
identified by `document_id`; `source_document` stays as a display name.

## Consequences
- The API becomes a thin adapter; the 147 existing tests keep testing the unchanged domain.
- Every service needs its own tests in `tests/services/`.
- Additive DB columns (`document_id`, `tenant_id`) need a small migration step in `init_db`.
- Multi-tenant from day one (user decision, 2026-11-01): `tenant_id` on every table, vector collection
  and repository call. Cloud SaaS uses one tenant per client; an isolated on-prem install uses a
  configured default tenant id, so the same code serves both.

## Findings F1–F16
See the architecture review document (section 1) for the full table with file:line evidence.

## Service inventory
| Service function | Replaces | Status |
|---|---|---|
| `ingest_document` | `streamlit_app.process_single_document` | todo |
| `answer_question` | chat block in `streamlit_app.render_ui` | todo |
| `dashboard_kpis` | KPI day counts in `streamlit_app.render_ui` | todo |
| `build_platform_report` | `_build_platform_report`, `_build_platform_word` | todo |
| `run_extraction` | manual extraction block + `render_platform_pipeline` | todo |
