from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import store_chunks_in_chromadb, get_or_create_collection

if __name__ == "__main__":
    print("Testing ChromaDB storage pipeline...")

    # نمونه داده‌های آزمایشی فاز ۴
    sample_chunks = [
        {
            "chunk_id": "test-uuid-001",
            "document_name": "sample.pdf",
            "page_number": 1,
            "text": "Politecnico di Torino is a historical technical university in Turin, Italy.",
            "char_length": 75
        },
        {
            "chunk_id": "test-uuid-002",
            "document_name": "sample.pdf",
            "page_number": 2,
            "text": "Retrieval-Augmented Generation bridges the gap between static LLMs and dynamic knowledge.",
            "char_length": 89
        }
    ]

    print("Generating embeddings for sample chunks...")
    sample_texts = [c["text"] for c in sample_chunks]
    sample_embeddings = get_batch_embeddings(sample_texts)

    print("Storing chunks in ChromaDB...")
    stored_count = store_chunks_in_chromadb(sample_chunks, sample_embeddings, collection_name="test_collection")
    print(f"Stored {stored_count} items in ChromaDB successfully.")

    # بررسی صحت ذخیره‌سازی و پایداری
    collection = get_or_create_collection("test_collection")
    total_count = collection.count()
    print(f"Total documents in test collection: {total_count}")

    # بازیابی ساده رکورد اول برای بازبینی
    sample_record = collection.get(ids=["test-uuid-001"])
    print(f"Verified Record: {sample_record['documents'][0]}")
    print(f"Metadata: {sample_record['metadatas'][0]}")