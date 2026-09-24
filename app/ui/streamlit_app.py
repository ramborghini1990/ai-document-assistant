import streamlit as st
import pandas as pd
from app.ai.gemini import generate_answer
from app.ai.prompts import build_rag_prompt
from app.rag.loader import load_document_content
from app.rag.chunker import split_text_into_chunks
from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import store_chunks_in_chromadb
from app.rag.retriever import retrieve_relevant_chunks
from app.extraction.schemas import AVAILABLE_SCHEMAS
from app.extraction.extractor import extract_structured_data
from app.database.database import (
    init_db,
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history,
)


def initialize_session():
    """مقداردهی اولیه پایگاه داده و متغیرهای نشست کاربر."""
    init_db()

    if "user_id" not in st.session_state:
        st.session_state.user_id = create_user()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = create_conversation(st.session_state.user_id)

    # {filename: {"id": doc_id, "chunks": count, "pages": pages_data, "status": "Ready"}}
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = {}

    if "processing_errors" not in st.session_state:
        st.session_state.processing_errors = {}

    # نگهداری رکوردهای استخراج‌شده جهت بازبینی کاربر: {schema_name: List[Dict]}
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = {}


def reset_conversation():
    """شروع نشست گفتگوی تازه."""
    st.session_state.conversation_id = create_conversation(st.session_state.user_id)


def process_single_document(file) -> int:
    """خط لوله پردازش چندفرمت (PDF, DOCX) همراه با نگهداری متن صفحات جهت استخراج."""
    pages = load_document_content(file, file.name)
    if not pages:
        raise ValueError("No readable text could be extracted from document.")

    chunks = split_text_into_chunks(pages, file.name)
    if not chunks:
        raise ValueError("Document did not produce any valid chunks.")

    chunk_texts = [c["text"] for c in chunks]
    embeddings = get_batch_embeddings(chunk_texts)
    store_chunks_in_chromadb(chunks, embeddings, collection_name="document_chunks")
    doc_id = create_document(st.session_state.user_id, file.name)

    # ذخیره متادیتای صفحات در سشن برای استفاده مستقیم در موتور استخراج
    st.session_state.indexed_documents[file.name] = {
        "id": doc_id,
        "chunks": len(chunks),
        "pages": pages,
        "status": "Ready"
    }

    if file.name in st.session_state.processing_errors:
        del st.session_state.processing_errors[file.name]

    return len(chunks)


