"""Core modules for PPE Detection & Compliance System (lazily exported)."""

__all__ = [
    "PPEDetector",
    "RiskAssessmentEngine",
    "annotate_image",
    "generate_pdf_report",
    "generate_html_report",
    "REPORTLAB_AVAILABLE",
]


def __getattr__(name: str):
    if name == "PPEDetector":
        from core.detector import PPEDetector
        return PPEDetector
    if name == "RiskAssessmentEngine":
        from core.risk_engine import RiskAssessmentEngine
        return RiskAssessmentEngine
    if name == "annotate_image":
        from core.visualizer import annotate_image
        return annotate_image
    if name in {"generate_pdf_report", "generate_html_report", "REPORTLAB_AVAILABLE"}:
        from core import report_generator
        return getattr(report_generator, name)
    raise AttributeError(f"module 'core' has no attribute {name!r}")
