# CLAUDE.md — Document Intelligence & Compliance Platform

@AGENTS.md

> This file is the router. It stays under ~150 lines. Details live next to the code
> (`app/*/CLAUDE.md`, loaded when Claude works in that folder) and in `docs/adr/`.
> If a doc disagrees with the code or with `python check_health.py`, the code wins:
> say so and propose a doc fix instead of guessing.

## 1. State (update at every milestone via `/milestone`)
- Version v2.6. Phase 1 of 3 done. Baseline: `python check_health.py` → 6 modules / 10 schemas /
  1 fallback / 147 tests green.
- Active phase: **Phase 2 prep** (see `docs/adr/0001-phase2-service-layer.md`).
- Phase names: "Phase 2" = FastAPI + jobs + Postgres. "Phase 3" = on-prem local models.
  `docs/archive/INSTRUCTIONS.md` uses an older, unrelated PHASE 0–13 numbering: never read
  phase numbers from it.

## 2. Commands
- Full gate (must exit 0 before any task is done): `python check_health.py`
- Fast suite: `python -m pytest -q -p no:cacheprovider`
- One file: `python -m pytest tests/test_pipeline.py -q -p no:cacheprovider`
- Lint/types: `ruff check app tests` · `mypy app/extraction app/alerts app/reporting/analytics.py`
- App: `streamlit run app/ui/streamlit_app.py` · Alerts CLI: `python -m app.alerts.run --dry-run`
- Root-level `test_*.py` hit the live Gemini API. They are not the suite. Never add tests there.

## 3. Layers (dependencies point DOWN only)
```
app/ui/  api/  worker/          presentation & transport  → may import services only
app/services/                   use-cases                 → domain + storage + providers
app/extraction/ app/alerts/ app/reporting/ app/rag/      domain (pure)
app/storage/                    repositories (SQLite now, Postgres later)
app/ai/providers/               model access (the ONLY place a model SDK/HTTP client is imported)
schemas/*.json                  domain configuration (fields, routing, alerts, layout, analytics)
```
- A loop over records, a date diff, a DB/vector call or a model call in `app/ui/` or a router = bug.
- Domain code never imports from `app/reporting/` exporters, `streamlit`, `fastapi` or a model SDK.

## 4. Where things go
| Need | Put it in |
|---|---|
| New domain/doc type/field/alert/keyword/expiry rule/layout/chat wording | `schemas/*.json` + validation in `registry._parse_schema` |
| Numeric/date derivation | `app/extraction/calculators.py` (+ op in `registry.COMPUTE_OPS`) |
| Parsing of numbers/dates/codes | `app/extraction/normalizer.py` (single implementation) |
| Orchestration / use-case | `app/services/` |
| Persistence | `app/storage/` (scoped connections, `?` params, UUID ids, ISO dates) |
| Model calls | `app/ai/providers/` behind the Protocols in `base.py` |
| Exports | `app/reporting/*` (layout from `SchemaDef.layout`, scope via `resolve_scope`) |

## 5. Contracts that never change silently (ask first)
- Field status: `EXTRACTED | EDITED | CALCULATED | UNCERTAIN | MISSING`. Derivations never overwrite
  `EXTRACTED`/`EDITED`. A new status is an architecture change.
- Public signatures: `extract_structured_data`, `merge_result`, `run_batch_extraction`,
  `build_rag_prompt`, `get_chroma_collection`, `app/extraction/schemas.py` shim. New params only as
  optional keywords.
- Identity: new code keys documents by `document_id`; `source_document` is a display name only.
- Tenancy (decided 2026-11-01): every table, vector collection and repository call carries `tenant_id`.
  Single-company on-prem installs use the configured default tenant (`DEFAULT_TENANT_ID`).
- Embedding dimension is model-specific: a model change = a new collection, never a mixed one.
- No LangChain / LlamaIndex. No new runtime dependency or service without the user's explicit go.

## 6. Workflow
1. `/plan-change <goal>` first for anything touching more than one module: files, invariants at risk,
   tests to write. No code until the plan is accepted.
2. Step A: domain/service logic + offline tests (fakes, `isolated_database`). Step B: `check_health`.
   Step C: wire UI / router.
3. `/review-invariants` before declaring done. `/milestone` after a significant step.
4. Commit only when asked. Conventional messages (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`).
5. Decisions that change structure → a new ADR in `docs/adr/` (template `0000-template.md`).

## 7. Language
- Code, comments, docstrings, commit messages, docs: **English**.
- User-facing strings (UI, reports, alert texts, prompts' Italian sections): **Italian**.
- Existing Persian comments: translate to English when you touch that function, nowhere else.

## 8. Known debt (verify before relying on it)
See `docs/adr/0001-phase2-service-layer.md` → "Findings F1–F16".
