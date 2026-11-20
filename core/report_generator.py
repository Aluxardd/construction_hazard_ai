"""
Safety Report Generation Engine.
Supports:
1. Professional PDF Report generation via ReportLab (aligned with BSc proposal).
2. Clean print-optimized HTML Safety Audit Report (fallback or direct browser printing).
"""

import io
from datetime import datetime
from typing import Dict, List, Any

# Try importing reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(audit_data: Dict[str, Any], project_name: str = "Construction Site Alpha") -> bytes:
    """
    Builds a formal PDF safety inspection report using ReportLab.
    Returns bytes of the generated PDF.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab is not installed. Please run `pip install reportlab`.")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1A202C"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    story = []

    # Title & Header
    story.append(Paragraph("Construction Site Hazard Identification & Risk Assessment Audit", title_style))
    story.append(Paragraph(
        f"<b>Project Location / Site:</b> {project_name} | "
        f"<b>Audit Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"<b>Framework:</b> OSHA 29 CFR 1926 / 5×5 Matrix",
        subtitle_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

    # Executive Summary Box
    site_risk = audit_data.get("overall_site_risk", "Unknown")
    total_hazards = audit_data.get("total_hazards", 0)
    tier_counts = audit_data.get("tier_counts", {})
    summary_stmt = audit_data.get("summary_statement", "")

    tier_color_map = {
        "Critical": colors.HexColor("#E53E3E"),
        "High": colors.HexColor("#DD6B20"),
        "Medium": colors.HexColor("#D69E2E"),
        "Low": colors.HexColor("#38A169"),
        "Compliant / Clear": colors.HexColor("#38A169")
    }
    status_bg = tier_color_map.get(site_risk, colors.HexColor("#4A5568"))

    summary_data = [
        [
            Paragraph("<b>Overall Site Status:</b>", body_style),
            Paragraph(f"<font color='white'><b>{site_risk.upper()}</b></font>", body_bold),
            Paragraph("<b>Total Hazards Detected:</b>", body_style),
            Paragraph(f"<b>{total_hazards}</b>", body_style)
        ],
        [
            Paragraph("<b>Risk Breakdown:</b>", body_style),
            Paragraph(
                f"Critical: <b>{tier_counts.get('Critical', 0)}</b> | "
                f"High: <b>{tier_counts.get('High', 0)}</b> | "
                f"Medium: <b>{tier_counts.get('Medium', 0)}</b> | "
                f"Low: <b>{tier_counts.get('Low', 0)}</b>",
                body_style
            ),
            Paragraph("<b>Intervention Priority:</b>", body_style),
            Paragraph(f"<b>{summary_stmt}</b>", body_style)
        ]
    ]

    summary_table = Table(summary_data, colWidths=[110, 160, 120, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ('BACKGROUND', (1, 0), (1, 0), status_bg),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Detailed Hazards Table
    story.append(Paragraph("Identified Hazard Register & Action Plan", h2_style))

    hazards = audit_data.get("hazards", [])
    if not hazards:
        story.append(Paragraph("No safety hazards detected in the inspected imagery.", body_style))
    else:
        table_rows = [
            [
                Paragraph("<b>Hazard / Finding</b>", body_bold),
                Paragraph("<b>L</b>", body_bold),
                Paragraph("<b>S</b>", body_bold),
                Paragraph("<b>Score</b>", body_bold),
                Paragraph("<b>Tier</b>", body_bold),
                Paragraph("<b>Standard</b>", body_bold),
                Paragraph("<b>Corrective Recommendation</b>", body_bold)
            ]
        ]

        for h in hazards:
            tier = h.get("risk_tier", "Low")
            badge_bg = tier_color_map.get(tier, colors.HexColor("#718096"))

            table_rows.append([
                Paragraph(f"<b>{h.get('title', '')}</b><br/><font color='#718096'>Conf: {int(h.get('confidence', 0)*100)}%</font>", body_style),
                Paragraph(str(h.get("likelihood", 1)), body_style),
                Paragraph(str(h.get("severity", 1)), body_style),
                Paragraph(f"<b>{h.get('risk_score', 1)}</b>", body_bold),
                Paragraph(f"<font color='{badge_bg.hexval()}'><b>{tier}</b></font>", body_style),
                Paragraph(h.get("standard_ref", "OSHA 1926"), body_style),
                Paragraph(h.get("recommendation", "Review on site."), body_style),
            ])

        haz_table = Table(table_rows, colWidths=[110, 22, 22, 35, 55, 95, 201])
        haz_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        story.append(haz_table)

    # Footer note
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceAfter=6))
    story.append(Paragraph(
        "<i>Automated Construction Site Safety Risk Assessment Tool — BSc (Hons) Computer Science Project | University of Bolton & Regent College London</i>",
        subtitle_style
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_html_report(audit_data: Dict[str, Any], project_name: str = "Construction Site Alpha") -> str:
    """
    Generates a print-ready HTML safety audit report that can be saved directly to PDF.
    """
    site_risk = audit_data.get("overall_site_risk", "Unknown")
    total_hazards = audit_data.get("total_hazards", 0)
    tier_counts = audit_data.get("tier_counts", {})
    hazards = audit_data.get("hazards", [])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tier_colors = {
        "Critical": "#dc3545",
        "High": "#fd7e14",
        "Medium": "#ffc107",
        "Low": "#28a745",
        "Compliant / Clear": "#28a745"
    }
    status_color = tier_colors.get(site_risk, "#6c757d")

    rows_html = ""
    for h in hazards:
        t = h.get("risk_tier", "Low")
        c = tier_colors.get(t, "#6c757d")
        text_c = "#ffffff" if t != "Medium" else "#212529"
        rows_html += f"""
        <tr>
            <td>
                <strong>{h.get('title')}</strong><br>
                <small style="color: #666;">Raw: {h.get('raw_label')} | Conf: {int(h.get('confidence',0)*100)}%</small>
            </td>
            <td style="text-align: center;">{h.get('likelihood')}</td>
            <td style="text-align: center;">{h.get('severity')}</td>
            <td style="text-align: center; font-weight: bold;">{h.get('risk_score')}</td>
            <td style="text-align: center;">
                <span style="background-color: {c}; color: {text_c}; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">
                    {t.upper()}
                </span>
            </td>
            <td><code>{h.get('standard_ref')}</code></td>
            <td>{h.get('recommendation')}</td>
        </tr>
        """

    if not rows_html:
        rows_html = "<tr><td colspan='7' style='text-align:center; padding: 20px;'>No safety hazards detected in the submitted site imagery.</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Construction Safety Risk Assessment Audit Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 30px;
            color: #2d3748;
            background-color: #ffffff;
        }}
        .header {{
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 8px 0;
            font-size: 22px;
            color: #1a202c;
        }}
        .header p {{
            margin: 0;
            color: #718096;
            font-size: 13px;
        }}
        .summary-card {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .badge-status {{
            display: inline-block;
            background-color: {status_color};
            color: #ffffff;
            font-weight: bold;
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 16px;
            text-transform: uppercase;
        }}
        .stat-grid {{
            display: flex;
            gap: 20px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-num {{
            font-size: 20px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 15px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 8px 10px;
            text-align: left;
        }}
        th {{
            background-color: #edf2f7;
            color: #2d3748;
            font-weight: 600;
        }}
        @media print {{
            body {{ margin: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Construction Site Hazard Identification & Risk Assessment Audit</h1>
        <p>Project: <strong>{project_name}</strong> | Generated: {now_str} | Standard: OSHA 29 CFR 1926 & 5×5 Matrix</p>
    </div>

    <div class="summary-card">
        <div>
            <div style="font-size: 12px; text-transform: uppercase; color: #718096; margin-bottom: 4px;">Overall Site Safety Status</div>
            <div class="badge-status">{site_risk}</div>
            <div style="margin-top: 8px; font-size: 13px; color: #4a5568;">{audit_data.get('summary_statement', '')}</div>
        </div>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-num">{total_hazards}</div>
                <div style="font-size: 11px; color: #718096;">Total Hazards</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #dc3545;">{tier_counts.get('Critical', 0)}</div>
                <div style="font-size: 11px; color: #718096;">Critical</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #fd7e14;">{tier_counts.get('High', 0)}</div>
                <div style="font-size: 11px; color: #718096;">High</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #d69e2e;">{tier_counts.get('Medium', 0)}</div>
                <div style="font-size: 11px; color: #718096;">Medium</div>
            </div>
            <div class="stat-item">
                <div class="stat-num" style="color: #28a745;">{tier_counts.get('Low', 0)}</div>
                <div style="font-size: 11px; color: #718096;">Low</div>
            </div>
        </div>
    </div>

    <h3>Identified Hazards Register</h3>
    <table>
        <thead>
            <tr>
                <th style="width: 22%;">Hazard Finding</th>
                <th style="width: 5%; text-align: center;">L</th>
                <th style="width: 5%; text-align: center;">S</th>
                <th style="width: 6%; text-align: center;">Score</th>
                <th style="width: 10%; text-align: center;">Risk Tier</th>
                <th style="width: 15%;">OSHA / HSE Standard</th>
                <th>Actionable Corrective Recommendation</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div style="margin-top: 40px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 11px; color: #a0aec0; text-align: center;">
        University of Bolton & Regent College London &bull; Department of Computer Science &bull; BSc (Hons) Final Year Project &bull; Serghei Coceban
    </div>
</body>
</html>
"""
    return html
