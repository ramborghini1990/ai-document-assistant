import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    return genai.Client(api_key=api_key)


# لیست مدل‌ها جهت سوئیچ خودکار در صورت اشباع ظرفیت
CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]


def generate_answer(prompt: str) -> str:
    """ارسال پرامپت با قابلیت سوئیچ خودکار به مدل‌های جایگزین در صورت پر شدن سهمیه."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client()
    last_error = ""

    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response.text and response.text.strip():
                return response.text
        except APIError as e:
            last_error = e.message
            # اگر خطای پر شدن سهمیه (429) یا ترافیک (503) بود، مدل بعدی را امتحان کن
            if "429" in str(e) or "503" in str(e) or "Quota" in str(e):
                time.sleep(1)
                continue
            raise RuntimeError(f"Gemini API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {str(e)}")

    raise RuntimeError(f"All models temporarily busy. Details: {last_error}")