"""Extracts actionable deadlines from reviewed records and schemas."""
import uuid
from typing import Any, Dict, List
from app.extraction.registry import resolve_schema, SchemaDef

NAMESPACE_DEADLINE = uuid.uuid5(uuid.NAMESPACE_DNS, "ai-document-assistant.deadlines")


def make_deadline_id(module_id: str, schema_name: str, doc: str, page: int, field_name: str, desc: str) -> str:
    """تولید شناسه قطعی و یکتا (UUID5) بر اساس مشخصات سررسید."""
    key = f"{module_id}|{schema_name}|{doc}|{page}|{field_name}|{desc}"
    return str(uuid.uuid5(NAMESPACE_DEADLINE, key))


def extract_deadlines_from_records(
    module_id: str,
    schema_name: str,
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    استخراج سررسیدهای قطعی از رکوردهای بازبینی‌شده.
    تاریخ‌های نامعتبر یا گم‌شده نادیده گرفته می‌شوند.
    """
    schema: SchemaDef = resolve_schema(schema_name, module_id)
    out = []

    for rec in records:
        src_doc = rec.get("source_document") or "-"
        src_page = rec.get("source_page") or 1
        fields = rec.get("fields", {})

        for fname, fdef in schema.fields.items():
            if not fdef.alert:
                continue

            fdata = fields.get(fname, {})
            # فقط رکوردهای تأییدشده با مقدار معتبر ISO استخراج می‌شوند
            if fdata.get("status") not in ("EXTRACTED", "EDITED", "CALCULATED"):
                continue

            iso_date = fdata.get("normalized_value")
            if not iso_date or not isinstance(iso_date, str) or len(iso_date) != 10:
                continue

            # استخراج عنوان توصیفی از label_fields
            label_parts = []
            for lf in fdef.alert.get("label_fields", []):
                val = fields.get(lf, {}).get("normalized_value") or fields.get(lf, {}).get("raw_value")
                if val:
                    label_parts.append(str(val))

            desc_text = " — ".join(label_parts) if label_parts else f"{schema.label}: {fdef.label}"
            thresholds = fdef.alert.get("thresholds_days", [30, 15, 7])

            d_id = make_deadline_id(module_id, schema_name, src_doc, src_page, fname, desc_text)

            out.append({
                "id": d_id,
                "module_id": module_id,
                "schema_name": schema_name,
                "field_name": fname,
                "description": desc_text,
                "due_date": iso_date,
                "thresholds": thresholds,
                "source_document": src_doc,
                "source_page": src_page
            })

    return out