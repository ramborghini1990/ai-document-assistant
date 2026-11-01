# app/extraction — local rules

Loaded when Claude reads or edits files in this folder.

- This package is pure: no Streamlit, no FastAPI, no SQL, no model SDK. The only model access is the
  injected provider (`extract_fn=` / `providers=`), so every test can use a fake.
- The LLM returns `raw_value` strings only. Normalisation (`normalizer.py`), math (`calculators.py`)
  and derived dates are deterministic Python. Never ask a model for a number it could misread twice.
- One parser per concept. Numbers, dates, plates, EER/POD/PDR codes and P.IVA live in
  `normalizer.py`. If you find a second implementation elsewhere, flag it. Don't add a third.
- A value that is ambiguous (two numbers in one raw string, `31/02`, an unknown date shape) becomes
  `UNCERTAIN`, never a best guess.
- Grounding: an `EXTRACTED` value must be locatable in the source page text (see `grounding.py`);
  otherwise it becomes `UNCERTAIN` with warning `ungrounded:<field>`.
- `registry._parse_schema` must reject every malformed new JSON key with a message naming
  `<file>: <schema>.<key>`. Add a test in `tests/test_registry.py` for each rejection.
- Prompt size is bounded by `config.EXTRACTION_MAX_CHARS`; long documents are windowed by page.
