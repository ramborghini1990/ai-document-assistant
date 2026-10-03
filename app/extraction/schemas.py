"""Deprecated: use app.extraction.registry. Kept so legacy imports/tests keep working."""
from app.extraction.registry import build_legacy_schemas

AVAILABLE_SCHEMAS = build_legacy_schemas()