# AI Document Intelligence & Enterprise Reporting Platform
### Production-Grade Multimodal RAG & ISO 14001 Compliance Audit System

An enterprise-ready Document Intelligence platform built with Python, Google Gemini, ChromaDB, and SQLite. The system processes complex heterogeneous corporate documentation (spreadsheets, digital PDFs, scanned files, Word documents, and images), provides grounded cross-document Q&A with page provenance, executes schema-driven compliance extraction with zero hallucination, and generates scoped audit-ready Excel and Word deliverables.

---

## Executive Summary & Architecture Highlights

Traditional LLM document pipelines suffer from unverified hallucinations, lost page citations, and brittle document ingestion. This platform resolves these issues through a deterministic, framework-free architecture:

* **Zero-Hallucination Principle:** The LLM is restricted strictly to text extraction and field normalization. All mathematical calculations (ratios, sums, differences, products), expiries, and aggregations are computed deterministically in pure Python. Unfound data points explicitly evaluate to `null` (`MISSING`).
* **Framework-Free Core:** Direct integration with official SDKs (`google-genai`, `chromadb`, `sqlite3`), avoiding heavy abstraction overheads from LangChain or LlamaIndex.
* **Guaranteed Provenance:** Source documents and page numbers are preserved through chunking, vector indexing, retrieval, UI review, and final report generation.
* **Strict Module Scoping:** Generated deliverables (Excel workbooks and Word reports) isolate data to the selected standard/module, eliminating cross-domain schema contamination.

---

## System Architecture

