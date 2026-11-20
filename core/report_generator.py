"""Generate detection summaries for manual review."""

import io
from datetime import datetime
from html import escape
from typing import Any, Dict

try:
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


NOTICE = (
    "Model detections are estimates and require human review. "
    "They do not establish PPE compliance or site safety."
)


def generate_html_report(audit_data: Dict[str, Any], project_name: str = "Construction Site") -> str:
    rows = "".join(
        f"<tr><td>{escape(str(item.get('raw_label', '')))}</td>"
        f"<td>{float(item.get('confidence', 0)) * 100:.1f}%</td>"
        f"<td>{escape(str(item.get('bbox', [])))}</td></tr>"
        for item in audit_data.get("all_items", [])
    )
    if not rows:
        rows = "<tr><td colspan='3'>No objects detected.</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Detection Summary</title>
<style>body{{font-family:Arial,sans-serif;margin:30px;color:#1e293b}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #cbd5e1;padding:8px;text-align:left}}</style>
</head><body><h1>Detection Summary</h1>
<p>Site: {escape(project_name)} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<p>{NOTICE}</p>
<table><thead><tr><th>Model label</th><th>Confidence</th><th>Bounding box (xyxy)</th></tr></thead>
<tbody>{rows}</tbody></table></body></html>"""


def generate_pdf_report(audit_data: Dict[str, Any], project_name: str = "Construction Site") -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise ImportError("PDF generation requires reportlab.")
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Detection Summary", styles["Title"]),
        Paragraph(f"Site: {escape(project_name)}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(NOTICE, styles["Normal"]),
        Spacer(1, 12),
    ]
    items = audit_data.get("all_items", [])
    if not items:
        story.append(Paragraph("No objects detected.", styles["Normal"]))
    for item in items:
        label = escape(str(item.get("raw_label", "")))
        confidence = float(item.get("confidence", 0)) * 100
        bbox = escape(str(item.get("bbox", [])))
        story.append(Paragraph(f"{label}: {confidence:.1f}% - xyxy {bbox}", styles["Normal"]))
    SimpleDocTemplate(buffer).build(story)
    return buffer.getvalue()
