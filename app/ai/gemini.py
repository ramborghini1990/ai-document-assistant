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


def generate_answer(prompt: str, model: str = "gemini-3.6-flash", max_retries: int = 2) -> str:
    """ارسال پرامپت با مدیریت خطا و بازتلاش خودکار در صورت بروز خطای ترافیک یا محدودیت سهمیه."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = get_gemini_client()

    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            if not response.text:
                return "The model returned an empty response."
            return response.text

        except APIError as e:
            # اگر خطای ترافیک بالا (503) یا محدودیت موقت تعداد درخواست (429) بود، چند ثانیه صبر و مجدد تلاش کن
            if attempt < max_retries and ("429" in str(e) or "503" in str(e) or "Quota" in str(e)):
                time.sleep(4)
                continue
            return f"Gemini API Error: {e.message}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

    return "Service temporarily busy. Please wait a few seconds and try again."