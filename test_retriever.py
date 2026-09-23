from app.rag.retriever import retrieve_relevant_chunks

if __name__ == "__main__":
    print("Testing Semantic Retrieval against ChromaDB...")

    # سوال اول: مرتبط با رکورد ایتالیا و دانشگاه که در فاز ۶ ذخیره شد
    query_1 = "Tell me about technical universities in Italy"
    print(f"\n--- Query 1: '{query_1}' ---")
    results_1 = retrieve_relevant_chunks(query_1, collection_name="test_collection", top_k=1)
    
    if results_1:
        match = results_1[0]
        print(f"Top Match Found:")
        print(f"- Text: {match['text']}")
        print(f"- Page: {match['page_number']}")
        print(f"- Document: {match['document_name']}")
        print(f"- Cosine Distance: {match['distance']:.4f}")
    else:
        print("No matches found.")

    # سوال دوم: مرتبط با مفهوم هوش مصنوعی و RAG
    query_2 = "What connects LLMs with external knowledge?"
    print(f"\n--- Query 2: '{query_2}' ---")
    results_2 = retrieve_relevant_chunks(query_2, collection_name="test_collection", top_k=1)
    
    if results_2:
        match = results_2[0]
        print(f"Top Match Found:")
        print(f"- Text: {match['text']}")
        print(f"- Page: {match['page_number']}")
        print(f"- Document: {match['document_name']}")
        print(f"- Cosine Distance: {match['distance']:.4f}")
    else:
        print("No matches found.")