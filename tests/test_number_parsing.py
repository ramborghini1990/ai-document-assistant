"""F11: one number parser for extraction and reports; several figures in one value are never guessed."""
import pytest

from app.extraction.extractor import normalize_field
from app.extraction.normalizer import count_standalone_numbers, normalize_number, parse_number_token
from app.extraction.registry import FieldDef
from app.reporting.expansion import parse_number, split_value_unit

NUMBER = FieldDef("importo", "number", "Importo")

SAME_TEXT = [
    ("1.250,50", 1250.5),
    ("1,250.50", 1250.5),      # was 1.2505 in reports, 1250.5 in extraction
    ("1.234.567,89", 1234567.89),
    ("2.000", 2000.0),
    ("12.5", 12.5),
    ("250,00", 250.0),
    ("9", 9.0),
]


@pytest.mark.offline
@pytest.mark.parametrize("text,expected", SAME_TEXT)
def test_extraction_and_reports_read_numbers_identically(text, expected):
    assert normalize_number(text) == pytest.approx(expected)
    assert parse_number_token(text) == pytest.approx(expected)
    assert parse_number(text) == pytest.approx(expected)


@pytest.mark.offline
def test_report_parser_keeps_int_for_integral_values_and_rejects_text():
    assert parse_number("1.500") == 1500 and isinstance(parse_number("1.500"), int)
    assert parse_number("abc") is None
    assert parse_number("9 t") is None                    # strict: a whole token only
    assert split_value_unit("1,250.50 t/a") == (1250.5, "t/a")


@pytest.mark.offline
@pytest.mark.parametrize("text,count", [
    ("877", 1), ("€ 1.234,56", 1), ("125 m3", 1), ("6,5 L/100km", 1), ("CO2 12,5 t", 1),
    ("IVA 22% su 1.234,00", 2), ("F1 120 F2 80", 2), ("877 kWh al 31/12/2025", 2),  # a d/m/y date counts once
])
def test_count_standalone_numbers_ignores_unit_digits(text, count):
    assert count_standalone_numbers(text) == count


@pytest.mark.offline
def test_value_with_several_figures_becomes_uncertain_not_a_guess():
    out = normalize_field(NUMBER, "IVA 22% su 1.234,00")
    assert out == {"raw_value": "IVA 22% su 1.234,00", "normalized_value": None, "status": "UNCERTAIN"}


@pytest.mark.offline
def test_single_figure_with_unit_still_extracts():
    assert normalize_field(NUMBER, "€ 1.234,56")["normalized_value"] == pytest.approx(1234.56)
    assert normalize_field(NUMBER, "125 m3")["status"] == "EXTRACTED"


@pytest.mark.offline
def test_review_edit_with_several_figures_is_uncertain_too():
    out = normalize_field(NUMBER, "150 o 160", ok_status="EDITED")
    assert out["status"] == "UNCERTAIN"
