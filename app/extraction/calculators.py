"""Deterministic mathematical calculations on extracted fields (Whitelist-only)."""
from typing import Dict, Optional
from app.extraction.registry import ComputedDef


def compute_value(cdef: ComputedDef, numbers: Dict[str, Optional[float]]) -> Optional[float]:
    if cdef.op == "ratio":
        num, den = (numbers.get(i) for i in cdef.inputs)
        if num is None or den is None or den <= 0 or num < 0:
            return None
        return round(num / den * cdef.scale, cdef.decimals)
    raise ValueError(f"Unsupported op: {cdef.op}")