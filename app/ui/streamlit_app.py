import streamlit as st
from app.ai.gemini import generate_answer
from app.ai.prompts import build_rag_prompt
from app.rag.loader import extract_text_from_pdf
from app.rag.chunker import split_text_into_chunks
from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import store_chunks_in_chromadb, get_or_create_collection
from app.rag.retriever import retrieve_relevant_chunks


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant",
        page_icon="📄",
        layout="wide",
    )

    st.title("📄 AI Document Assistant")
    st.caption("Phase 8 — Complete End-to-End RAG System")

    # مدیریت State برای رهگیری وضعیت ایندکس سند
    if "indexed_document" not in st.session_state:
        st.session_state.indexed_document = None
    if "total_chunks_indexed" not in st.session_state:
        st.session_state.total_chunks_indexed = 0

    col1, col2 = st.columns([1, 1], gap="medium")

    # ستون چپ: بارگذاری و آماده‌سازی سند در وکتور دیتابیس
    with col1:
        st.subheader("1. Document Ingestion")
        uploaded_file = st.file_uploader(
            "Upload a PDF document to index:",
            type=["pdf"],
            help="Upload a PDF. It will be extracted, chunked, embedded, and indexed into ChromaDB.",
        )

        if uploaded_file is not None:
            # فقط در صورتی که فایل جدیدی آپلود شده باشد پردازش انجام شود
            if st.session_state.indexed_document != uploaded_file.name:
                with st.status("Processing and indexing document...", expanded=True) as status:
                    try:
                        # گام ۱: استخراج متن
                        st.write("Extracting text from PDF...")
                        pages = extract_text_from_pdf(uploaded_file, uploaded_file.name)

                        # گام ۲: تکه‌تکه کردن
                        st.write("Splitting text into semantic chunks...")
                        chunks = split_text_into_chunks(pages, uploaded_file.name)

                        # گام ۳: تولید بردارها
                        st.write("Generating vector embeddings via Gemini API...")
                        chunk_texts = [c["text"] for c in chunks]
                        embeddings = get_batch_embeddings(chunk_texts)

                        # گام ۴: ذخیره در پایگاه داده برداری ChromaDB
                        st.write("Storing vectors and metadata in ChromaDB...")
                        stored_count = store_chunks_in_chromadb(chunks, embeddings, collection_name="document_chunks")

                        st.session_state.indexed_document = uploaded_file.name
                        st.session_state.total_chunks_indexed = stored_count
                        status.update(label="Document successfully processed and indexed!", state="complete", expanded=False)

                    except Exception as e:
                        status.update(label="Document processing failed!", state="error")
                        st.error(f"Error: {str(e)}")

        if st.session_state.indexed_document:
            st.success(
                f"Active Document: **{st.session_state.indexed_document}** "
                f"({st.session_state.total_chunks_indexed} chunks ready for retrieval)"
            )

    # ستون راست: پرسش، بازیابی و تولید پاسخ RAG
    with col2:
        st.subheader("2. Ask Questions")
        
        user_query = st.text_area(
            "Ask anything about the uploaded document:",
            placeholder="e.g., What is the main objective discussed in the document?",
            height=110,
        )

        top_k = st.slider("Number of retrieved chunks (top_k):", min_value=1, max_value=5, value=3)

        if st.button("Ask Assistant", type="primary"):
            if not st.session_state.indexed_document:
                st.warning("Please upload and index a PDF document first.")
            elif not user_query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Searching document and generating grounded answer..."):
                    # ۱. بازیابی قطعات مرتبط
                    retrieved_chunks = retrieve_relevant_chunks(
                        query=user_query,
                        collection_name="document_chunks",
                        top_k=top_k
                    )

                    # ۲. ساخت پرامپت استاندارد RAG
                    rag_prompt = build_rag_prompt(user_query, retrieved_chunks)

                    # ۳. فراخوانی جمینای
                    answer = generate_answer(rag_prompt)

                    # ۴. نمایش پاسخ
                    st.subheader("Answer:")
                    st.markdown(answer)

                    # ۵. نمایش شواهد و منابع بازخوانی‌شده (Grounding Evidence)
                    with st.expander("🔍 Inspect Retrieved Context & Evidence Sources", expanded=False):
                        if retrieved_chunks:
                            for idx, c in enumerate(retrieved_chunks, 1):
                                st.markdown(f"**Source {idx}:** Page `{c['page_number']}` (Distance: `{c['distance']:.4f}`)")
                                st.caption(c["text"])
                                st.divider()
                        else:
                            st.info("No matching chunks retrieved.")