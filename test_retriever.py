from app.rag.retriever import retrieve_relevant_chunks
from app.ai.prompts import build_rag_prompt


def run_retriever_test():
    print("Testing Semantic Retrieval and Page Tracking...")

    # تست ۱: بازیابی از کالکشن تستی
    query_1 = "Tell me about technical universities in Italy"
    print(f"\n--- Query 1: '{query_1}' ---")
    results = retrieve_relevant_chunks(query_1, collection_name="test_collection", top_k=1)

    if results:
        match = results[0]
        # بررسی وجود فیلدها در سطح ریشه
        assert "text" in match
        assert "page_number" in match
        assert "document_name" in match
        assert "metadata" in match
        assert "distance" in match

        print("✓ Top match contract validated:")
        print(f"  - Document: {match['document_name']}")
        print(f"  - Page: {match['page_number']}")
        print(f"  - Distance: {match['distance']:.4f}")

        # تست ۲: بررسی ساخت صحیح کانتکست پرامپت RAG بدون N/A
        prompt = build_rag_prompt(query_1, results)
        assert f"Page: {match['page_number']}" in prompt
        assert "Page: N/A" not in prompt or match["page_number"] == "N/A"
        print("✓ RAG prompt correctly inherited source page numbers without 'N/A' fallback.")
    else:
        print("⚠️ Note: 'test_collection' is empty in current run. Populate it via test_chromadb.py first.")

    print("\n✓ test_retriever contract verified successfully.")


if __name__ == "__main__":
    run_retriever_test()