
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)


NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#3659D9")
TEXT = colors.HexColor("#243447")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#D5DDE5")
PALE = colors.HexColor("#E8EEF5")
ROW_ALT = colors.HexColor("#F4F7FA")


def register_report_fonts():
    """Use DejaVu Sans when available; otherwise use built-in Helvetica."""
    font_candidates = [
        (
            Path("C:/Windows/Fonts/DejaVuSans.ttf"),
            Path("C:/Windows/Fonts/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/arialbd.ttf"),
        ),
    ]

    # Also check common Linux font locations.
    font_candidates.extend([
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
        (
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
        ),
    ])

    for regular_path, bold_path in font_candidates:
        if regular_path.exists() and bold_path.exists():
            try:
                pdfmetrics.registerFont(
                    TTFont("AccessGuardSans", str(regular_path))
                )
                pdfmetrics.registerFont(
                    TTFont("AccessGuardSans-Bold", str(bold_path))
                )
                pdfmetrics.registerFontFamily(
                    "AccessGuardSans",
                    normal="AccessGuardSans",
                    bold="AccessGuardSans-Bold",
                    italic="AccessGuardSans",
                    boldItalic="AccessGuardSans-Bold",
                )
                return "AccessGuardSans", "AccessGuardSans-Bold"
            except (OSError, ValueError):
                continue

    return "Helvetica", "Helvetica-Bold"


