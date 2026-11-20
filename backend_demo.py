"""
FastAPI Backend for Construction Hazard AI - DEMO MODE
Serves detection, risk assessment, and report generation APIs
(No YOLOv8/ultralytics required for demo)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import io
import json
import base64
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
import numpy as np
import random

app = FastAPI(
    title="Construction Hazard AI API - DEMO",
    description="Demo mode - YOLOv8-based hazard detection and 5×5 risk assessment",
    version="1.0.0"
)

# CORS Configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditMetadata(BaseModel):
    site_name: str = "Bolton Central Construction Phase 2"
    inspector_name: str = "S. Coceban (Safety Lead)"
    inspection_date: str = None


class ReportRequest(BaseModel):
    site_assessment: Dict[str, Any]
    audit_metadata: AuditMetadata
    report_format: str = "html"


HAZARD_CLASSES = {
    "hard_hat": "Personal Protective Equipment",
    "safety_vest": "Personal Protective Equipment",
    "gloves": "Personal Protective Equipment",
    "safety_boots": "Personal Protective Equipment",
    "exposed_wiring": "Electrical Hazard",
    "unprotected_height": "Fall Hazard",
    "unsecured_scaffold": "Structural Hazard",
    "debris_field": "Environmental Hazard",
    "missing_guard": "Structural Hazard",
    "poor_lighting": "Environmental Hazard"
}

RISK_MATRIX = {
    "hard_hat": {"likelihood": 1, "severity": 2},
    "safety_vest": {"likelihood": 1, "severity": 2},
    "gloves": {"likelihood": 1, "severity": 2},
    "safety_boots": {"likelihood": 1, "severity": 2},
    "exposed_wiring": {"likelihood": 4, "severity": 5},
    "unprotected_height": {"likelihood": 5, "severity": 5},
    "unsecured_scaffold": {"likelihood": 4, "severity": 5},
    "debris_field": {"likelihood": 3, "severity": 3},
    "missing_guard": {"likelihood": 4, "severity": 4},
    "poor_lighting": {"likelihood": 2, "severity": 3}
}


def generate_demo_detections(image: Image.Image) -> dict:
    """Generate mock detections for demo purposes"""
    width, height = image.size
    num_detections = random.randint(3, 8)
    
    detections = []
    hazard_items = []
    compliant_items = []
    
    for i in range(num_detections):
        class_name = random.choice(list(HAZARD_CLASSES.keys()))
        
        # Random bounding box
        x1 = random.randint(50, width - 150)
        y1 = random.randint(50, height - 150)
        x2 = x1 + random.randint(80, 150)
        y2 = y1 + random.randint(80, 150)
        
        confidence = round(random.uniform(0.6, 0.99), 3)
        
        detection = {
            "class": class_name,
            "class_id": list(HAZARD_CLASSES.keys()).index(class_name),
            "confidence": confidence,
            "bbox": [x1, y1, x2, y2],
            "category": HAZARD_CLASSES[class_name]
        }
        detections.append(detection)
        
        # Classify as hazard or compliant
        if class_name in ["hard_hat", "safety_vest", "gloves", "safety_boots"]:
            compliant_items.append(detection)
        else:
            hazard_items.append(detection)
    
    return {
        "detections": detections,
        "hazards": hazard_items,
        "compliant_items": compliant_items,
        "num_detections": len(detections),
        "num_hazards": len(hazard_items),
        "num_compliant": len(compliant_items)
    }


def generate_risk_assessment(detections: dict) -> dict:
    """Generate risk assessment from detections"""
    risk_matrix = [[0] * 5 for _ in range(5)]
    hazard_summary = {}
    
    for detection in detections["hazards"]:
        class_name = detection["class"]
        risk_data = RISK_MATRIX.get(class_name, {"likelihood": 2, "severity": 2})
        likelihood = min(5, max(1, risk_data["likelihood"]))
        severity = min(5, max(1, risk_data["severity"]))
        
        risk_matrix[severity - 1][likelihood - 1] += 1
        
        category = HAZARD_CLASSES.get(class_name, "Unknown")
        if category not in hazard_summary:
            hazard_summary[category] = {"count": 0, "items": []}
        
        hazard_summary[category]["count"] += 1
        hazard_summary[category]["items"].append({
            "type": class_name,
            "confidence": detection["confidence"],
            "bbox": detection["bbox"],
            "risk_level": f"L{likelihood}S{severity}"
        })
    
    # Calculate overall risk
    total_hazards = sum(sum(row) for row in risk_matrix)
    high_risk_count = risk_matrix[4][3] + risk_matrix[4][4] + risk_matrix[3][4]
    
    return {
        "risk_matrix": risk_matrix,
        "hazard_summary": hazard_summary,
        "total_hazards": total_hazards,
        "high_risk_count": high_risk_count,
        "overall_risk_level": "HIGH" if high_risk_count > 2 else "MEDIUM" if total_hazards > 0 else "LOW",
        "assessment_date": datetime.now().isoformat(),
        "recommendations": [
            "Ensure all workers wear complete PPE including hard hat, safety vest, and boots",
            "Secure all electrical installations and use proper conduit",
            "Install guardrails on elevated work areas",
            "Clear debris regularly from work site",
            "Increase lighting in dark areas",
            "Conduct daily safety briefings"
        ]
    }


def annotate_image_with_detections(image: Image.Image, detections: dict) -> Image.Image:
    """Draw bounding boxes on image"""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    
    all_items = detections["compliant_items"] + detections["hazards"]
    
    for item in all_items:
        bbox = item["bbox"]
        class_name = item["class"]
        confidence = item["confidence"]
        
        # Color: green for compliant, red for hazards
        color = "green" if item in detections["compliant_items"] else "red"
        
        # Draw bounding box
        draw.rectangle(bbox, outline=color, width=2)
        
        # Draw label
        label = f"{class_name} ({confidence:.2f})"
        draw.text((bbox[0], bbox[1] - 10), label, fill=color)
    
    return img_copy


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "detector_ready": True,
        "mode": "DEMO - No YOLOv8 Required",
        "is_custom_model": False,
        "class_names": list(HAZARD_CLASSES.keys()),
        "status_message": "Demo mode active - generating mock detections"
    }


@app.get("/config")
async def get_config():
    """Get system configuration"""
    return {
        "default_confidence": 0.5,
        "default_iou_threshold": 0.45,
        "mode": "DEMO",
        "is_custom_model": False,
        "class_names": list(HAZARD_CLASSES.keys()),
        "detector_status": "Demo mode - mock detections"
    }


@app.post("/detect")
async def detect_hazards(
    file: UploadFile = File(...),
    conf_threshold: float = Form(0.5),
    iou_threshold: float = Form(0.45),
    show_compliant: bool = Form(True)
):
    """
    Detect hazards in a single image (DEMO MODE)
    Returns: mock detections, annotated image, risk assessment
    """
    try:
        # Read and validate image
        contents = await file.read()
        
        # Try to open the image - handle various formats including WEBP
        try:
            pil_img = Image.open(io.BytesIO(contents))
            # Convert to RGB if necessary (handles RGBA, grayscale, WEBP, etc.)
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
        except Exception as img_error:
            raise ValueError(f"Could not process image file: {str(img_error)}")
        
        # Resize to reasonable size if needed
        max_size = 800
        if max(pil_img.size) > max_size:
            pil_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Generate demo detections
        dets = generate_demo_detections(pil_img)
        
        # Generate risk assessment
        assessment = generate_risk_assessment(dets)
        
        # Annotate image
        items_to_show = dets.copy()
        if not show_compliant:
            items_to_show["compliant_items"] = []
        
        annotated_img = annotate_image_with_detections(pil_img, items_to_show)
        
        # Convert annotated image to base64
        img_buffer = io.BytesIO()
        annotated_img.save(img_buffer, format="PNG")
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            "filename": file.filename,
            "detections": dets,
            "evaluation": assessment,
            "annotated_image": f"data:image/png;base64,{img_base64}",
            "success": True,
            "mode": "DEMO"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Image processing error: {str(e)}")


@app.post("/detect-batch")
async def detect_batch(
    files: List[UploadFile] = File(...),
    conf_threshold: float = Form(0.5),
    iou_threshold: float = Form(0.45),
    show_compliant: bool = Form(True)
):
    """Detect hazards in multiple images"""
    results = []
    aggregate_assessment = {
        "total_images": len(files),
        "total_hazards": 0,
        "hazard_summary": {},
        "risk_matrix": [[0] * 5 for _ in range(5)]
    }
    
    for file in files:
        try:
            contents = await file.read()
            pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
            max_size = 800
            if max(pil_img.size) > max_size:
                pil_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            dets = generate_demo_detections(pil_img)
            assessment = generate_risk_assessment(dets)
            
            results.append({
                "filename": file.filename,
                "detections": dets,
                "assessment": assessment
            })
            
            aggregate_assessment["total_hazards"] += assessment["total_hazards"]
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "results": results,
        "aggregate_assessment": aggregate_assessment,
        "success": True
    }


@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    """Generate PDF or HTML report"""
    try:
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .metadata {{ background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .hazards {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .high {{ background-color: #ffcccc; }}
                .medium {{ background-color: #ffffcc; }}
                .low {{ background-color: #ccffcc; }}
            </style>
        </head>
        <body>
            <h1>🏗️ Construction Hazard Assessment Report</h1>
            
            <div class="metadata">
                <h3>Audit Information</h3>
                <p><strong>Site:</strong> {request.audit_metadata.site_name}</p>
                <p><strong>Inspector:</strong> {request.audit_metadata.inspector_name}</p>
                <p><strong>Date:</strong> {request.audit_metadata.inspection_date or datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="hazards">
                <h3>Assessment Summary</h3>
                <p>This is a demo report. In production, this would contain detailed hazard analysis, risk matrices, and recommendations.</p>
                <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div>
                <h3>Recommendations</h3>
                <ul>
                    <li>Ensure all workers wear complete PPE</li>
                    <li>Secure all electrical installations</li>
                    <li>Install guardrails on elevated work areas</li>
                    <li>Clear debris regularly</li>
                    <li>Increase lighting in dark areas</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return {
            "content": html_content,
            "format": request.report_format,
            "filename": f"hazard_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
