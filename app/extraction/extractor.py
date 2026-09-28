import json
from typing import Dict, Any, List
from app.extraction.schemas import AVAILABLE_SCHEMAS
from app.ai.gemini import generate_structured_json
from app.extraction.normalizer import normalize_date, normalize_number, normalize_plate

EXTRACTION_SYSTEM_PROMPT = (
    "You are a certified ISO 14001 Environmental Management System (SGA) and legal compliance data extraction auditor. "
    "Your objective is to extract structured entities from organizational documents with absolute fidelity to the source text. "
    "Adhere to the Zero Hallucination protocol: never invent expiries, amounts, or roles. "
    "If a field is not present in the document text, return null."
)


def _build_extraction_prompt(schema_name: str, schema_def: Dict[str, Any], pages: List[Dict[str, Any]]) -> str:
    fields_spec = schema_def["fields"]
    required_fields = schema_def.get("required", [])

    context_blocks = []
    for p in pages:
        p_num = p.get("page_number", 1)
        p_txt = p.get("text", "").strip()
        if p_txt:
            context_blocks.append(f"--- [PAGINA {p_num}] ---\n{p_txt}")

    corpus = "\n\n".join(context_blocks)

    prompt = f"""
TARGET EXTRACTION SCHEMA: '{schema_name.upper()}'
DESCRIPTION: {schema_def['description']}

FIELDS TO EXTRACT:
{json.dumps(fields_spec, indent=2)}

MANDATORY RULES:
1. Scan the document corpus and identify every valid record matching this schema.
2. For each identified record, extract the exact textual value as found in the text into 'raw_value'.
3. Assign the exact 'source_page' (integer) where this record was located.
4. If a field is not present, set 'raw_value' to null.
5. Return a valid JSON object matching the exact specification below.

JSON OUTPUT STRUCTURE:
{{
  "schema": "{schema_name}",
  "total_records": <integer>,
  "records": [
    {{
      "source_page": <integer>,
      "fields": {{
        "<field_name>": {{
          "raw_value": <string or null>
        }}
      }}
    }}
  ]
}}

DOCUMENT CONTEXT:
{corpus}
"""
    return prompt.strip()


def extract_structured_data(pages: List[Dict[str, Any]], schema_name: str = "scadenziario") -> Dict[str, Any]:
    if schema_name not in AVAILABLE_SCHEMAS:
        raise ValueError(f"Unknown schema '{schema_name}'. Available: {list(AVAILABLE_SCHEMAS.keys())}")

    if not pages:
        return {"schema": schema_name, "total_records": 0, "records": []}

    schema_def = AVAILABLE_SCHEMAS[schema_name]
    fields_spec = schema_def["fields"]

    prompt = _build_extraction_prompt(schema_name, schema_def, pages)
    raw_json_str = generate_structured_json(prompt, system_instruction=EXTRACTION_SYSTEM_PROMPT)

    try:
        data = json.loads(raw_json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse model JSON extraction output: {str(e)}")

    records = data.get("records", [])

    # شناسایی پویای فیلدهای عددی و تاریخی جهت نرمال‌سازی
    date_field_names = [f for f in fields_spec if any(k in f for k in ["data", "scadenza", "emissione", "rinnovo", "rilascio"])]
    number_field_names = [f for f in fields_spec if any(k in f for k in ["litri", "chilometri", "km", "ore", "spesa", "consumo", "anni", "totale"])]

    for rec in records:
        f_map = rec.get("fields", {})

        for fname in fields_spec:
            if fname not in f_map:
                f_map[fname] = {"raw_value": None, "normalized_value": None, "status": "MISSING"}
                continue

            item = f_map[fname]
            raw_v = item.get("raw_value")

            if raw_v is None or str(raw_v).strip().lower() in ["null", "none", "", "-", "n/a"]:
                item["raw_value"] = None
                item["normalized_value"] = None
                item["status"] = "MISSING"
                continue

            item["status"] = "EXTRACTED"

            # نرمال‌سازی تاریخ‌ها
            if fname in date_field_names:
                norm_d = normalize_date(str(raw_v))
                item["normalized_value"] = norm_d

            # نرمال‌سازی اعداد
            elif fname in number_field_names:
                norm_n = normalize_number(str(raw_v))
                item["normalized_value"] = norm_n

            # نرمال‌سازی پلاک خودرو
            elif fname == "targa":
                norm_p = normalize_plate(str(raw_v))
                item["normalized_value"] = norm_p
            else:
                item["normalized_value"] = str(raw_v).strip()

        # محاسبه قطعی نرخ مصرف سوخت در صورت وجود
        if schema_name == "vehicle_fuel":
            litri_data = f_map.get("litri", {})
            km_data = f_map.get("chilometri", {})
            l_val = litri_data.get("normalized_value")
            km_val = km_data.get("normalized_value")

            if l_val is not None and km_val is not None and km_val > 0:
                calc_val = round((l_val / km_val) * 100.0, 2)
                f_map["consumo_l_100km"] = {
                    "raw_value": f"{calc_val} L/100km",
                    "normalized_value": calc_val,
                    "status": "CALCULATED"
                }

    return {
        "schema": schema_name,
        "total_records": len(records),
        "records": records
    }