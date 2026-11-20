"""
Visualization Engine for Construction Site Safety AI.
Generates:
1. Annotated bounding box imagery with risk-tier color coding.
2. Publication-grade 5x5 Risk Assessment Matrix heatmaps with overlaid hazard counts.
"""

from typing import List, Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io

from config import (
    LIKELIHOOD_LABELS,
    SEVERITY_LABELS,
    get_risk_tier
)

def annotate_image(image: Image.Image, hazards: List[Dict[str, Any]]) -> Image.Image:
    """
    Draws bounding boxes and risk status labels on the image using PIL.
    Color codes by hazard severity tier (Red=Critical, Orange=High, Yellow=Medium, Green=Low).
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

    for item in hazards:
        bbox = item.get("bbox", [])
        if len(bbox) != 4:
            continue
        
        x1, y1, x2, y2 = bbox
        color = item.get("color", "#dc3545")
        tier = item.get("risk_tier", "Hazard")
        conf = item.get("confidence", 0.0)
        title = item.get("title", item.get("raw_label", "Hazard"))
        score = item.get("risk_score", 0)

        # Draw thick rectangle
        line_width = max(3, int(min(w, h) * 0.005))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        # Format label text
        if not item.get("is_hazard", False):
            label_text = f"✔ {title} ({int(conf * 100)}%)"
        else:
            label_text = f"⚠ [{tier.upper()} | Score: {score}] {title} ({int(conf * 100)}%)"

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


def generate_risk_matrix_plot(matrix_counts: List[List[int]]) -> plt.Figure:
    """
    Generates an academic-grade 5x5 Risk Assessment Matrix with cell counts.
    X-axis: Likelihood (1 - 5)
    Y-axis: Severity (1 - 5)
    """
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)

    # 5x5 grid background colors based on score = Likelihood * Severity
    # Y is severity (1 bottom, 5 top), X is likelihood (1 left, 5 right)
    for s_idx in range(5):  # 0 to 4 (representing severity 1 to 5)
        for l_idx in range(5):  # 0 to 4 (representing likelihood 1 to 5)
            s_val = s_idx + 1
            l_val = l_idx + 1
            score = s_val * l_val
            tier_info = get_risk_tier(score)
            bg_color = tier_info["color"]

            # Draw cell rectangle
            rect = patches.Rectangle(
                (l_idx, s_idx), 1, 1,
                linewidth=1.2,
                edgecolor="#ffffff",
                facecolor=bg_color,
                alpha=0.82
            )
            ax.add_patch(rect)

            # Cell text: show Risk Score in top corner, and count of detected hazards in center
            count = matrix_counts[s_idx][l_idx] if matrix_counts else 0

            # Score badge in top-left of cell
            ax.text(
                l_idx + 0.12, s_idx + 0.85, f"{score}",
                fontsize=8, fontweight="bold",
                color=tier_info["text_color"], alpha=0.85,
                va="center", ha="left"
            )

            # Hazard count badge in center if count > 0
            if count > 0:
                ax.text(
                    l_idx + 0.5, s_idx + 0.48, f"{count} hazard{'s' if count > 1 else ''}",
                    fontsize=10, fontweight="black",
                    color="#ffffff" if tier_info["tier"] != "Medium" else "#000000",
                    va="center", ha="center",
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="#111111", alpha=0.65, edgecolor="#ffffff")
                )

    # Configure axes
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 5)

    likelihood_ticks = [f"{i}\n{LIKELIHOOD_LABELS[i]}" for i in range(1, 6)]
    severity_ticks = [f"{i}\n{SEVERITY_LABELS[i].split(' ')[0]}" for i in range(1, 6)]

    ax.set_xticks(np.arange(5) + 0.5)
    ax.set_xticklabels(likelihood_ticks, fontsize=9, fontweight="medium")
    ax.set_xlabel("Likelihood (Probability)", fontsize=11, fontweight="bold", labelpad=10)

    ax.set_yticks(np.arange(5) + 0.5)
    ax.set_yticklabels(severity_ticks, fontsize=9, fontweight="medium")
    ax.set_ylabel("Severity (Impact Consequence)", fontsize=11, fontweight="bold", labelpad=10)

    ax.set_title("5×5 Construction Risk Assessment Matrix", fontsize=13, fontweight="bold", pad=15)

    # Add legend at bottom
    legend_patches = [
        patches.Patch(facecolor="#28a745", label="Low (1-4)"),
        patches.Patch(facecolor="#ffc107", label="Medium (5-9)"),
        patches.Patch(facecolor="#fd7e14", label="High (10-14)"),
        patches.Patch(facecolor="#dc3545", label="Critical (15-25)")
    ]
    ax.legend(handles=legend_patches, loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=4, frameon=False, fontsize=9)

    plt.tight_layout()
    return fig
