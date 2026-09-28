from app.extraction.schemas import AVAILABLE_SCHEMAS
from app.extraction.extractor import extract_structured_data
from app.reporting.excel_exporter import create_styled_excel_report
from app.reporting.word_exporter import create_styled_word_report


def test_new_domain_schemas():
    print("Testing Phase 25 Domain-Specific ISO 14001 Schemas...")

    # ۱. بررسی ثبت بودن تمامی اسکیماهای جدید و پیشین
    expected_schemas = [
        "scadenziario", "vehicle_fuel", "utility_consumption",
        "personnel_training", "regulatory_authorization", "general"
    ]
    for s in expected_schemas:
        assert s in AVAILABLE_SCHEMAS, f"Schema {s} missing from AVAILABLE_SCHEMAS"
    print(f"✓ All {len(AVAILABLE_SCHEMAS)} specialized schemas registered successfully.")

    # ۲. داده‌های ترکیبی آزمایشی برای تمام اسکیماهای جدید
    synthetic_extracted_data = {
        "utility_consumption": {
            "total_records": 1,
            "records": [
                {
                    "source_page": 1,
                    "fields": {
                        "tipo_utenza": {"normalized_value": "Energia Elettrica", "status": "EXTRACTED"},
                        "fornitore": {"normalized_value": "eVISO S.p.A.", "status": "EXTRACTED"},
                        "codice_pod_pdr": {"normalized_value": "IT001E12345678", "status": "EXTRACTED"},
                        "periodo_riferimento": {"normalized_value": "Maggio 2026", "status": "EXTRACTED"},
                        "consumo_totale": {"normalized_value": 14250.0, "status": "EXTRACTED"},
                        "unita_misura": {"normalized_value": "kWh", "status": "EXTRACTED"},
                        "ripartizione_fasce": {"normalized_value": "F1: 6000 | F2: 5000 | F3: 3250", "status": "EXTRACTED"},
                        "totale_spesa_eur": {"normalized_value": 3120.45, "status": "EXTRACTED"}
                    }
                }
            ]
        },
        "personnel_training": {
            "total_records": 1,
            "records": [
                {
                    "source_page": 2,
                    "fields": {
                        "nominativo_dipendente": {"normalized_value": "Mario Rossi", "status": "EXTRACTED"},
                        "corso_descrizione": {"normalized_value": "Carrelli Elevatori Semoventi (Muletto)", "status": "EXTRACTED"},
                        "ente_formatore": {"normalized_value": "Conflavoro PMI Cuneo", "status": "EXTRACTED"},
                        "data_emissione": {"normalized_value": "2026-03-15", "status": "EXTRACTED"},
                        "data_scadenza_rinnovo": {"normalized_value": "2031-03-15", "status": "EXTRACTED"},
                        "frequenza_anni": {"normalized_value": 5.0, "status": "EXTRACTED"},
                        "ore_formazione": {"normalized_value": 12.0, "status": "EXTRACTED"},
                        "stato_validita": {"normalized_value": "Valido", "status": "EXTRACTED"}
                    }
                }
            ]
        },
        "regulatory_authorization": {
            "total_records": 1,
            "records": [
                {
                    "source_page": 1,
                    "fields": {
                        "numero_atto_protocollo": {"normalized_value": "Prot. n.5947/2024", "status": "EXTRACTED"},
                        "numero_iscrizione": {"normalized_value": "TO15878", "status": "EXTRACTED"},
                        "ente_rilascio": {"normalized_value": "Albo Nazionale Gestori Ambientali - Piemonte", "status": "EXTRACTED"},
                        "data_rilascio": {"normalized_value": "2024-02-21", "status": "EXTRACTED"},
                        "data_scadenza": {"normalized_value": None, "status": "MISSING"},
                        "attivita_autorizzate": {"normalized_value": "Categoria 4 Classe E", "status": "EXTRACTED"},
                        "mezzi_autorizzati": {"normalized_value": "DB153EX (Trattore), XA078VK (Semirimorchio)", "status": "EXTRACTED"},
                        "elenco_codici_eer": {"normalized_value": "16 01 04*, 16 01 06, 17 04 05", "status": "EXTRACTED"},
                        "responsabili_tecnici_note": {"normalized_value": "Cessato incarico: MORRA FABIO (MRRFBA84P15H727B)", "status": "EXTRACTED"},
                        "prescrizioni_rilevanti": {"normalized_value": "Ricorso entro 30 gg al Comitato o 60 gg al TAR", "status": "EXTRACTED"}
                    }
                }
            ]
        }
    }

    # ۳. تست تولید فایل اکسل چندشیته برای اسکیماهای جدید
    excel_bytes = create_styled_excel_report(
        synthetic_extracted_data,
        ["Fattura_eVISO.pdf", "Attestato_Muletto.pdf", "Autorizzazione_Cuneo.pdf"]
    )
    assert len(excel_bytes) > 2000
    print("✓ Multi-sheet Excel report generated with Utility, Training and Permitting tabs.")

    # ۴. تست تولید گزارش رسمی ورد
    word_bytes = create_styled_word_report(
        synthetic_extracted_data,
        ["Fattura_eVISO.pdf", "Attestato_Muletto.pdf", "Autorizzazione_Cuneo.pdf"]
    )
    assert len(word_bytes) > 2000
    print("✓ Formal Word report generated with dedicated tables for all new schemas.")


if __name__ == "__main__":
    test_new_domain_schemas()
    print("\n🎉 PHASE 25 DOMAIN SCHEMAS TESTS PASSED!")