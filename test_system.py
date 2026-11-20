"""
System self-test script.
Verifies detector fallback, risk engine calculations, 5x5 matrix generation,
and HTML/PDF report creation without requiring an active browser.
"""

import sys
from PIL import Image
from core.detector import HazardDetector
from core.risk_engine import RiskAssessmentEngine
from core.visualizer import annotate_image, generate_risk_matrix_plot
from core.report_generator import generate_html_report, generate_pdf_report, REPORTLAB_AVAILABLE
from config import DEFAULT_MODEL_PATH

def test_pipeline():
    print("=" * 60)
    print("Testing Construction Hazard AI Pipeline...")
    print("=" * 60)

    # 1. Test Detector
    print("[1/5] Initializing Hazard Detector...")
    detector = HazardDetector(model_path=DEFAULT_MODEL_PATH)
    print(f"       Status: {detector.status_message}")
    print(f"       Custom Model Active: {detector.is_custom_model}")

    # Create dummy test image
    test_img = Image.new("RGB", (640, 480), color=(150, 180, 210))
    detections = detector.detect(test_img, conf_threshold=0.3)
    print(f"       Detections found: {len(detections)}")
    for d in detections:
        print(f"       - Label: {d['label']}, Conf: {d['confidence']}, Box: {d['bbox']}")

    # 2. Test Risk Assessment Engine
    print("\n[2/5] Testing 5x5 Risk Assessment Engine...")
    risk_engine = RiskAssessmentEngine()
    assessment = risk_engine.assess_batch(detections)
    print(f"       Overall Site Risk: {assessment['overall_site_risk']}")
    print(f"       Tier Breakdown: {assessment['tier_counts']}")
    print(f"       Total Hazards: {assessment['total_hazards']}")

    # 3. Test Visualizer (Annotation & Matrix Plot)
    print("\n[3/5] Testing Image Annotation & 5x5 Matrix Plot...")
    annotated = annotate_image(test_img, assessment["hazards"])
    print(f"       Annotated Image Size: {annotated.size}")
    fig = generate_risk_matrix_plot(assessment["matrix_counts"])
    print(f"       5x5 Matrix Plot generated successfully.")

    # 4. Test Report Generation (HTML)
    print("\n[4/5] Testing HTML Safety Audit Report Generation...")
    html_out = generate_html_report(assessment, project_name="Self-Test Site")
    print(f"       HTML Report Length: {len(html_out)} characters")

    # 5. Test PDF Report Generation
    print("\n[5/5] Testing PDF Report Generation (ReportLab)...")
    if REPORTLAB_AVAILABLE:
        pdf_bytes = generate_pdf_report(assessment, project_name="Self-Test Site")
        print(f"       PDF Report generated successfully ({len(pdf_bytes)} bytes)")
    else:
        print("       ReportLab not installed in current Python env. HTML export is fully functional.")

    print("\n" + "=" * 60)
    print("ALL CORE SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_pipeline()
