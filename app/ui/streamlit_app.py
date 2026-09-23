import streamlit as st
from app.ai.gemini import generate_answer
from app.rag.loader import extract_text_from_pdf


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant",
        page_icon="📄",
        layout="centered",
    )

    st.title("📄 AI Document Assistant")
    st.caption("Phase 3 — PDF Text Extraction Active")

    # متغیرهای حالت نشست (Session State) برای نگهداری سند پردازش‌شده
    if "extracted_pages" not in st.session_state:
        st.session_state.extracted_pages = None
    if "document_name" not in st.session_state:
        st.session_state.document_name = None

    # بخش آپلود فایل PDF
    st.subheader("1. Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        help="Upload a text-based PDF to extract its contents.",
    )

    if uploaded_file is not None:
        if st.session_state.document_name != uploaded_file.name:
            with st.spinner("Extracting text from PDF..."):
                try:
                    pages = extract_text_from_pdf(uploaded_file, uploaded_file.name)
                    st.session_state.extracted_pages = pages
                    st.session_state.document_name = uploaded_file.name
                    st.success(f"Successfully extracted text from {len(pages)} pages!")
                except Exception as e:
                    st.session_state.extracted_pages = None
                    st.session_state.document_name = None
                    st.error(f"Extraction Error: {str(e)}")

    # نمایش خلاصه سند در صورت وجود
    if st.session_state.extracted_pages:
        total_chars = sum(len(p["text"]) for p in st.session_state.extracted_pages)
        with st.expander("📄 Document Extraction Summary", expanded=False):
            st.write(f"**Filename:** {st.session_state.document_name}")
            st.write(f"**Total Pages:** {len(st.session_state.extracted_pages)}")
            st.write(f"**Total Characters:** {total_chars}")
            st.text_area("Preview (Page 1):", st.session_state.extracted_pages[0]["text"][:500] + "...", height=120)

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