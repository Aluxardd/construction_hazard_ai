"""
Configuration settings for PPE (Personal Protective Equipment) Detection & Review.
Model classes are read from the loaded checkpoint.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
WEIGHTS_DIR = MODELS_DIR / "weights"
DEFAULT_MODEL_PATH = WEIGHTS_DIR / "best.pt"

# Default Inference Parameters
DEFAULT_CONFIDENCE = 0.30
DEFAULT_IOU_THRESHOLD = 0.45

# Supported positive PPE classes
PPE_ITEMS = ["helmet", "gloves", "vest", "boots", "goggles"]


def calculate_ppe_compliance(detections: list) -> dict:
    """Summarize positive detections without inferring compliance from absence."""
    detected_ppe = {d.get("label", "").lower() for d in detections} & set(PPE_ITEMS)
    return {
        "compliance_rate": None,
        "detected_items": sorted(detected_ppe),
        "missing_items": [],
        "status": {
            "level": "NOT ASSESSED",
            "color": "#64748b",
            "text_color": "#ffffff",
            "message": "Detections require human review; they do not establish compliance.",
        },
    }


# PPE Knowledge Base (descriptive metadata; applicability depends on site context)
PPE_KNOWLEDGE_BASE = {
    "helmet": {
        "title": "Hard Hat / Head Protection",
        "category": "Head Protection",
        "description": "Protects against head injuries from falling objects and bumps.",
    },
    "vest": {
        "title": "High-Visibility Safety Vest",
        "category": "Visibility Protection",
        "description": "Ensures worker visibility around mobile plant and vehicles.",
    },
    "boots": {
        "title": "Protective Safety Footwear",
        "category": "Foot Protection",
        "description": "Protects feet from crushing, puncture, and electrical hazards.",
    },
    "gloves": {
        "title": "Hand Protection (Gloves)",
        "category": "Hand Protection",
        "description": "Protects hands from cuts, abrasions, and chemical exposure.",
    },
    "goggles": {
        "title": "Eye & Face Protection (Goggles/Safety Glasses)",
        "category": "Eye Protection",
        "description": "Protects eyes from debris, dust, and chemical splashes.",
    },
}
