"""
FastAPI Backend for PPE Detection & Compliance
Serves detection, compliance assessment, and report generation APIs
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import io
import json
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np

# Local core modules
from config import (
    DEFAULT_MODEL_PATH,
    DEFAULT_CONFIDENCE,
    DEFAULT_IOU_THRESHOLD,
    WEIGHTS_DIR,
    calculate_ppe_compliance,
    PPE_KNOWLEDGE_BASE
)
from core.detector import PPEDetector, ULTRALYTICS_AVAILABLE
from core.risk_engine import RiskAssessmentEngine
from core.visualizer import annotate_image, generate_risk_matrix_plot
from core.report_generator import generate_pdf_report, generate_html_report, REPORTLAB_AVAILABLE

app = FastAPI(
    title="PPE Detection & Compliance AI",
    description="YOLOv8-based PPE detection and compliance assessment",
    version="2.0.0"
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


class DetectionRequest(BaseModel):
    conf_threshold: float = DEFAULT_CONFIDENCE
    iou_threshold: float = DEFAULT_IOU_THRESHOLD
    show_compliant: bool = True


class AuditMetadata(BaseModel):
    site_name: str = "Construction Site"
    inspector_name: str = "Safety Inspector"
    inspection_date: str = None


class ReportRequest(BaseModel):
    site_assessment: Dict[str, Any]
    audit_metadata: AuditMetadata
    report_format: str = "html"  # "html" or "pdf"


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "detector_ready": detector.is_ready(),
        "model_path": str(DEFAULT_MODEL_PATH),
        "is_custom_model": detector.is_custom_model,
        "class_names": detector.class_names,
        "status_message": detector.status_message,
        "ultralytics_available": ULTRALYTICS_AVAILABLE,
        "reportlab_available": REPORTLAB_AVAILABLE,
        "detection_mode": "PPE Detection"
    }


@app.get("/config")
async def get_config():
    """Get system configuration"""
    weights_exist = DEFAULT_MODEL_PATH.exists()
    return {
        "default_confidence": DEFAULT_CONFIDENCE,
        "default_iou_threshold": DEFAULT_IOU_THRESHOLD,
        "weights_path": str(DEFAULT_MODEL_PATH),
        "weights_exist": weights_exist,
        "is_custom_model": detector.is_custom_model,
        "class_names": detector.class_names,
        "detector_status": detector.status_message,
        "detection_mode": "PPE Identification"
    }


@app.post("/detect")
async def detect_ppe(
    file: UploadFile = File(...),
    conf_threshold: float = DEFAULT_CONFIDENCE,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    show_compliant: bool = True
):
    """
    Detect PPE items in a single image
    Returns: detections, compliance score, annotated image
    """
    try:
        # Read and validate image
        contents = await file.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")

        # Run PPE detection
        dets = detector.detect(pil_img, conf_threshold=conf_threshold, iou_threshold=iou_threshold)

        # Calculate PPE compliance
        compliance = calculate_ppe_compliance(dets)

        # Risk assessment (for context, though PPE-focused)
        img_eval = risk_engine.assess_batch(dets)
        items_to_draw = img_eval["all_items"] if show_compliant else img_eval["hazards"]

        # Annotate image
        annotated_img = annotate_image(pil_img, items_to_draw)

        # Convert annotated image to base64 for JSON response
        import base64
        img_buffer = io.BytesIO()
        annotated_img.save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        return {
            "filename": file.filename,
            "detections": dets,
            "ppe_compliance": compliance,
            "evaluation": img_eval,
            "annotated_image": f"data:image/png;base64,{img_base64}",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/detect-batch")
async def detect_batch_ppe(
    files: List[UploadFile] = File(...),
    conf_threshold: float = DEFAULT_CONFIDENCE,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    show_compliant: bool = True
):
    """
    Detect PPE in multiple images and generate aggregate compliance assessment
    """
    try:
        import base64
        all_detections = []
        processed_results = []
        all_compliance = []

        for file in files:
            contents = await file.read()
            pil_img = Image.open(io.BytesIO(contents)).convert("RGB")

            dets = detector.detect(pil_img, conf_threshold=conf_threshold, iou_threshold=iou_threshold)
            compliance = calculate_ppe_compliance(dets)
            img_eval = risk_engine.assess_batch(dets)
            items_to_draw = img_eval["all_items"] if show_compliant else img_eval["hazards"]
            annotated_img = annotate_image(pil_img, items_to_draw)

            # Convert to base64
            img_buffer = io.BytesIO()
            annotated_img.save(img_buffer, format="PNG")
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            processed_results.append({
                "filename": file.filename,
                "annotated_image": f"data:image/png;base64,{img_base64}",
                "ppe_compliance": compliance,
                "evaluation": img_eval
            })

            all_detections.extend(dets)
            all_compliance.append(compliance)

        # Aggregate compliance assessment
        avg_compliance = sum(c["compliance_rate"] for c in all_compliance) / len(all_compliance) if all_compliance else 0
        site_assessment = risk_engine.assess_batch(all_detections)
        site_assessment["average_ppe_compliance"] = round(avg_compliance, 1)

        return {
            "results": processed_results,
            "site_assessment": site_assessment,
            "average_compliance": round(avg_compliance, 1),
            "total_images": len(files),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """
    Generate HTML or PDF PPE compliance audit report
    """
    try:
        if request.report_format == "html":
            html_report = generate_html_report(
                request.site_assessment,
                project_name=request.audit_metadata.site_name
            )
            return {
                "format": "html",
                "content": html_report,
                "success": True
            }

        elif request.report_format == "pdf":
            if not REPORTLAB_AVAILABLE:
                raise HTTPException(
                    status_code=400,
                    detail="PDF generation requires reportlab. Install with: pip install reportlab"
                )

            pdf_bytes = generate_pdf_report(
                request.site_assessment,
                project_name=request.audit_metadata.site_name
            )
            return {
                "format": "pdf",
                "content": pdf_bytes.hex(),  # Convert bytes to hex string for JSON
                "filename": f"PPE_Compliance_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                "success": True
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid report format")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
            "message": f"Weights uploaded successfully. Please restart the backend to load new PPE model."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/ppe-standards")
async def get_ppe_standards():
    """Get PPE standards and requirements"""
    return {
        "ppe_items": PPE_KNOWLEDGE_BASE,
        "success": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
