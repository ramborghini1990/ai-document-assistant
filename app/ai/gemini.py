import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    return genai.Client(api_key=api_key)


def generate_answer(prompt: str, max_retries: int = 3) -> str:
    """
    ارسال پرامپت به مدل gemini-3.6-flash با قابلیت بازتلاش هوشمند 
    در صورت شلوغی سرور یا محدودیت موقت سهمیه (Rate Limit).
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client()

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            if response.text and response.text.strip():
                return response.text
            return "The model returned an empty response."

        except APIError as e:
            # در صورت خطای ترافیک بالا (503) یا محدودیت سهمیه (429)، چند ثانیه مکث و تلاش مجدد
            is_rate_limit = any(term in str(e) for term in ["429", "503", "Quota", "quota", "demand"])
            if is_rate_limit and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3  # مکث ۳ و سپس ۶ ثانیه‌ای
                time.sleep(wait_time)
                continue
            raise RuntimeError(f"Gemini API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {str(e)}")

    raise RuntimeError("The model is currently experiencing high demand. Please try again in a few moments.")