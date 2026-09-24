import os
import re
import time
import warnings
from typing import List, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

warnings.filterwarnings("ignore")
load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def get_api_keys() -> List[str]:
    """دریافت و پالایش کلیدها از متغیرهای محیطی."""
    raw_keys = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY") or ""
    keys = [k.strip().strip("'\"") for k in raw_keys.split(",") if k.strip().strip("'\"")]
    if not keys:
        raise ValueError("No Gemini API key found. Please set GEMINI_API_KEY or GEMINI_API_KEYS.")
    return keys


def get_gemini_client(api_key: str = None) -> genai.Client:
    """ایجاد کلاینت با کلید مشخص یا اولین کلید فعال."""
    if not api_key:
        api_key = get_api_keys()[0]
    return genai.Client(api_key=api_key)


def generate_answer(prompt: str) -> str:
    """تولید پاسخ متنی با چرخش هوشمند کلیدها."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    keys = get_api_keys()
    last_error = ""

    for key in keys:
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
            if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand"]):
                continue
            raise RuntimeError(f"Gemini API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected Error: {str(e)}")

    raise RuntimeError(f"All API keys are currently rate-limited or unavailable. Details: {last_error}")


def generate_structured_json(prompt: str, system_instruction: str = "", max_attempts: int = 4) -> str:
    """تولید خروجی ساختاریافته JSON با شکیبایی تطبیقی تا بازنشانی پنجره سهمیه گوگل."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    keys = get_api_keys()
    last_error = ""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction if system_instruction else None,
        response_mime_type="application/json",
    )

    for attempt in range(max_attempts):
        for key in keys:
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config=config,
                )
                if response.text and response.text.strip():
                    return response.text.strip()
                return "{}"

            except APIError as e:
                last_error = e.message
                if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand"]):
                    continue
                raise RuntimeError(f"Gemini Structured JSON API Error: {e.message}")
            except Exception as e:
                raise RuntimeError(f"Unexpected error during structured generation: {str(e)}")

        # در صورت پر بودن سهمیه تمام کلیدها، خواندن دقیق ثانیه اعلامی گوگل و شکیبایی هوشمند
        if attempt < max_attempts - 1:
            wait_match = re.search(r"retry in ([\d\.]+)s", last_error, re.IGNORECASE)
            delay = int(float(wait_match.group(1))) + 2 if wait_match else 25
            print(f"\n⏳ Google quota cooling down. Waiting {delay}s for window reset (attempt {attempt+1}/{max_attempts})...")
            time.sleep(delay)

    raise RuntimeError(f"All API keys rate-limited or busy. Details: {last_error}")


def transcribe_image_with_vision(image: Any, prompt: str) -> str:
    """استخراج متن از تصویر با چرخش هوشمند کلیدها."""
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
            if any(term in str(e).lower() for term in ["429", "503", "quota", "resource_exhausted", "demand"]):
                continue
            raise RuntimeError(f"Gemini Vision API Error: {e.message}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during image transcription: {str(e)}")

    raise RuntimeError(f"All API keys rate-limited or busy. Details: {last_error}")