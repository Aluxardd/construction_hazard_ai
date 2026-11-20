"""
PPE (Personal Protective Equipment) Detection Engine for Construction Sites.
Supports trained YOLOv8 models (.pt weights) via Ultralytics.
Focuses exclusively on detecting the presence or absence of safety equipment.
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


class PPEDetector:
    """Detects Personal Protective Equipment (PPE) on construction workers."""
    
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
            self.status_message = f"No trained weights found at '{self.model_path}'. Running in Demo Mode with simulated PPE detections."

    def is_ready(self) -> bool:
        return self.model is not None

    def detect(self, image: Union[Image.Image, np.ndarray], conf_threshold: float = 0.30, iou_threshold: float = 0.45) -> List[Dict[str, Any]]:
        """
        Run inference on the image and return detected PPE items.
        
        Returns:
            List of dicts: [{'label': str, 'confidence': float, 'bbox': [x1, y1, x2, y2], 'type': 'ppe_item' or 'worker'}]
        """
        if self.is_ready():
            return self._detect_with_yolo(image, conf_threshold, iou_threshold)
        else:
            return self._detect_mock(image, conf_threshold)

    def _detect_with_yolo(self, image: Union[Image.Image, np.ndarray], conf: float, iou: float) -> List[Dict[str, Any]]:
        """Runs actual YOLO inference for PPE detection."""
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
                    label = self.model.names.get(cls_id, f"ppe_{cls_id}")
                    confidence = float(box.conf[0].item())
                    coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Classify as PPE item or worker
                    ppe_type = self._classify_ppe_type(label)
                    
                    detections.append({
                        "label": label,
                        "confidence": round(confidence, 4),
                        "bbox": [round(c, 1) for c in coords],
                        "type": ppe_type
                    })
        return detections

    def _classify_ppe_type(self, label: str) -> str:
        """Classify detection as PPE item or worker."""
        worker_labels = ["person", "worker"]
        if any(worker in label.lower() for worker in worker_labels):
            return "worker"
        return "ppe_item"

    def _detect_mock(self, image: Union[Image.Image, np.ndarray], conf: float) -> List[Dict[str, Any]]:
        """
        Simulation mode: Returns representative PPE detections on the image
        for demonstration before custom weights are loaded.
        """
        if isinstance(image, Image.Image):
            w, h = image.size
        elif isinstance(image, np.ndarray):
            h, w = image.shape[:2]
        else:
            w, h = 800, 600

        # Generate sample plausible PPE detections
        simulated_ppe = [
            {
                "label": "helmet",
                "confidence": 0.92,
                "bbox": [int(w * 0.35), int(h * 0.12), int(w * 0.50), int(h * 0.25)],
                "type": "ppe_item"
            },
            {
                "label": "vest",
                "confidence": 0.88,
                "bbox": [int(w * 0.32), int(h * 0.28), int(w * 0.55), int(h * 0.58)],
                "type": "ppe_item"
            },
            {
                "label": "gloves",
                "confidence": 0.85,
                "bbox": [int(w * 0.28), int(h * 0.52), int(w * 0.38), int(h * 0.62)],
                "type": "ppe_item"
            },
            {
                "label": "boots",
                "confidence": 0.80,
                "bbox": [int(w * 0.38), int(h * 0.75), int(w * 0.52), int(h * 0.92)],
                "type": "ppe_item"
            },
            {
                "label": "goggles",
                "confidence": 0.75,
                "bbox": [int(w * 0.40), int(h * 0.15), int(w * 0.48), int(h * 0.22)],
                "type": "ppe_item"
            }
        ]

        # Filter by requested confidence threshold
        return [p for p in simulated_ppe if p["confidence"] >= conf]
