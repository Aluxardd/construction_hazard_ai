"""
FastAPI Backend for PPE Detection & Review
Serves detection, legislation-informed visual assessment, and report generation APIs.
"""

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict, Any, Literal
import io
import json
import base64
import logging
import threading
import time
from datetime import datetime
from PIL import Image, ImageOps, UnidentifiedImageError

# Local core modules
from config import (
    BASE_DIR,
    DEFAULT_MODEL_PATH,
    DEFAULT_CONFIDENCE,
    DEFAULT_IOU_THRESHOLD,
    WEIGHTS_DIR,
    calculate_ppe_compliance,
    PPE_KNOWLEDGE_BASE,
)
from core.detector import PPEDetector, ULTRALYTICS_AVAILABLE
from core.risk_engine import RiskAssessmentEngine
from core.legal_assessment import assess_image
from core.visualizer import annotate_image
from core.report_generator import generate_pdf_report, generate_html_report, REPORTLAB_AVAILABLE

app = FastAPI(
    title="PPE Detection & Compliance AI",
    description="YOLOv8-based PPE detection and conservative visual review",
    version="2.0.0",
)

# CORS Configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
detector = PPEDetector(model_path=str(DEFAULT_MODEL_PATH))
risk_engine = RiskAssessmentEngine()
_inference_lock = threading.Lock()
logger = logging.getLogger("uvicorn.error")
logger.info("Detector ready=%s, classes=%s, status=%s", detector.is_ready(), detector.class_names, detector.status_message)


class SiteContext(BaseModel):
    jurisdiction: Literal["unknown", "great_britain", "northern_ireland"] = "unknown"
    activity: Literal["unknown", "construction", "other"] = "unknown"
    work_area: str = Field(default="", max_length=500)
    hazards: List[Literal["height", "substances", "noise"]] = Field(default_factory=list)
    requirements: List[
        Literal[
            "helmet",
            "vest",
            "gloves",
            "boots",
            "goggles",
            "respirator",
            "hearing_protection",
            "fall_protection",
        ]
    ] = Field(default_factory=list)
    requirement_source: Literal["site_rule", "risk_assessment", "construction_phase_plan"] = "site_rule"
    notes: str = Field(default="", max_length=2000)


def parse_site_context(value: str) -> dict:
    try:
        context = SiteContext(**json.loads(value))
        return context.model_dump() if hasattr(context, "model_dump") else context.dict()
    except (ValueError, TypeError, ValidationError):
        raise HTTPException(status_code=422, detail="Invalid site assessment context.")


class AuditMetadata(BaseModel):
    site_name: str = "Construction Site"
    inspector_name: str = "Safety Inspector"
    inspection_date: Optional[str] = None


class ReportRequest(BaseModel):
    site_assessment: Dict[str, Any]
    audit_metadata: AuditMetadata
    report_format: str = "html"  # "html" or "pdf"
    results: Optional[List[Dict[str, Any]]] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "detector_ready": detector.is_ready(),
        "is_custom_model": detector.is_custom_model,
        "model_name": DEFAULT_MODEL_PATH.name if detector.is_ready() else None,
        "class_names": detector.class_names,
        "status_message": "Model loaded." if detector.is_ready() else "Model unavailable. Check backend logs.",
        "ultralytics_available": ULTRALYTICS_AVAILABLE,
        "reportlab_available": REPORTLAB_AVAILABLE,
        "detection_mode": "PPE Detection",
    }


@app.get("/config")
async def get_config():
    """Get system configuration."""
    weights_exist = DEFAULT_MODEL_PATH.exists()
    return {
        "default_confidence": DEFAULT_CONFIDENCE,
        "default_iou_threshold": DEFAULT_IOU_THRESHOLD,
        "weights_exist": weights_exist,
        "is_custom_model": detector.is_custom_model,
        "model_name": DEFAULT_MODEL_PATH.name if detector.is_ready() else None,
        "class_names": detector.class_names,
        "detector_status": "Model loaded." if detector.is_ready() else "Model unavailable. Check backend logs.",
        "detection_mode": "PPE Identification",
    }


