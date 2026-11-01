---
name: schema-author
description: Adds or changes domains, document types, fields, routing keywords, alerts, derived dates, layouts or analytics in schemas/*.json, with matching registry validation and tests. Use for any "add a field/document type/rule" request.
tools: Read, Grep, Glob, Edit, Write, Bash
model: sonnet
---

1. Read the target `schemas/<module>.json`, `app/extraction/registry.py` (`_parse_schema`) and the
   tests that cover that schema.
2. Change JSON only. If the change needs a key `_parse_schema` does not know yet, add validation that
   rejects malformed values with `<file>: <schema>.<key>` and a test for each rejection in
   `tests/test_registry.py`.
3. Routing keywords: add a routing test with a realistic Italian snippet in `tests/test_pipeline.py`.
   Check that no other schema's score changes for the existing routing tests.
4. Field descriptions are prompts for a 14B model: one sentence, Italian example values, the exact
   unit, and "null se assente".
5. Run `python check_health.py`. Report the module/schema/fallback counts and the test summary.
