# FastAPI Backend - AI-Based Multimodal OA Screening System

This is the backend service for the **AI-Based Multimodal Osteoarthritis Screening and Risk Assessment System**.

## Features
- **FastAPI** with automatic interactive API documentation (`/docs` and `/redoc`).
- **OpenCV & Computer Vision** prototype modules for Knee X-ray joint space analysis and Gait movement asymmetry calculation.
- **Multimodal Fusion Engine** combining image findings, video movement, and clinical scores.
- **Digital Screening Report** generator providing printable HTML reports.
- **Healthcare Worker Review & Verification** workflow.
- **Cloud Deployment Ready** with `$PORT` support and `0.0.0.0` binding.

## Setup Instructions

### 1. Create and Activate Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Base: `http://127.0.0.1:8000`
- Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`
- Mounted Frontend: `http://127.0.0.1:8000/app`

## Production Deployment
The backend respects the `$PORT` environment variable:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Security & Compliance Note
This is a research prototype. Before deploying into clinical healthcare environments:
- Enforce TLS/HTTPS encryption.
- Implement JWT/OAuth2 authentication and role-based access control (RBAC).
- Implement HIPAA/GDPR-compliant data storage and audit logging.
- Store sensitive patient health information in encrypted healthcare databases.
