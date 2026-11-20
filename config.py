"""
Configuration settings for Construction Site AI Hazard Identification & Risk Assessment.
Aligned with BSc (Hons) Research Proposal (University of Bolton / Regent College London).
Tailored for the trained YOLOv8 model classes:
['helmet', 'gloves', 'vest', 'boots', 'goggles', 'Person', 'no_helmet', 'no_goggle', 'no_gloves', 'no_boots', 'forklift', 'no_vest']
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

# 5x5 Risk Assessment Matrix Definitions
# Likelihood scale: 1 (Rare) to 5 (Almost Certain)
LIKELIHOOD_LABELS = {
    1: "Rare",
    2: "Unlikely",
    3: "Possible",
    4: "Likely",
    5: "Almost Certain"
}

# Severity scale: 1 (Negligible) to 5 (Catastrophic)
SEVERITY_LABELS = {
    1: "Negligible (First aid)",
    2: "Minor (Medical aid)",
    3: "Moderate (Lost time / Fracture)",
    4: "Major (Disability / Severe injury)",
    5: "Catastrophic (Fatality / Mass collapse)"
}

# Risk Rating Bands (Score = Likelihood x Severity, range 1 - 25)
def get_risk_tier(score: int) -> dict:
    if score >= 15:
        return {
            "tier": "Critical",
            "color": "#dc3545",  # Red
            "text_color": "#ffffff",
            "action_priority": "Immediate Work Stoppage",
            "timeframe": "Instant resolution required before any work continues."
        }
    elif score >= 10:
        return {
            "tier": "High",
            "color": "#fd7e14",  # Orange
            "text_color": "#ffffff",
            "action_priority": "Urgent Rectification",
            "timeframe": "Remedy within 1 hour; restrict access to danger zone."
        }
    elif score >= 5:
        return {
            "tier": "Medium",
            "color": "#ffc107",  # Yellow
            "text_color": "#212529",
            "action_priority": "Remedial Action",
            "timeframe": "Rectify within the current working shift."
        }
    else:
        return {
            "tier": "Low",
            "color": "#28a745",  # Green
            "text_color": "#ffffff",
            "action_priority": "Routine Monitoring",
            "timeframe": "Address during scheduled maintenance and toolbox talks."
        }

# Hazard Rule-Based Knowledge Base
# Aligned with OSHA 29 CFR 1926 & UK Health and Safety Executive (HSE)
HAZARD_KNOWLEDGE_BASE = {
    "no_helmet": {
        "title": "Missing Hard Hat / Head Protection",
        "category": "Head Protection Violation",
        "default_likelihood": 4,
        "default_severity": 4,
        "standard_ref": "OSHA 1926.100(a) / BS EN 397",
        "recommendation": "Worker observed without hard hat. Immediately suspend worker from active site zone until an approved ANSI Z89.1 / EN 397 Type I/II protective helmet is issued and equipped."
    },
    "no_vest": {
        "title": "Missing High-Visibility Safety Vest",
        "category": "Struck-by / Visibility Hazard",
        "default_likelihood": 3,
        "default_severity": 3,
        "standard_ref": "OSHA 1926.201 / ISO 20471 Class 2",
        "recommendation": "Worker not wearing high-visibility apparel. Equip with fluorescent, retroreflective class 2 or class 3 vest, mandatory around mobile plant and vehicle traffic corridors."
    },
    "no_boots": {
        "title": "Missing Protective Safety Footwear",
        "category": "Foot Protection Violation",
        "default_likelihood": 3,
        "default_severity": 3,
        "standard_ref": "OSHA 1926.96 / ASTM F2413 / EN ISO 20345",
        "recommendation": "Worker lacks safety boots. Mandatory steel-toe, puncture-resistant footwear (S3 standard) must be equipped before allowing entry into active construction zones."
    },
    "no_gloves": {
        "title": "Missing Hand Protection (Gloves)",
        "category": "Hand Protection Violation",
        "default_likelihood": 3,
        "default_severity": 2,
        "standard_ref": "OSHA 1926.95 / BS EN 388",
        "recommendation": "Worker handling materials without hand protection. Provide task-matched cut-resistant (Level D/E) or chemical-resistant protective safety gloves."
    },
    "no_goggle": {
        "title": "Missing Eye & Face Protection (Goggles)",
        "category": "Eye & Face Protection Violation",
        "default_likelihood": 3,
        "default_severity": 3,
        "standard_ref": "OSHA 1926.102 / ANSI Z87.1 / EN 166",
        "recommendation": "Worker observed without eye protection. Issue ANSI Z87.1 certified safety glasses/goggles to protect against airborne debris, dust, and chemical splashes."
    },
    "forklift": {
        "title": "Active Mobile Plant (Forklift in Zone)",
        "category": "Plant & Pedestrian Interface",
        "default_likelihood": 2,
        "default_severity": 4,
        "standard_ref": "OSHA 1910.178 / LOLER 1998",
        "recommendation": "Mobile plant operating in vicinity. Ensure strict pedestrian-vehicle segregation, check working reverse alarms, and verify operator certification."
    },
    "missing_guardrail": {
        "title": "Missing Guardrail / Unguarded Edge",
        "category": "Fall Hazard",
        "default_likelihood": 3,
        "default_severity": 5,
        "standard_ref": "OSHA 1926.502 / HSE Guardrail Specs",
        "recommendation": "Barricade edge immediately. Install compliant guardrail system with top rail (42±3 inches), mid-rail (21 inches), and 3.5-inch toeboard."
    },
    "unsafe_scaffold": {
        "title": "Improper / Unsafe Scaffolding",
        "category": "Access & Structures",
        "default_likelihood": 3,
        "default_severity": 5,
        "standard_ref": "OSHA 1926.451 / BS EN 12811",
        "recommendation": "Red-tag scaffold as 'UNSAFE - DO NOT USE'. Inspect base plates, screw jacks, cross bracing, and building tie-ins with certified scaffolding inspector."
    },
    "unsafe_ladder": {
        "title": "Unsafe Ladder / Improper Angle",
        "category": "Access Equipment",
        "default_likelihood": 4,
        "default_severity": 4,
        "standard_ref": "OSHA 1926.1053",
        "recommendation": "Re-position ladder to 4:1 slope ratio (75° angle). Tie off top rungs, extend rails 3ft above landing, and maintain 3-point contact."
    },
    "no_harness": {
        "title": "No Safety Harness / Fall Arrest System",
        "category": "Working at Height",
        "default_likelihood": 4,
        "default_severity": 5,
        "standard_ref": "OSHA 1926.501(b)(1) / WAHR 2005",
        "recommendation": "Halt work at height immediately. Equip full-body harness with shock-absorbing lanyard secured to certified 5,000 lbs anchorage point."
    },
    "trip_hazard": {
        "title": "Poor Housekeeping / Obstruction",
        "category": "General Site Safety",
        "default_likelihood": 4,
        "default_severity": 2,
        "standard_ref": "OSHA 1926.25",
        "recommendation": "Clear walk corridors, elevate trailing power cables, and remove trip hazards and construction debris."
    },
    "default_hazard": {
        "title": "Unclassified Construction Hazard",
        "category": "General Site Hazard",
        "default_likelihood": 3,
        "default_severity": 3,
        "standard_ref": "OSHA General Duty Clause Sec 5(a)(1)",
        "recommendation": "Conduct on-site dynamic risk assessment with the appointed site safety supervisor before continuing work."
    }
}
