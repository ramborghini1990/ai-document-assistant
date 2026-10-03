"""Offline validation test for Step 1: Schema Registry and Type-Driven Normalizers."""
from app.extraction.registry import list_modules, get_module, resolve_schema, build_legacy_schemas, FieldDef
from app.extraction.calculators import compute_value, ComputedDef
from app.extraction.extractor import normalize_field


def test_schema_registry():
    print("Testing Step 1: Schema Registry & Normalizer Mechanics...")

    # ۱. بارگذاری ماژول‌ها از فایل‌های JSON
    modules = list_modules()
    assert len(modules) >= 3, f"Expected at least 3 modules, got {len(modules)}"
    m_ids = [m.module_id for m in modules]
    assert "iso_14001" in m_ids
    assert "fleet_fuel_expenses" in m_ids
    assert "general_documents" in m_ids
    print(f"✓ Successfully loaded {len(modules)} modules: {m_ids}")

    # ۲. بررسی سازگاری رو به عقب (Backward Compatibility)
    legacy = build_legacy_schemas()
    for legacy_name in ["scadenziario", "vehicle_fuel", "utility_consumption", "personnel_training", "regulatory_authorization", "general"]:
        assert legacy_name in legacy, f"Legacy schema '{legacy_name}' missing from flat view!"
    print(f"✓ All 6 legacy schemas are present in flat AVAILABLE_SCHEMAS shim.")

    # ۳. بررسی رفع باگ کلمه 'ore' (رفع رگرسیون)
    f_ente = FieldDef(name="ente_formatore", type="string", label="Ente Formatore")
    norm_res = normalize_field(f_ente, "3R International S.r.l.")
    assert norm_res["normalized_value"] == "3R International S.r.l."
    assert norm_res["status"] == "EXTRACTED"
    print("✓ Regression test passed: 'ente_formatore' is correctly treated as string, not number!")

    # ۴. تست نرمال‌سازی تاریخ‌های معتبر و نامعتبر
    f_date = FieldDef(name="scadenza", type="date", label="Scadenza")
    valid_d = normalize_field(f_date, "31 luglio 2026")
    assert valid_d["normalized_value"] == "2026-07-31"

    invalid_d = normalize_field(f_date, "31/02/2026")  # ۳۱ فوریه وجود ندارد
    assert invalid_d["status"] == "UNCERTAIN"
    assert invalid_d["normalized_value"] is None
    print("✓ Date normalizer accurately marks non-existent dates as UNCERTAIN.")

    # ۵. تست محاسبات قطعی Whitelist (محاسبه نرخ مصرف سوخت)
    cdef = ComputedDef(name="consumo_l_100km", op="ratio", inputs=["litri", "chilometri"], scale=100.0, decimals=2, unit="L/100km", label="Consumo")
    calc_res = compute_value(cdef, {"litri": 250.0, "chilometri": 2000.0})
    assert calc_res == 12.5, f"Expected 12.5, got {calc_res}"

    # تقسیم بر صفر یا مقادیر خالی نباید کرش کند
    assert compute_value(cdef, {"litri": 250.0, "chilometri": 0.0}) is None
    assert compute_value(cdef, {"litri": None, "chilometri": 2000.0}) is None
    print("✓ Deterministic ratio calculator passed all boundary conditions.")


if __name__ == "__main__":
    test_schema_registry()
    print("\n🎉 STEP 1 (SCHEMA REGISTRY) FULLY VERIFIED & PASSED!")