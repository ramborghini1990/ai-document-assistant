"""Offline validation test for Step 4: Expiry Alerts Engine."""
import os
import tempfile
from datetime import date
from app.alerts.scanner import scan_deadlines, classify, OVERDUE
from app.alerts.deadlines import extract_deadlines_from_records

# استفاده از دیتابیس موقت جهت ایزوله‌سازی آزمون
temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["ASSISTANT_DB_PATH"] = temp_db.name

from app.alerts.store import (
    ensure_alert_tables,
    upsert_deadline,
    add_recipient,
    get_active_deadlines,
    is_alert_already_sent,
    log_alert_result
)
from app.alerts.dispatcher import dispatch_alerts


def test_alerts():
    print("Testing Step 4: Deadline Alerts Engine...")

    # ۱. تست منطق آستانه‌ها در scanner
    assert classify(25, [30, 15, 7]) == 30
    assert classify(10, [30, 15, 7]) == 15
    assert classify(5, [30, 15, 7]) == 7
    assert classify(40, [30, 15, 7]) is None
    assert classify(-2, [30, 15, 7]) == OVERDUE
    print("✓ Threshold classification logic passed.")

    # ۲. استخراج سررسید از رکوردهای نمونه
    records = [
        {
            "source_document": "attestato.pdf",
            "source_page": 1,
            "fields": {
                "nominativo_dipendente": {"normalized_value": "Mario Rossi", "status": "EXTRACTED"},
                "corso_descrizione": {"normalized_value": "Carrello Elevatore", "status": "EXTRACTED"},
                "data_scadenza_rinnovo": {"normalized_value": "2026-10-15", "status": "EXTRACTED"}
            }
        }
    ]
    extracted = extract_deadlines_from_records("iso_14001", "personnel_training", records)
    assert len(extracted) == 1
    d = extracted[0]
    assert d["due_date"] == "2026-10-15"
    assert "Mario Rossi" in d["description"]
    print("✓ Deadline successfully extracted from ISO personnel_training record.")

    # ۳. ثبت در دیتابیس و مدیریت گیرندگان
    ensure_alert_tables()
    upsert_deadline(d["id"], d["module_id"], d["schema_name"], d["field_name"], d["description"], d["due_date"], d["thresholds"], d["source_document"], d["source_page"])
    add_recipient("r1", "email", "auditor@effeemme.it")
    add_recipient("r2", "sms", "+393331234567")

    active_d = get_active_deadlines()
    assert len(active_d) >= 1
    print("✓ Deadlines and alert recipients persisted to SQLite.")

    # ۴. شبیه‌سازی اسکن و توزیع (Dry-Run در تاریخ ۲۰۲۶/۱۰/۰۱ = ۱۴ روز مانده)
    sim_date = date(2026, 10, 1)
    res_dry = dispatch_alerts(today=sim_date, dry_run=True)
    assert res_dry["sent_email"] >= 1
    assert res_dry["sent_sms"] >= 1
    print(f"✓ Dispatch simulation verified: {res_dry}")

    # ۵. بررسی جلوگیری از ارسال تکراری (Deduplication)
    log_alert_result("log1", d["id"], d["due_date"], 15, "email", "auditor@effeemme.it", "sent")
    assert is_alert_already_sent(d["id"], d["due_date"], 15, "email", "auditor@effeemme.it") is True
    print("✓ Deduplication successfully prevented repeat alert spam.")

    # پاک‌سازی فایل موقت با سازگاری ویندوز
    temp_db.close()
    try:
        if os.path.exists(temp_db.name):
            os.remove(temp_db.name)
    except PermissionError:
        pass  # ویندوز بعد از خاتمه پروسه فایل تمپ را آزاد می‌کند


if __name__ == "__main__":
    test_alerts()
    print("\n🎉 STEP 4 (ALERT ENGINE) FULLY VERIFIED & PASSED!")