def _run_image_pipeline(
    contents: bytes,
    filename: Optional[str],
    conf_threshold: float,
    iou_threshold: float,
    show_compliant: bool,
    site_context: dict,
) -> Dict[str, Any]:
    try:
        with Image.open(io.BytesIO(contents)) as image:
            pil_img = ImageOps.exif_transpose(image).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable image.")

    try:
        start = time.perf_counter()
        with _inference_lock:
            dets = detector.detect(pil_img, conf_threshold=conf_threshold, iou_threshold=iou_threshold)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        evaluation = risk_engine.assess_batch(dets)
        items = evaluation["all_items"]
        if not show_compliant:
            items = [item for item in items if not item["is_ppe_item"]]
        annotated = annotate_image(pil_img, items)
        buffer = io.BytesIO()
        annotated.save(buffer, format="PNG")
        model_overrides = getattr(detector.model, "overrides", None)
        configured_imgsz = model_overrides.get("imgsz") if isinstance(model_overrides, dict) else None
        logger.debug(
            "Inference image_size=%s configured_imgsz=%s elapsed_ms=%s detections=%s",
            pil_img.size,
            configured_imgsz,
            elapsed_ms,
            dets,
        )
        return {
            "filename": filename,
            "image_size": list(pil_img.size),
            "inference_ms": elapsed_ms,
            "detections": dets,
            "ppe_compliance": calculate_ppe_compliance(dets),
            "evaluation": evaluation,
            "legal_assessment": assess_image(dets, site_context, detector.class_names),
            "annotated_image": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode(),
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Image inference or annotation failed")
        raise HTTPException(status_code=500, detail="Image processing failed. Check backend logs.")


async def process_image(file, conf_threshold, iou_threshold, show_compliant, site_context):
    if not detector.is_ready():
        raise HTTPException(status_code=503, detail="Detection model is unavailable. Check backend logs and model weights.")
    contents = await file.read()
    return await run_in_threadpool(
        _run_image_pipeline,
        contents,
        file.filename,
        conf_threshold,
        iou_threshold,
        show_compliant,
        site_context,
    )


@app.post("/detect")
async def detect_ppe(
    file: UploadFile = File(...),
    conf_threshold: float = Form(DEFAULT_CONFIDENCE, ge=0, le=1),
    iou_threshold: float = Form(DEFAULT_IOU_THRESHOLD, ge=0, le=1),
    show_compliant: bool = Form(True),
    site_context: str = Form("{}"),
):
    """Detect PPE items in a single image and return detections, visual assessment, and annotated image."""
    result = await process_image(file, conf_threshold, iou_threshold, show_compliant, parse_site_context(site_context))
    return {**result, "success": True}


@app.get("/sample-image")
async def sample_image():
    sample_path = BASE_DIR / "samples" / "sample_site.jpg"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found.")
    return FileResponse(sample_path, media_type="image/jpeg")


@app.post("/detect-batch")
async def detect_batch_ppe(
    files: List[UploadFile] = File(...),
    conf_threshold: float = Form(DEFAULT_CONFIDENCE, ge=0, le=1),
    iou_threshold: float = Form(DEFAULT_IOU_THRESHOLD, ge=0, le=1),
    show_compliant: bool = Form(True),
    site_context: str = Form("{}"),
):
    """Detect PPE in multiple images and generate aggregate detection summary."""
    if not detector.is_ready():
        raise HTTPException(status_code=503, detail="Detection model is unavailable. Check backend logs and model weights.")

    processed_results = []
    all_detections = []
    failed_images = 0
    context = parse_site_context(site_context)

    for file in files:
        try:
            result = await process_image(file, conf_threshold, iou_threshold, show_compliant, context)
            processed_results.append(result)
            all_detections.extend(result["detections"])
        except HTTPException as exc:
            if exc.status_code == 503:
                raise
            failed_images += 1
            processed_results.append({
                "filename": file.filename,
                "error": exc.detail,
                "detections": [],
                "image_size": None,
            })

    return {
        "results": processed_results,
        "site_assessment": risk_engine.assess_batch(all_detections),
        "average_compliance": None,
        "total_images": len(files),
        "failed_images": failed_images,
        "success": True,
    }


@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """Generate HTML or PDF PPE detection and review summary report."""
    metadata_dict = (
        request.audit_metadata.model_dump()
        if hasattr(request.audit_metadata, "model_dump")
        else request.audit_metadata.dict()
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    try:
        if request.report_format == "html":
            html_report = generate_html_report(
                request.site_assessment,
                project_name=request.audit_metadata.site_name,
                audit_metadata=metadata_dict,
                results=request.results,
            )
            return {
                "format": "html",
                "content": html_report,
                "filename": f"PPE_Detection_Summary_{timestamp}.html",
                "success": True,
            }

        if request.report_format == "pdf":
            if not REPORTLAB_AVAILABLE:
                raise HTTPException(
                    status_code=400,
                    detail="PDF generation requires reportlab. Install with: pip install reportlab",
                )

            pdf_bytes = await run_in_threadpool(
                generate_pdf_report,
                request.site_assessment,
                request.audit_metadata.site_name,
                metadata_dict,
                request.results,
            )
            return {
                "format": "pdf",
                "content": pdf_bytes.hex(),
                "filename": f"PPE_Compliance_Report_{timestamp}.pdf",
                "success": True,
            }

        raise HTTPException(status_code=400, detail="Invalid report format")

    except HTTPException:
        raise
    except Exception:
        logger.exception("Report generation failed")
        raise HTTPException(status_code=500, detail="Report generation failed. Check backend logs.")


@app.post("/upload-weights")
async def upload_custom_weights(file: UploadFile = File(...)):
    """
    Upload custom YOLOv8 weights (.pt file) for PPE detection
    """
    try:
        if not file.filename.endswith(".pt"):
            raise HTTPException(status_code=400, detail="File must be a .pt weights file")

        WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
        target_path = WEIGHTS_DIR / file.filename

        contents = await file.read()
        with open(target_path, "wb") as f:
            f.write(contents)

        return {
            "success": True,
            "filename": file.filename,
            "path": str(target_path),
            "message": "Weights uploaded successfully. Please restart the backend to load new PPE model.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ppe-standards")
async def get_ppe_standards():
    """Get PPE categories and descriptive metadata."""
    return {
        "ppe_items": {
            key: {
                "title": item["title"],
                "category": item["category"],
                "description": item["description"],
                "is_required": None,
                "standard_ref": None,
            }
            for key, item in PPE_KNOWLEDGE_BASE.items()
        },
        "notice": "PPE requirements depend on the work, risks, jurisdiction and site context.",
        "success": True,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
