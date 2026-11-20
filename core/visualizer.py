"""
Visualization Engine for PPE Detection & Compliance.
Generates:
1. Annotated bounding box imagery with compliance-tier color coding.
2. Publication-grade compliance assessment visualizations.
"""

from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io

def annotate_image(image: Image.Image, items: List[Dict[str, Any]]) -> Image.Image:
    """
    Draws bounding boxes and PPE compliance labels on the image using PIL.
    Color codes by PPE item type (Green=PPE, Blue=Worker, Gray=Unknown).
    """
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    # Try to load a reasonable font, or fallback to default
    try:
        font_size = max(14, int(min(w, h) * 0.025))
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except Exception:
        font = ImageFont.load_default()

    for item in items:
        bbox = item.get("bbox", [])
        if len(bbox) != 4:
            continue
        
        x1, y1, x2, y2 = bbox
        color = item.get("color", "#808080")
        conf = item.get("confidence", 0.0)
        title = item.get("title", item.get("raw_label", "Detection"))
        normalized_key = item.get("normalized_key", "unknown")

        # Draw thick rectangle
        line_width = max(3, int(min(w, h) * 0.005))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        # Format label text
        if item.get("is_ppe_item", False):
            label_text = f"✓ {title} ({int(conf * 100)}%)"
        elif normalized_key == "person":
            label_text = f"👤 Worker ({int(conf * 100)}%)"
        else:
            label_text = f"? {title} ({int(conf * 100)}%)"

        # Calculate text bounding box
        text_bbox = draw.textbbox((x1, y1), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        # Draw label background badge
        label_y1 = max(0, y1 - text_h - 8)
        label_y2 = label_y1 + text_h + 8
        label_x2 = min(w, x1 + text_w + 12)

        draw.rectangle([x1, label_y1, label_x2, label_y2], fill=color)
        draw.text((x1 + 6, label_y1 + 4), label_text, fill="#ffffff", font=font)

    return annotated


def generate_risk_matrix_plot(matrix_counts: List[List[int]] = None) -> plt.Figure:
    """
    Generates a compliance visualization (placeholder for compatibility).
    For PPE detection, compliance is tracked via compliance_rate metric.
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)
    
    # Simple compliance message visualization
    ax.text(0.5, 0.5, "PPE Compliance Assessment", 
            ha='center', va='center', fontsize=16, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.5, 0.4, "See compliance score and detailed analysis above", 
            ha='center', va='center', fontsize=12,
            transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    return fig
