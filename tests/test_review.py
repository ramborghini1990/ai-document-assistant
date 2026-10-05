import pytest
from app.extraction.registry import resolve_schema
from app.extraction.review import records_to_dataframe, dataframe_to_records


@pytest.mark.offline
def test_review_roundtrip():
    schema = resolve_schema("vehicle_fuel", module_id="iso_14001")
    original = [{
        "source_document": "fleet.xlsx",
        "source_page": 1,
        "fields": {
            "targa": {"raw_value": "gf619xa", "normalized_value": "GF619XA", "status": "EXTRACTED"},
            "litri": {"raw_value": "100", "normalized_value": 100.0, "status": "EXTRACTED"},
            "chilometri": {"raw_value": "1000", "normalized_value": 1000.0, "status": "EXTRACTED"},
            "consumo_l_100km": {"raw_value": "10.0", "normalized_value": 10.0, "status": "CALCULATED"}
        },
        "warnings": []
    }]

    df = records_to_dataframe(original, schema)
    df.loc[0, "litri"] = "150"

    reviewed = dataframe_to_records(df, original, schema)
    rec = reviewed[0]

    assert rec["fields"]["litri"]["normalized_value"] == 150.0
    assert rec["fields"]["litri"]["status"] == "EDITED"
    assert rec["fields"]["consumo_l_100km"]["normalized_value"] == 15.0
    assert rec["fields"]["consumo_l_100km"]["status"] == "CALCULATED"