def generate_audit_report(employees, findings, source_name):
    buffer = BytesIO()

    page_width, page_height = landscape(A4)
    font_regular, font_bold = register_report_fonts()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=13 * mm,
        bottomMargin=15 * mm,
        title="AccessGuard IT Access Control Audit Report",
        author="AccessGuard",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="AGTitle",
        fontName=font_bold,
        fontSize=21,
        leading=26,
        alignment=TA_LEFT,
        textColor=NAVY,
        spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name="AGSubtitle",
        fontName=font_bold,
        fontSize=12,
        leading=16,
        alignment=TA_LEFT,
        textColor=TEXT,
        spaceAfter=2 * mm,
    ))

    styles.add(ParagraphStyle(
        name="AGSection",
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=NAVY,
        spaceBefore=5 * mm,
        spaceAfter=2.5 * mm,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
    name="AGBody",
    fontName=font_regular,
    fontSize=9,
    leading=13,
    textColor=TEXT,
    alignment=TA_LEFT,
    leftIndent=4 * mm,
    firstLineIndent=0,
    rightIndent=2 * mm,
    spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name="AGCell",
        fontName=font_regular,
        fontSize=7.5,
        leading=10,
        textColor=TEXT,
        alignment=TA_LEFT,
        splitLongWords=1,
    ))

    styles.add(ParagraphStyle(
        name="AGHeaderCell",
        fontName=font_bold,
        fontSize=7.5,
        leading=9,
        textColor=colors.white,
        alignment=TA_LEFT,
        splitLongWords=1,
    ))

    styles.add(ParagraphStyle(
        name="AGSummaryLabel",
        fontName=font_bold,
        fontSize=8,
        leading=10,
        textColor=NAVY,
    ))

    styles.add(ParagraphStyle(
        name="AGSummaryValue",
        fontName=font_regular,
        fontSize=8.5,
        leading=11,
        textColor=TEXT,
        splitLongWords=1,
    ))

    story = []

    story.append(Paragraph("AccessGuard", styles["AGTitle"]))
    story.append(Paragraph(
        "IT ACCESS CONTROL AUDIT SCREENING REPORT",
        styles["AGSubtitle"],
    ))
    story.append(Spacer(1, 3 * mm))

    report_time = datetime.now(timezone.utc).astimezone(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d %B %Y, %I:%M %p IST")

    critical = int((findings["severity"] == "Critical").sum())
    high = int((findings["severity"] == "High").sum())
    medium = int((findings["severity"] == "Medium").sum())

    affected = (
        int(findings["employee_id"].nunique())
        if not findings.empty else 0
    )

    summary_data = [
        [
            Paragraph("Report generated", styles["AGSummaryLabel"]),
            Paragraph(escape(report_time), styles["AGSummaryValue"]),
            Paragraph("Dataset", styles["AGSummaryLabel"]),
            Paragraph(escape(str(source_name)), styles["AGSummaryValue"]),
        ],
        [
            Paragraph("Accounts reviewed", styles["AGSummaryLabel"]),
            Paragraph(str(len(employees)), styles["AGSummaryValue"]),
            Paragraph("Total findings", styles["AGSummaryLabel"]),
            Paragraph(str(len(findings)), styles["AGSummaryValue"]),
        ],
        [
            Paragraph("Affected accounts", styles["AGSummaryLabel"]),
            Paragraph(str(affected), styles["AGSummaryValue"]),
            Paragraph(
                "Critical / High / Medium", styles["AGSummaryLabel"]
            ),
            Paragraph(
                f"{critical} / {high} / {medium}",
                styles["AGSummaryValue"],
            ),
        ],
    ]
    summary_widths = [
        39 * mm,
        56 * mm,
        42 * mm,
        doc.width - 39 * mm - 56 * mm - 42 * mm,
    ]
    summary_table = Table(
        summary_data,
        colWidths=summary_widths,
        hAlign="LEFT",
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE),
        ("BACKGROUND", (2, 0), (2, -1), PALE),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("BACKGROUND", (3, 0), (3, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph(
        "1. Detailed Findings", styles["AGSection"]
    ))

    if findings.empty:
        story.append(Paragraph(
            "No findings were generated by the configured rules. "
            "This does not establish that all access is appropriate "
            "or that all risks have been identified.",
            styles["AGBody"],
        ))
    else:
        columns = [
            ("Finding ID", "finding_id", 24),
            ("Employee ID", "employee_id", 23),
            ("Control", "rule_id", 15),
            ("Severity", "severity", 19),
            ("Finding", "finding", 42),
            ("Evidence", "evidence", 57),
            ("Recommended Action", "recommended_action", 60),
        ]

        total_units = sum(width for _, _, width in columns)
        widths = [
            doc.width * units / total_units
            for _, _, units in columns
        ]

        table_data = [[
            Paragraph(escape(name), styles["AGHeaderCell"])
            for name, _, _ in columns
        ]]

        for _, row in findings.iterrows():
            cells = []

            for _, field, _ in columns:
                value = row.get(field, "")
                if pd.isna(value):
                    value = ""

                cells.append(Paragraph(
                    escape(str(value)),
                    styles["AGCell"],
                ))

            table_data.append(cells)

        findings_table = Table(
            table_data,
            colWidths=widths,
            repeatRows=1,
            hAlign="LEFT",
        )

        findings_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.45, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white, ROW_ALT
            ]),
        ]))

        story.append(findings_table)

    story.append(Paragraph(
        "2. Executive Summary", styles["AGSection"]
    ))
    story.append(Paragraph(
        f"The screening reviewed {len(employees)} account record(s) "
        f"and identified {len(findings)} potential exception(s) "
        f"across {affected} affected account(s). "
        f"The results comprise {critical} Critical, {high} High, "
        f"and {medium} Medium finding(s).",
        styles["AGBody"],
    ))

    story.append(Paragraph(
        "3. Scope and Methodology", styles["AGSection"]
    ))
    story.append(Paragraph(
        "The application evaluates supplied employee access records "
        "against five predefined rules: terminated employees with active "
        "accounts (AC-01), privileged roles (AC-02), potential "
        "segregation-of-duties conflicts (AC-03), active accounts with "
        "no recent login (AC-04), and missing or invalid last-login dates "
        "(AC-05). Results are rule-based indicators requiring appropriate "
        "human review and corroboration.",
        styles["AGBody"],
    ))

    story.append(Paragraph(
        "4. Important Limitations", styles["AGSection"]
    ))
    story.append(Paragraph(
        "This report is generated by a demonstration tool using "
        "predefined rules and the supplied dataset. Findings are not "
        "independently verified audit conclusions. The report does not "
        "establish completeness or accuracy of source records, prove "
        "unauthorized access, or replace review of system configurations, "
        "approvals, business context, and supporting evidence. "
        "A qualified reviewer should validate each exception before "
        "reaching a conclusion. This document is not a formal audit opinion.",
        styles["AGBody"],
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont(font_regular, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            12 * mm,
            8 * mm,
            "AccessGuard | Screening report | Handle according to your data policy",
        )
        canvas.drawRightString(
            page_width - 12 * mm,
            8 * mm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)
    return buffer.getvalue()