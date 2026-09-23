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
    """مقداردهی اولیه پایگاه داده و تولید شناسه‌های نشست کاربر در صورت عدم وجود."""
    init_db()

    if "user_id" not in st.session_state:
        st.session_state.user_id = create_user()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = create_conversation(st.session_state.user_id)

    if "indexed_document" not in st.session_state:
        st.session_state.indexed_document = None

    if "document_id" not in st.session_state:
        st.session_state.document_id = None

    if "total_chunks_indexed" not in st.session_state:
        st.session_state.total_chunks_indexed = 0


def reset_conversation():
    """ایجاد یک نشست گفتگوی تازه و خالی کردن تاریخچه پیام‌ها."""
    st.session_state.conversation_id = create_conversation(
        st.session_state.user_id,
        st.session_state.document_id
    )


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant",
        page_icon="📄",
        layout="wide",
    )

    initialize_session()

    # نوار کناری (Sidebar) برای مدیریت نشست و متادیتا
    with st.sidebar:
        st.header("⚙️ Session & System Info")
        st.markdown(f"**User ID:** `{st.session_state.user_id[:8]}...`")
        st.markdown(f"**Conversation ID:** `{st.session_state.conversation_id[:8]}...`")

        if st.session_state.indexed_document:
            st.divider()
            st.subheader("Active Document")
            st.write(f"📄 **{st.session_state.indexed_document}**")
            st.write(f"🧩 Indexed Chunks: `{st.session_state.total_chunks_indexed}`")

        st.divider()
        if st.button("🔄 Start New Conversation", use_container_width=True):
            reset_conversation()
            st.rerun()

    st.title("📄 AI Document Assistant")
    st.caption("Phase 10 — Full RAG with SQLite Conversation History")

    col_ingest, col_chat = st.columns([1, 1], gap="large")

    # بخش پردازش و ایندکس سند
    with col_ingest:
        st.subheader("1. Document Ingestion")
        uploaded_file = st.file_uploader(
            "Upload a text-based PDF document:",
            type=["pdf"],
            help="Upload a PDF to extract, chunk, embed, and index into ChromaDB.",
        )

        if uploaded_file is not None:
            if st.session_state.indexed_document != uploaded_file.name:
                with st.status("Processing and indexing document...", expanded=True) as status:
                    try:
                        # ۱. ثبت در SQLite
                        doc_id = create_document(st.session_state.user_id, uploaded_file.name)
                        st.session_state.document_id = doc_id

                        # ۲. استخراج متن
                        st.write("Extracting text from PDF pages...")
                        pages = extract_text_from_pdf(uploaded_file, uploaded_file.name)

                        # ۳. خرد کردن
                        st.write(f"Splitting {len(pages)} pages into chunks...")
                        chunks = split_text_into_chunks(pages, uploaded_file.name)

                        # ۴. تولید بردارها
                        st.write(f"Generating embeddings for {len(chunks)} chunks...")
                        chunk_texts = [c["text"] for c in chunks]
                        embeddings = get_batch_embeddings(chunk_texts)

                        # ۵. ذخیره در ChromaDB
                        st.write("Indexing into ChromaDB vector store...")
                        stored_count = store_chunks_in_chromadb(chunks, embeddings, collection_name="document_chunks")

                        st.session_state.indexed_document = uploaded_file.name
                        st.session_state.total_chunks_indexed = stored_count
                        status.update(label="Document indexed successfully!", state="complete", expanded=False)

                    except Exception as e:
                        status.update(label="Ingestion failed!", state="error")
                        st.error(f"Error: {str(e)}")

        if st.session_state.indexed_document:
            st.success(
                f"Ready: **{st.session_state.indexed_document}** "
                f"({st.session_state.total_chunks_indexed} chunks in ChromaDB)"
            )

    # بخش پرسش و نمایش تعاملی تاریخچه گفتگو
    with col_chat:
        st.subheader("2. Document Chat")

        # نمایش تاریخچه پیام‌های ذخیره‌شده در SQLite
        history = get_conversation_history(st.session_state.conversation_id)

        chat_container = st.container(height=420)
        with chat_container:
            if not history:
                st.info("No messages in this conversation yet. Ask a question below!")
            for msg in history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # دریافت پرسش جدید
        top_k = st.slider("Context chunks (top_k):", min_value=1, max_value=5, value=3)
        user_query = st.chat_input("Ask a question about the active document...")

        if user_query:
            if not st.session_state.indexed_document:
                st.warning("Please upload and index a PDF document before asking questions.")
            else:
                with st.spinner("Searching document context and generating answer..."):
                    try:
                        # ۱. بازیابی قطعات مرتبط
                        retrieved_chunks = retrieve_relevant_chunks(
                            query=user_query,
                            collection_name="document_chunks",
                            top_k=top_k
                        )

                        # ۲. ساخت پرامپت و تولید پاسخ
                        rag_prompt = build_rag_prompt(user_query, retrieved_chunks)
                        assistant_answer = generate_answer(rag_prompt)

                        # ۳. ثبت در دیتابیس فقط در صورت موفقیت کامل
                        save_message(st.session_state.conversation_id, "user", user_query)
                        save_message(st.session_state.conversation_id, "assistant", assistant_answer)
                        st.rerun()

                    except Exception as e:
                        st.error(f"⚠️ {str(e)}")