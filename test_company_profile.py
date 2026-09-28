from app.database.database import init_db, get_company_profile, update_company_profile
from app.reporting.excel_exporter import create_styled_excel_report
from app.reporting.word_exporter import create_styled_word_report


def test_company_profile_lifecycle():
    print("Testing Company Profile Database & Dynamic Reporting...")

    # ۱. اطمینان از راه‌اندازی دیتابیس
    init_db()
    prof = get_company_profile()
    assert "company_name" in prof
    print(f"✓ Initial default profile loaded: {prof['company_name']}")

    # ۲. به‌روزرسانی مشخصات سازمانی جدید
    new_company = "ACME Environmental Solutions S.p.A."
    new_vat = "IT99887766554"
    new_addr = "Corso Francia 100, Torino (TO)"
    new_rsga = "Ing. Mario Rossi"
    new_dir = "Dott. Giuseppe Verdi"

    update_company_profile(
        company_name=new_company,
        vat_number=new_vat,
        address=new_addr,
        rsga_name=new_rsga,
        technical_director=new_dir
    )

    updated_prof = get_company_profile()
    assert updated_prof["company_name"] == new_company
    assert updated_prof["vat_number"] == new_vat
    assert updated_prof["rsga_name"] == new_rsga
    print(f"✓ Profile successfully updated in SQLite: {updated_prof['company_name']}")

    # ۳. تست تولید فایل اکسل با پروفایل جدید
    dummy_data = {
        "scadenziario": {
            "total_records": 1,
            "records": [
                {
                    "source_page": 1,
                    "fields": {
                        "tema": {"normalized_value": "Sicurezza", "raw_value": "Sicurezza", "status": "EXTRACTED"},
                        "adempimento": {"normalized_value": "Test Adempimento", "raw_value": "Test", "status": "EXTRACTED"},
                        "scadenza": {"normalized_value": "2026-12-31", "raw_value": "31/12/2026", "status": "EXTRACTED"}
                    }
                }
            ]
        }
    }

    excel_bytes = create_styled_excel_report(dummy_data, ["test_doc.pdf"], company_profile=updated_prof)
    assert len(excel_bytes) > 1000
    print("✓ Excel generated successfully with dynamic company metadata.")

    # ۴. تست تولید فایل ورد با کادرهای امضای جدید
    word_bytes = create_styled_word_report(dummy_data, ["test_doc.pdf"], company_profile=updated_prof)
    assert len(word_bytes) > 1000
    print("✓ Word report generated successfully with dynamic sign-off roles.")

    # ۵. بازگرداندن مقادیر مرجع به EFFE.EMME جهت ادامه کار
    update_company_profile(
        company_name="EFFE.EMME S.r.l.",
        vat_number="IT 03412580048",
        address="Via dell'Artigianato 12, Cuneo (CN)",
        rsga_name="Laura Mellano / RSGA",
        technical_director="Ermes Frossasco / Direzione Tecnica"
    )
    print("✓ Restored default corporate configuration for EFFE.EMME S.r.l.")


if __name__ == "__main__":
    test_company_profile_lifecycle()
    print("\n🎉 PHASE 23 TESTS PASSED!")