# 🏗️ Construction Safety AI - React + FastAPI Application

**AI-Powered Hazard Detection & 5×5 Risk Assessment**

**Department of Computer Science — BSc (Hons) Final Year Project**  
*Student:* **Serghei Coceban**  
*Institutions:* **University of Bolton & Regent College London**  
*Stack:* **React 18 (Frontend) + FastAPI (Backend) + YOLOv8 (Detection)**

---

## 📋 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements-api.txt
cd frontend && npm install && cd ..
```

### 2. Start Application
**Windows:**
```bash
run-full-stack.bat
```

**macOS/Linux:**
```bash
./run-full-stack.sh
```

### 3. Open Browser
Navigate to: **http://localhost:3000**

---

## 🏗️ Application Overview

This system provides automated construction safety analysis by:
1. **Uploading** site photographs
2. **Detecting** hazards with YOLOv8 deep learning
3. **Assessing** risk using a 5×5 Likelihood × Severity matrix (OSHA compliant)
4. **Generating** downloadable safety audit reports (HTML/PDF)

### Architecture
```
React Frontend (Port 3000)
        ↓↑ REST API (HTTP)
FastAPI Backend (Port 8000)
        ↓
YOLOv8 Detection + Risk Engine
```

---

## 📊 5×5 Risk Assessment Matrix

Risk Score = **Likelihood (1–5) × Severity (1–5)**

| Score | Tier | Action | Timeframe |
|:---:|:---:|:---|:---|
| **15–25** | 🔴 Critical | Immediate Work Stoppage | Instant |
| **10–14** | 🟠 High | Urgent Rectification | Within 1 hour |
| **5–9** | 🟡 Medium | Remedial Action | Current shift |
| **1–4** | 🟢 Low | Routine Monitoring | Standard supervision |

---

## 📁 Project Structure

```
construction_hazard_ai/
├── backend.py                     ← FastAPI REST API server
├── requirements-api.txt           ← Python dependencies
├── config.py                      ← Hazard knowledge base, OSHA rules
│
├── frontend/                      ← React application
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx               ← Main component
│       ├── App.css               ← Global styles
│       ├── main.jsx
│       └── components/           ← 7 reusable components
│           ├── ConfigPanel.jsx
│           ├── ImageUploader.jsx
│           ├── KPICard.jsx
│           ├── DetectionResults.jsx
│           ├── RiskMatrix.jsx
│           ├── HazardRegister.jsx
│           └── ReportGenerator.jsx
│
├── core/                          ← Detection & analysis
│   ├── detector.py               ← YOLOv8 inference
│   ├── risk_engine.py            ← Risk assessment
│   ├── visualizer.py             ← Image annotation
│   └── report_generator.py       ← PDF/HTML reports
│
├── models/weights/               ← YOLOv8 models
│   ├── best.pt                   ← Your trained model
│   └── exp.pt                    ← Alternative model
│
├── run-full-stack.bat            ← Windows startup
├── run-full-stack.sh             ← Unix startup
├── verify_setup.py               ← Verification script
│
├── 00_READ_ME_FIRST.md           ← Start here!
├── START_HERE.md                 ← Navigation guide
├── QUICKSTART.md                 ← 5-minute setup
├── REACT_README.md               ← Complete guide (50+ pages)
├── MIGRATION_GUIDE.md            ← Streamlit comparison
└── CONVERSION_SUMMARY.md         ← Technical details
```

---

## 🚀 Deploying Your Trained Model

### Step 1: Add Your Weights
Copy your trained YOLOv8 model:
```bash
cp /path/to/your/best.pt models/weights/best.pt
```

Or upload via UI: Config Panel → "Upload Custom Weights (.pt)"

### Step 2: Verify Classes (config.py)
Ensure your class names map to the hazard knowledge base:
```python
HAZARD_KNOWLEDGE_BASE = {
    "no_helmet": {
        "title": "Missing Hard Hat / Head Protection",
        "default_likelihood": 4,
        "default_severity": 4,
        "standard_ref": "OSHA 1926.100",
        "recommendation": "..."
    },
    # Add custom hazards here
}
```

### Step 3: Start Application
```bash
run-full-stack.bat    # Windows
./run-full-stack.sh   # macOS/Linux
```

---

## ✨ Features

✅ Image upload (single or batch)  
✅ YOLOv8 hazard detection  
✅ 5×5 risk matrix assessment  
✅ Annotated image display  
✅ KPI dashboard (6 metrics)  
✅ Hazard register (filterable table)  
✅ HTML & PDF report generation  
✅ Configuration management  
✅ Custom model weights upload  
✅ Demo mode (simulated detections)  
✅ Full REST API with Swagger docs  
✅ Responsive design  

---

## 🌐 Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | User interface |
| **Backend API** | http://localhost:8000 | REST API |
| **Swagger Docs** | http://localhost:8000/docs | Interactive API docs |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |

---

## 📚 Documentation

| Guide | Time | Purpose |
|-------|------|---------|
| **00_READ_ME_FIRST.md** | 5 min | Main entry point |
| **QUICKSTART.md** | 5 min | Quick setup |
| **REACT_README.md** | 20 min | Complete guide |
| **MIGRATION_GUIDE.md** | 10 min | Streamlit comparison |

---

## 🔧 Development

### Frontend
```bash
cd frontend
npm run dev              # Start dev server with hot reload
npm run build          # Production build
```

### Backend
```bash
python -m uvicorn backend:app --reload
```

---

## 🚢 Production Deployment

### Frontend (Vercel, Netlify, etc.)
```bash
cd frontend && npm run build  # Creates: frontend/dist/
```

### Backend (Render, Railway, etc.)
```bash
python -m uvicorn backend:app --host 0.0.0.0 --port 8000
```

---

## ✅ Verification

```bash
python verify_setup.py
```

Should show: `[OK] All verification checks passed!`

---

**📖 For detailed information, see: `00_READ_ME_FIRST.md`**
