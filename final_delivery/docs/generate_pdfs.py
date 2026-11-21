"""
PDF Generator for Milestone 2 Documentation & Technical Report
Uses ReportLab to convert Markdown documents into styled PDF deliverables.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    KeepTogether,
    HRFlowable,
)


def md_to_pdf(input_md_path: str, output_pdf_path: str, doc_title: str, compact: bool = False):
    """Parse a Markdown file and render it as a styled PDF."""
    with open(input_md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=35 if compact else 40,
        rightMargin=35 if compact else 40,
        topMargin=28 if compact else 40,
        bottomMargin=28 if compact else 40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=15 if compact else 20,
        leading=18 if compact else 24,
        textColor=colors.HexColor("#312e81"),
        spaceAfter=6 if compact else 15,
        alignment=0,
    )

    h1_style = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12 if compact else 14,
        leading=15 if compact else 18,
        textColor=colors.HexColor("#1e1b4b"),
        spaceBefore=8 if compact else 14,
        spaceAfter=4 if compact else 8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.5 if compact else 12,
        leading=13 if compact else 16,
        textColor=colors.HexColor("#4338ca"),
        spaceBefore=6 if compact else 10,
        spaceAfter=3 if compact else 6,
        keepWithNext=True,
    )

    h3_style = ParagraphStyle(
        "H3",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=9.5 if compact else 10,
        leading=12 if compact else 14,
        textColor=colors.HexColor("#374151"),
        spaceBefore=5 if compact else 8,
        spaceAfter=2 if compact else 4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5 if compact else 9,
        leading=11.5 if compact else 13,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=3 if compact else 6,
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=12 if compact else 15,
        firstLineIndent=-8 if compact else -10,
        spaceAfter=2 if compact else 3,
    )

    code_style = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#111827"),
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1f2937"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    story = []
    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        
        # Determine number of columns
        col_count = max(len(r) for r in table_rows)
        # Pad shorter rows
        for r in table_rows:
            while len(r) < col_count:
                r.append("")
        
        # Convert strings to Paragraphs
        data = []
        for row_idx, r in enumerate(table_rows):
            row_data = []
            for cell in r:
                c_style = table_header_style if row_idx == 0 else table_cell_style
                # escape XML characters
                safe_cell = cell.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                row_data.append(Paragraph(safe_cell, c_style))
            data.append(row_data)

        # Distribute available page width (612 - 80 = 532)
        total_w = 532
        col_w = total_w / col_count
        t = Table(data, colWidths=[col_w] * col_count)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))
        table_rows = []
        in_table = False

    for line in lines:
        stripped = line.strip()

        # Handle Code Fences
        if stripped.startswith("```"):
            if in_code_block:
                # Flush code block
                full_code = "\n".join(code_lines)
                # Cap code block display to prevent blowout
                if len(full_code.splitlines()) > 60:
                    truncated = full_code.splitlines()[:60]
                    full_code = "\n".join(truncated) + "\n... [truncated for print length] ..."
                p = Preformatted(full_code, code_style)
                code_table = Table([[p]], colWidths=[532])
                code_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]))
                story.append(code_table)
                story.append(Spacer(1, 6))
                code_lines = []
                in_code_block = False
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Handle Tables
        if "|" in line and not line.startswith("```"):
            # Check if divider line
            if re.match(r"^\|?\s*[-:]+[-| :]*$", stripped):
                continue
            parts = [p.strip() for p in stripped.split("|")]
            if parts and parts[0] == "":
                parts = parts[1:]
            if parts and parts[-1] == "":
                parts = parts[:-1]
            if parts:
                in_table = True
                table_rows.append(parts)
                continue
        else:
            if in_table:
                flush_table()

        if not stripped:
            continue

        # Horizontal Rule
        if stripped in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=10, spaceBefore=6))
            continue

        # Headings
        if stripped.startswith("# "):
            clean = stripped[2:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean, title_style if not story else h1_style))
            continue
        elif stripped.startswith("## "):
            clean = stripped[3:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean, h2_style))
            continue
        elif stripped.startswith("### "):
            clean = stripped[4:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean, h3_style))
            continue
        elif stripped.startswith("#### "):
            clean = stripped[5:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean, h3_style))
            continue

        # Bullets
        if stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            # simple bold markup conversion
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            story.append(Paragraph(f"• {content}", bullet_style))
            continue

        # Numbered list
        num_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if num_match:
            num = num_match.group(1)
            content = num_match.group(2).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
            story.append(Paragraph(f"{num}. {content}", bullet_style))
            continue

        # Standard Paragraph
        content = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        content = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", content)
        content = re.sub(r"\*(.*?)\*", r"<i>\1</i>", content)
        content = re.sub(r"`(.*?)`", r"<font face='Courier'>\1</font>", content)
        story.append(Paragraph(content, body_style))

    # Build document
    doc.build(story)
    print(f"Generated PDF: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")


if __name__ == "__main__":
    base = r"c:\Users\Asus\OneDrive\Desktop\prompt\Bug-Explanation-and-Fix-Assistant\docs"
    m2_md = os.path.join(base, "milestone_2_report.md")
    
    # Check if primary target is locked
    m2_pdf = os.path.join(base, "milestone_2_report.pdf")
    try:
        with open(m2_pdf, "a") as f:
            pass
    except PermissionError:
        m2_pdf = os.path.join(base, "milestone_2_report_submission.pdf")
        print(f"Primary milestone_2_report.pdf is locked; rendering to {m2_pdf}")

    md_to_pdf(m2_md, m2_pdf, "SCSE4041 Milestone 2 Documentation")

    tech_md = os.path.join(base, "technical_report.md")
    tech_pdf = os.path.join(base, "technical_report.pdf")
    try:
        with open(tech_pdf, "a") as f:
            pass
    except PermissionError:
        tech_pdf = os.path.join(base, "technical_report_submission.pdf")
        print(f"Primary technical_report.pdf is locked; rendering to {tech_pdf}")

    md_to_pdf(tech_md, tech_pdf, "Technical Report: Bug Explanation and Fix Assistant", compact=True)
