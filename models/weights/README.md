# Model Weights Directory

Place your trained YOLOv8 model weights file in this directory.

### Quick Deployment Steps:
1. Copy your trained `.pt` file (typically saved by YOLOv8 at `runs/detect/train/weights/best.pt`):
   ```bash
   cp /path/to/your/trained/runs/detect/train/weights/best.pt ./models/weights/best.pt
   ```
2. Ensure the filename is named:
   ```text
   best.pt
   ```
3. Alternatively, you can upload `best.pt` directly inside the running Streamlit web application via the **"Upload Custom Weights (.pt)"** tool in the sidebar!

### Custom Class Names & Risk Rules:
When your YOLOv8 model is loaded, the system automatically reads your model's class dictionary (`model.names`).
If you need to customize the Likelihood, Severity, OSHA standard, or mitigation recommendations for your specific class labels, edit `config.py`:
```python
HAZARD_KNOWLEDGE_BASE = {
    "your_custom_class_label": {
        "title": "Human Readable Hazard Name",
        "category": "PPE / Fall Hazard / Access",
        "default_likelihood": 4,   # 1 (Rare) to 5 (Almost Certain)
        "default_severity": 4,     # 1 (Negligible) to 5 (Catastrophic)
        "standard_ref": "OSHA 1926.xxx",
        "recommendation": "Corrective action..."
    }
}
```
