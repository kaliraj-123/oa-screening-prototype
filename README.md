# AI-Based Multimodal Osteoarthritis Screening and Risk Assessment System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg)](https://opencv.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end, multimodal research prototype designed for healthcare workers to perform rapid, AI-assisted screening and risk assessment of knee osteoarthritis (OA) by combining **radiological imaging (knee X-rays)**, **functional biomechanics (walking/movement video)**, and **patient-reported clinical symptomatology**.

> [!IMPORTANT]
> **MEDICAL DISCLAIMER & PROTOTYPE NOTICE:**  
> This application is a college/research demonstration prototype. It does **NOT** provide a medical diagnosis. The system outputs "AI-assisted screening indications", "risk indications", and consistently advises that **"further clinical evaluation is recommended."** It must not be used as a standalone diagnostic device.

---

## Table of Contents
1. [Key Features](#1-key-features)
2. [System Architecture](#2-system-architecture)
3. [Folder Structure](#3-folder-structure)
4. [Technologies Used](#4-technologies-used)
5. [Installation & Setup](#5-installation--setup)
6. [Running the Backend](#6-running-the-backend)
7. [Running the Frontend](#7-running-the-frontend)
8. [REST API Endpoints](#8-rest-api-endpoints)
9. [Sample API Request](#9-sample-api-request)
10. [Cloud Deployment Instructions](#10-cloud-deployment-instructions)
11. [Prototype Limitations](#11-prototype-limitations)
12. [Healthcare Worker Verification & Reporting](#12-healthcare-worker-verification--reporting)
13. [License](#13-license)

---

## 1. Key Features

- **Multimodal AI Fusion**: Synthesizes structural findings (Knee X-ray), functional biomechanical movement (video gait asymmetry), and clinical symptomatology (pain, stiffness, mobility restrictions, BMI, age) into a unified risk assessment.
- **Computer Vision X-Ray Assessment**: Evaluates image quality, tibiofemoral joint space narrowing proxies, and subchondral density gradients using OpenCV.
- **Kinematic Gait Video Analysis**: Extracts movement consistency, cadence variations, and bilateral movement asymmetry percentages from short walking clips.
- **Healthcare Worker Dashboard**: Interactive overview displaying aggregate statistics (Total Screenings, Higher/Moderate/Lower Risk distributions, Pending Reviews, Referrals) and dynamic Chart.js visualizations.
- **Clinical Verification Workflow**: In-app decision support enabling healthcare workers to **Accept Result (Reviewed)**, **Flag for Review**, or **Refer to Clinician** with custom notes.
- **Printable Digital Screening Report**: Generates a standardized clinical report with full patient history, radiological findings, gait metrics, and clinician signature block ready for physical printing or PDF export.
- **Ready-to-Use Synthetic Demo Assets**: Includes synthetic knee radiograph and gait video files allowing instant, zero-setup demonstration.

---

## 2. System Architecture

```
+-------------------------------------------------------------------------+
|                           Healthcare Worker UI                          |
|         (Bootstrap 5 + Chart.js + Responsive Medical Dashboard)         |
+-------------------------------------------------------------------------+
         |                                                 ^
         | [1] Patient Data + X-Ray + Video                | [5] Multimodal Report
         v                                                 |
+-------------------------------------------------------------------------+
|                         FastAPI Backend (app.main)                      |
|                  (CORS Enabled, Swagger Docs at /docs)                  |
+-------------------------------------------------------------------------+
    |                    |                                |
    v                    v                                v
+-------------+   +-------------------+    +------------------------------+
| X-Ray AI    |   | Gait / Movement   |    | Clinical Symptoms            |
| (xray_model)|   | AI (gait_model)   |    | (Pain, Stiffness, BMI, etc.) |
| OpenCV      |   | OpenCV Kinematics |    +------------------------------+
| Features    |   | Asymmetry Calc    |                   |
+-------------+   +-------------------+                   |
       \                    |                            /
        \                   |                           /
         v                  v                          v
      +---------------------------------------------------+
      |             Multimodal Fusion Engine              |
      |                   (fusion.py)                     |
      |   Weighting: 40% X-Ray + 35% Clinical + 25% Gait  |
      +---------------------------------------------------+
                            |
                            v
      +---------------------------------------------------+
      |            Overall OA Risk Indication             |
      |   "Lower Risk" | "Moderate Risk" | "Higher Risk"  |
      +---------------------------------------------------+
```

---

## 3. Folder Structure

```
oa-screening-prototype/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application & endpoints
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── xray_model.py           # Prototype X-ray computer vision model
│   │   │   ├── gait_model.py           # Prototype video gait & asymmetry model
│   │   │   └── fusion.py               # Multimodal risk synthesis engine
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── xray_service.py         # File persistence & X-ray processing
│   │   │   ├── gait_service.py         # Video sampling & gait processing
│   │   │   └── report_service.py       # Printable HTML & JSON report generation
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── preprocessing.py        # Validation, CLAHE enhancement, BMI
│   ├── uploads/
│   │   ├── xray/                       # Storage for uploaded knee radiographs
│   │   └── movement/                   # Storage for uploaded movement videos
│   ├── requirements.txt                # Python backend dependencies
│   └── README.md
│
├── frontend/
│   ├── index.html                      # Healthcare worker interface
│   ├── css/
│   │   └── style.css                   # Medical dashboard stylesheet & print rules
│   ├── js/
│   │   └── app.js                      # UI logic, Chart.js, API client
│   └── assets/
│       └── images/                     # Graphic assets and icons
│
├── demo/
│   ├── README.md                       # Sample data documentation & guidelines
│   ├── generate_demo_assets.py         # Synthetic demo assets generator script
│   ├── sample_knee_xray.png            # Synthetic AP knee radiograph
│   └── sample_movement.mp4             # Synthetic cyclic gait movement video
│
├── .gitignore
├── README.md                           # Main documentation (this file)
└── LICENSE                             # MIT License
```

---

## 4. Technologies Used

- **Backend**:
  - Python 3.11+
  - FastAPI (High-performance async web framework)
  - Uvicorn (ASGI server)
  - OpenCV (Computer vision, image enhancement, video frame extraction)
  - NumPy (Array operations, signal processing)
  - Pillow (Image decoding and transformation)
  - python-multipart (Streaming multipart/form-data file uploads)
- **Frontend**:
  - HTML5 & CSS3
  - Modern JavaScript (ES6+, Fetch API)
  - Bootstrap 5.3 (Responsive layout and medical dashboard components)
  - Bootstrap Icons (Healthcare and diagnostic iconography)
  - Chart.js (Interactive risk distribution doughnut chart)

---

## 5. Installation & Setup

### Prerequisites
- Python 3.11 or higher installed on your system.
- Standard modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox, or Safari).

### Clone or Extract Project
Open a terminal in the root directory `oa-screening-prototype`:

```bash
cd oa-screening-prototype
```

### Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

*(Optional)* Regenerate synthetic demonstration assets if needed:
```bash
python demo/generate_demo_assets.py
```

---

## 6. Running the Backend

Start the FastAPI application with Uvicorn:

```bash
# Windows (PowerShell or Command Prompt)
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Backend API Base**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **System Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 7. Running the Frontend

You can run the frontend in either of two convenient ways:

### Option A: Via FastAPI Built-in Static Server (Recommended)
The backend automatically serves the frontend on the same port:
- Open your browser and navigate to: **[http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)**

### Option B: Standalone Web Server
You can open `frontend/index.html` directly or serve it with Python's HTTP server:
```bash
cd frontend
python -m http.server 3000
```
Then visit: **[http://127.0.0.1:3000](http://127.0.0.1:3000)**

> **Frontend Configuration:**
> If your backend is hosted on a different URL (or port), open `frontend/js/app.js` and edit line 12:
> ```javascript
> const API_URL = "http://127.0.0.1:8000"; // Replace with your deployed backend URL
> ```

---

## 8. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status, version, and disclaimer |
| `GET` | `/health` | System health check and total records count |
| `GET` | `/api/stats` | Aggregate dashboard metrics and risk distribution |
| `POST` | `/api/screen` | Multimodal screening (Demographics + Symptoms + X-Ray + Video) |
| `POST` | `/api/xray` | Dedicated standalone Knee X-Ray analysis |
| `POST` | `/api/gait` | Dedicated standalone Knee Movement/Gait video analysis |
| `POST` | `/api/verify` | Healthcare worker review action (`Reviewed`, `Flagged`, `Referred`) |
| `POST` | `/api/report` | Generate structured JSON and printable HTML report |
| `GET` | `/api/report/{patient_id}/print` | Direct browser-printable HTML screening report |

---

## 9. Sample API Request

You can test the multimodal screening endpoint directly using `cURL`:

```bash
curl -X POST "http://127.0.0.1:8000/api/screen" \
  -F "patient_name=Jane Doe" \
  -F "patient_id=OA-2026-0042" \
  -F "age=58" \
  -F "sex=Female" \
  -F "height=162.0" \
  -F "weight=74.0" \
  -F "previous_injury=true" \
  -F "oa_history=false" \
  -F "symptom_duration=6-12 months" \
  -F "pain_score=6" \
  -F "morning_stiffness=true" \
  -F "joint_stiffness=true" \
  -F "swelling=false" \
  -F "walking_difficulty=true" \
  -F "stairs_difficulty=true" \
  -F "standing_difficulty=false" \
  -F "bending_difficulty=true" \
  -F "xray_file=@demo/sample_knee_xray.png" \
  -F "movement_file=@demo/sample_movement.mp4"
```

### Sample Response JSON:
```json
{
  "screening_id": "SCR-OA-2026-0042",
  "created_at": "2026-09-17 12:30:00",
  "patient": {
    "patient_id": "OA-2026-0042",
    "name": "Jane Doe",
    "age": 58,
    "sex": "Female",
    "height_cm": 162.0,
    "weight_kg": 74.0,
    "bmi": 28.2,
    "bmi_category": "Overweight"
  },
  "xray": {
    "result": {
      "image_quality": "Good",
      "abnormality_detected": true,
      "severity": "Moderate",
      "confidence": 0.82
    }
  },
  "gait": {
    "result": {
      "movement_quality": "Fair",
      "movement_risk": "Moderate",
      "asymmetry": 0.15,
      "asymmetry_percentage": "15.0%",
      "movement_consistency": 0.78
    }
  },
  "fusion": {
    "overall_risk": "Higher Risk",
    "risk_score": 71.4,
    "primary_recommendation": "Further clinical evaluation recommended.",
    "explanations": [
      "X-ray analysis indicated moderate joint space asymmetry and subchondral density changes.",
      "Elevated self-reported pain score (6/10) during knee loading.",
      "Active clinical symptoms present: morning stiffness, joint stiffness.",
      "Multiple mobility restrictions reported (3 functional difficulties).",
      "Gait analysis detected notable bilateral movement asymmetry (15.0%)."
    ]
  },
  "verification": {
    "status": "Pending",
    "comments": ""
  }
}
```

---

## 10. Cloud Deployment Instructions

The backend is cloud-native and adheres to Twelve-Factor app principles. It automatically reads the `$PORT` environment variable provided by cloud platforms:

### Deploying to Render / Railway / Heroku
1. Connect your Git repository.
2. Build Command:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Start Command:
   ```bash
   uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
   ```
4. Update `API_URL` in `frontend/js/app.js` with your assigned public cloud domain (e.g. `https://oa-screening.onrender.com`).

---

## 11. Prototype Limitations

1. **Demonstration Heuristics**: The computer vision algorithms in this first release are OpenCV feature-extraction demonstration models. They are engineered to demonstrate workflow feasibility rather than medical-grade clinical accuracy.
2. **Modular Deep Learning Interface**: The codebase provides abstract interfaces (`BaseXRayModel`, `BaseGaitModel`) structured so that clinical-grade deep learning models (such as an EfficientNet trained on Kellgren-Lawrence graded radiographs and MediaPipe 3D pose estimation) can be dropped in without changing the API contract.
3. **Production Security Considerations**: A clinical deployment requires:
   - HTTPS/TLS termination
   - OAuth2/JWT authentication and Role-Based Access Control (RBAC)
   - HIPAA / GDPR compliant encryption at rest and in transit
   - Complete de-identification pipelines for DICOM images

---

## 12. Healthcare Worker Verification & Reporting

1. **Healthcare Worker Review**:
   - **[ Accept Result ]**: Marks status as `Reviewed`.
   - **[ Flag for Review ]**: Flags findings when clinical symptoms deviate from imaging evidence.
   - **[ Refer to Clinician ]**: Immediately designates the patient for an orthopedic or rheumatology referral.
2. **Digital Screening Report**:
   - Printable HTML format with custom print stylesheets.
   - Includes hospital letterhead styling, patient ID badge, radiological findings, kinematic gait measurements, and clinician signature block.
   - Triggers native browser print preview or "Save as PDF".

---

## 13. License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for terms.
