import os
import time
from typing import List, Any
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_api_keys() -> List[str]:
    """دریافت لیست کلیدها از متغیرهای محیطی."""
    raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
    keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
    if not keys:
        raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY or GEMINI_API_KEYS.")
    return keys


def get_gemini_client(api_key: str = None) -> genai.Client:
    """ایجاد کلاینت با کلید مشخص یا اولین کلید فعال."""
    if not api_key:
        api_key = get_api_keys()[0]
    return genai.Client(api_key=api_key)


def generate_answer(prompt: str) -> str:
    """تولید پاسخ متنی با چرخش بین کلیدها و بازتلاش در زمان ترافیک سرور."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    keys = get_api_keys()
    last_error = ""

    for idx, key in enumerate(keys):
        client = genai.Client(api_key=key)
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                )
                if response.text and response.text.strip():
                    return response.text
                return "The model returned an empty response."

            except APIError as e:
                last_error = e.message
                is_busy = any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand", "unavailable"])
                if is_busy and attempt < 2:
                    time.sleep((attempt + 1) * 2)  # مکث ۲ و ۴ ثانیه‌ای
                    continue
                if is_busy and idx < len(keys) - 1:
                    break  # سوئیچ به کلید بعدی
                raise RuntimeError(f"Gemini API Error: {e.message}")
            except Exception as e:
                raise RuntimeError(f"Unexpected Error: {str(e)}")

    raise RuntimeError(f"All API keys are currently rate-limited or unavailable. Details: {last_error}")


def transcribe_image_with_vision(image: Any, prompt: str) -> str:
    """استخراج متن از تصویر با چرخش هوشمند کلیدها بدون اتلاف سهمیه."""
    keys = get_api_keys()
    last_error = ""

    for key in keys:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[image, prompt],
            )
            if response.text and response.text.strip():
                return response.text.strip()
            return ""

        except APIError as e:
            last_error = e.message
            # اگر خطای ترافیک یا محدودیت سهمیه بود، فوراً کلید بعدی را تست کن
            if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand"]):
                continue
            raise RuntimeError(f"Gemini Vision API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during image transcription: {str(e)}")

    raise RuntimeError(f"All API keys rate-limited or busy. Details: {last_error}")