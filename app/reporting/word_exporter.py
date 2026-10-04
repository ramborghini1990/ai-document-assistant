import io
from datetime import datetime
from typing import Dict, Any, List, Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from app.reporting.common import (
    resolve_scope,
    report_meta,
    column_plan,
    cell_value,
    signoff_labels
)


def _set_cell_shading(cell, color_hex: str):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))


def create_styled_word_report(
    extracted_data_by_schema: Dict[str, Any],
    source_documents: List[str],
    company_profile: Optional[Dict[str, Any]] = None,
    selected_fields_by_schema: Optional[Dict[str, List[str]]] = None,
    module_id: Optional[str] = None
) -> bytes:
    """
    تولید سند رسمی و مدیریتی Word (.docx) با تفکیک قطعی ماژول و متادیتای پویا.
    """
    module, scoped_data = resolve_scope(extracted_data_by_schema, module_id)
    meta = report_meta(module)

    doc = Document()
    comp = company_profile or {}
    comp_name = comp.get("company_name", "AZIENDA")
    vat_number = comp.get("vat_number", "")
    address = comp.get("address", "")

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    COLOR_PRIMARY = RGBColor(30, 77, 43)
    COLOR_SECONDARY = RGBColor(85, 85, 85)

    # عنوان اصلی
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run(f"{meta.get('doc_title', 'RAPPORTO')} — {comp_name.upper()}")
    run_title.font.name = "Segoe UI"
    run_title.font.size = Pt(15)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    # زیرعنوان
    sub_title = meta.get("doc_subtitle", "")
    if sub_title:
        sub_p = doc.add_paragraph()
        sub_p.paragraph_format.space_after = Pt(4)
        run_sub = sub_p.add_run(sub_title)
        run_sub.font.name = "Segoe UI"
        run_sub.font.size = Pt(10.5)
        run_sub.font.bold = True
        run_sub.font.color.rgb = COLOR_SECONDARY

    if vat_number or address:
        p_cinfo = doc.add_paragraph()
        p_cinfo.paragraph_format.space_after = Pt(10)
        c_line = f"P.IVA / C.F.: {vat_number}" if vat_number else ""
        if address:
            c_line += f"  |  Sede Operativa: {address}"
        run_cinfo = p_cinfo.add_run(c_line)
        run_cinfo.font.name = "Segoe UI"
        run_cinfo.font.size = Pt(9.5)
        run_cinfo.font.italic = True
        run_cinfo.font.color.rgb = COLOR_SECONDARY

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    run_div = p_div.add_run("―" * 58)
    run_div.font.color.rgb = RGBColor(200, 200, 200)

    # بخش ۱: متادیتای ممیزی و اسناد
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

    # بخش ۲: جداول استخراج‌شده به تفکیک اسکیما
    h2 = doc.add_heading(level=1)
    run_h2 = h2.add_run("2. Tabelle di Dettaglio per Schema")
    run_h2.font.name = "Segoe UI"
    run_h2.font.color.rgb = COLOR_PRIMARY

    for schema_name, data in scoped_data.items():
        records = data.get("records", [])
        
        p_schema_title = doc.add_paragraph()
        p_schema_title.paragraph_format.space_before = Pt(8)
        p_schema_title.paragraph_format.space_after = Pt(4)
        run_sname = p_schema_title.add_run(f"Tabella: {schema_name.upper()} (Totale Record: {len(records)})")
        run_sname.font.name = "Segoe UI"
        run_sname.font.size = Pt(11.5)
        run_sname.font.bold = True

        if not records:
            p_empty = doc.add_paragraph("Nessun record identificato nei documenti per questo schema.")
            p_empty.runs[0].font.italic = True
            continue

        user_selected = (selected_fields_by_schema or {}).get(schema_name)
        col_plan = column_plan(schema_name, module, records, user_selected)

        headers = ["Pagina Fonte"] + [col[1] for col in col_plan] + ["Stato"]

        table = doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True

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

        for rec in records:
            row_cells = table.add_row().cells
            src_page = rec.get("source_page", 1)
            fields = rec.get("fields", {})

            row_cells[0].text = f"Pag. {src_page}"
            row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            overall_status = "EXTRACTED"
            for c_idx, (fname, flabel) in enumerate(col_plan, start=1):
                fdata = fields.get(fname, {})
                status = fdata.get("status", "EXTRACTED")
                if status == "EDITED":
                    overall_status = "EDITED"
                elif status == "CALCULATED" and overall_status != "EDITED":
                    overall_status = "CALCULATED"

                val_to_display = cell_value(fdata)
                row_cells[c_idx].text = str(val_to_display if val_to_display is not None else "-")

            row_cells[-1].text = overall_status
            row_cells[-1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

            for cell in row_cells:
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = "Segoe UI"
                        run.font.size = Pt(8)

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # بخش ۳: کادرهای امضا (داینامیک بر اساس ماژول)
    signs = signoff_labels(meta, comp)
    if signs:
        h3 = doc.add_heading(level=1)
        run_h3 = h3.add_run("3. Approvazione e Visto")
        run_h3.font.name = "Segoe UI"
        run_h3.font.color.rgb = COLOR_PRIMARY

        sign_table = doc.add_table(rows=2, cols=len(signs))
        sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        for idx, sign_txt in enumerate(signs):
            sign_table.rows[0].cells[idx].text = sign_txt
            sign_table.rows[1].cells[idx].text = "Firma: _________________________\nData:   ____ / ____ / ________"

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