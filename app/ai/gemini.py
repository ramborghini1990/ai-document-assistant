import os
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()


def get_gemini_client() -> genai.Client:
    """ساخت و بازگرداندن کلاینت جمینای با اعتبارسنجی کلید API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set it in your .env file."
        )
    return genai.Client(api_key=api_key)


def generate_answer(prompt: str, model: str = "gemini-3.6-flash") -> str:
    """ارسال پرامپت به جمینای و دریافت پاسخ با مدیریت خطاهای احتمالی."""
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        if response.text:
            return response.text
        return "No text response received from Gemini."

    except APIError as e:
        return f"Gemini API Error: {e.message}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"