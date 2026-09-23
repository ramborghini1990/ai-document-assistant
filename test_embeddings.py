from app.rag.embeddings import get_text_embedding, get_batch_embeddings

if __name__ == "__main__":
    print("Testing Gemini Embedding API...")

    single_text = "Retrieval-Augmented Generation improves LLM reliability."
    single_vector = get_text_embedding(single_text)
    print(f"Single text embedding generated successfully!")
    print(f"- Vector dimensions: {len(single_vector)}")
    print(f"- First 5 values: {single_vector[:5]}")

    batch_texts = [
        "First test chunk about civil engineering.",
        "Second test chunk about artificial intelligence."
    ]
    batch_vectors = get_batch_embeddings(batch_texts)
    print(f"\nBatch embeddings generated successfully!")
    print(f"- Number of vectors: {len(batch_vectors)}")
    print(f"- Vector 1 dimensions: {len(batch_vectors[0])}")