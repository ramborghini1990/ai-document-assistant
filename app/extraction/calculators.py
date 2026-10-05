"""Deterministic mathematical calculations on extracted fields (Whitelist-only)."""
from typing import Dict, Optional
from app.extraction.registry import ComputedDef


def compute_value(cdef: ComputedDef, numbers: Dict[str, Optional[float]]) -> Optional[float]:
    """
    محاسبه کاملاً قطعی مقادیر مشتق‌شده با عملگرهای مجاز.
    در صورت ناقص بودن هر یک از ورودی‌ها، مقدار None (Missing) برگردانده می‌شود.
    """
    vals = [numbers.get(i) for i in cdef.inputs]
    if any(v is None for v in vals):
        return None

    if cdef.op == "ratio":
        num, den = vals[0], vals[1]
        if den <= 0 or num < 0:
            return None
        return round((num / den) * cdef.scale, cdef.decimals)

    elif cdef.op == "sum":
        total = sum(vals)
        return round(total * cdef.scale, cdef.decimals)

    elif cdef.op == "diff":
        diff = vals[0] - vals[1]
        return round(diff * cdef.scale, cdef.decimals)

    elif cdef.op == "product":
        prod = 1.0
        for v in vals:
            prod *= v
        return round(prod * cdef.scale, cdef.decimals)

    raise ValueError(f"Unsupported op: {cdef.op}")