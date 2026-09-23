from typing import List, Dict, Any
from app.rag.embeddings import get_text_embedding
from app.rag.vectorstore import get_or_create_collection


def retrieve_relevant_chunks(
    query: str,
    collection_name: str = "document_chunks",
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    بازیابی معنایی برترین قطعات سند متناسب با پرسش کاربر.
    
    مراحل:
    ۱. تبدیل پرسش متنی به بردار امبدینگ
    ۲. اجرای جستجوی شباهت کسینوسی در ChromaDB
    ۳. فرمت‌بندی خروجی شامل متن، متادیتا و فاصله برداری
    """
    if not query or not query.strip():
        raise ValueError("Query text cannot be empty for retrieval.")

    if top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    collection = get_or_create_collection(collection_name)

    # بررسی خالی نبودن کالکشن
    if collection.count() == 0:
        return []

    # گام ۱: ساخت بردار برای سوال کاربر
    query_vector = get_text_embedding(query)

    # گام ۲: جستجوی برداری در ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    retrieved_chunks = []

    # گام ۳: استخراج و ساختاردهی نتایج
    if results and results.get("documents") and len(results["documents"][0]) > 0:
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        ids = results["ids"][0]

        for i in range(len(docs)):
            retrieved_chunks.append({
                "chunk_id": ids[i],
                "text": docs[i],
                "document_name": metadatas[i].get("document_name", "unknown"),
                "page_number": metadatas[i].get("page_number", 0),
                "distance": distances[i]  # مقدار فاصله کسینوسی (کمتر = مرتبط‌تر)
            })

    return retrieved_chunks