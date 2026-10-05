import pytest
from datetime import date
from app.alerts.scanner import scan_deadlines, classify, OVERDUE
from app.alerts.deadlines import extract_deadlines_from_records
from app.alerts.store import (
    upsert_deadline,
    add_recipient,
    get_active_deadlines,
    is_alert_already_sent,
    log_alert_result
)
from app.alerts.dispatcher import dispatch_alerts


@pytest.mark.offline
def test_alert_engine_full():
    assert classify(25, [30, 15, 7]) == 30
    assert classify(10, [30, 15, 7]) == 15
    assert classify(-2, [30, 15, 7]) == OVERDUE

    records = [{
        "source_document": "cert.pdf",
        "source_page": 1,
        "fields": {
            "nominativo_dipendente": {"normalized_value": "Mario Rossi", "status": "EXTRACTED"},
            "corso_descrizione": {"normalized_value": "Forklift", "status": "EXTRACTED"},
            "data_scadenza_rinnovo": {"normalized_value": "2026-10-15", "status": "EXTRACTED"}
        }
    }]
    dls = extract_deadlines_from_records("iso_14001", "personnel_training", records)
    assert len(dls) == 1
    d = dls[0]

    upsert_deadline(d["id"], d["module_id"], d["schema_name"], d["field_name"], d["description"], d["due_date"], d["thresholds"], d["source_document"], d["source_page"])
    add_recipient("r1", "email", "auditor@effeemme.it")
    add_recipient("r2", "sms", "+393331234567")

    res = dispatch_alerts(today=date(2026, 10, 1), dry_run=True)
    assert res["sent_email"] >= 1
    assert res["sent_sms"] >= 1

    log_alert_result("log1", d["id"], d["due_date"], 15, "email", "auditor@effeemme.it", "sent")
    assert is_alert_already_sent(d["id"], d["due_date"], 15, "email", "auditor@effeemme.it") is True