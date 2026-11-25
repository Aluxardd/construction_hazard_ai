"""Generate HTML and PDF detection and assessment summaries for manual review."""

import io
from datetime import datetime
from html import escape
from typing import Any, Dict, List, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


NOTICE = (
    "Model detections and spatial associations are estimates and require human review. "
    "They do not establish PPE compliance, suitability, or site safety."
)


def _format_metadata(project_name: str, audit_metadata: Optional[Dict[str, Any]]) -> Dict[str, str]:
    meta = audit_metadata or {}
    site_name = str(meta.get("site_name") or project_name or "Construction Site")
    inspector_name = str(meta.get("inspector_name") or "Not specified")
    inspection_date = str(meta.get("inspection_date") or datetime.now().strftime("%Y-%m-%d"))
    return {
        "site_name": site_name,
        "inspector_name": inspector_name,
        "inspection_date": inspection_date,
    }


def _collect_detection_rows(audit_data: Dict[str, Any], results: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    if results:
        rows = []
        for result in results:
            filename = result.get("filename") or "Unknown image"
            items = result.get("evaluation", {}).get("all_items")
            if items is None:
                items = result.get("detections", [])
            for item in items:
                rows.append({
                    "filename": filename,
                    "label": item.get("raw_label", item.get("label", "")),
                    "confidence": float(item.get("confidence", 0.0)),
                    "bbox": item.get("bbox", []),
                })
        return rows

    return [
        {
            "filename": "-",
            "label": item.get("raw_label", item.get("label", "")),
            "confidence": float(item.get("confidence", 0.0)),
            "bbox": item.get("bbox", []),
        }
        for item in audit_data.get("all_items", [])
    ]


def _render_html_results_section(results: Optional[List[Dict[str, Any]]]) -> str:
    if not results:
        return ""

    blocks = []
    for result in results:
        filename = escape(str(result.get("filename") or "Image"))
        if result.get("error"):
            blocks.append(
                f"<div class='card'><h3>{filename} — Processing Error</h3>"
                f"<p>{escape(str(result['error']))}</p></div>"
            )
            continue

        assessment = result.get("legal_assessment")
        if not assessment:
            continue

        ctx = assessment.get("context", {})
        requirements = ", ".join(ctx.get("requirements") or []) or "None declared"
        hazards = ", ".join(ctx.get("hazards") or []) or "None declared"
        workers = assessment.get("workers", [])

        worker_html = []
        for worker in workers:
            obs_text = ", ".join(
                f"{escape(str(o.get('label', '')))} ({float(o.get('confidence', 0)) * 100:.1f}%)"
                for o in worker.get("observations", [])
            ) or "None associated"
            findings_html = "".join(
                f"<li><strong>{escape(str(f.get('ppe_item', '')))}: {escape(str(f.get('status', '')))}</strong>"
                f" — {escape(str(f.get('reasoning', '')))}</li>"
                for f in worker.get("findings", [])
            ) or "<li>No PPE requirements declared for item-level review.</li>"
            worker_html.append(
                f"<div class='worker'><strong>{escape(str(worker.get('id', 'Worker')))} — "
                f"{escape(str(worker.get('status', '')))}</strong> "
                f"(person confidence {float(worker.get('confidence', 0)) * 100:.1f}%)<br>"
                f"<span>Associated observations: {obs_text}</span>"
                f"<ul>{findings_html}</ul></div>"
            )
        if not worker_html:
            worker_html.append("<p>No person was detected in this image.</p>")

        refs_html = "".join(
            f"<li><a href='{escape(str(ref.get('url', '')))}'>{escape(str(ref.get('title', '')))} "
            f"— {escape(str(ref.get('section', '')))}</a> ({escape(str(ref.get('source_organisation', '')))}, "
            f"reviewed {escape(str(ref.get('last_verified', '')))})</li>"
            for ref in assessment.get("references", [])
        ) or "<li>No Great Britain statutory references applied (confirm jurisdiction).</li>"

        blocks.append(
            f"<div class='card'>"
            f"<h3>{filename} — {escape(str(assessment.get('status', 'NOT ASSESSABLE')))}</h3>"
            f"<p>{escape(str(assessment.get('jurisdiction_notice', '')))}</p>"
            f"<p><strong>Declared context:</strong> Jurisdiction={escape(str(ctx.get('jurisdiction', 'unknown')))}; "
            f"Activity={escape(str(ctx.get('activity', 'unknown')))}; "
            f"Source={escape(str(ctx.get('requirement_source', 'site_rule')))}; "
            f"Required PPE={escape(requirements)}; Hazards={escape(hazards)}</p>"
            f"{''.join(worker_html)}"
            f"<p><strong>Potentially relevant references:</strong></p><ul>{refs_html}</ul>"
            f"</div>"
        )

    if not blocks:
        return ""
    return f"<h2>Legislation-Informed Visual Assessment</h2>{''.join(blocks)}"


def generate_html_report(
    audit_data: Dict[str, Any],
    project_name: str = "Construction Site",
    audit_metadata: Optional[Dict[str, Any]] = None,
    results: Optional[List[Dict[str, Any]]] = None,
) -> str:
    meta = _format_metadata(project_name, audit_metadata)
    detection_rows = _collect_detection_rows(audit_data, results)
    show_filename = bool(results)

    rows_html = "".join(
        "<tr>"
        + (f"<td>{escape(str(row['filename']))}</td>" if show_filename else "")
        + f"<td>{escape(str(row['label']))}</td>"
        + f"<td>{row['confidence'] * 100:.1f}%</td>"
        + f"<td>{escape(str(row['bbox']))}</td></tr>"
        for row in detection_rows
    )
    if not rows_html:
        colspan = 4 if show_filename else 3
        rows_html = f"<tr><td colspan='{colspan}'>No objects detected.</td></tr>"

    filename_header = "<th>Image</th>" if show_filename else ""
    assessment_section = _render_html_results_section(results)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Detection Summary</title>
<style>
body{{font-family:Arial,sans-serif;margin:30px;color:#1e293b;line-height:1.5}}
.meta,.card{{border:1px solid #cbd5e1;border-radius:6px;padding:14px;margin:14px 0;background:#f8fafc}}
.worker{{border-top:1px solid #cbd5e1;padding-top:8px;margin-top:8px}}
table{{border-collapse:collapse;width:100%;margin-top:12px}}
th,td{{border:1px solid #cbd5e1;padding:8px;text-align:left}}
th{{background:#f1f5f9}}
</style>
</head><body>
<h1>Construction Safety AI — Detection &amp; Review Summary</h1>
<div class="meta">
  <p><strong>Site:</strong> {escape(meta['site_name'])} |
     <strong>Inspector:</strong> {escape(meta['inspector_name'])} |
     <strong>Audit Date:</strong> {escape(meta['inspection_date'])} |
     <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
  <p>{escape(NOTICE)}</p>
</div>
{assessment_section}
<h2>Model Detections</h2>
<table><thead><tr>{filename_header}<th>Model label</th><th>Confidence</th><th>Bounding box (xyxy)</th></tr></thead>
<tbody>{rows_html}</tbody></table>
</body></html>"""


def generate_pdf_report(
    audit_data: Dict[str, Any],
    project_name: str = "Construction Site",
    audit_metadata: Optional[Dict[str, Any]] = None,
    results: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise ImportError("PDF generation requires reportlab.")

    meta = _format_metadata(project_name, audit_metadata)
    detection_rows = _collect_detection_rows(audit_data, results)
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()

    story = [
        Paragraph("Construction Safety AI — Detection &amp; Review Summary", styles["Title"]),
        Paragraph(
            f"Site: {escape(meta['site_name'])} | "
            f"Inspector: {escape(meta['inspector_name'])} | "
            f"Audit Date: {escape(meta['inspection_date'])}",
            styles["Normal"],
        ),
        Spacer(1, 8),
        Paragraph(escape(NOTICE), styles["Normal"]),
        Spacer(1, 12),
    ]

    if results:
        story.append(Paragraph("Legislation-Informed Visual Assessment", styles["Heading2"]))
        for result in results:
            filename = escape(str(result.get("filename") or "Image"))
            if result.get("error"):
                story.append(Paragraph(f"{filename} — Error: {escape(str(result['error']))}", styles["Normal"]))
                continue
            assessment = result.get("legal_assessment")
            if not assessment:
                continue
            story.append(
                Paragraph(
                    f"<b>{filename}</b> — {escape(str(assessment.get('status', 'NOT ASSESSABLE')))}",
                    styles["Heading3"],
                )
            )
            story.append(Paragraph(escape(str(assessment.get("jurisdiction_notice", ""))), styles["Normal"]))
            workers = assessment.get("workers", [])
            if not workers:
                story.append(Paragraph("No person detected in this image.", styles["Normal"]))
            for worker in workers:
                story.append(
                    Paragraph(
                        f"<b>{escape(str(worker.get('id', 'Worker')))}</b>: {escape(str(worker.get('status', '')))} "
                        f"(confidence {float(worker.get('confidence', 0)) * 100:.1f}%)",
                        styles["Normal"],
                    )
                )
                for finding in worker.get("findings", []):
                    story.append(
                        Paragraph(
                            f"• {escape(str(finding.get('ppe_item', '')))}: "
                            f"{escape(str(finding.get('status', '')))} — {escape(str(finding.get('reasoning', '')))}",
                            styles["Normal"],
                        )
                    )
            story.append(Spacer(1, 8))

    story.append(Paragraph("Model Detections", styles["Heading2"]))
    if not detection_rows:
        story.append(Paragraph("No objects detected.", styles["Normal"]))
    else:
        show_filename = bool(results)
        table_data = [["Image", "Model label", "Confidence", "Bounding box (xyxy)"]] if show_filename else [["Model label", "Confidence", "Bounding box (xyxy)"]]
        for row in detection_rows:
            entry = [
                str(row["label"]),
                f"{row['confidence'] * 100:.1f}%",
                str(row["bbox"]),
            ]
            if show_filename:
                entry.insert(0, str(row["filename"]))
            table_data.append(entry)
        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ])
        )
        story.append(table)

    SimpleDocTemplate(buffer).build(story)
    return buffer.getvalue()
