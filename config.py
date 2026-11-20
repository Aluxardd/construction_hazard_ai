"""
Configuration settings for PPE (Personal Protective Equipment) Detection & Compliance.
Focuses exclusively on identifying safety equipment worn by construction workers.
Aligned with OSHA 1926 regulations and international safety standards.
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

# PPE Compliance Score (0-100 scale)
# Based on number of detections vs. expected PPE items
PPE_ITEMS = ["helmet", "gloves", "vest", "boots", "goggles"]
TOTAL_PPE_ITEMS = len(PPE_ITEMS)

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
            "message": "Detections require human review; they do not establish compliance."
        }
    }

def get_compliance_status(rate: float) -> dict:
    """Determine compliance status based on completion rate."""
    if rate >= 100:
        return {
            "level": "COMPLIANT",
            "color": "#28a745",  # Green
            "text_color": "#ffffff",
            "message": "All required PPE detected"
        }
    elif rate >= 80:
        return {
            "level": "ACCEPTABLE",
            "color": "#ffc107",  # Yellow
            "text_color": "#212529",
            "message": "Most PPE detected - review missing items"
        }
    elif rate >= 50:
        return {
            "level": "WARNINGS",
            "color": "#fd7e14",  # Orange
            "text_color": "#ffffff",
            "message": "Multiple PPE items missing - compliance required"
        }
    else:
        return {
            "level": "NON-COMPLIANT",
            "color": "#dc3545",  # Red
            "text_color": "#ffffff",
            "message": "Critical PPE deficiencies detected"
        }

# PPE Knowledge Base with Compliance Standards
PPE_KNOWLEDGE_BASE = {
    "helmet": {
        "title": "Hard Hat / Head Protection",
        "category": "Head Protection",
        "is_required": True,
        "standard_ref": "OSHA 1926.100(a) / BS EN 397",
        "description": "Protects against head injuries from falling objects and bumps.",
        "compliance_weight": 20,
        "recommendation": "Must be an approved ANSI Z89.1 / EN 397 Type I or II helmet in good condition."
    },
    "vest": {
        "title": "High-Visibility Safety Vest",
        "category": "Visibility Protection",
        "is_required": True,
        "standard_ref": "OSHA 1926.201 / ISO 20471 Class 2",
        "description": "Ensures worker visibility around mobile plant and vehicles.",
        "compliance_weight": 20,
        "recommendation": "Must be fluorescent with retroreflective stripes, minimum ISO 20471 Class 2."
    },
    "boots": {
        "title": "Protective Safety Footwear",
        "category": "Foot Protection",
        "is_required": True,
        "standard_ref": "OSHA 1926.96 / ASTM F2413 / EN ISO 20345",
        "description": "Protects feet from crushing, puncture, and electrical hazards.",
        "compliance_weight": 20,
        "recommendation": "Must be steel-toe, puncture-resistant footwear meeting S3 standard."
    },
    "gloves": {
        "title": "Hand Protection (Gloves)",
        "category": "Hand Protection",
        "is_required": True,
        "standard_ref": "OSHA 1926.95 / BS EN 388",
        "description": "Protects hands from cuts, abrasions, and chemical exposure.",
        "compliance_weight": 20,
        "recommendation": "Task-matched cut-resistant (Level D/E) or chemical-resistant protective gloves."
    },
    "goggles": {
        "title": "Eye & Face Protection (Goggles/Safety Glasses)",
        "category": "Eye Protection",
        "is_required": True,
        "standard_ref": "OSHA 1926.102 / ANSI Z87.1 / EN 166",
        "description": "Protects eyes from debris, dust, and chemical splashes.",
        "compliance_weight": 20,
        "recommendation": "Must be ANSI Z87.1 certified for impact resistance and UV protection."
    }
}

# Default Risk Assessment (applies to PPE compliance violations)
DEFAULT_HAZARD_PROFILE = {
    "title": "PPE Non-Compliance",
    "category": "Personal Protective Equipment Violation",
    "default_likelihood": 4,
    "default_severity": 4,
    "standard_ref": "OSHA General Duty Clause / OSH Act Section 5(a)(1)",
    "recommendation": "Worker does not have all required PPE equipped. Provide immediate instruction and equipment before allowing work to continue."
}
