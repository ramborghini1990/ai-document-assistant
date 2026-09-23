import streamlit as st
from app.ai.gemini import generate_answer


def render_ui():
    st.set_page_config(
        page_title="AI Document Assistant",
        page_icon="📄",
        layout="centered",
    )

    st.title("📄 AI Document Assistant")
    st.caption("Phase 2 — Direct Gemini Interaction (RAG pipeline coming soon)")

    # بخش بارگذاری فایل برای فازهای بعدی
    st.subheader("1. Document Upload")
    uploaded_file = st.file_uploader(
        "Upload a PDF document (will be processed in Phase 3)",
        type=["pdf"],
        disabled=True,
        help="PDF processing will be activated in Phase 3.",
    )
    if uploaded_file is not None:
        st.info("PDF upload detected. Pipeline will process this in later phases.")

    st.divider()

    # بخش پرسش و پاسخ متنی اولیه
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