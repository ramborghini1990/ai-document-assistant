"""
Review round-trip engine:
records -> DataFrame (st.data_editor) -> records (with deterministic re-normalization).
Ensures user manual edits persist into export payloads without hallucination.
"""
from typing import Any, Dict, List, Optional
import pandas as pd
from app.extraction.extractor import finalize_record, normalize_field
from app.extraction.registry import SchemaDef

_META = ["_rid", "source_document", "source_page"]


def _display(fdata: Dict[str, Any]) -> str:
    """دریافت رشته نمایشی برای سلول جدول بازبینی."""
    v = fdata.get("normalized_value")
    if v is None:
        v = fdata.get("raw_value")
    return "" if v is None else str(v)


def records_to_dataframe(records: List[Dict[str, Any]], schema: SchemaDef) -> pd.DataFrame:
    """تبدیل رکوردهای استخراج‌شده به دیتافریم پایدار با شناسه مخفی ردیف (_rid)."""
    rows = []
    for i, rec in enumerate(records):
        row = {
            "_rid": str(i),
            "source_document": rec.get("source_document", ""),
            "source_page": str(rec.get("source_page", ""))
        }
        for n in schema.fields:
            row[n] = _display(rec.get("fields", {}).get(n, {}))
        rows.append(row)
    return pd.DataFrame(rows, columns=_META + list(schema.fields), dtype="object")


def _cell_text(cell: Any) -> str:
    if cell is None or (not isinstance(cell, str) and pd.isna(cell)):
        return ""
    return str(cell).strip()


def dataframe_to_records(df: pd.DataFrame, original: List[Dict[str, Any]], schema: SchemaDef) -> List[Dict[str, Any]]:
    """
    تبدیل خروجی ویرایش‌شده دیتافریم به رکوردهای معتبر با نرمال‌سازی مجدد و محاسبه مجدد فیلدهای مشتق‌شده.
    """
    out = []
    for _, row in df.iterrows():
        rid = _cell_text(row.get("_rid"))
        orig: Optional[Dict[str, Any]] = (
            original[int(rid)] if rid.isdigit() and int(rid) < len(original) else None
        )
        fields = {}
        for n, fdef in schema.fields.items():
            text = _cell_text(row.get(n))
            prev = ((orig or {}).get("fields") or {}).get(n)
            
            # اگر سلول تغییر نکرده باشد، وضعیت و مقدار خام قبلی حفظ می‌شود
            if prev is not None and text == _display(prev):
                fields[n] = dict(prev)
            else:
                # در صورت ویرایش دستی، وضعیت فیلد به EDITED ارتقا می‌یابد
                fields[n] = normalize_field(fdef, text or None, ok_status="EDITED")

        # محاسبه مجدد قطعی فرمول‌ها (مثل L/100km) و اخطارهای فیلدهای اجباری
        warnings = finalize_record(schema, fields)
        page = (orig or {}).get("source_page")
        src_doc = (orig or {}).get("source_document") or _cell_text(row.get("source_document")) or "manual"

        out.append({
            "source_document": src_doc,
            "source_page": page,
            "fields": fields,
            "warnings": warnings
        })
    return out