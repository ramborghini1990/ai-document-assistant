import streamlit as st
from app.ai.gemini import generate_answer
from app.rag.loader import extract_text_from_pdf
from app.rag.chunker import split_text_into_chunks


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant",
        page_icon="📄",
        layout="centered",
    )

    st.title("📄 AI Document Assistant")
    st.caption("Phase 4 — Chunking & Metadata Pipeline Active")

    # مدیریت State
    if "extracted_pages" not in st.session_state:
        st.session_state.extracted_pages = None
    if "document_chunks" not in st.session_state:
        st.session_state.document_chunks = None
    if "document_name" not in st.session_state:
        st.session_state.document_name = None

    # بخش آپلود و پردازش PDF
    st.subheader("1. Document Upload & Processing")
    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        help="Upload a text-based PDF to extract and chunk its contents.",
    )

    if uploaded_file is not None:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Extracting and chunking document..."):
                try:
                    pages = extract_text_from_pdf(uploaded_file, uploaded_file.name)
                    chunks = split_text_into_chunks(pages, uploaded_file.name)

                    st.session_state.extracted_pages = pages
                    st.session_state.document_chunks = chunks
                    st.session_state.document_name = uploaded_file.name

                    st.success(
                        f"Extracted {len(pages)} pages and generated {len(chunks)} chunks successfully!"
                    )
                except Exception as e:
                    st.session_state.extracted_pages = None
                    st.session_state.document_chunks = None
                    st.session_state.document_name = None
                    st.error(f"Processing Error: {str(e)}")

    # نمایش جزییات فاز ۳ و ۴
    if st.session_state.document_chunks:
        chunks = st.session_state.document_chunks
        with st.expander("🧩 Chunking Summary & Inspection", expanded=False):
            st.write(f"**Document Name:** {st.session_state.document_name}")
            st.write(f"**Total Pages:** {len(st.session_state.extracted_pages)}")
            st.write(f"**Total Chunks:** {len(chunks)}")
            
            # پیش‌نمایش چانک اول
            st.markdown("---")
            st.markdown("**Chunk 1 Details:**")
            st.write(f"- **Chunk ID (UUID):** `{chunks[0]['chunk_id']}`")
            st.write(f"- **Page:** {chunks[0]['page_number']}")
            st.write(f"- **Length:** {chunks[0]['char_length']} chars")
            st.text_area("Chunk Content Preview:", chunks[0]["text"][:400] + "...", height=120)

    st.divider()

    # بخش پرسش و پاسخ
    st.subheader("2. Ask a Question")
    user_query = st.text_area(
        "Enter your question for Gemini:",
        placeholder="e.g., What are the core benefits of Retrieval-Augmented Generation?",
        height=100,
    )

    if st.button("Submit Question", type="primary"):
        if not user_query.strip():
            st.warning("Please enter a question before submitting.")
        else:
            with st.spinner("Generating answer from Gemini..."):
                response = generate_answer(user_query)
                st.subheader("Answer:")
                st.write(response)