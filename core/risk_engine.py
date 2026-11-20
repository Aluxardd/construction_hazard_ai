"""
Risk Assessment Engine.
Translates detected computer vision objects into formal 5x5 risk matrix scores,
standard OSHA/HSE regulatory references, and actionable safety recommendations.
"""

from typing import Dict, List, Any
import numpy as np
from config import (
    HAZARD_KNOWLEDGE_BASE,
    LIKELIHOOD_LABELS,
    SEVERITY_LABELS,
    get_risk_tier
)

class RiskAssessmentEngine:
    def __init__(self, custom_rules: Dict[str, Any] = None):
        self.rules = dict(HAZARD_KNOWLEDGE_BASE)
        if custom_rules:
            self.rules.update(custom_rules)

    def normalize_label(self, raw_label: str) -> str:
        """
        Normalize detected label string into standard hazard or compliance keys.
        Supports the user's 12 classes:
        ['helmet', 'gloves', 'vest', 'boots', 'goggles', 'Person',
         'no_helmet', 'no_goggle', 'no_gloves', 'no_boots', 'forklift', 'no_vest']
        """
        clean = raw_label.lower().replace("-", "_").replace(" ", "_").strip()

        # 1. Exact Compliant PPE / Personnel detections
        compliant_keys = ["helmet", "gloves", "glove", "vest", "boots", "boot", "goggles", "goggle", "person"]
        if clean in compliant_keys:
            return "compliant"

        # 2. Explicit Hazard Violations
        if clean in ["no_helmet", "no_hard_hat", "without_helmet"]:
            return "no_helmet"
        elif clean in ["no_vest", "no_hi_vis", "without_vest"]:
            return "no_vest"
        elif clean in ["no_boots", "no_boot", "no_safety_boots", "without_boots"]:
            return "no_boots"
        elif clean in ["no_gloves", "no_glove", "without_gloves"]:
            return "no_gloves"
        elif clean in ["no_goggle", "no_goggles", "without_goggles"]:
            return "no_goggle"
        elif clean in ["forklift", "fork_lift"]:
            return "forklift"
        elif any(w in clean for w in ["guardrail", "edge", "fall_hazard", "unguarded"]):
            return "missing_guardrail"
        elif any(w in clean for w in ["scaffold", "scaffolding"]):
            return "unsafe_scaffold"
        elif any(w in clean for w in ["ladder"]):
            return "unsafe_ladder"
        elif any(w in clean for w in ["harness"]):
            return "no_harness"
        elif any(w in clean for w in ["trip", "slip", "debris", "housekeeping"]):
            return "trip_hazard"

        # Direct dictionary match
        if clean in self.rules:
            return clean

        return "default_hazard"

    def evaluate_hazard(self, detection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single detected object box and enriches with risk assessment metadata.
        """
        raw_label = detection.get("label", "unknown")
        confidence = float(detection.get("confidence", 0.0))
        bbox = detection.get("bbox", [])

        clean = raw_label.lower().replace("-", "_").replace(" ", "_").strip()
        norm_key = self.normalize_label(raw_label)
        
        # If compliant PPE item or personnel
        if norm_key == "compliant":
            compliant_descriptions = {
                "helmet": "Compliant: Wearing Hard Hat",
                "vest": "Compliant: Wearing Hi-Vis Vest",
                "boots": "Compliant: Wearing Safety Boots",
                "boot": "Compliant: Wearing Safety Boots",
                "gloves": "Compliant: Wearing Protective Gloves",
                "glove": "Compliant: Wearing Protective Gloves",
                "goggles": "Compliant: Wearing Eye Protection",
                "goggle": "Compliant: Wearing Eye Protection",
                "person": "Site Personnel / Worker Observed"
            }
            title = compliant_descriptions.get(clean, f"Compliant: {raw_label.title()}")
            return {
                "raw_label": raw_label,
                "normalized_key": "compliant",
                "is_hazard": False,
                "confidence": confidence,
                "bbox": bbox,
                "title": title,
                "category": "Safety Adherence",
                "likelihood": 1,
                "likelihood_label": "Rare",
                "severity": 1,
                "severity_label": "Negligible",
                "risk_score": 1,
                "risk_tier": "Compliant",
                "color": "#28a745",
                "text_color": "#ffffff",
                "action_priority": "Maintained Standard",
                "timeframe": "N/A",
                "standard_ref": "Standard Compliant",
                "recommendation": "Safety equipment present and compliant with site standards."
            }

        rule = self.rules.get(norm_key, self.rules["default_hazard"])

        # Default Likelihood & Severity from rule
        likelihood = rule["default_likelihood"]
        severity = rule["default_severity"]

        # Calculate Risk Score (1 to 25)
        risk_score = likelihood * severity
        tier_info = get_risk_tier(risk_score)

        return {
            "raw_label": raw_label,
            "normalized_key": norm_key,
            "is_hazard": True,
            "confidence": confidence,
            "bbox": bbox,
            "title": rule["title"],
            "category": rule["category"],
            "likelihood": likelihood,
            "likelihood_label": LIKELIHOOD_LABELS.get(likelihood, ""),
            "severity": severity,
            "severity_label": SEVERITY_LABELS.get(severity, ""),
            "risk_score": risk_score,
            "risk_tier": tier_info["tier"],
            "color": tier_info["color"],
            "text_color": tier_info["text_color"],
            "action_priority": tier_info["action_priority"],
            "timeframe": tier_info["timeframe"],
            "standard_ref": rule["standard_ref"],
            "recommendation": rule["recommendation"]
        }

    def assess_batch(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess a batch of detections from one or more images.
        Computes 5x5 matrix frequency grid, compliance rate, and aggregate safety metrics.
        """
        evaluated_all = []
        evaluated_hazards = []
        compliant_count = 0
        person_count = 0

        # 5x5 frequency matrix: rows = severity (1-5), cols = likelihood (1-5)
        matrix_counts = np.zeros((5, 5), dtype=int)

        tier_counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }

        for det in detections:
            eval_result = self.evaluate_hazard(det)
            evaluated_all.append(eval_result)

            if eval_result.get("is_hazard", False):
                evaluated_hazards.append(eval_result)
                s = eval_result["severity"]
                l = eval_result["likelihood"]
                matrix_counts[s - 1][l - 1] += 1
                tier = eval_result["risk_tier"]
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            else:
                if eval_result.get("raw_label", "").lower() == "person":
                    person_count += 1
                else:
                    compliant_count += 1

        total_hazards = len(evaluated_hazards)
        total_ppe_observations = compliant_count + total_hazards
        compliance_rate = (compliant_count / total_ppe_observations * 100) if total_ppe_observations > 0 else 100.0

        # Overall Site Risk Determination
        if tier_counts["Critical"] > 0:
            overall_site_risk = "Critical"
            overall_color = "#dc3545"
            summary_statement = "Immediate safety intervention required! Critical life-safety hazards detected on site."
        elif tier_counts["High"] > 0:
            overall_site_risk = "High"
            overall_color = "#fd7e14"
            summary_statement = "High risk conditions detected. Urgent mitigation actions required before continuing work."
        elif tier_counts["Medium"] > 0:
            overall_site_risk = "Medium"
            overall_color = "#ffc107"
            summary_statement = "Moderate safety deviations identified. Remediate hazards within the current work shift."
        elif total_hazards > 0:
            overall_site_risk = "Low"
            overall_color = "#28a745"
            summary_statement = "Low risk site conditions. Maintain standard safety supervision and monitoring."
        else:
            overall_site_risk = "Compliant / Clear"
            overall_color = "#28a745"
            summary_statement = "All detected personnel are fully compliant with mandatory site PPE requirements."

        return {
            "total_hazards": total_hazards,
            "compliant_count": compliant_count,
            "person_count": person_count,
            "compliance_rate": round(compliance_rate, 1),
            "all_items": evaluated_all,
            "hazards": evaluated_hazards,
            "matrix_counts": matrix_counts.tolist(),
            "tier_counts": tier_counts,
            "overall_site_risk": overall_site_risk,
            "overall_color": overall_color,
            "summary_statement": summary_statement
        }
