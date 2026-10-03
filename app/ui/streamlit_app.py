import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

from app.ai.gemini import generate_answer
from app.ai.prompts import build_rag_prompt
from app.rag.loader import load_document_content
from app.rag.chunker import split_text_into_chunks
from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import (
    store_chunks_in_chromadb, 
    remove_document_from_chromadb, 
    clear_chroma_collection
)
from app.rag.retriever import retrieve_relevant_chunks

from app.extraction.registry import list_modules, get_module
from app.extraction.extractor import extract_for_documents
from app.extraction.review import records_to_dataframe, dataframe_to_records

from app.reporting.excel_exporter import create_styled_excel_report, COLUMN_LABELS
from app.reporting.word_exporter import create_styled_word_report
from app.database.database import (
    init_db,
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history,
    get_company_profile,
    update_company_profile,
)


def initialize_session():
    """مقداردهی اولیه پایگاه داده و نشست کاربر با معماری ماژولار."""
    init_db()

    if "user_id" not in st.session_state:
        st.session_state.user_id = create_user()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = create_conversation(st.session_state.user_id)

    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = {}
        clear_chroma_collection()

    if "processing_errors" not in st.session_state:
        st.session_state.processing_errors = {}

    # ساختار تفکیک‌شده داده‌ها بر اساس module_id
    all_mods = list_modules()
    st.session_state.setdefault("active_module", all_mods[0].module_id if all_mods else "iso_14001")
    st.session_state.setdefault("extracted_data", {})     # {module_id: {schema: result}}
    st.session_state.setdefault("reviewed_data", {})      # {module_id: {schema: [records]}}
    st.session_state.setdefault("editor_version", {})     # {(module_id, schema): int}
    st.session_state.setdefault("export_fields", {})      # {module_id: {schema: [fields]}}

    if "company_profile" not in st.session_state:
        st.session_state.company_profile = get_company_profile()


def reset_conversation():
    """شروع نشست گفتگوی تازه."""
    st.session_state.conversation_id = create_conversation(st.session_state.user_id)


def process_single_document(file) -> int:
    """خط لوله پردازش چندفرمت همراه با نگهداری متن صفحات جهت استخراج."""
    pages = load_document_content(file, file.name)
    if not pages:
        raise ValueError("No readable text could be extracted from document.")

    for p in pages:
        p["document_name"] = file.name

    chunks = split_text_into_chunks(pages, file.name)
    if not chunks:
        raise ValueError("Document did not produce any valid chunks.")

    chunk_texts = [c["text"] for c in chunks]
    embeddings = get_batch_embeddings(chunk_texts)
    store_chunks_in_chromadb(chunks, embeddings, collection_name="document_chunks")
    doc_id = create_document(st.session_state.user_id, file.name)

    st.session_state.indexed_documents[file.name] = {
        "id": doc_id,
        "chunks": len(chunks),
        "pages": pages,
        "status": "Ready"
    }

    if file.name in st.session_state.processing_errors:
        del st.session_state.processing_errors[file.name]

    return len(chunks)


def build_export_payload(mid: str) -> Dict[str, Any]:
    """آماده‌سازی پکیج خروجی که ویرایش‌های انسانی را در اولویت قرار می‌دهد."""
    out = {}
    mod_data = st.session_state.extracted_data.get(mid, {})
    for s_name, res in mod_data.items():
        reviewed = st.session_state.reviewed_data.get(mid, {}).get(s_name)
        recs = reviewed if reviewed is not None else res.get("records", [])
        out[s_name] = {**res, "records": recs, "total_records": len(recs)}
    return out


