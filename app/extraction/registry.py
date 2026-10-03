"""Schema Registry: loads modules/schemas from schemas/*.json (no domain logic in code)."""
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"
FIELD_TYPES = {"string", "date", "number", "plate"}
COMPUTE_OPS = {"ratio"}
DEFAULT_SYSTEM_PROMPT = (
    "You are a precise document data extraction engine. Extract structured entities with absolute "
    "fidelity to the source text. Never invent values. If a field is not present, return null."
)


@dataclass
class FieldDef:
    name: str
    type: str
    label: str
    description: str = ""
    required: bool = False
    alert: Optional[Dict[str, Any]] = None


@dataclass
class ComputedDef:
    name: str
    op: str
    inputs: List[str]
    label: str
    scale: float = 1.0
    decimals: int = 2
    unit: str = ""


@dataclass
class SchemaDef:
    name: str
    module_id: str
    label: str
    description: str
    fields: Dict[str, FieldDef]
    computed: Dict[str, ComputedDef] = field(default_factory=dict)

    @property
    def required(self) -> List[str]:
        return [f.name for f in self.fields.values() if f.required]

    def ordered_field_names(self) -> List[str]:
        return list(self.fields) + list(self.computed)

    def all_labels(self) -> Dict[str, str]:
        labels = {n: f.label for n, f in self.fields.items()}
        labels.update({n: c.label for n, c in self.computed.items()})
        return labels


@dataclass
class ModuleDef:
    module_id: str
    label: str
    version: str
    system_prompt: str
    report: Dict[str, Any]
    schemas: Dict[str, SchemaDef]


def _parse_schema(module_id: str, name: str, raw: Dict[str, Any], src: str) -> SchemaDef:
    fields: Dict[str, FieldDef] = {}
    for fname, fr in (raw.get("fields") or {}).items():
        ftype = fr.get("type", "string")
        if ftype not in FIELD_TYPES:
            raise ValueError(f"{src}: {name}.{fname}: invalid type '{ftype}'")
        alert = fr.get("alert")
        if alert is not None:
            th = alert.get("thresholds_days")
            if ftype != "date" or not th or not all(isinstance(t, int) and t > 0 for t in th):
                raise ValueError(f"{src}: {name}.{fname}: alert requires date type and positive int thresholds_days")
        fields[fname] = FieldDef(fname, ftype, fr.get("label") or fname.replace("_", " ").title(),
                                 fr.get("description", ""), bool(fr.get("required", False)), alert)
    if not fields:
        raise ValueError(f"{src}: schema '{name}' has no fields")

    for f in fields.values():
        for lf in (f.alert or {}).get("label_fields", []):
            if lf not in fields:
                raise ValueError(f"{src}: {name}.{f.name}: unknown label_field '{lf}'")

    computed: Dict[str, ComputedDef] = {}
    for cname, cr in (raw.get("computed") or {}).items():
        op, inputs = cr.get("op"), cr.get("inputs", [])
        if op not in COMPUTE_OPS or cname in fields:
            raise ValueError(f"{src}: {name}.{cname}: invalid op or name clash")
        if len(inputs) != 2 or any(i not in fields or fields[i].type != "number" for i in inputs):
            raise ValueError(f"{src}: {name}.{cname}: inputs must be 2 existing number fields")
        computed[cname] = ComputedDef(cname, op, inputs, cr.get("label") or cname,
                                      float(cr.get("scale", 1)), int(cr.get("decimals", 2)), cr.get("unit", ""))

    return SchemaDef(name, module_id, raw.get("label") or name, raw.get("description", ""), fields, computed)


@lru_cache(maxsize=1)
def load_registry() -> Dict[str, ModuleDef]:
    modules: Dict[str, ModuleDef] = {}
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        mid = raw["module_id"]
        if mid in modules:
            raise ValueError(f"{path.name}: duplicate module_id '{mid}'")
        schemas = {n: _parse_schema(mid, n, sr, path.name) for n, sr in (raw.get("schemas") or {}).items()}
        modules[mid] = ModuleDef(
            mid, raw.get("label", mid), raw.get("version", "0"),
            (raw.get("extraction") or {}).get("system_prompt") or DEFAULT_SYSTEM_PROMPT,
            raw.get("report") or {}, schemas,
        )
    if not modules:
        raise RuntimeError(f"No schema modules found in {SCHEMAS_DIR}")
    return modules


def list_modules() -> List[ModuleDef]:
    return list(load_registry().values())


def get_module(module_id: str) -> ModuleDef:
    try:
        return load_registry()[module_id]
    except KeyError:
        raise ValueError(f"Unknown module '{module_id}'. Available: {list(load_registry())}")


def resolve_schema(schema_name: str, module_id: Optional[str] = None) -> SchemaDef:
    if module_id:
        mod = get_module(module_id)
        if schema_name not in mod.schemas:
            raise ValueError(f"Schema '{schema_name}' not in module '{module_id}'")
        return mod.schemas[schema_name]
    matches = [m.schemas[schema_name] for m in load_registry().values() if schema_name in m.schemas]
    if len(matches) != 1:
        raise ValueError(f"Schema '{schema_name}' is {'ambiguous' if matches else 'unknown'}; specify module_id")
    return matches[0]


def build_legacy_schemas() -> Dict[str, Dict[str, Any]]:
    """Flat view compatible with the old AVAILABLE_SCHEMAS (first module wins on name clash)."""
    out: Dict[str, Dict[str, Any]] = {}
    for m in load_registry().values():
        for s in m.schemas.values():
            fields = {n: f"{f.type} ({f.description})" for n, f in s.fields.items()}
            fields.update({n: f"number (calcolato, {c.unit})" for n, c in s.computed.items()})
            out.setdefault(s.name, {"description": s.description, "fields": fields, "required": s.required})
    return out