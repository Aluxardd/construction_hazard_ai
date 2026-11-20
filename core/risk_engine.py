"""
PPE Compliance Assessment Engine.
Translates detected computer vision objects into PPE compliance scores
and actionable safety recommendations aligned with OSHA/HSE standards.
"""

from typing import Dict, List, Any
import numpy as np
from config import (
    PPE_KNOWLEDGE_BASE,
    PPE_ITEMS,
    calculate_ppe_compliance,
    get_compliance_status,
    DEFAULT_HAZARD_PROFILE
)

class RiskAssessmentEngine:
    def __init__(self, custom_rules: Dict[str, Any] = None):
        self.rules = dict(PPE_KNOWLEDGE_BASE)
        if custom_rules:
            self.rules.update(custom_rules)

    def normalize_label(self, raw_label: str) -> str:
        """
        Normalize detected label string into standard PPE keys.
        Supports PPE classes: ['helmet', 'gloves', 'vest', 'boots', 'goggles', 'person']
        """
        clean = raw_label.lower().replace("-", "_").replace(" ", "_").strip()
        if clean.startswith("no_"):
            return clean

        # PPE items - all positive detections
        ppe_keys = ["helmet", "hard_hat", "gloves", "glove", "vest", "hi_vis", "boots", "boot", "goggles", "goggle", "person", "worker"]
        if any(key in clean for key in ppe_keys):
            if "helmet" in clean or "hard_hat" in clean:
                return "helmet"
            elif "vest" in clean or "hi_vis" in clean:
                return "vest"
            elif "boot" in clean:
                return "boots"
            elif "glove" in clean:
                return "gloves"
            elif "goggle" in clean:
                return "goggles"
            elif "person" in clean or "worker" in clean:
                return "person"

        return "unknown"

    def evaluate_ppe_item(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single detected PPE item and enriches with compliance metadata.
        """
        raw_label = detection.get("label", "unknown")
        confidence = float(detection.get("confidence", 0.0))
        bbox = detection.get("bbox", [])

        norm_key = self.normalize_label(raw_label)
        
        # Check if this is a known PPE item
        if norm_key in PPE_KNOWLEDGE_BASE:
            rule = PPE_KNOWLEDGE_BASE[norm_key]
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
                "color": "#28a745",  # Green for detected PPE
                "text_color": "#ffffff"
            }
        elif norm_key == "person":
            return {
                "raw_label": raw_label,
                "normalized_key": "person",
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": "Site Personnel / Worker Observed",
                "category": "Worker Detection",
                "is_required": False,
                "color": "#0066cc",  # Blue for worker
                "text_color": "#ffffff"
            }
        elif norm_key.startswith("no_"):
            return {
                "raw_label": raw_label,
                "normalized_key": norm_key,
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": raw_label,
                "category": "Model flag - review required",
                "color": "#dc3545",
                "text_color": "#ffffff"
            }
        else:
            return {
                "raw_label": raw_label,
                "normalized_key": "unknown",
                "is_ppe_item": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": f"Unclassified Detection: {raw_label}",
                "category": "Unknown",
                "color": "#808080",  # Gray for unknown
                "text_color": "#ffffff"
            }

    def assess_batch(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess a batch of PPE detections from one or more images.
        Computes compliance rate, identified gaps, and aggregate safety metrics.
        """
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

        # Calculate PPE compliance from detections
        compliance = calculate_ppe_compliance(detections)

        # Determine overall site compliance status
        compliance_status = compliance["status"]

        # Aggregate statistics
        total_detections = len(evaluated_all)
        total_ppe = len(ppe_items)
        total_workers = len(workers)

        return {
            "total_detections": total_detections,
            "total_ppe_items": total_ppe,
            "total_workers": total_workers,
            "compliance_rate": compliance["compliance_rate"],
            "detected_items": compliance["detected_items"],
            "missing_items": compliance["missing_items"],
            "compliance_status": compliance_status,
            "all_items": evaluated_all,
            "ppe_items": ppe_items,
            "workers": workers,
            "summary_statement": compliance_status["message"],
            "overall_color": compliance_status["color"],
            "total_hazards": None,
            "compliant_count": None
        }
