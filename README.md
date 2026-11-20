# Construction Safety AI

React, FastAPI and Ultralytics YOLO provide image-based PPE detection and downloadable detection summaries. Results are model predictions, not a safety or compliance assessment; a qualified person must review them.

## Run locally

From the project directory:

```powershell
python -m pip install -r requirements-api.txt
Set-Location frontend
npm install
Set-Location ..
python -m uvicorn backend:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
Set-Location frontend
npm run dev
```

Open http://localhost:3000. Alternatively, run `run-full-stack.bat` from the project directory. The Vite development server proxies `/api` to port 8000. A production web server must provide the same proxy, including for reports and the sample image.

Upload one or more photographs and select **Analyze Images**. The included sample is a synthetic illustration, not a realistic PPE test image, and may produce no detections. Check model readiness and classes at http://localhost:8000/health; API documentation is at http://localhost:8000/docs. If the weights cannot be loaded, inference returns an error rather than simulated results.

## Model and interpretation

The backend loads `models/weights/best.pt` using Ultralytics. The supplied `exp.pt` is byte-identical to it. The checkpoint specifies a 640-pixel inference size and these class IDs:

| ID | Label | ID | Label |
|---:|---|---:|---|
| 0 | helmet | 6 | no_helmet |
| 1 | gloves | 7 | no_goggle |
| 2 | vest | 8 | no_gloves |
| 3 | boots | 9 | no_boots |
| 4 | goggles | 10 | forklift |
| 5 | Person | 11 | no_vest |

Classes are read from the loaded checkpoint. Replace `best.pt` and restart the backend to use different compatible trusted weights. Do not load untrusted `.pt` files.

The `no_*` classes are model predictions, not confirmed violations. No conclusion is made from the absence of a detection; positive PPE detections are not associated with individual workers or verified against task requirements. The system does not compute a compliance percentage or a 5×5 risk score. Images with occlusion, unusual viewpoints or unfamiliar scenes can produce missed or false detections.

Images are EXIF-oriented and converted to RGB before being passed to Ultralytics, which performs its own resizing, normalization and non-maximum suppression. Returned `bbox` values are original oriented image pixel coordinates `[x1, y1, x2, y2]`; boxes are drawn directly on that image before display. Confidence and IoU controls are submitted as multipart form fields. Single and batch results include image dimensions, inference time, labels, confidence and coordinates.

## Diagnostics and tests

Backend startup logs report model readiness and labels. For local debugging, run Uvicorn with `--log-level debug` to log image dimensions, inference time and detection details; do not enable debug logging for sensitive production images. The API does not include image contents in logs.

```powershell
python -m unittest discover -s tests -v
Set-Location frontend
npm run build
```

Realistic, labelled construction images are needed to measure accuracy and verify behavior for specific PPE, multiple workers and occlusion. The training dataset is not included in this repository.
