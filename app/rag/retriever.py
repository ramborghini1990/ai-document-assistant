from typing import List, Dict, Any, Optional
from app.rag.embeddings import get_batch_embeddings
from app.rag.vectorstore import get_chroma_collection


def retrieve_relevant_chunks(
    query: str,
    collection_name: str = "document_chunks",
    top_k: int = 4,
    document_names: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    بازیابی معنایی مرتبط‌ترین چانک‌ها با امکان فیلتر کردن دقیق روی اسناد سشن فعال.
    فیلدهای page_number و document_name هم در سطح ریشه دیکشنری و هم درون metadata
    قرار داده می‌شوند تا سازگاری کامل حفظ شود.
    """
    if not query or not query.strip():
        raise ValueError("Retrieval query cannot be empty.")

    collection = get_chroma_collection(collection_name)
    total_count = collection.count()
    if total_count == 0:
        return []

    query_embedding = get_batch_embeddings([query])[0]

    # ایجاد فیلتر بر اساس نام اسناد فعال (در صورت مشخص بودن)
    where_filter = None
    if document_names:
        if len(document_names) == 1:
            where_filter = {"document_name": document_names[0]}
        else:
            where_filter = {"document_name": {"$in": document_names}}

    effective_k = min(top_k, total_count)

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=effective_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        print(f"Warning in retrieval query: {e}")
        return []

    retrieved_chunks = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for doc_text, meta, dist in zip(docs, metas, dists):
            safe_meta = meta if isinstance(meta, dict) else {}
            page_num = safe_meta.get("page_number", "N/A")
            doc_name = safe_meta.get("document_name", "unknown")

            retrieved_chunks.append({
                "text": doc_text,
                "metadata": safe_meta,
                "page_number": page_num,
                "document_name": doc_name,
                "distance": dist
            })

    return retrieved_chunks