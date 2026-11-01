"""PostToolUse hook: fast, deterministic checks on the file Claude just edited.

Reads the hook payload (JSON) from stdin. Exit code 2 sends stderr back to Claude so it fixes the
violation in the same turn; exit 0 means nothing to report. Keep it fast (< 1 s): no pytest here.
"""
import json
import re
import sys
from pathlib import Path

RULES = [
    # (applies_to(path) -> bool, regex, message)
    (lambda p: not p.startswith("app/ai/providers/"),
     re.compile(r"^\s*(from google import genai|import google\.genai|from google\.genai|import ollama|from openai)", re.M),
     "Model SDK imported outside app/ai/providers/ (CLAUDE.md §3, AGENTS.md §4.1)."),
    (lambda p: p.startswith("app/") and not p.startswith("app/ui/"),
     re.compile(r"^\s*(import streamlit|from streamlit)", re.M),
     "Streamlit imported outside app/ui/ (AGENTS.md Principle 2)."),
    (lambda p: p.startswith(("app/extraction/", "app/alerts/", "app/reporting/", "app/rag/")),
     re.compile(r"^\s*(import fastapi|from fastapi|import sqlalchemy|from sqlalchemy)", re.M),
     "Transport/ORM imported into the pure domain layer (CLAUDE.md §3)."),
    (lambda p: p.startswith("app/") and p.endswith(".py"),
     re.compile(r"^\s*print\(", re.M),
     "print() in app code: use logging.getLogger(__name__)."),
    (lambda p: p.startswith("tests/"),
     re.compile(r"@pytest\.mark\.skip|pytest\.skip\(", re.M),
     "Skipping a test is not allowed (AGENTS.md Principle 6). Fix the cause instead."),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path") or ""
    root = Path(payload.get("cwd") or ".").resolve()
    try:
        rel = Path(file_path).resolve().relative_to(root).as_posix()
    except ValueError:
        return 0
    if not rel.endswith(".py"):
        return 0
    try:
        text = (root / rel).read_text(encoding="utf-8")
    except OSError:
        return 0

    problems = [msg for applies, rx, msg in RULES if applies(rel) and rx.search(text)]
    if problems:
        print(f"{rel}:\n- " + "\n- ".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
