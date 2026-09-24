import json
from typing import List, Dict, Any, Optional
from app.ai.gemini import generate_structured_json
from app.extraction.schemas import AVAILABLE_SCHEMAS
from app.extraction.normalizer import normalize_date, normalize_number, normalize_plate


EXTRACTION_SYSTEM_PROMPT = """
You are an expert enterprise document intelligence and structured data extraction engine.
Your task is to extract structured entities from the provided document text according to the requested schema.

STRICT ANTI-HALLUCINATION RULES:
1. ONLY extract information that is explicitly stated in the document.
2. If a field is NOT mentioned in the text, you MUST output null for that field. NEVER guess or invent dates, numbers, or names.
3. For each extracted record, indicate the source page number where the information was found.
4. For each field, assign an extraction_status:
   - "EXTRACTED": The value is directly stated in the text.
   - "MISSING": The value does not exist in the document.
   - "UNCERTAIN": The text is ambiguous or partially readable.
5. Return ONLY a valid JSON object matching the requested schema. No conversational preamble.
"""


def extract_structured_data(
    pages_data: List[Dict[str, Any]], 
    schema_name: str = "scadenziario"
) -> Dict[str, Any]:
    """
    استخراج ساختاریافته داده‌ها از صفحات سند بر اساس اسکیمای مشخص همراه با نرمال‌سازی و مهار توهم.
    """
    if schema_name not in AVAILABLE_SCHEMAS:
        raise ValueError(f"Unknown schema '{schema_name}'. Available: {list(AVAILABLE_SCHEMAS.keys())}")

    schema = AVAILABLE_SCHEMAS[schema_name]

    # آماده‌سازی کانتکست با درج شماره صفحه
    full_context_blocks = []
    for p in pages_data:
        p_num = p.get("page_number", 1)
        p_text = p.get("text", "").strip()
        if p_text:
            full_context_blocks.append(f"--- PAGE {p_num} ---\n{p_text}")

    full_context = "\n\n".join(full_context_blocks)
    if not full_context.strip():
        return {"schema": schema_name, "records": [], "warnings": ["Document has no readable text."]}

    prompt = f"""
SCHEMA REQUESTED: {schema['name']} - {schema['description']}
TARGET FIELDS: {json.dumps(schema['fields'])}

DOCUMENT CONTENT:
{full_context}

INSTRUCTIONS:
Extract all instances/rows matching the target fields.
Return a JSON object in this exact format:
{{
  "records": [
    {{
      "source_page": 1,
      "fields": {{
        "<field_name>": {{
          "raw_value": "string or null",
          "status": "EXTRACTED" | "MISSING" | "UNCERTAIN",
          "confidence": 0.95
        }}
      }}
    }}
  ]
}}
"""

    raw_json_str = generate_structured_json(prompt, system_instruction=EXTRACTION_SYSTEM_PROMPT)

    try:
        parsed_data = json.loads(raw_json_str)
    except json.JSONDecodeError:
        # پاکسازی مارک‌داون احتمالی در خروجی
        cleaned_str = raw_json_str.replace("```json", "").replace("```", "").strip()
        try:
            parsed_data = json.loads(cleaned_str)
        except Exception as e:
            return {
                "schema": schema_name, 
                "records": [], 
                "warnings": [f"Failed to parse extraction JSON response: {str(e)}"],
                "raw_response": raw_json_str
            }

    raw_records = parsed_data.get("records", [])
    cleaned_records = []

    # پردازش، نرمال‌سازی و محاسبه فیلدهای مشتق‌شده
    for rec in raw_records:
        src_page = rec.get("source_page", 1)
        fields_dict = rec.get("fields", {})

        processed_fields = {}
        for fname in schema["fields"]:
            fdata = fields_dict.get(fname, {})
            if not isinstance(fdata, dict):
                fdata = {"raw_value": str(fdata) if fdata else None, "status": "EXTRACTED" if fdata else "MISSING", "confidence": 0.8}

            val = fdata.get("raw_value")
            status = fdata.get("status", "EXTRACTED" if val else "MISSING")
            conf = fdata.get("confidence", 0.9 if val else 0.0)

            # نرمال‌سازی فیلدهای شناخته‌شده
            norm_val = val
            if val:
                if any(k in fname for k in ["data", "scadenza", "periodo"]):
                    norm_val = normalize_date(val)
                elif any(k in fname for k in ["litri", "chilometri", "consumo"]):
                    norm_val = normalize_number(val)
                elif "targa" in fname:
                    norm_val = normalize_plate(val)

            processed_fields[fname] = {
                "raw_value": val,
                "normalized_value": norm_val,
                "status": status,
                "confidence": conf
            }

        # قانون ویژه فاز ۱۸ (محاسبه خودکار مصرف سوخت L/100km در صورت وجود لیتر و کیلومتر)
        if schema_name == "vehicle_fuel":
            liters = processed_fields.get("litri", {}).get("normalized_value")
            kms = processed_fields.get("chilometri", {}).get("normalized_value")
            consumo_field = processed_fields.get("consumo_l_100km", {})

            if liters and kms and (kms > 0) and not consumo_field.get("raw_value"):
                calc_val = round((liters / kms) * 100, 2)
                processed_fields["consumo_l_100km"] = {
                    "raw_value": f"{calc_val} (calculated)",
                    "normalized_value": calc_val,
                    "status": "CALCULATED",
                    "confidence": 1.0
                }

        cleaned_records.append({
            "source_page": src_page,
            "fields": processed_fields
        })

    return {
        "schema": schema_name,
        "total_records": len(cleaned_records),
        "records": cleaned_records,
        "warnings": []
    }