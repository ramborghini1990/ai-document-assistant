import io
from datetime import datetime
from typing import Dict, Any, List
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from app.reporting.excel_exporter import COLUMN_LABELS


def _set_cell_shading(cell, color_hex: str):
    """اعمال رنگ پس‌زمینه بر روی سلول جدول Word."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))


def create_styled_word_report(
    extracted_data_by_schema: Dict[str, Any],
    source_documents: List[str]
) -> bytes:
    """
    تولید سند رسمی و مدیریتی Word (.docx) مطابق با استانداردهای ممیزی و ایزو ۱۴۰۰۱.
    """
    doc = Document()

    # تنظیم حاشیه‌های استاندارد گزارش (Normal Margins)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # رنگ‌های استاندارد سازمانی
    COLOR_PRIMARY = RGBColor(30, 77, 43)    # سبز زیتونی ایزو ۱۴۰۰۱
    COLOR_SECONDARY = RGBColor(85, 85, 85) # خاکستری تیره برای متاداده

    # -------------------------------------------------------------
    # سربرگ و عنوان گزارش
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run("RAPPORTO DI CONFORMITÀ E AUDIT DOCUMENTALE")
    run_title.font.name = "Segoe UI"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(14)
    run_sub = sub_p.add_run("Sistema di Gestione Ambientale (UNI EN ISO 14001:2026) — Estrazione Intelligente")
    run_sub.font.name = "Segoe UI"
    run_sub.font.size = Pt(10.5)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_SECONDARY

    # خط تفکیک افقی
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    run_div = p_div.add_run("―" * 58)
    run_div.font.color.rgb = RGBColor(200, 200, 200)

    # -------------------------------------------------------------
    # بخش ۱: متادیتای ممیزی و اسناد مبدأ
    # -------------------------------------------------------------
    h1 = doc.add_heading(level=1)
    run_h1 = h1.add_run("1. Informazioni Generali e Documenti Analizzati")
    run_h1.font.name = "Segoe UI"
    run_h1.font.color.rgb = COLOR_PRIMARY

    p_meta = doc.add_paragraph()
    p_meta.add_run("Data di Generazione: ").bold = True
    p_meta.add_run(f"{datetime.now().strftime('%d/%m/%Y ore %H:%M:%S')}\n")
    p_meta.add_run("Metodologia: ").bold = True
    p_meta.add_run("Analisi multimodale semantica con verifica anti-allucinazione e tracciabilità di pagina.\n")
    p_meta.add_run("Documenti di Origine Verificati:\n").bold = True
    
    for doc_name in source_documents:
        p_doc = doc.add_paragraph(style="List Bullet")
        p_doc.paragraph_format.space_after = Pt(2)
        r = p_doc.add_run(doc_name)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # بخش ۲: جداول استخراج‌شده به تفکیک اسکیما
    # -------------------------------------------------------------
    h2 = doc.add_heading(level=1)
    run_h2 = h2.add_run("2. Tabelle di Dettaglio per Schema")
    run_h2.font.name = "Segoe UI"
    run_h2.font.color.rgb = COLOR_PRIMARY

    for schema_name, data in extracted_data_by_schema.items():
        records = data.get("records", [])
        
        p_schema_title = doc.add_paragraph()
        p_schema_title.paragraph_format.space_before = Pt(8)
        p_schema_title.paragraph_format.space_after = Pt(4)
        run_sname = p_schema_title.add_run(f"Tabella: {schema_name.upper()} (Totale Record: {len(records)})")
        run_sname.font.name = "Segoe UI"
        run_sname.font.size = Pt(12)
        run_sname.font.bold = True

        if not records:
            p_empty = doc.add_paragraph("Nessun record identificato nei documenti per questo schema.")
            p_empty.runs[0].font.italic = True
            continue

        sample_fields = list(records[0].get("fields", {}).keys())
        headers = ["Pagina Fonte"] + [COLUMN_LABELS.get(f, f.replace("_", " ").title()) for f in sample_fields] + ["Stato Estrazione"]

        # ایجاد جدول
        table = doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True

        # استایل هدر جدول
        hdr_cells = table.rows[0].cells
        for idx, text in enumerate(headers):
            hdr_cells[idx].text = text
            _set_cell_shading(hdr_cells[idx], "1E4D2B")
            hdr_p = hdr_cells[idx].paragraphs[0]
            hdr_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in hdr_p.runs:
                run.font.name = "Segoe UI"
                run.font.bold = True
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(255, 255, 255)

        # درج داده‌ها
        for rec in records:
            row_cells = table.add_row().cells
            src_page = rec.get("source_page", 1)
            fields = rec.get("fields", {})

            # ستون شماره صفحه
            row_cells[0].text = f"Pag. {src_page}"
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            overall_status = "EXTRACTED"
            for c_idx, fname in enumerate(sample_fields, start=1):
                fdata = fields.get(fname, {})
                norm_val = fdata.get("normalized_value")
                raw_val = fdata.get("raw_value")
                status = fdata.get("status", "EXTRACTED")
                if status == "CALCULATED":
                    overall_status = "CALCULATED"

                display_val = str(norm_val if norm_val is not None else (raw_val if raw_val is not None else "-"))
                row_cells[c_idx].text = display_val

            # ستون وضعیت
            row_cells[-1].text = overall_status
            row_cells[-1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            # تنظیم فونت تمام سلول‌های ردیف
            for cell in row_cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = "Segoe UI"
                        run.font.size = Pt(8)

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # بخش ۳: کادر تأیید و امضای نهایی (Sign-off & Verification)
    # -------------------------------------------------------------
    h3 = doc.add_heading(level=1)
    run_h3 = h3.add_run("3. Approvazione e Visto del Responsabile")
    run_h3.font.name = "Segoe UI"
    run_h3.font.color.rgb = COLOR_PRIMARY

    sign_table = doc.add_table(rows=2, cols=2)
    sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    sign_table.rows[0].cells[0].text = "Verificato da (Responsabile SGA / RSGA):"
    sign_table.rows[0].cells[1].text = "Approvato da (Direzione Generale / Tecnico):"
    sign_table.rows[1].cells[0].text = "Firma: _________________________\nData:   ____ / ____ / ________"
    sign_table.rows[1].cells[1].text = "Firma: _________________________\nData:   ____ / ____ / ________"

    for row in sign_table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.name = "Segoe UI"
                    run.font.size = Pt(9.5)

    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()