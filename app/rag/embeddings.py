from typing import List
from google import genai
from google.genai.errors import APIError
from app.ai.gemini import get_api_keys


def get_text_embedding(text: str, model: str = "gemini-embedding-001") -> List[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty for embedding generation.")

    keys = get_api_keys()
    last_error = ""

    for idx, key in enumerate(keys):
        try:
            client = genai.Client(api_key=key)
            response = client.models.embed_content(
                model=model,
                contents=text,
            )
            if not response.embeddings:
                raise ValueError("No embeddings returned by the API.")
            return list(response.embeddings[0].values)
        except APIError as e:
            last_error = e.message
            if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted"]) and idx < len(keys) - 1:
                continue
            raise RuntimeError(f"Gemini Embedding API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during embedding generation: {str(e)}")

    raise RuntimeError(f"All API keys rate-limited during embedding. Last error: {last_error}")


def get_batch_embeddings(texts: List[str], model: str = "gemini-embedding-001") -> List[List[float]]:
    if not texts:
        return []

    keys = get_api_keys()
    last_error = ""

    for idx, key in enumerate(keys):
        try:
            client = genai.Client(api_key=key)
            response = client.models.embed_content(
                model=model,
                contents=texts,
            )
            if not response.embeddings:
                raise ValueError("No embeddings returned by the API.")
            return [list(emb.values) for emb in response.embeddings]
        except APIError as e:
            last_error = e.message
            if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted"]) and idx < len(keys) - 1:
                continue
            raise RuntimeError(f"Gemini Batch Embedding API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during batch embedding generation: {str(e)}")

    raise RuntimeError(f"All API keys rate-limited during batch embedding. Last error: {last_error}")