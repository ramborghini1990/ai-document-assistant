import json
from app.extraction.normalizer import normalize_date, normalize_number, normalize_plate
from app.extraction.extractor import extract_structured_data


def test_normalizers():
    print("Testing Normalizers...")
    # تست تاریخ
    assert normalize_date("31/07/2026") == "2026-07-31"
    assert normalize_date("15-05-2025") == "2025-05-15"
    assert normalize_date("31 luglio 2026") == "2026-07-31"
    print("✓ Date normalization passed.")

    # تست ارقام ایتالیایی
    assert normalize_number("1.250,50 L") == 1250.50
    assert normalize_number("15000 km") == 15000.0
    print("✓ Number normalization passed.")

    # تست پلاک
    assert normalize_plate("bg 750 ee") == "BG750EE"
    print("✓ Plate normalization passed.")


def test_scadenziario_extraction():
    print("\nTesting Scadenziario Extraction with Gemini...")
    sample_text = (
        "DOCUMENTO VISITE MEDICHE AZIENDALI\n"
        "Frossasco Ivano: Visita medica periodica, Scadenza: 04/11/2026, Responsabile: Dott. Rossi, Stato: Programmata.\n"
        "Mellano Laura: Idoneità specifica, Scadenza: 10/06/2030, Responsabile: Dott.ssa Bianchi.\n"
        "Oddoero Michael: Scadenza: 14/01/2027, Stato: Da confermare."
    )
    pages = [{"page_number": 1, "text": sample_text}]

    result = extract_structured_data(pages, schema_name="scadenziario")
    print(f"Total Extracted Records: {result['total_records']}")
    assert result["total_records"] >= 3

    for r in result["records"]:
        scad = r["fields"]["scadenza"]
        print(f" - Scadenza raw: {scad['raw_value']} -> normalized: {scad['normalized_value']} (Status: {scad['status']})")

    print("✓ Scadenziario extraction successfully verified!")


def test_vehicle_fuel_calculation():
    print("\nTesting Vehicle & Fuel Auto-Calculation...")
    sample_text = (
        "RIEPILOGO CONSUMI MENSILI MEZZI AZIENDALI\n"
        "Mezzo Targa: BG 750 EE - Modello: Iveco Daily\n"
        "Periodo: Giugno 2026\n"
        "Litri erogati: 250,00 L\n"
        "Chilometri percorsi: 2.000 km\n"
        "Scadenza revisione: 31/12/2026"
    )
    pages = [{"page_number": 1, "text": sample_text}]

    result = extract_structured_data(pages, schema_name="vehicle_fuel")
    assert result["total_records"] >= 1
    rec = result["records"][0]
    targa = rec["fields"]["targa"]["normalized_value"]
    consumo = rec["fields"]["consumo_l_100km"]

    print(f"Vehicle: {targa}")
    print(f"Consumption Status: {consumo['status']} -> Value: {consumo['normalized_value']} L/100km")
    # محاسبه فرمول: (250 / 2000) * 100 = 12.5 L/100km
    assert consumo["status"] == "CALCULATED"
    assert consumo["normalized_value"] == 12.5
    print("✓ Fuel consumption calculation successfully verified!")


if __name__ == "__main__":
    test_normalizers()
    test_scadenziario_extraction()
    test_vehicle_fuel_calculation()
    print("\n🎉 ALL PHASE 18 EXTRACTION TESTS PASSED!")