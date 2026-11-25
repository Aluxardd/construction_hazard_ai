"""Shared detection label normalization across detection, risk assessment, and legal review."""

PPE_LABELS = frozenset({"helmet", "gloves", "vest", "boots", "goggles"})
VEHICLE_HAZARD_LABELS = frozenset({"forklift"})

_NEGATIVE_ALIASES = {
    "no_hard_hat": "no_helmet",
    "no_hardhat": "no_helmet",
    "no_hi_vis": "no_vest",
    "no_safety_vest": "no_vest",
    "no_glove": "no_gloves",
    "no_boot": "no_boots",
    "no_goggles": "no_goggle",
    "no_safety_glasses": "no_goggle",
}


def normalize_detection_label(raw_label: str) -> str:
    """Normalize raw model class labels into canonical project keys."""
    clean = (raw_label or "").lower().replace("-", "_").replace(" ", "_").strip()
    if not clean:
        return "unknown"

    if clean.startswith("no_"):
        return _NEGATIVE_ALIASES.get(clean, clean)

    if "person" in clean or "worker" in clean:
        return "person"
    if "helmet" in clean or "hard_hat" in clean or "hardhat" in clean:
        return "helmet"
    if "vest" in clean or "hi_vis" in clean:
        return "vest"
    if "boot" in clean:
        return "boots"
    if "glove" in clean:
        return "gloves"
    if "goggle" in clean or "safety_glass" in clean:
        return "goggles"
    if "forklift" in clean:
        return "forklift"
    return "unknown"


def classify_detection_type(raw_label: str) -> str:
    """Classify a raw label into coarse detection categories."""
    normalized = normalize_detection_label(raw_label)
    if normalized == "person":
        return "worker"
    if normalized.startswith("no_"):
        return "missing_ppe"
    if normalized in PPE_LABELS:
        return "ppe_item"
    if normalized in VEHICLE_HAZARD_LABELS:
        return "vehicle_hazard"
    return "object"
