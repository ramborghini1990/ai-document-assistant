---
name: add-schema-field
description: Add or change a field, computed value, alert, derived date or routing keyword in a schemas/*.json module, including registry validation and offline tests. Use whenever the user asks to extract something new from a document type.
---

# Add a schema field

1. Identify module and schema: `grep -l '"<schema>"' schemas/*.json`. Read the whole schema.
2. Choose the type from `registry.FIELD_TYPES`. Numbers and dates are always `number`/`date`, never
   `string`, so the deterministic normaliser runs.
3. Write the description as a prompt for a 14B model: what it is, where it usually appears on the
   document, one Italian example, the unit, "null se assente".
4. If the value feeds a calculation, add a `computed` entry (ops from `registry.COMPUTE_OPS` only).
   If it is a deadline, add `alert.thresholds_days` and `label_fields`.
5. Reports: add it to `layout.word_table_fields` / `word_header_fields` only if the user asked.
6. Tests:
   - `tests/test_registry.py`: the schema loads; a malformed variant is rejected.
   - A fake extraction (`extract_fn=`) returning the field: assert status and normalized value,
     including one ambiguous input that must become `UNCERTAIN`.
7. Run `python check_health.py` and report the counts.
