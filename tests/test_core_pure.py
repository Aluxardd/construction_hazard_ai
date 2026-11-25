import unittest

from core.label_mapping import classify_detection_type, normalize_detection_label
from core.report_generator import generate_html_report
from core.risk_engine import RiskAssessmentEngine


class LabelMappingTests(unittest.TestCase):
    def test_normalizes_positive_negative_and_vehicle_labels(self):
        self.assertEqual(normalize_detection_label("hard_hat"), "helmet")
        self.assertEqual(normalize_detection_label("hi-vis vest"), "vest")
        self.assertEqual(normalize_detection_label("no_goggles"), "no_goggle")
        self.assertEqual(normalize_detection_label("forklift"), "forklift")
        self.assertEqual(normalize_detection_label("Person"), "person")

        self.assertEqual(classify_detection_type("forklift"), "vehicle_hazard")
        self.assertEqual(classify_detection_type("no_helmet"), "missing_ppe")
        self.assertEqual(classify_detection_type("helmet"), "ppe_item")
        self.assertEqual(classify_detection_type("Person"), "worker")


class RiskEngineTests(unittest.TestCase):
    def test_forklift_is_classified_as_vehicle_hazard(self):
        item = RiskAssessmentEngine().evaluate_ppe_item(
            {"label": "forklift", "confidence": 0.88, "bbox": [10, 20, 100, 120]}
        )
        self.assertEqual(item["normalized_key"], "forklift")
        self.assertEqual(item["category"], "Vehicle / Struck-By Hazard")
        self.assertFalse(item["is_ppe_item"])

    def test_custom_rules_override_default_ppe_metadata(self):
        engine = RiskAssessmentEngine(
            custom_rules={
                "helmet": {
                    "title": "Custom Site Helmet",
                    "category": "Custom Head PPE",
                    "description": "Custom site standard.",
                }
            }
        )
        item = engine.evaluate_ppe_item({"label": "helmet", "confidence": 0.9, "bbox": [1, 2, 3, 4]})
        self.assertEqual(item["title"], "Custom Site Helmet")
        self.assertEqual(item["category"], "Custom Head PPE")


class ReportGeneratorTests(unittest.TestCase):
    def test_html_report_includes_metadata_legal_findings_and_escapes_html(self):
        assessment = RiskAssessmentEngine().assess_batch([
            {"label": "no_helmet", "confidence": 0.91, "bbox": [5, 5, 30, 30]}
        ])
        results = [
            {
                "filename": "zone_a_<1>.jpg",
                "evaluation": assessment,
                "legal_assessment": {
                    "status": "POTENTIAL NON-COMPLIANCE",
                    "jurisdiction_notice": "Sources are potentially relevant.",
                    "context": {
                        "jurisdiction": "great_britain",
                        "activity": "construction",
                        "requirement_source": "site_rule",
                        "requirements": ["helmet"],
                        "hazards": ["height"],
                    },
                    "workers": [
                        {
                            "id": "Worker 1",
                            "status": "POTENTIAL NON-COMPLIANCE",
                            "confidence": 0.92,
                            "observations": [{"label": "no_helmet", "confidence": 0.91}],
                            "findings": [
                                {
                                    "ppe_item": "helmet",
                                    "status": "POTENTIAL NON-COMPLIANCE",
                                    "reasoning": "Declared required; review image.",
                                }
                            ],
                        }
                    ],
                    "references": [
                        {
                            "title": "PPE Regulations 1992",
                            "section": "Reg 4",
                            "url": "https://www.legislation.gov.uk/uksi/1992/2966/regulation/4",
                            "source_organisation": "legislation.gov.uk",
                            "last_verified": "2026-11-20",
                        }
                    ],
                },
            }
        ]
        html = generate_html_report(
            assessment,
            project_name="Demo <Site>",
            audit_metadata={
                "site_name": "North Yard <A>",
                "inspector_name": "J. Doe",
                "inspection_date": "2026-11-24",
            },
            results=results,
        )
        self.assertIn("North Yard &lt;A&gt;", html)
        self.assertIn("J. Doe", html)
        self.assertIn("2026-11-24", html)
        self.assertIn("zone_a_&lt;1&gt;.jpg", html)
        self.assertIn("Worker 1", html)
        self.assertIn("POTENTIAL NON-COMPLIANCE", html)
        self.assertIn("PPE Regulations 1992", html)


if __name__ == "__main__":
    unittest.main()
