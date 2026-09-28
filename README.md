# AI Document Intelligence & Enterprise Reporting Platform
### Production-Grade Multimodal RAG & ISO 14001 Compliance Audit System

An enterprise-ready Document Intelligence platform built with Python, Google Gemini, ChromaDB, and SQLite. The system processes complex corporate documentation (spreadsheets, digital PDFs, scanned contracts, Word documents, and images), provides grounded cross-document Q&A, performs schema-driven compliance extraction with zero hallucination, and generates configurable audit-ready Excel and Word deliverables.

---

## Key Enterprise Capabilities

1. **Multimodal & Spreadsheet Ingestion**
   - **Unified Formats:** Supports PDF (digital and scanned), Word (`.docx`), Excel (`.xlsx`, `.xls`), and Images (PNG, JPG, WEBP).
   - **Hybrid PDF Parsing:** Direct text parsing via `pypdf`; automated fallback to `PyMuPDF` rasterization and Gemini Vision for scanned pages.
   - **Spreadsheet Preservation:** Excel sheets are mapped to individual pages with row-level key-value pairs to prevent context degradation during chunking.

2. **Specialized ISO 14001 SGA Schemas**
   - **Compliance Deadlines (`scadenziario`):** Legal obligations, statutory expiries, medical surveillance, and audit schedules.
   - **Vehicle Fleet & Fuel (`vehicle_fuel`):** Fleet inventory, revision expiries, fuel consumption, and deterministic $L/100km$ calculations.
   - **Energy & Utilities (`utility_consumption`):** Electricity (eVISO), water (ACDA), gas, POD/PDR tracking, and multi-tariff (F1/F2/F3) breakdowns.
   - **Personnel Safety Training (`personnel_training`):** Worker certifications, Codice Fiscale tracking, D.Lgs. 81/08 compliance, and 5-year renewal cycles.
   - **Environmental Authorizations (`regulatory_authorization`):** Provincial Art. 208 permits, Albo Gestori classifications, vehicle authorizations, and 53+ EER/CER waste codes.

3. **Dynamic Enterprise Configuration & Reporting**
   - **Multi-Tenant Profile:** Configurable company profile (Name, VAT, Address, RSGA, Technical Director) stored in SQLite.
   - **Customizable Export Engine:** Real-time column filtering via `st.multiselect` prior to download.
   - **Multi-Sheet Excel Deliverables:** Corporate olive-green styling, metadata audit sheets, and frozen headers via `openpyxl`.
   - **Formal Signed Word Reports:** Executive `.docx` deliverables with page provenance, audit metadata, and sign-off blocks.

---

## Tech Stack

- **Core:** Python 3.12, Streamlit
- **AI Models:** Google Gemini 3.6 Flash (Vision & Language), Gemini Embedding 001
- **Storage:** ChromaDB (Vector Store), SQLite (Relational Store)
- **Document Parsers:** `pymupdf`, `pypdf`, `python-docx`, `pandas`, `openpyxl`, `Pillow`
- **Infrastructure:** Google AI Studio Tier-1 (1,000 RPM)