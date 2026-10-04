from typing import List, Dict, Any


def build_rag_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    ساخت پرامپت مهندسی‌شده RAG با تفکیک دقیق دستورالعمل، زمینه سند، و سوال کاربر.
    شامل قانون اکید عدم حدس زدن و درج شماره صفحه هر قطعه (با خوانش دوگانه ایمن از ریشه و metadata).
    """
    if not retrieved_chunks:
        context_str = "No relevant context found in the uploaded document."
    else:
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            meta = chunk.get("metadata", {}) if isinstance(chunk.get("metadata"), dict) else {}
            page_num = chunk.get("page_number") or meta.get("page_number") or "N/A"
            doc_name = chunk.get("document_name") or meta.get("document_name")

            header = f"Source {i} | Page: {page_num}"
            if doc_name and doc_name != "unknown":
                header += f" | Doc: {doc_name}"

            block = (
                f"[{header}]:\n"
                f"{chunk.get('text', '').strip()}"
            )
            context_blocks.append(block)
        context_str = "\n\n".join(context_blocks)

    prompt = f"""You are a helpful and precise AI Document Assistant.
Your task is to answer the user's question STRICTLY based on the provided document context below.

CRITICAL INSTRUCTIONS:
1. Answer using ONLY facts directly mentioned in the document context.
2. If the document context does not contain enough information to answer the question, clearly state:
   "The uploaded document does not provide enough information to answer this question."
3. Do NOT make assumptions, extrapolate, or fabricate information.
4. Mention the relevant page number(s) if applicable when referencing facts.

---
DOCUMENT CONTEXT:
{context_str}
---

USER QUESTION:
{query}

ANSWER:"""

    return prompt