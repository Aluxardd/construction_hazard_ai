"""
Visualization Engine for PPE Detection & Compliance.
Generates annotated bounding-box imagery with category color coding.
"""

from pathlib import Path
from typing import List, Dict, Any
from PIL import Image, ImageDraw, ImageFont


_FONT_CANDIDATES = (
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:/Windows/Fonts/arial.ttf",
)


def _load_font(font_size: int) -> ImageFont.ImageFont:
    """Load a scalable font across macOS, Linux, and Windows with safe fallback."""
    for font_path in _FONT_CANDIDATES:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, font_size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=font_size)
    except TypeError:
        return ImageFont.load_default()


def annotate_image(image: Image.Image, items: List[Dict[str, Any]]) -> Image.Image:
    """
    Draw bounding boxes and model labels on the image using PIL.
    """
    annotated = image.copy().convert("RGB")
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    font_size = max(14, int(min(w, h) * 0.025))
    font = _load_font(font_size)
    line_width = max(3, int(min(w, h) * 0.005))

    for item in items:
        bbox = item.get("bbox", [])
        if len(bbox) != 4:
            continue

        x1, y1, x2, y2 = bbox
        color = item.get("color", "#808080")
        conf = float(item.get("confidence", 0.0))
        title = item.get("raw_label", item.get("label", "Detection"))

        draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

        label_text = f"{title} ({conf * 100:.1f}%)"
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]

        badge_w = text_w + 12
        badge_h = text_h + 8
        label_x1 = max(0, min(x1, w - badge_w))
        label_x2 = min(w, label_x1 + badge_w)
        label_y1 = max(0, y1 - badge_h)
        label_y2 = min(h, label_y1 + badge_h)

        draw.rectangle([label_x1, label_y1, label_x2, label_y2], fill=color)
        draw.text((label_x1 + 6, label_y1 + 4), label_text, fill="#ffffff", font=font)

    return annotated
