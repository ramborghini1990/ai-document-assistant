import re
import unicodedata
from datetime import datetime
from typing import Optional

SUPPORTED_MONTHS = {
    # ایتالیایی
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
    "gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
    "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12,
    # انگلیسی
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}


_TIME_SUFFIX = re.compile(r"[T\s]+\d{1,2}:\d{2}(?::\d{2}(?:[.,]\d+)?)?\s*(?:Z|[+-]\d{2}:?\d{2})?$")


def normalize_date(raw_date_str: Optional[str]) -> Optional[str]:
    """
    نرمال‌سازی تاریخ‌های گوناگون (ایتالیایی، انگلیسی، اسلش، نقطه و خط فاصله) به فرمت YYYY-MM-DD.
    """
    if not raw_date_str or not isinstance(raw_date_str, str):
        return None

    # timestamps (Excel datetimes, ISO 8601): only the calendar day matters
    raw_date_str = _TIME_SUFFIX.sub("", raw_date_str.strip())

    cleaned = raw_date_str.strip().lower()
    cleaned = re.sub(r"[,\.]", " ", cleaned)
    cleaned = " ".join(cleaned.split())

    # تاریخ‌های حروفی مانند '31 luglio 2026' یا '15 October 2026'
    for m_name, m_num in SUPPORTED_MONTHS.items():
        if m_name in cleaned:
            pattern = rf"(\d{{1,2}})\s+{m_name}\s+(\d{{4}})"
            match = re.search(pattern, cleaned)
            if match:
                day, year = int(match.group(1)), int(match.group(2))
                return f"{year:04d}-{m_num:02d}-{day:02d}"

    raw_norm = raw_date_str.strip().replace(".", "/").replace("-", "/")

    # DD/MM/YYYY
    match_dmy = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", raw_norm)
    if match_dmy:
        d, m, y = int(match_dmy.group(1)), int(match_dmy.group(2)), int(match_dmy.group(3))
        return f"{y:04d}-{m:02d}-{d:02d}"

    # YYYY/MM/DD
    match_ymd = re.match(r"^(\d{4})/(\d{1,2})/(\d{1,2})$", raw_norm)
    if match_ymd:
        y, m, d = int(match_ymd.group(1)), int(match_ymd.group(2)), int(match_ymd.group(3))
        return f"{y:04d}-{m:02d}-{d:02d}"

    return raw_date_str.strip()


_NUMBER_TOKEN = re.compile(r"[-+]?[0-9]+(?:[\.\,][0-9]+)*")
# A number that stands on its own: not glued to letters or other digits, so unit suffixes such as
# "m3", "CO2" or "L/100km" are not counted as separate figures.
_STANDALONE_NUMBER = re.compile(r"(?<![A-Za-z0-9/])[-+]?[0-9]+(?:[\.\,][0-9]+)*(?![A-Za-z0-9])")
_THOUSANDS_DOT = re.compile(r"^[-+]?\d{1,3}(\.\d{3})+$")


def _token_to_float(token: str) -> Optional[float]:
    """
    Single source of truth for Italian/international separators (used by every number parser).
    - '.' and ',' both present: the right-most one is the decimal separator ('1.250,50', '1,250.50').
    - only ',': decimal comma ('250,00').
    - only '.': thousands when it groups exactly 3 digits ('2.000', '1.234.567'), else decimal ('12.5').
    """
    t = token.strip()
    if "." in t and "," in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        t = t.replace(",", ".")
    elif "." in t and _THOUSANDS_DOT.match(t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def parse_number_token(token: Optional[str]) -> Optional[float]:
    """Strict: the whole token must be one number ('1.500,5' -> 1500.5, '9 t' -> None)."""
    if token is None:
        return None
    t = str(token).strip()
    if not _NUMBER_TOKEN.fullmatch(t):
        return None
    return _token_to_float(t)


def count_standalone_numbers(text: Optional[str]) -> int:
    """How many separate figures a raw value contains ('IVA 22% su 1.234,00' -> 2, '125 m3' -> 1)."""
    return len(_STANDALONE_NUMBER.findall(str(text or "")))


def normalize_number(raw_num_str: Optional[str]) -> Optional[float]:
    """
    نرمال‌سازی دقیق اعداد با فرمت ایتالیایی و بین‌المللی به عدد float استاندارد.
    Returns the first number found in the text. Callers that must not guess when several figures are
    present (extraction) check `count_standalone_numbers` first.
    """
    if raw_num_str is None:
        return None

    if isinstance(raw_num_str, (int, float)):
        return float(raw_num_str)

    num_match = _NUMBER_TOKEN.search(str(raw_num_str).strip())
    if not num_match:
        return None
    return _token_to_float(num_match.group(0))


def normalize_plate(plate_str: Optional[str]) -> Optional[str]:
    """یکسان‌سازی پلاک خودرو (حذف فاصله‌ها و بزرگ‌نویسی حروف)."""
    if not plate_str:
        return None
    return re.sub(r"[\s\-_]", "", str(plate_str)).upper()


def normalize_key(text: str) -> str:
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[\s_\-\./]+", " ", s).strip()


def keyword_matches(term: str, text: str) -> bool:
    t = normalize_key(term)
    prefix = t.endswith("*")
    body = re.escape(t.rstrip("*").strip())
    return re.search(r"(?<![a-z0-9])" + body + ("" if prefix else r"(?![a-z0-9])"),
                     normalize_key(text)) is not None
