import re
from datetime import datetime
from typing import Optional, Tuple

ITALIAN_MONTHS = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
    "gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
    "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12
}


def normalize_date(raw_date_str: Optional[str]) -> Optional[str]:
    """
    نرمال‌سازی تاریخ‌های گوناگون (ایتالیایی، اسلش، نقطه، خط فاصله و حروفی) به فرمت YYYY-MM-DD.
    در صورت عدم امکان تشخیص، مقدار اولیه حفظ شده یا None بازگردانده می‌شود.
    """
    if not raw_date_str or not isinstance(raw_date_str, str):
        return None

    cleaned = raw_date_str.strip().lower()
    cleaned = re.sub(r"[,\.]", " ", cleaned)
    cleaned = " ".join(cleaned.split())

    # الگوی ۱: تاریخ‌های حروفی مانند '31 luglio 2026'
    for m_name, m_num in ITALIAN_MONTHS.items():
        if m_name in cleaned:
            pattern = rf"(\d{{1,2}})\s+{m_name}\s+(\d{{4}})"
            match = re.search(pattern, cleaned)
            if match:
                day, year = int(match.group(1)), int(match.group(2))
                return f"{year:04d}-{m_num:02d}-{day:02d}"

    # بازگردانی علائم تفکیک‌کننده برای الگوهای عددی
    raw_norm = raw_date_str.strip().replace(".", "/").replace("-", "/")

    # الگوی ۲: DD/MM/YYYY
    match_dmy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", raw_norm)
    if match_dmy:
        d, m, y = int(match_dmy.group(1)), int(match_dmy.group(2)), int(match_dmy.group(3))
        return f"{y:04d}-{m:02d}-{d:02d}"

    # الگوی ۳: YYYY/MM/DD
    match_ymd = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", raw_norm)
    if match_ymd:
        y, m, d = int(match_ymd.group(1)), int(match_ymd.group(2)), int(match_ymd.group(3))
        return f"{y:04d}-{m:02d}-{d:02d}"

    return raw_date_str.strip()


def normalize_number(raw_num_str: Optional[str]) -> Optional[float]:
    """
    نرمال‌سازی دقیق اعداد با فرمت ایتالیایی و بین‌المللی به عدد float استاندارد.
    """
    if raw_num_str is None:
        return None

    if isinstance(raw_num_str, (int, float)):
        return float(raw_num_str)

    val = str(raw_num_str).strip()
    num_match = re.search(r"[-+]?[0-9]+(?:[\.\,][0-9]+)*", val)
    if not num_match:
        return None

    clean_str = num_match.group(0)

    # حالت اول: هم نقطه و هم ویرگول وجود دارد (مانند 1.250,50 یا 1,250.50)
    if "." in clean_str and "," in clean_str:
        if clean_str.rfind(",") > clean_str.rfind("."):
            clean_str = clean_str.replace(".", "").replace(",", ".")
        else:
            clean_str = clean_str.replace(",", "")
    # حالت دوم: فقط ویرگول وجود دارد (مانند 250,00 -> 250.00)
    elif "," in clean_str:
        clean_str = clean_str.replace(",", ".")
    # حالت سوم: فقط نقطه وجود دارد (تشخیص هوشمند هزارگان ایتالیایی مثل 2.000 یا اعشار مثل 12.5)
    elif "." in clean_str:
        # اگر نقطه قبل از دقیقاً ۳ رقم قرار گرفته باشد، جداکننده هزارگان است
        if re.match(r"^\d{1,3}(\.\d{3})+$", clean_str):
            clean_str = clean_str.replace(".", "")

    try:
        return float(clean_str)
    except ValueError:
        return None


def normalize_plate(plate_str: Optional[str]) -> Optional[str]:
    """یکسان‌سازی پلاک خودرو (حذف فاصله‌ها و بزرگ‌نویسی حروف)."""
    if not plate_str:
        return None
    return re.sub(r"[\s\-_]", "", str(plate_str)).upper()