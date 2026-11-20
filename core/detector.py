"""
Object Detection Engine for Construction Site Hazards.
Supports trained YOLOv8 models (.pt weights) via Ultralytics,
with automatic fallback to simulation/demo mode for development and testing.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
from PIL import Image
import numpy as np

# Try importing Ultralytics YOLO
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


class HazardDetector:
    def __init__(self, model_path: Union[str, Path] = None):
        self.model_path = Path(model_path) if model_path else None
        self.model = None
        self.is_custom_model = False
        self.class_names = []
        self.status_message = ""

        self._initialize_model()

    def _initialize_model(self):
        """Attempts to load the trained YOLOv8 model."""
        if not ULTRALYTICS_AVAILABLE:
            self.status_message = "Ultralytics package not installed. Running in Simulation/Demo Mode."
            return

        if self.model_path and self.model_path.exists():
            try:
                self.model = YOLO(str(self.model_path))
                self.is_custom_model = True
                self.class_names = list(self.model.names.values()) if hasattr(self.model, "names") else []
                self.status_message = f"Loaded trained weights from: {self.model_path.name}"
            except Exception as e:
                self.status_message = f"Failed to load weights at {self.model_path}: {e}. Falling back to demo mode."
                self.model = None
        else:
            self.status_message = f"No trained weights found at '{self.model_path}'. Running in Demo Mode with simulated construction hazards."

    def is_ready(self) -> bool:
        return self.model is not None

    def detect(self, image: Union[Image.Image, np.ndarray], conf_threshold: float = 0.35, iou_threshold: float = 0.45) -> List[Dict[str, Any]]:
        """
        Run inference on the image and return detected hazards.
        Returns:
            List of dicts: [{'label': str, 'confidence': float, 'bbox': [x1, y1, x2, y2]}]
        """
        if self.is_ready():
            return self._detect_with_yolo(image, conf_threshold, iou_threshold)
        else:
            return self._detect_mock(image, conf_threshold)

    def _detect_with_yolo(self, image: Union[Image.Image, np.ndarray], conf: float, iou: float) -> List[Dict[str, Any]]:
        """Runs actual YOLO inference."""
        # Convert PIL to RGB if needed
        if isinstance(image, Image.Image):
            image = image.convert("RGB")

        results = self.model.predict(
            source=image,
            conf=conf,
            iou=iou,
            verbose=False
        )

        detections = []
        if len(results) > 0:
            result = results[0]
            boxes = result.boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    label = self.model.names.get(cls_id, f"hazard_{cls_id}")
                    confidence = float(box.conf[0].item())
                    coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    detections.append({
                        "label": label,
                        "confidence": round(confidence, 4),
                        "bbox": [round(c, 1) for c in coords]
                    })
        return detections

    def _detect_mock(self, image: Union[Image.Image, np.ndarray], conf: float) -> List[Dict[str, Any]]:
        """
        Simulation mode: Returns representative hazards on the image
        so the system, risk matrix, and PDF reports can be demonstrated
        even before the user copies their custom best.pt weights.
        """
        if isinstance(image, Image.Image):
            w, h = image.size
        elif isinstance(image, np.ndarray):
            h, w = image.shape[:2]
        else:
            w, h = 800, 600

        # Generate sample plausible construction site detections
        simulated_hazards = [
            {
                "label": "no_helmet",
                "confidence": 0.88,
                "bbox": [int(w * 0.35), int(h * 0.15), int(w * 0.50), int(h * 0.32)]
            },
            {
                "label": "no_vest",
                "confidence": 0.82,
                "bbox": [int(w * 0.32), int(h * 0.30), int(w * 0.55), int(h * 0.60)]
            },
            {
                "label": "missing_guardrail",
                "confidence": 0.74,
                "bbox": [int(w * 0.65), int(h * 0.40), int(w * 0.95), int(h * 0.75)]
            },
            {
                "label": "unsafe_ladder",
                "confidence": 0.69,
                "bbox": [int(w * 0.08), int(h * 0.45), int(w * 0.28), int(h * 0.90)]
            }
        ]

        # Filter by requested confidence threshold
        return [h for h in simulated_hazards if h["confidence"] >= conf]
