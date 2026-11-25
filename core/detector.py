"""
PPE (Personal Protective Equipment) Detection Engine for Construction Sites.
Supports trained YOLOv8 models (.pt weights) via Ultralytics.
Focuses exclusively on detecting the presence or absence of safety equipment.
"""

from pathlib import Path
from typing import List, Dict, Any, Union
from PIL import Image
import numpy as np

from core.label_mapping import classify_detection_type

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
            self.status_message = "Ultralytics package is not installed."
            return

        if self.model_path and self.model_path.exists():
            try:
                self.model = YOLO(str(self.model_path))
                self.is_custom_model = True
                self.class_names = list(self.model.names.values()) if hasattr(self.model, "names") else []
                self.status_message = f"Loaded trained weights from: {self.model_path.name}"
            except Exception as e:
                self.status_message = f"Failed to load model weights: {e}"
                self.model = None
        else:
            self.status_message = "Trained model weights were not found."

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
        raise RuntimeError(self.status_message or "Detection model is unavailable.")

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
                    label = result.names[cls_id]
                    confidence = float(box.conf[0].item())
                    coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                    
                    # Classify as PPE item or worker
                    ppe_type = self._classify_ppe_type(label)
                    
                    detections.append({
                        "label": label,
                        "class_id": cls_id,
                        "confidence": round(confidence, 4),
                        "bbox": [round(c, 1) for c in coords],
                        "type": ppe_type
                    })
        return detections

    def _classify_ppe_type(self, label: str) -> str:
        """Classify detection as PPE item, missing PPE flag, worker, or vehicle hazard."""
        return classify_detection_type(label)