def render_ui():
    st.set_page_config(
        page_title="AI Document Intelligence Platform",
        page_icon="📋",
        layout="wide",
    )

    initialize_session()
    total_chunks = sum(doc["chunks"] for doc in st.session_state.indexed_documents.values())

    # نوار کناری (Sidebar)
    with st.sidebar:
        st.header("⚙️ Workspace & Standards")

        # انتخابگر ماژول استاندارد (Module Switcher)
        available_mods = {m.module_id: m for m in list_modules()}
        selected_mod_id = st.selectbox(
            "🧩 Modulo / Standard Operativo:",
            options=list(available_mods.keys()),
            format_func=lambda k: available_mods[k].label,
            key="active_module"
        )
        current_module = available_mods[selected_mod_id]

        st.caption(f"**Versione Standard:** `{current_module.version}`")
        st.divider()

        # تنظیمات مشخصات شرکت
        with st.expander("🏢 Profilo Aziendale / Tenant", expanded=False):
            prof = st.session_state.company_profile
            c_name = st.text_input("Ragione Sociale:", value=prof.get("company_name", ""))
            c_vat = st.text_input("P.IVA / Codice Fiscale:", value=prof.get("vat_number", ""))
            c_addr = st.text_input("Sede Operativa:", value=prof.get("address", ""))
            c_rsga = st.text_input("Responsabile SGA / Referente:", value=prof.get("rsga_name", ""))
            c_dir = st.text_input("Direzione Tecnica / Firmatario:", value=prof.get("technical_director", ""))

            if st.button("💾 Salva Profilo Aziendale", use_container_width=True):
                update_company_profile(c_name, c_vat, c_addr, c_rsga, c_dir)
                st.session_state.company_profile = get_company_profile()
                st.success("Profilo salvato!")

        st.divider()
        st.subheader("📚 Active Knowledge Base")
        st.write(f"**Documenti Caricati:** `{len(st.session_state.indexed_documents)}`")
        st.write(f"**Chunk Indicizzati:** `{total_chunks}`")

        if st.session_state.indexed_documents:
            for fname, meta in st.session_state.indexed_documents.items():
                st.caption(f"✓ **{fname}** ({meta['chunks']} chunks)")

        st.divider()
        if st.button("🔄 Nuova Sessione Chat", use_container_width=True):
            reset_conversation()
            st.rerun()

    active_comp = st.session_state.company_profile.get("company_name", "Azienda")
    st.title(f"📋 {current_module.label}")
    st.caption(f"Enterprise Document Intelligence — Multi-Tenant Platform | {active_comp}")

    col_ingest, col_workspace = st.columns([1, 1.2], gap="large")

    # ستون اول: بارگذاری اسناد
    with col_ingest:
        st.subheader("1. Ingestion Pipeline")
        uploaded_files = st.file_uploader(
            "Carica documenti aziendali (PDF, DOCX, XLSX, Immagini):",
            type=["pdf", "docx", "xlsx", "xls", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            help="Supporta PDF nativi o scansionati, Word (.docx), fogli Excel (.xlsx/.xls) e immagini."
        )

        current_filenames = [f.name for f in uploaded_files] if uploaded_files else []

        # --- همگام‌سازی خودکار: تشخیص و حذف اسنادی که کاربر حذف کرده است ---
        indexed_names = list(st.session_state.indexed_documents.keys())
        for existing_name in indexed_names:
            if existing_name not in current_filenames:
                # حذف چانک‌های سند حذف‌شده از ChromaDB
                remove_document_from_chromadb(existing_name)
                # حذف از حافظه وضعیت اسناد
                del st.session_state.indexed_documents[existing_name]
                st.session_state.processing_errors.pop(existing_name, None)

        # اگر کاربر همه فایل‌ها را حذف کرد، کل حافظه چت و وکتورها خودکار صفر شود
        if not current_filenames and indexed_names:
            clear_chroma_collection()
            reset_conversation()
            st.session_state.extracted_data.clear()
            st.session_state.reviewed_data.clear()
            st.rerun()

        # پردازش اسناد جدیدی که هنوز ایندکس نشده‌اند
        if uploaded_files:
            files_to_process = [
                f for f in uploaded_files 
                if f.name not in st.session_state.indexed_documents 
                and f.name not in st.session_state.processing_errors
            ]

            if files_to_process:
                with st.status(f"Elaborazione in corso ({len(files_to_process)} file)...", expanded=True) as status:
                    for f in files_to_process:
                        try:
                            st.write(f"Analisi **{f.name}**...")
                            chunk_count = process_single_document(f)
                            st.write(f"✓ **{f.name}**: indicizzato ({chunk_count} chunk)")
                        except Exception as e:
                            st.session_state.processing_errors[f.name] = str(e)
                            st.write(f"✗ **{f.name}**: errore ({str(e)})")

                    status.update(label="Elaborazione batch completata!", state="complete", expanded=False)
        else:
            st.session_state.processing_errors = {}

        if st.session_state.indexed_documents:
            st.success(f"Archivio attivo: {len(st.session_state.indexed_documents)} documenti pronti per RAG ed estrazione.")

        if st.session_state.processing_errors:
            st.error("Errori di elaborazione:")
            for fname, err in st.session_state.processing_errors.items():
                st.markdown(f"- ⚠️ **{fname}**: {err}")

    # ستون دوم: چت و استخراج ساختاریافته
    with col_workspace:
        tab_chat, tab_extraction = st.tabs(["💬 Document Chat (RAG)", "📊 Structured Extraction & Review"])

        # زبانه چت
        with tab_chat:
            st.caption("Interroga semanticamente tutti i documenti attivi.")
            history = get_conversation_history(st.session_state.conversation_id)

            chat_container = st.container(height=380)
            with chat_container:
                if not history:
                    st.info("La Knowledge Base è attiva. Poni una domanda sui documenti.")
                for msg in history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            top_k = st.slider("Chunk di contesto (top_k):", min_value=1, max_value=8, value=4)
            user_query = st.chat_input("Fai una domanda sui documenti...")

            if user_query:
                if not st.session_state.indexed_documents:
                    st.warning("Carica almeno un documento prima di avviare la chat.")
                else:
                    with st.spinner("Sintesi della risposta dai documenti verificati..."):
                        try:
                            active_doc_names = list(st.session_state.indexed_documents.keys())
                            retrieved_chunks = retrieve_relevant_chunks(
                                query=user_query,
                                collection_name="document_chunks",
                                top_k=top_k,
                                document_names=active_doc_names
                            )
                            rag_prompt = build_rag_prompt(user_query, retrieved_chunks)
                            assistant_answer = generate_answer(rag_prompt)
                            save_message(st.session_state.conversation_id, "user", user_query)
                            save_message(st.session_state.conversation_id, "assistant", assistant_answer)
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ {str(e)}")

        # زبانه استخراج و بازبینی انسانی
        with tab_extraction:
            mid = current_module.module_id
            st.caption(f"Estrazione mirata per: **{current_module.label}**")

            if not st.session_state.indexed_documents:
                st.info("Carica i documenti per abilitare l'estrazione conforme allo standard.")
            else:
                c_schema, c_doc = st.columns([1, 1])
                with c_schema:
                    schema_name = st.selectbox(
                        "Schema di Estrazione:",
                        options=list(current_module.schemas.keys()),
                        format_func=lambda s: f"{current_module.schemas[s].label} — {current_module.schemas[s].description}",
                        key=f"schema_select_{mid}"
                    )
                    schema_def = current_module.schemas[schema_name]

                with c_doc:
                    docs_map = st.session_state.indexed_documents
                    target_doc = st.selectbox(
                        "Documento Sorgente:",
                        options=["ALL ACTIVE DOCUMENTS"] + list(docs_map.keys()),
                        key=f"doc_target_{mid}"
                    )

                if st.button("🚀 Avvia Estrazione Strutturata", use_container_width=True):
                    chosen_docs = (
                        docs_map if target_doc == "ALL ACTIVE DOCUMENTS" else {target_doc: docs_map[target_doc]}
                    )
                    pages_by_doc = {name: meta["pages"] for name, meta in chosen_docs.items()}

                    with st.spinner(f"Estrazione schema '{schema_def.label}' in corso..."):
                        result = extract_for_documents(pages_by_doc, schema_name, module_id=mid)
                        
                        st.session_state.extracted_data.setdefault(mid, {})[schema_name] = result
                        st.session_state.reviewed_data.setdefault(mid, {}).pop(schema_name, None)
                        
                        ver_key = (mid, schema_name)
                        st.session_state.editor_version[ver_key] = st.session_state.editor_version.get(ver_key, 0) + 1

                        if result.get("errors"):
                            for err_doc, err_msg in result["errors"].items():
                                st.warning(f"⚠️ Errore su {err_doc}: {err_msg}")
                        else:
                            st.success(f"Estratti {result['total_records']} record con successo!")

                # نمایش جدول بازبینی و ویرایش
                current_res = st.session_state.extracted_data.get(mid, {}).get(schema_name)
                if current_res and current_res.get("records"):
                    st.markdown(f"### 📋 Revisione Record: `{schema_def.label}`")
                    st.info("💡 Modifica i dati direttamente nella griglia: i valori modificati saranno ricalcolati e inseriti nei report finali.")

                    ver = st.session_state.editor_version.get((mid, schema_name), 0)
                    initial_records = current_res["records"]
                    df_for_editor = records_to_dataframe(initial_records, schema_def)

                    edited_df = st.data_editor(
                        df_for_editor,
                        use_container_width=True,
                        num_rows="dynamic",
                        key=f"editor_{mid}_{schema_name}_{ver}",
                        column_config={"_rid": None},
                        disabled=["source_document", "source_page"]
                    )

                    # ذخیره تغییرات انسانی در reviewed_data
                    reviewed_records = dataframe_to_records(edited_df, initial_records, schema_def)
                    st.session_state.reviewed_data.setdefault(mid, {})[schema_name] = reviewed_records

                    st.caption(f"✓ Record verificati: `{len(reviewed_records)}` | Modulo attivo: `{current_module.label}`")

                    # بخش خروجی‌های رسمی
                    st.divider()
                    st.subheader("📥 Genera Report Ufficiali")
                    
                    # فیلتر داینامیک ستون‌ها
                    all_schema_fields = schema_def.ordered_field_names()
                    schema_labels = schema_def.all_labels()
                    
                    selected_cols = st.multiselect(
                        "Seleziona colonne per l'esportazione:",
                        options=all_schema_fields,
                        default=all_schema_fields,
                        format_func=lambda f: schema_labels.get(f, f),
                        key=f"export_cols_{mid}_{schema_name}"
                    )
                    st.session_state.export_fields.setdefault(mid, {})[schema_name] = selected_cols

                    col_dl_excel, col_dl_word = st.columns(2)
                    payload = build_export_payload(mid)
                    prefix = current_module.report.get("filename_prefix", "REPORT")

                    with col_dl_excel:
                        excel_bytes = create_styled_excel_report(
                            extracted_data_by_schema=payload,
                            source_documents=list(st.session_state.indexed_documents.keys()),
                            company_profile=st.session_state.company_profile,
                            selected_fields_by_schema=st.session_state.export_fields.get(mid, {})
                        )
                        st.download_button(
                            label=f"📊 Scarica Excel Ufficiale ({prefix})",
                            data=excel_bytes,
                            file_name=f"Report_{prefix}_{schema_name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

                    with col_dl_word:
                        word_bytes = create_styled_word_report(
                            extracted_data_by_schema=payload,
                            source_documents=list(st.session_state.indexed_documents.keys()),
                            company_profile=st.session_state.company_profile,
                            selected_fields_by_schema=st.session_state.export_fields.get(mid, {})
                        )
                        st.download_button(
                            label="📄 Scarica Verbale Word Ufficiale (.docx)",
                            data=word_bytes,
                            file_name=f"Verbale_{prefix}_{datetime.now().strftime('%Y%m%d')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )