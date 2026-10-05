import io
import openpyxl
import pytest
from docx import Document
from app.reporting.excel_exporter import create_styled_excel_report
from app.reporting.word_exporter import create_styled_word_report


@pytest.mark.offline
def test_scoped_reporting_isolation():
    mixed_data = {
        "scadenziario": {
            "total_records": 1,
            "records": [{"source_document": "env.pdf", "source_page": 1, "fields": {"adempimento": {"normalized_value": "MUD", "status": "EXTRACTED"}}}]
        },
        "fuel_expense": {
            "total_records": 1,
            "records": [{"source_document": "fuel.xlsx", "source_page": 1, "fields": {"targa": {"normalized_value": "AA111BB", "status": "EXTRACTED"}}}]
        }
    }

    # ISO 14001 Excel isolation
    excel_bytes = create_styled_excel_report(mixed_data, ["env.pdf"], module_id="iso_14001")
    wb = openpyxl.load_workbook(io.BytesIO(excel_bytes))
    assert "SCADENZIARIO" in wb.sheetnames
    assert "FUEL_EXPENSE" not in wb.sheetnames

    # Fleet Word isolation
    word_bytes = create_styled_word_report(mixed_data, ["fuel.xlsx"], module_id="fleet_fuel_expenses")
    doc = Document(io.BytesIO(word_bytes))
    full_text = "\n".join([p.text for p in doc.paragraphs])
    assert "ISO 14001" not in full_text
    assert "FLOTTA" in full_text.upper()