import io
from app.ai.gemini import generate_answer
from app.ai.prompts import build_rag_prompt
from app.rag.chunker import split_text_into_chunks
from app.rag.loader import extract_text_from_pdf
from app.rag.retriever import retrieve_relevant_chunks
from app.database.database import init_db, get_conversation_history


def test_empty_prompt_validation():
    """تست اعتبارسنجی ارسال پرامپت خالی به جمینای."""
    try:
        generate_answer("")
        assert False, "Failed: Empty prompt should have raised a ValueError."
    except ValueError:
        print("[PASS] Empty prompt correctly rejected.")


def test_chunker_invalid_overlap():
    """تست جلوگیری از تنظیم اندازه چانک کمتر از همپوشانی."""
    try:
        split_text_into_chunks([{"page_number": 1, "text": "Test"}], "test.pdf", chunk_size=100, chunk_overlap=200)
        assert False, "Failed: Overlap greater than chunk_size should raise ValueError."
    except ValueError:
        print("[PASS] Invalid chunk overlap correctly rejected.")


def test_rag_prompt_empty_context():
    """تست ساختار پرامپت زمانی که هیچ کانتکستی از سند استخراج نشده است."""
    prompt = build_rag_prompt("Any question?", [])
    assert "No relevant context found" in prompt
    print("[PASS] RAG prompt gracefully handles empty retrieval context.")


def test_retriever_empty_query():
    """تست بازیابی با ورودی خالی."""
    try:
        retrieve_relevant_chunks("")
        assert False, "Failed: Empty query should raise ValueError."
    except ValueError:
        print("[PASS] Empty retrieval query rejected gracefully.")


def test_database_empty_history():
    """تست بازخوانی تاریخچه برای شناسه مکالمه‌ای که وجود ندارد."""
    init_db()
    history = get_conversation_history("non-existent-uuid")
    assert history == []
    print("[PASS] Database returns empty list for non-existent conversation history.")


def test_empty_pdf_stream():
    """تست واکنش لودر به یک بایت‌استریم خالی."""
    try:
        empty_stream = io.BytesIO(b"")
        extract_text_from_pdf(empty_stream, "empty.pdf")
        assert False, "Failed: Empty stream should raise ValueError."
    except ValueError:
        print("[PASS] Empty/corrupt PDF stream detected and rejected.")


if __name__ == "__main__":
    print("Running Edge Cases and Failure Modes Verification...\n")
    test_empty_prompt_validation()
    test_chunker_invalid_overlap()
    test_rag_prompt_empty_context()
    test_retriever_empty_query()
    test_database_empty_history()
    test_empty_pdf_stream()
    print("\nAll edge-case tests passed successfully!")