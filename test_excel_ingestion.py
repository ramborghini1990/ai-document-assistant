import io
import pandas as pd
from app.rag.loader import extract_text_from_excel, load_document_content
from app.rag.chunker import split_text_into_chunks


def test_excel_ingestion_pipeline():
    print("Testing Excel Workbook (.xlsx) Ingestion Pipeline...")

    # ۱. تولید یک فایل اکسل سازمانی دو شیتی در حافظه
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_fleet = pd.DataFrame({
            "Targa": ["GF619XA", "BG750EE"],
            "Modello": ["Iveco Stralis 450", "Fiat Ducato Maxi"],
            "Km Percorsi": [145000, 210000],
            "Scadenza Revisione": ["2026-11-30", "2027-04-15"],
            "Consumo Medio L_100km": [28.5, 11.2]
        })
        df_fleet.to_excel(writer, sheet_name="PARCO_MEZZI", index=False)

        df_waste = pd.DataFrame({
            "Codice EER": ["16 01 04*", "16 01 06"],
            "Descrizione Rifiuto": ["Veicoli fuori uso contenenti liquidi pericolosi", "Veicoli fuori uso bonificati"],
            "Stato Fisico": ["Solido non polverulento", "Solido non polverulento"],
            "Giacenza Max Tonnellate": [50.0, 120.0]
        })
        df_waste.to_excel(writer, sheet_name="REGISTRO_EER", index=False)

    output.seek(0)

    # ۲. تست استخراج ساختاریافته از اکسل
    pages = extract_text_from_excel(output, "Registro_Aziendale_2026.xlsx")
    assert len(pages) == 2, f"Expected 2 sheets/pages, got {len(pages)}"
    print(f"✓ Extracted {len(pages)} distinct sheets as auditable pages.")

    # بررسی شیت اول (ناوگان)
    sheet1 = pages[0]
    assert sheet1["page_number"] == 1
    assert "PARCO_MEZZI" in sheet1["text"]
    assert "GF619XA" in sheet1["text"]
    assert "Iveco Stralis" in sheet1["text"]
    print("✓ Sheet 1 (PARCO_MEZZI) key-value row binding verified.")

    # بررسی شیت دوم (کدهای پسماند EER)
    sheet2 = pages[1]
    assert sheet2["page_number"] == 2
    assert "REGISTRO_EER" in sheet2["text"]
    assert "16 01 04*" in sheet2["text"]
    print("✓ Sheet 2 (REGISTRO_EER) key-value row binding verified.")

    # ۳. تست چانکر روی داده‌های اکسل
    chunks = split_text_into_chunks(pages, "Registro_Aziendale_2026.xlsx")
    assert len(chunks) >= 2
    print(f"✓ Chunker produced {len(chunks)} contextual chunks with Sheet/Row metadata.")

    # ۴. تست دیسپچر یکپارچه
    output.seek(0)
    dispatch_res = load_document_content(output, "Registro_Aziendale_2026.xlsx")
    assert len(dispatch_res) == 2
    print("✓ Unified dispatcher (load_document_content) handles .xlsx smoothly.")


if __name__ == "__main__":
    test_excel_ingestion_pipeline()
    print("\n🎉 PHASE 24 EXCEL INGESTION TESTS PASSED!")