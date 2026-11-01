"""F3: a deadline keeps its id (and its alert history) when a reviewer corrects a record."""
import json

import pytest

from app.alerts.deadlines import extract_deadlines_from_records, make_deadline_id
from app.alerts.store import get_active_deadlines, is_alert_already_sent, log_alert_result
from app.extraction import extractor
from app.extraction.pipeline import sync_deadlines_to_db
from app.extraction.registry import resolve_schema
from app.extraction.review import dataframe_to_records, records_to_dataframe

MODULE, SCHEMA, DOC = "iso_14001", "personnel_training", "attestati.pdf"


def _fake_model_output(*_args, **_kwargs) -> str:
    """Two certificates on the same page: the case that forced the old id to hash the description."""
    def rec(name: str) -> dict:
        return {"source_page": 1, "fields": {
            "nominativo_dipendente": {"raw_value": name},
            "corso_descrizione": {"raw_value": "Corso Carrellisti"},
            "data_emissione": {"raw_value": "15/10/2021"},
            "data_scadenza_rinnovo": {"raw_value": "15/10/2026"},
        }}
    return json.dumps({"records": [rec("Mario Rosi"), rec("Anna Bianchi")]})


@pytest.fixture
def extracted(monkeypatch):
    monkeypatch.setattr(extractor, "generate_structured_json", _fake_model_output)
    pages = [{"page_number": 1, "text": "irrelevant: the model call is faked"}]
    return extractor.extract_structured_data(pages, SCHEMA, module_id=MODULE, source_document=DOC)["records"]


def _payload(records):
    return {MODULE: {SCHEMA: {"records": records}}}


@pytest.mark.offline
def test_extraction_assigns_stable_record_keys(extracted):
    assert [r["record_key"] for r in extracted] == ["p1-r1", "p1-r2"]
    ids = [d["id"] for d in extract_deadlines_from_records(MODULE, SCHEMA, extracted)]
    assert len(ids) == 2 and len(set(ids)) == 2          # two people on one page stay two deadlines


@pytest.mark.offline
def test_review_edit_of_label_field_keeps_deadline_id_and_alert_history(extracted):
    before = extract_deadlines_from_records(MODULE, SCHEMA, extracted)
    sync_deadlines_to_db(_payload(extracted), [DOC])
    d = before[0]
    log_alert_result("log-1", d["id"], d["due_date"], 30, "email", "rsga@example.it", "sent")

    # the reviewer fixes the typo "Rosi" -> "Rossi" (a label_field, so it is part of the description)
    schema = resolve_schema(SCHEMA, MODULE)
    df = records_to_dataframe(extracted, schema)
    df.loc[0, "nominativo_dipendente"] = "Mario Rossi"
    reviewed = dataframe_to_records(df, extracted, schema)
    assert reviewed[0]["fields"]["nominativo_dipendente"]["status"] == "EDITED"
    assert reviewed[0]["record_key"] == "p1-r1"

    after = extract_deadlines_from_records(MODULE, SCHEMA, reviewed)
    assert [x["id"] for x in after] == [x["id"] for x in before]
    assert "Mario Rossi" in after[0]["description"]       # the text is updated, the identity is not

    sync_deadlines_to_db(_payload(reviewed), [DOC])
    active = get_active_deadlines()
    assert sorted(r["id"] for r in active) == sorted(x["id"] for x in before)
    assert any("Mario Rossi" in r["description"] for r in active)
    # the threshold already notified is still recognised as sent: no duplicate alert
    assert is_alert_already_sent(d["id"], d["due_date"], 30, "email", "rsga@example.it") is True


@pytest.mark.offline
def test_records_without_record_key_keep_the_legacy_id():
    """Records stored before this change (and rows added by hand in review) must not change id."""
    rec = {
        "source_document": DOC, "source_page": 2,
        "fields": {
            "nominativo_dipendente": {"normalized_value": "Mario Rossi", "status": "EXTRACTED"},
            "corso_descrizione": {"normalized_value": "Primo Soccorso", "status": "EXTRACTED"},
            "data_scadenza_rinnovo": {"normalized_value": "2027-01-31", "status": "EXTRACTED"},
        },
    }
    (d,) = extract_deadlines_from_records(MODULE, SCHEMA, [rec])
    assert d["id"] == make_deadline_id(MODULE, SCHEMA, DOC, 2, "data_scadenza_rinnovo", d["description"])
