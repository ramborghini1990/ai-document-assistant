import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_api_keys() -> List[str]:
    raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not keys:
        raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY or GEMINI_API_KEYS.")
    return keys


def get_gemini_client(api_key: str = None) -> genai.Client:
    if not api_key:
        api_key = get_api_keys()[0]
    return genai.Client(api_key=api_key)


def generate_answer(prompt: str) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    keys = get_api_keys()
    last_error = ""

    for idx, key in enumerate(keys):
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            if response.text and response.text.strip():
                return response.text
            return "The model returned an empty response."

        except APIError as e:
            last_error = e.message
            is_rate_limit = any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand"])
            if is_rate_limit and idx < len(keys) - 1:
                continue
            raise RuntimeError(f"Gemini API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {str(e)}")

    raise RuntimeError(f"All API keys are currently rate-limited. Last error: {last_error}")