import io
import base64
import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from backend import app, detector
from config import calculate_ppe_compliance
from core.detector import PPEDetector
from core.risk_engine import RiskAssessmentEngine


def image_bytes(size=(120, 80)):
    output = io.BytesIO()
    Image.new("RGB", size, "white").save(output, "PNG")
    return output.getvalue()


class DetectionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_multipart_settings_control_inference_and_annotations(self):
        detection = {"label": "helmet", "confidence": 0.8, "bbox": [10, 10, 40, 40], "type": "ppe_item"}
        with patch.object(detector, "detect", return_value=[detection]) as predict:
            response = self.client.post(
                "/detect",
                files={"file": ("image.png", image_bytes(), "image/png")},
                data={"conf_threshold": "0.8", "iou_threshold": "0.7", "show_compliant": "false"},
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(predict.call_args.kwargs, {"conf_threshold": 0.8, "iou_threshold": 0.7})
        self.assertEqual(response.json()["detections"], [detection])

    def test_negative_class_is_not_positive_or_proof_of_compliance(self):
        detections = [{"label": "no_helmet", "confidence": 0.9, "bbox": [5, 5, 30, 30]}]
        result = RiskAssessmentEngine().assess_batch(detections)
        self.assertFalse(result["all_items"][0]["is_ppe_item"])
        self.assertEqual(result["all_items"][0]["raw_label"], "no_helmet")
        self.assertEqual(result["detected_items"], [])
        self.assertIsNone(result["compliance_rate"])
        self.assertEqual(result["missing_items"], [])
        self.assertIsNone(calculate_ppe_compliance([])["compliance_rate"])

    def test_generic_ppe_information_does_not_assert_universal_requirements(self):
        response = self.client.get("/ppe-standards")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["ppe_items"]["helmet"]["is_required"])
        evaluation = RiskAssessmentEngine().evaluate_ppe_item(
            {"label": "helmet", "confidence": 0.9, "bbox": [1, 1, 20, 20]}
        )
        self.assertIsNone(evaluation["is_required"])
        self.assertIsNone(evaluation["standard_ref"])

    def test_model_unavailable_does_not_return_simulated_detections(self):
        model = PPEDetector.__new__(PPEDetector)
        model.model = None
        model.status_message = "model unavailable"
        with self.assertRaises(RuntimeError):
            model.detect(Image.new("RGB", (20, 20)))

    def test_batch_includes_detections_and_preserves_image_dimensions(self):
        with patch.object(detector, "detect", return_value=[]):
            response = self.client.post(
                "/detect-batch",
                files=[
                    ("files", ("wide.png", image_bytes((120, 40)), "image/png")),
                    ("files", ("tall.png", image_bytes((40, 120)), "image/png")),
                ],
            )
        self.assertEqual(response.status_code, 200, response.text)
        results = response.json()["results"]
        self.assertEqual([r["image_size"] for r in results], [[120, 40], [40, 120]])
        self.assertEqual([r["detections"] for r in results], [[], []])

    def test_invalid_image_is_reported_as_client_error(self):
        response = self.client.post("/detect", files={"file": ("bad.png", b"bad", "image/png")})
        self.assertEqual(response.status_code, 400)

    def test_annotations_use_original_xyxy_coordinates_and_can_hide_positive_ppe(self):
        detection = {"label": "helmet", "confidence": 0.8, "bbox": [10, 20, 60, 55], "type": "ppe_item"}
        with patch.object(detector, "detect", return_value=[detection]):
            images = []
            for show in ("true", "false"):
                response = self.client.post(
                    "/detect",
                    files={"file": ("image.png", image_bytes(), "image/png")},
                    data={"show_compliant": show},
                )
                self.assertEqual(response.status_code, 200, response.text)
                png = base64.b64decode(response.json()["annotated_image"].split(",", 1)[1])
                images.append(Image.open(io.BytesIO(png)))
        self.assertEqual(images[0].size, (120, 80))
        self.assertEqual(images[0].getpixel((60, 55)), (40, 167, 69))
        self.assertEqual(images[1].getpixel((60, 55)), (255, 255, 255))

    def test_exif_orientation_is_applied_before_inference(self):
        output = io.BytesIO()
        image = Image.new("RGB", (40, 20), "white")
        exif = image.getexif()
        exif[274] = 6
        image.save(output, "JPEG", exif=exif)
        with patch.object(detector, "detect", return_value=[]) as predict:
            response = self.client.post("/detect", files={"file": ("oriented.jpg", output.getvalue(), "image/jpeg")})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["image_size"], [20, 40])
        self.assertEqual(predict.call_args.args[0].size, (20, 40))

    def test_unavailable_model_returns_503(self):
        with patch.object(detector, "is_ready", return_value=False):
            response = self.client.post("/detect", files={"file": ("image.png", image_bytes(), "image/png")})
        self.assertEqual(response.status_code, 503)

    def test_report_lists_model_labels_without_claiming_compliance(self):
        assessment = RiskAssessmentEngine().assess_batch([
            {"label": "no_helmet", "confidence": 0.9, "bbox": [5, 5, 30, 30]}
        ])
        response = self.client.post("/generate-report", json={"site_assessment": assessment, "audit_metadata": {}})
        self.assertEqual(response.status_code, 200, response.text)
        content = response.json()["content"]
        self.assertIn("no_helmet", content)
        self.assertIn("do not establish PPE compliance", content)

    def test_site_context_is_used_for_single_and_batch_images(self):
        detections = [
            {"label": "Person", "confidence": 0.9, "bbox": [0, 0, 100, 80], "type": "worker"},
            {"label": "no_helmet", "confidence": 0.9, "bbox": [20, 2, 60, 25], "type": "missing_ppe"},
        ]
        context = json.dumps({"jurisdiction": "great_britain", "requirements": ["helmet"], "requirement_source": "site_rule"})
        with patch.object(detector, "detect", return_value=detections):
            single = self.client.post(
                "/detect", files={"file": ("image.png", image_bytes(), "image/png")}, data={"site_context": context},
            )
            batch = self.client.post(
                "/detect-batch", files=[("files", ("image.png", image_bytes(), "image/png"))],
                data={"site_context": context},
            )
        self.assertEqual(single.status_code, 200, single.text)
        self.assertEqual(batch.status_code, 200, batch.text)
        self.assertEqual(single.json()["legal_assessment"]["status"], "POTENTIAL NON-COMPLIANCE")
        self.assertEqual(batch.json()["results"][0]["legal_assessment"]["status"], "POTENTIAL NON-COMPLIANCE")

    def test_invalid_site_context_is_rejected(self):
        response = self.client.post(
            "/detect", files={"file": ("image.png", image_bytes(), "image/png")},
            data={"site_context": '{"jurisdiction":"made_up"}'},
        )
        self.assertEqual(response.status_code, 422)

    def test_batch_worker_assessments_are_not_mixed_between_images(self):
        worker = {"label": "Person", "confidence": 0.9, "bbox": [0, 0, 100, 80], "type": "worker"}
        missing = {"label": "no_helmet", "confidence": 0.9, "bbox": [20, 2, 60, 25], "type": "missing_ppe"}
        context = json.dumps({"requirements": ["helmet"]})
        with patch.object(detector, "detect", side_effect=[[worker, missing], [worker]]):
            response = self.client.post(
                "/detect-batch",
                files=[("files", ("first.png", image_bytes(), "image/png")),
                       ("files", ("second.png", image_bytes(), "image/png"))],
                data={"site_context": context},
            )
        self.assertEqual(response.status_code, 200, response.text)
        statuses = [result["legal_assessment"]["status"] for result in response.json()["results"]]
        self.assertEqual(statuses, ["POTENTIAL NON-COMPLIANCE", "REVIEW REQUIRED"])


if __name__ == "__main__":
    unittest.main()
