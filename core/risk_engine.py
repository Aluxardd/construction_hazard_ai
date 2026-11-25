"""
PPE Compliance Assessment Engine.
Normalizes detected computer vision objects and prepares structured summaries
for human review without asserting automated compliance.
"""

from typing import Dict, List, Any
from config import PPE_KNOWLEDGE_BASE, calculate_ppe_compliance
from core.label_mapping import normalize_detection_label


class RiskAssessmentEngine:
    def __init__(self, custom_rules: Dict[str, Any] = None):
        self.rules = dict(PPE_KNOWLEDGE_BASE)
        if custom_rules:
            self.rules.update(custom_rules)

    def normalize_label(self, raw_label: str) -> str:
        """Normalize detected label string into canonical project keys."""
        return normalize_detection_label(raw_label)

    def evaluate_ppe_item(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single detected object and enrich it with review metadata."""
        raw_label = detection.get("label", "unknown")
        confidence = float(detection.get("confidence", 0.0))
        bbox = detection.get("bbox", [])

        norm_key = self.normalize_label(raw_label)

        if norm_key in self.rules:
            rule = self.rules[norm_key]
            return {
                "raw_label": raw_label,
                "normalized_key": norm_key,
                "is_ppe_item": True,
                "confidence": confidence,
                "bbox": bbox,
                "title": rule["title"],
                "category": rule["category"],
                "standard_ref": None,
                "description": rule["description"],
                "compliance_weight": None,
                "is_required": None,
                "recommendation": "Verify suitability and requirements against the applicable risk assessment.",
                "color": "#28a745",
                "text_color": "#ffffff",
            }
        if norm_key == "person":
            return {
                "raw_label": raw_label,
                "normalized_key": "person",
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": "Site Personnel / Worker Observed",
                "category": "Worker Detection",
                "is_required": False,
                "color": "#0066cc",
                "text_color": "#ffffff",
            }
        if norm_key == "forklift":
            return {
                "raw_label": raw_label,
                "normalized_key": "forklift",
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": "Mobile Plant / Forklift Observed",
                "category": "Vehicle / Struck-By Hazard",
                "recommendation": "Verify pedestrian segregation, traffic routes, and visibility controls around mobile plant.",
                "color": "#f59e0b",
                "text_color": "#1e293b",
            }
        if norm_key.startswith("no_"):
            return {
                "raw_label": raw_label,
                "normalized_key": norm_key,
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": raw_label,
                "category": "Model flag - review required",
                "color": "#dc3545",
                "text_color": "#ffffff",
            }
        return {
            "raw_label": raw_label,
            "normalized_key": "unknown",
            "is_ppe_item": False,
            "confidence": confidence,
            "bbox": bbox,
            "title": f"Unclassified Detection: {raw_label}",
            "category": "Unknown",
            "color": "#808080",
            "text_color": "#ffffff",
        }

    def assess_batch(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate evaluated detections from one or more images."""
        evaluated_all = []
        ppe_items = []
        workers = []

        for det in detections:
            eval_result = self.evaluate_ppe_item(det)
            evaluated_all.append(eval_result)

            if eval_result.get("is_ppe_item", False):
                ppe_items.append(eval_result)
            elif eval_result.get("normalized_key") == "person":
                workers.append(eval_result)

        compliance = calculate_ppe_compliance(detections)
        compliance_status = compliance["status"]

        return {
            "total_detections": len(evaluated_all),
            "total_ppe_items": len(ppe_items),
            "total_workers": len(workers),
            "compliance_rate": compliance["compliance_rate"],
            "detected_items": compliance["detected_items"],
            "missing_items": compliance["missing_items"],
            "compliance_status": compliance_status,
            "all_items": evaluated_all,
            "ppe_items": ppe_items,
            "workers": workers,
            "summary_statement": compliance_status["message"],
            "overall_color": compliance_status["color"],
        }