def flatten_extraction_records(records: list) -> pd.DataFrame:
    """تبدیل رکوردهای ساختاریافته به دیتافریم جهت نمایش و ویرایش آسان توسط کاربر."""
    rows = []
    for r in records:
        row = {"Source Page": r.get("source_page", 1)}
        fields = r.get("fields", {})
        for fname, fdata in fields.items():
            norm_val = fdata.get("normalized_value")
            raw_val = fdata.get("raw_value")
            status = fdata.get("status", "EXTRACTED")

            # اولویت نمایش مقدار نرمال‌شده
            display_val = norm_val if norm_val is not None else raw_val
            row[fname] = display_val
            row[f"{fname}_status"] = status
        rows.append(row)

    return pd.DataFrame(rows)


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant — Intelligence & Reporting",
        page_icon="📋",
        layout="wide",
    )

    initialize_session()
    total_chunks = sum(doc["chunks"] for doc in st.session_state.indexed_documents.values())

    # نوار کناری (Sidebar)
    with st.sidebar:
        st.header("⚙️ Session & Workspace")
        st.markdown(f"**User ID:** `{st.session_state.user_id[:8]}...`")
        st.markdown(f"**Conversation ID:** `{st.session_state.conversation_id[:8]}...`")

        st.divider()
        st.subheader("📚 Active Knowledge Base")
        st.write(f"**Total Documents:** `{len(st.session_state.indexed_documents)}`")
        st.write(f"**Total Indexed Chunks:** `{total_chunks}`")

        if st.session_state.indexed_documents:
            st.markdown("**Loaded Files:**")
            for fname, meta in st.session_state.indexed_documents.items():
                st.caption(f"✓ **{fname}** ({meta['chunks']} chunks)")

        st.divider()
        if st.button("🔄 Start New Conversation", use_container_width=True):
            reset_conversation()
            st.rerun()

    st.title("📋 AI Document Assistant — Document Intelligence & Reporting")
    st.caption("Phase 19 — Schema-Driven Extraction & Interactive Human Review")

    col_ingest, col_workspace = st.columns([1, 1.2], gap="large")

    # ستون اول: بارگذاری چندسندی
    with col_ingest:
        st.subheader("1. Ingestion Pipeline")
        uploaded_files = st.file_uploader(
            "Upload enterprise documents (PDF, DOCX, Images):",
            type=["pdf", "docx", "jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            help="Upload PDF (digital or scanned), Word (.docx), or Image files to ingest."
        )

        if uploaded_files:
            current_filenames = [f.name for f in uploaded_files]
            st.session_state.processing_errors = {
                fname: err for fname, err in st.session_state.processing_errors.items()
                if fname in current_filenames
            }

            files_to_process = [
                f for f in uploaded_files 
                if f.name not in st.session_state.indexed_documents 
                and f.name not in st.session_state.processing_errors
            ]

            if files_to_process:
                with st.status(f"Ingesting batch ({len(files_to_process)} new files)...", expanded=True) as status:
                    for f in files_to_process:
                        try:
                            st.write(f"Parsing **{f.name}**...")
                            chunk_count = process_single_document(f)
                            st.write(f"✓ **{f.name}**: indexed ({chunk_count} chunks)")
                        except Exception as e:
                            st.session_state.processing_errors[f.name] = str(e)
                            st.write(f"✗ **{f.name}**: failed ({str(e)})")

                    status.update(label="Batch processing complete!", state="complete", expanded=False)
        else:
            st.session_state.processing_errors = {}

        if st.session_state.indexed_documents:
            st.success(f"Active Knowledge Base: {len(st.session_state.indexed_documents)} documents ready.")
            for fname, meta in st.session_state.indexed_documents.items():
                st.markdown(f"- 📄 **{fname}** — `{meta['chunks']} chunks`")

        if st.session_state.processing_errors:
            st.error("Processing errors encountered:")
            for fname, err in st.session_state.processing_errors.items():
                st.markdown(f"- ⚠️ **{fname}**: {err}")

    # ستون دوم: فضای کاربری دوسطحی (چت مستند و استخراج داده)
    with col_workspace:
        tab_chat, tab_extraction = st.tabs(["💬 Document Chat (RAG)", "📊 Structured Extraction & Review"])

        # زبانه چت مستند
        with tab_chat:
            st.caption("Ask grounded questions across all uploaded documents.")
            history = get_conversation_history(st.session_state.conversation_id)

            chat_container = st.container(height=380)
            with chat_container:
                if not history:
                    st.info("Knowledge base is ready. Ask any question below!")
                for msg in history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            top_k = st.slider("Retrieval chunks (top_k):", min_value=1, max_value=8, value=4)
            user_query = st.chat_input("Ask a question about your documents...")

            if user_query:
                if not st.session_state.indexed_documents:
                    st.warning("Please upload at least one document first.")
                else:
                    with st.spinner("Synthesizing answer from verified document context..."):
                        try:
                            retrieved_chunks = retrieve_relevant_chunks(
                                query=user_query,
                                collection_name="document_chunks",
                                top_k=top_k
                            )
                            rag_prompt = build_rag_prompt(user_query, retrieved_chunks)
                            assistant_answer = generate_answer(rag_prompt)
                            save_message(st.session_state.conversation_id, "user", user_query)
                            save_message(st.session_state.conversation_id, "assistant", assistant_answer)
                            st.rerun()
                        except Exception as e:
                            st.error(f"⚠️ {str(e)}")

        # زبانه استخراج ساختاریافته و بازبینی داده‌ها (فاز ۱۹)
        with tab_extraction:
            st.caption("Extract structured entity tables, verify field accuracy, and edit before export.")

            if not st.session_state.indexed_documents:
                st.info("Upload and index documents to enable structured extraction.")
            else:
                c_schema, c_doc = st.columns([1, 1])
                with c_schema:
                    selected_schema = st.selectbox(
                        "Target Extraction Schema:",
                        options=list(AVAILABLE_SCHEMAS.keys()),
                        format_func=lambda x: f"{x.upper()} — {AVAILABLE_SCHEMAS[x]['description']}"
                    )
                with c_doc:
                    target_doc = st.selectbox(
                        "Source Document:",
                        options=["ALL ACTIVE DOCUMENTS"] + list(st.session_state.indexed_documents.keys())
                    )

                if st.button("🚀 Extract Structured Information", use_container_width=True):
                    with st.spinner(f"Extracting '{selected_schema}' schema via Gemini Tier-1 Engine..."):
                        # جمع‌آوری صفحات برای استخراج
                        pages_to_extract = []
                        if target_doc == "ALL ACTIVE DOCUMENTS":
                            for doc_meta in st.session_state.indexed_documents.values():
                                pages_to_extract.extend(doc_meta.get("pages", []))
                        else:
                            pages_to_extract = st.session_state.indexed_documents[target_doc].get("pages", [])

                        try:
                            result = extract_structured_data(pages_to_extract, schema_name=selected_schema)
                            st.session_state.extracted_data[selected_schema] = result
                            st.success(f"Extracted {result['total_records']} records successfully!")
                        except Exception as e:
                            st.error(f"Extraction failed: {str(e)}")

                # نمایش جدول بازبینی و امکان ویرایش فیلدها توسط کاربر
                if selected_schema in st.session_state.extracted_data:
                    current_res = st.session_state.extracted_data[selected_schema]
                    records = current_res.get("records", [])

                    if records:
                        st.markdown(f"### 📋 Review Extracted Records (`{selected_schema}`)")
                        st.info("💡 You can edit any cell directly in the table below to correct or refine values before export.")

                        df_records = flatten_extraction_records(records)

                        # جداسازی ستون‌های داده اصلی از وضعیت‌ها جهت نمایش تمیز
                        data_cols = [c for c in df_records.columns if not c.endswith("_status")]
                        
                        edited_df = st.data_editor(
                            df_records[data_cols],
                            use_container_width=True,
                            num_rows="dynamic",
                            key=f"editor_{selected_schema}"
                        )

                        st.caption(f"✓ Total Verified Rows: `{len(edited_df)}` | Source Document: `{target_doc}`")
                    else:
                        st.warning("No records matching this schema were found in the selected document(s).")