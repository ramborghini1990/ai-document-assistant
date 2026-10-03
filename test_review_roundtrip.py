"""Offline test verifying user edits roundtrip from DataFrame back to records."""
from app.extraction.registry import resolve_schema
from app.extraction.review import records_to_dataframe, dataframe_to_records


def test_review_roundtrip():
    print("Testing Step 2: Human-in-the-Loop Review Roundtrip...")

    schema = resolve_schema("vehicle_fuel", module_id="iso_14001")

    # رکوردهای نمونه با محاسبه اولیه (100 لیتر در 1000 کیلومتر = 10.0 L/100km)
    original_records = [
        {
            "source_document": "log_fleet.xlsx",
            "source_page": 1,
            "fields": {
                "targa": {"raw_value": "gf619xa", "normalized_value": "GF619XA", "status": "EXTRACTED"},
                "modello": {"raw_value": "Iveco Stralis", "normalized_value": "Iveco Stralis", "status": "EXTRACTED"},
                "scadenza_revisione": {"raw_value": "2026-11-30", "normalized_value": "2026-11-30", "status": "EXTRACTED"},
                "periodo": {"raw_value": "Gennaio 2026", "normalized_value": "Gennaio 2026", "status": "EXTRACTED"},
                "litri": {"raw_value": "100", "normalized_value": 100.0, "status": "EXTRACTED"},
                "chilometri": {"raw_value": "1000", "normalized_value": 1000.0, "status": "EXTRACTED"},
                "consumo_l_100km": {"raw_value": "10.0 L/100km", "normalized_value": 10.0, "status": "CALCULATED"}
            },
            "warnings": []
        }
    ]

    # ۱. تبدیل به DataFrame جهت نمایش در Streamlit
    df = records_to_dataframe(original_records, schema)
    assert len(df) == 1
    assert df.loc[0, "targa"] == "GF619XA"
    print("✓ Records converted to DataFrame with hidden _rid tracking.")

    # ۲. شبیه‌سازی ویرایش کاربر در جدول: تغییر لیتر از 100 به 150
    df.loc[0, "litri"] = "150"

    # ۳. بازگشت به رکوردها
    reviewed = dataframe_to_records(df, original_records, schema)
    assert len(reviewed) == 1
    rec = reviewed[0]

    # فیلد ویرایش‌شده باید مقدار جدید و وضعیت EDITED داشته باشد
    assert rec["fields"]["litri"]["normalized_value"] == 150.0
    assert rec["fields"]["litri"]["status"] == "EDITED"

    # فیلد دست‌نخورده باید وضعیت قبلی EXTRACTED را حفظ کند
    assert rec["fields"]["targa"]["status"] == "EXTRACTED"

    # فیلد محاسبه‌شده باید به صورت خودکار دوباره محاسبه شده باشد (150/1000 * 100 = 15.0)
    assert rec["fields"]["consumo_l_100km"]["normalized_value"] == 15.0
    assert rec["fields"]["consumo_l_100km"]["status"] == "CALCULATED"
    print("✓ User edit correctly updated status to EDITED and triggered automatic deterministic recalculation (15.0 L/100km)!")


if __name__ == "__main__":
    test_review_roundtrip()
    print("\n🎉 STEP 2 (REVIEW ROUNDTRIP) TEST PASSED!")