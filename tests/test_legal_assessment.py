import unittest

from core.legal_assessment import assess_image


def detection(label, bbox, confidence=0.9):
    return {"label": label, "bbox": bbox, "confidence": confidence}


class LegalAssessmentTests(unittest.TestCase):
    def test_explicit_negative_and_site_rule_produce_reviewable_potential_finding(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("no_helmet", [25, 10, 70, 50])],
            {"jurisdiction": "great_britain", "requirements": ["helmet"], "requirement_source": "site_rule"},
            ["Person", "helmet", "no_helmet"],
        )
        finding = result["workers"][0]["findings"][0]
        self.assertEqual(finding["status"], "POTENTIAL NON-COMPLIANCE")
        self.assertEqual(finding["requirement_source"], "site_rule")
        self.assertEqual(finding["observations"][0]["label"], "no_helmet")
        self.assertTrue(finding["human_verification_required"])

    def test_no_detection_is_not_proof_of_missing_ppe(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200])],
            {"jurisdiction": "great_britain", "requirements": ["helmet"]},
            ["Person", "helmet", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "REVIEW REQUIRED")

    def test_overlapping_people_do_not_share_ambiguous_evidence(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("Person", [30, 0, 130, 200]),
             detection("helmet", [40, 10, 70, 40])],
            {"requirements": ["helmet"]}, ["Person", "helmet"],
        )
        self.assertEqual(len(result["unassigned_observations"]), 1)
        self.assertTrue(all(not w["findings"][0]["observations"] for w in result["workers"]))

    def test_partial_overlap_with_second_worker_is_ambiguous(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("Person", [52, 0, 150, 200]),
             detection("helmet", [40, 10, 80, 40])],
            {"requirements": ["helmet"]}, ["Person", "helmet"],
        )
        self.assertEqual(len(result["unassigned_observations"]), 1)
        self.assertTrue(all(not w["findings"][0]["observations"] for w in result["workers"]))

    def test_low_confidence_worker_cannot_support_potential_finding(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200], 0.4), detection("no_helmet", [25, 10, 70, 50])],
            {"requirements": ["helmet"]}, ["Person", "helmet", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "REVIEW REQUIRED")

    def test_ambiguous_positive_prevents_negative_finding(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("Person", [70, 0, 170, 200]),
             detection("no_helmet", [10, 10, 40, 40]), detection("helmet", [60, 10, 90, 40])],
            {"requirements": ["helmet"]}, ["Person", "helmet", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "REVIEW REQUIRED")

    def test_conflicting_predictions_are_review_required(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("helmet", [25, 10, 70, 50]),
             detection("no_helmet", [25, 10, 70, 50])],
            {"requirements": ["helmet"]}, ["Person", "helmet", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "REVIEW REQUIRED")

    def test_low_confidence_negative_is_review_required(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("no_helmet", [25, 10, 70, 50], 0.4)],
            {"requirements": ["helmet"]}, ["Person", "helmet", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "REVIEW REQUIRED")

    def test_unsupported_class_is_not_assessable(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200])],
            {"requirements": ["respirator"]}, ["Person", "helmet"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "NOT ASSESSABLE")

    def test_unknown_jurisdiction_and_context_do_not_apply_gb_law(self):
        result = assess_image(
            [detection("Person", [0, 0, 100, 200]), detection("no_helmet", [25, 10, 70, 50])],
            {}, ["Person", "no_helmet"],
        )
        self.assertEqual(result["workers"][0]["status"], "REVIEW REQUIRED")
        self.assertFalse(any(ref["source_type"] == "legislation" for ref in result["references"]))

    def test_no_workers_never_implies_compliance(self):
        result = assess_image([], {"requirements": ["helmet"]}, ["Person", "helmet"])
        self.assertEqual(result["status"], "NOT ASSESSABLE")
        self.assertEqual(result["workers"], [])

    def test_hazard_references_require_context_and_great_britain(self):
        no_context = assess_image([], {"jurisdiction": "great_britain"}, ["Person"])
        with_context = assess_image([], {"jurisdiction": "great_britain", "hazards": ["noise"]}, ["Person"])
        self.assertNotIn("noise-2005-6", [r["id"] for r in no_context["references"]])
        self.assertIn("noise-2005-6", [r["id"] for r in with_context["references"]])

    def test_synonym_labels_are_normalized_for_legal_assessment(self):
        result = assess_image(
            [detection("worker", [0, 0, 100, 200]), detection("no_goggles", [25, 10, 70, 50])],
            {"requirements": ["goggles"]},
            ["worker", "safety_glasses", "no_goggles"],
        )
        self.assertEqual(result["workers"][0]["findings"][0]["status"], "POTENTIAL NON-COMPLIANCE")


if __name__ == "__main__":
    unittest.main()