```text
                               +-----------------------------+
                               |     Streamlit Web UI        |
                               |  (Multi-Tenant Workspace)   |
                               +--------------+--------------+
                                              |
                   +--------------------------+--------------------------+
                   |                                                     |
                   v                                                     v
       [ Ingestion Pipeline ]                                [ Workspace Tabs ]
                   |                                                     |
  +--------------------------------+                  +------------------+------------------+
  |  Multi-Format Document Loaders |                  |                  |                  |
  |  - PDF (pypdf + PyMuPDF Vision)|                  v                  v                  v
  |  - Excel (Smart Header Header) |             [ RAG Chat ]      [ Extraction ]    [ Alerts Engine ]
  |  - Word (.docx) & Images (OCR) |                  |                  |                  |
  +----------------+---------------+                  |                  |                  |
                   |                                  v                  |                  v
                   v                           [ Semantic Search ]       |          [ SQLite DB Store ]
         [ Recursive Chunker ]                        |                  |          - Deadlines (UUID5)
                   |                                  v                  |          - Alert Dispatcher
                   v                          (ChromaDB Vectors)         |          - Smtp/Twilio Client
        (Gemini Embeddings API)                       |                  |
                   |                                  v                  v
                   v                           +--------------+  +------------------+
         (ChromaDB Persistent)                 | Gemini Flash |  | Human-in-the-Loop|
                   |                           | (Grounding)  |  | Review Grid (UI) |
                   +-------------------------->+--------------+  +--------+---------+
                                                                          |
                                                                          v
                                                                 [ Scoped Exporters ]
                                                                 - Excel (.xlsx)
                                                                 - Word (.docx)
Key Enterprise Capabilities1. Robust Multimodal & Spreadsheet IngestionHybrid PDF Parsing: Direct text extraction via pypdf, falling back automatically to PyMuPDF rendering (150 DPI) and Gemini Vision for scanned documentation.   Spreadsheet Preservation: Excel sheets are parsed via intelligent header detection (_parse_excel_sheet), mapping rows with .iloc to unique key-value pairs to prevent ambiguous pandas Series errors and preserving sheet-page indexes.   Word & Image OCR: Extraction of .docx paragraphs/tables and verbatim Vision transcription for PNG/JPG/WEBP.   2. Specialized Operational Standards & SchemasDomain logic resides entirely in external JSON files (schemas/*.json):   ISO 14001 SGA (iso_14001.json): Compliance schedules (scadenziario), fleet and fuel consumption (vehicle_fuel), utility metrics (utility_consumption), worker safety certifications (personnel_training), and environmental permits (regulatory_authorization).   Fleet Management (fleet_fuel_expenses.json): Operational mileage, fuel volume, cost per liter, and deterministic $L/100\text{km}$ consumption ratios.   General Documents (general_documents.json): Protocol numbers, issuing bodies, and statutory contractual expiry tracking.   3. Human-in-the-Loop Review RoundtripExtracted entities feed directly into an interactive grid (st.data_editor).   Manual corrections elevate field statuses to EDITED, instantly triggering deterministic recalculations in Python before exporting.   4. Scoped Multi-Tenant ReportingExecutive Excel Deliverables: Color-coded headers, metadata audit summary sheets, freeze panes, and custom field selections.   Formal Word Reports: Styled .docx reports containing audit methodology statements, structured tables, and dynamic sign-off blocks populated from the company profile.   5. Automated Deadline Alerts EngineExtracts compliance deadlines into deterministic UUID5 identifiers.   Pure-logic threshold classification (e.g., 30, 15, 7 days remaining or overdue).   Deduplicated alert logging in SQLite and notification dispatching via SMTP Email and Twilio SMS.   Tech StackComponentTechnologyDescriptionRuntime & LanguagePython 3.12Core execution environment   Frontend UIStreamlitResponsive multi-tenant workspace with CSS theme injections   LLM & VisionGoogle Gemini 3.6 FlashMultimodal text generation, Vision OCR, and JSON schema extraction[cite: 1, 2]Vector EmbeddingsGemini Embedding 001768-dimensional semantic embeddings[cite: 1, 2]Vector StoreChromaDBPersistent local vector store configured with Cosine similarity[cite: 1, 2]Relational DatabaseSQLite (sqlite3)Users, conversations, company tenant profiles, deadlines, and alert logs[cite: 1, 2]Document Parserspypdf, pymupdf, python-docx, pandas, openpyxl, PillowRobust multimodal and spreadsheet ingestors[cite: 1, 2]Test FrameworkPytestAutomated test suite with dynamic temp-database isolation   Project StructurePlaintextai-document-assistant/
├── .streamlit/
│   └── config.toml             # Custom dark glassmorphism theme settings
├── app/
│   ├── ai/
│   │   ├── gemini.py           # Google GenAI SDK client, key rotation & retry backoff[cite: 1, 2]
│   │   └── prompts.py          # Grounded RAG prompts with page citation instructions[cite: 1, 2]
│   ├── alerts/
│   │   ├── deadlines.py        # Deterministic UUID5 deadline extractor[cite: 1, 2]
│   │   ├── dispatcher.py       # Notification aggregator (Email digest & SMS)[cite: 1, 2]
│   │   ├── notifiers.py        # Standard SMTP and Twilio clients[cite: 1, 2]
│   │   ├── run.py              # CLI entrypoint for daily scheduled scanning[cite: 1, 2]
│   │   ├── scanner.py          # Pure-logic threshold classification & overdue detection[cite: 1, 2]
│   │   └── store.py            # SQLite persistence for alerts and deduplication logs[cite: 1, 2]
│   ├── database/
│   │   └── database.py         # Relational store (conversations, messages, tenant profiles)[cite: 1, 2]
│   ├── extraction/
│   │   ├── calculators.py      # Whitelist deterministic calculations (ratio, sum, diff, product)[cite: 1, 2]
│   │   ├── extractor.py        # Batch JSON extraction engine with provenance tracking[cite: 1, 2]
│   │   ├── normalizer.py       # Multilingual date (IT/EN), number, and plate normalizers[cite: 1, 2]
│   │   ├── registry.py         # Schema registry loader with hot-reload and cache invalidation[cite: 1, 2]
│   │   ├── review.py           # DataFrame <-> Record bidirectional roundtrip engine[cite: 1, 2]
│   │   └── schemas.py          # Backward-compatible shim for legacy imports[cite: 1, 2]
│   ├── rag/
│   │   ├── chunker.py          # Sliding-window text chunker preserving page numbers[cite: 1, 2]
│   │   ├── embeddings.py       # Batch vector generation with key rotation[cite: 1, 2]
│   │   ├── loader.py           # Unified document parser (PDF, Word, Excel, Images)[cite: 1, 2]
│   │   ├── retriever.py        # Semantic search filtered by active session documents[cite: 1, 2]
│   │   └── vectorstore.py      # Persistent ChromaDB client and document lifecycle handlers[cite: 1, 2]
│   ├── reporting/
│   │   ├── common.py           # Scope resolvers, column planners, and legacy mappings[cite: 1, 2]
│   │   ├── excel_exporter.py   # Multi-sheet audit Excel generator (openpyxl)[cite: 1, 2]
│   │   └── word_exporter.py    # Formal signed Word report generator (python-docx)[cite: 1, 2]
│   ├── ui/
│   │   ├── streamlit_app.py    # Main UI application layout, tabs, and event handlers[cite: 1, 2]
│   │   └── theme.py            # Glassmorphism styling and KPI metric renderers[cite: 1, 2]
│   ├── config.py               # Centralized configuration with dynamic env fallbacks[cite: 1, 2]
│   └── main.py                 # Application root entrypoint[cite: 1, 2]
├── schemas/                    # Externalized schema definitions (JSON)[cite: 1, 2]
│   ├── fleet_fuel_expenses.json
│   ├── general_documents.json
│   └── iso_14001.json
├── tests/                      # Automated Pytest suite
│   ├── conftest.py             # Database isolation fixtures[cite: 1]
│   ├── test_alerts.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_registry.py
│   ├── test_reports.py
│   └── test_review.py
├── .env.example                # Example environment variables[cite: 1]
├── pytest.ini                  # Pytest configuration settings[cite: 1]
├── requirements.txt            # Project dependencies[cite: 1]
└── PROJECT_STATE.md            # Architectural milestone tracking[cite: 1]
Getting StartedPrerequisitesPython 3.12+[cite: 1]Google Gemini API Key (obtainable via Google AI Studio)[cite: 1]InstallationClone the repository:Bashgit clone [https://github.com/your-username/ai-document-assistant.git](https://github.com/your-username/ai-document-assistant.git)
cd ai-document-assistant
Create and activate a virtual environment:Bashpython -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
Install dependencies:Bashpip install -r requirements.txt
Configure environment variables:Copy .env.example to .env and supply your Gemini API key:Bashcp .env.example .env
Edit .env:Code snippetGEMINI_API_KEY=AIzaSy...your_actual_key_here
GEMINI_MODEL=gemini-3.6-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
Running the Application1. Launch the Streamlit Web WorkspaceExecute using either command:Bashpython -m streamlit run app/ui/streamlit_app.py
or:Bashpython -m streamlit run app/main.py
Open your browser at http://localhost:8501.2. Run Daily Scheduled Deadline Scanner (CLI)To run the automated alert scanner directly from the command line:Bash# Dry-run simulation (prints digest without sending):
python -m app.alerts.run --dry-run

# Run against a specific target date:
python -m app.alerts.run --today 2026-10-15
Running Automated TestsAll core logic, schema registries, deterministic calculators, database models, scoped exporters, and alert systems are verified offline via Pytest[cite: 1, 2]:Bashpytest
Sample output:Plaintexttests/test_alerts.py::test_alert_engine_full PASSED                      [  8%]
tests/test_config.py::test_default_config_values PASSED                  [ 16%]
tests/test_config.py::test_dynamic_db_path PASSED                        [ 25%]
tests/test_config.py::test_chunker_uses_config PASSED                    [ 33%]
tests/test_database.py::test_database_lifecycle PASSED                   [ 41%]
tests/test_database.py::test_company_profile PASSED                      [ 50%]
tests/test_registry.py::test_schema_registry_loading PASSED              [ 58%]
tests/test_registry.py::test_legacy_shim PASSED                          [ 66%]
tests/test_registry.py::test_deterministic_calculators PASSED            [ 75%]
tests/test_registry.py::test_date_and_field_normalizers PASSED           [ 83%]
tests/test_reports.py::test_scoped_reporting_isolation PASSED            [ 91%]
tests/test_review.py::test_review_roundtrip PASSED                       [100%]

============================== 12 passed in 2.60s ==============================
Known Limitations & Future Roadmap (V2)Current Architecture Limitations (MVP Scope)Single Shared Chroma Collection: Vector chunks reside in a shared persistent Chroma collection filtered at query-time by session document names[cite: 1, 2].Single Tenant Profile per Session: The corporate tenant profile is stored in a single-row SQLite table intended for single-tenant or demo operation[cite: 1, 2].Embedding Batch Size: Large documents (>100 pages) require external chunk batching during embedding to avoid single-call payload limits.   Planned V2 EnhancementsFastAPI Backend Migration: Decouple Streamlit to consume an asynchronous FastAPI REST/WebSocket backend[cite: 1].Multi-User Role-Based Access (RBAC): Integrate OAuth2/JWT authentication with dedicated schema permissions[cite: 1].Chunk Batching & Context Pagination: Implement adaptive sub-batching during embedding and multi-page chunk merging for documents exceeding 300 pages.   