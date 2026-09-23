from typing import List
from google.genai.errors import APIError
from app.ai.gemini import get_gemini_client


def get_text_embedding(text: str, model: str = "gemini-embedding-001") -> List[float]:
    """
    تولید بردار امبدینگ برای یک متن منفرد (مانند پرسش کاربر).
    خروجی: فهرستی از اعداد اعشاری (Vector).
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for embedding generation.")

    try:
        client = get_gemini_client()
        response = client.models.embed_content(
            model=model,
            contents=text,
        )
        if not response.embeddings:
            raise ValueError("No embeddings returned by the API.")
        return list(response.embeddings[0].values)
    except APIError as e:
        raise RuntimeError(f"Gemini Embedding API Error: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during embedding generation: {str(e)}")


def get_batch_embeddings(texts: List[str], model: str = "gemini-embedding-001") -> List[List[float]]:
    """
    تولید بردار امبدینگ به‌صورت دسته‌ای (Batch) برای فهرستی از Chunks.
    """
    if not texts:
        return []

    try:
        client = get_gemini_client()
        response = client.models.embed_content(
            model=model,
            contents=texts,
        )
        if not response.embeddings:
            raise ValueError("No embeddings returned by the API.")
        return [list(emb.values) for emb in response.embeddings]
    except APIError as e:
        raise RuntimeError(f"Gemini Batch Embedding API Error: {e.message}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during batch embedding generation: {str(e)}")