import streamlit as st
from app.ai.gemini import generate_answer
from app.ai.prompts import build_rag_prompt
from app.rag.loader import extract_text_from_pdf
from app.rag.chunker import split_text_into_chunks
from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import store_chunks_in_chromadb
from app.rag.retriever import retrieve_relevant_chunks
from app.database.database import (
    init_db,
    create_user,
    create_document,
    create_conversation,
    save_message,
    get_conversation_history,
)


def initialize_session():
    """مقداردهی اولیه پایگاه داده و وضعیت نشست کاربر."""
    init_db()

    if "user_id" not in st.session_state:
        st.session_state.user_id = create_user()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = create_conversation(st.session_state.user_id)

    # دیکشنری نگهداری اسناد نمایه شده: {filename: {"id": doc_id, "chunks": count, "status": "Ready"}}
    if "indexed_documents" not in st.session_state:
        st.session_state.indexed_documents = {}

    # لیست خطاهای پردازش برای فایل‌های ناموفق: {filename: error_message}
    if "processing_errors" not in st.session_state:
        st.session_state.processing_errors = {}


def reset_conversation():
    """شروع یک نشست گفتگوی تازه و پاکسازی تاریخچه سشن."""
    st.session_state.conversation_id = create_conversation(st.session_state.user_id)


def process_single_pdf(file) -> int:
    """خط لوله پردازش مستقل یک فایل PDF همراه با ثبت در SQLite و ChromaDB."""
    # ۱. استخراج متن از صفحات
    pages = extract_text_from_pdf(file, file.name)
    if not pages:
        raise ValueError("No readable text found in document.")

    # ۲. خردسازی متن
    chunks = split_text_into_chunks(pages, file.name)
    if not chunks:
        raise ValueError("Document did not produce any valid chunks.")

    # ۳. تولید بردارها
    chunk_texts = [c["text"] for c in chunks]
    embeddings = get_batch_embeddings(chunk_texts)

    # ۴. ذخیره در پایگاه داده برداری ChromaDB
    stored_count = store_chunks_in_chromadb(chunks, embeddings, collection_name="document_chunks")

    # ۵. ثبت در پایگاه داده رابطه‌ای SQLite
    doc_id = create_document(st.session_state.user_id, file.name)

    # به‌روزرسانی سشن با اطلاعات فایل پردازش‌شده
    st.session_state.indexed_documents[file.name] = {
        "id": doc_id,
        "chunks": len(chunks),
        "status": "Ready"
    }

    # اگر قبلاً خطایی برای این فایل ثبت شده بود، پاک شود
    if file.name in st.session_state.processing_errors:
        del st.session_state.processing_errors[file.name]

    return len(chunks)


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant — Multi-Document",
        page_icon="📚",
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

    st.title("📚 AI Document Assistant — Multi-Document Intelligence")
    st.caption("Phase 15 — Batch Ingestion & Cross-Document Grounded RAG")

    col_ingest, col_chat = st.columns([1, 1], gap="large")

    # ستون اول: بارگذاری چندسندی و پایش وضعیت دسته‌ای
    with col_ingest:
        st.subheader("1. Multi-Document Ingestion")
        uploaded_files = st.file_uploader(
            "Upload one or more PDF documents:",
            type=["pdf"],
            accept_multiple_files=True,
            help="Select multiple PDF documents to ingest into the unified knowledge base."
        )

        if uploaded_files:
            # بررسی فایل‌هایی که نیاز به پردازش دارند
            files_to_process = [
                f for f in uploaded_files 
                if f.name not in st.session_state.indexed_documents
            ]

            if files_to_process:
                with st.status(f"Processing batch ({len(files_to_process)} new files)...", expanded=True) as status:
                    for f in files_to_process:
                        try:
                            st.write(f"Indexing **{f.name}**...")
                            chunk_count = process_single_pdf(f)
                            st.write(f"✓ **{f.name}**: successfully indexed ({chunk_count} chunks)")
                        except Exception as e:
                            st.session_state.processing_errors[f.name] = str(e)
                            st.write(f"✗ **{f.name}**: failed ({str(e)})")

                    status.update(label="Batch processing complete!", state="complete", expanded=False)

        # نمایش لیست وضعیت اسناد جاری
        if st.session_state.indexed_documents:
            st.success(f"Active Knowledge Base: {len(st.session_state.indexed_documents)} documents indexed.")
            for fname, meta in st.session_state.indexed_documents.items():
                st.markdown(f"- 📄 **{fname}** — `{meta['chunks']} chunks ready`")

        # نمایش خطاهای احتمالی فایل‌های معیوب (Fault Tolerance)
        if st.session_state.processing_errors:
            st.error("Some documents encountered errors during processing:")
            for fname, err in st.session_state.processing_errors.items():
                st.markdown(f"- ⚠️ **{fname}**: {err}")

    # ستون دوم: پرسش و پاسخ متقابل از تمام اسناد (Cross-Document Chat)
    with col_chat:
        st.subheader("2. Multi-Document Chat")

        # بازیابی تاریخچه مکالمه از دیتابیس SQLite
        history = get_conversation_history(st.session_state.conversation_id)

        chat_container = st.container(height=420)
        with chat_container:
            if not history:
                st.info("No messages in this session. Ingest documents and ask a question below!")
            for msg in history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        top_k = st.slider("Context chunks to retrieve (top_k):", min_value=1, max_value=8, value=4)
        user_query = st.chat_input("Ask a question across all active documents...")

        if user_query:
            if not st.session_state.indexed_documents:
                st.warning("Please upload and index at least one valid document before asking questions.")
            else:
                with st.spinner("Searching cross-document context and synthesizing answer..."):
                    try:
                        # ۱. بازیابی قطعات مرتبط از ChromaDB
                        retrieved_chunks = retrieve_relevant_chunks(
                            query=user_query,
                            collection_name="document_chunks",
                            top_k=top_k
                        )

                        # ۲. ساخت پرامپت RAG
                        rag_prompt = build_rag_prompt(user_query, retrieved_chunks)

                        # ۳. دریافت پاسخ از مدل
                        assistant_answer = generate_answer(rag_prompt)

                        # ۴. ذخیره در تاریخچه پایگاه داده
                        save_message(st.session_state.conversation_id, "user", user_query)
                        save_message(st.session_state.conversation_id, "assistant", assistant_answer)
                        st.rerun()

                    except Exception as e:
                        st.error(f"⚠️ {str(e)}")