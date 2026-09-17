"""
FastAPI Backend Application for AI-Based Multimodal Osteoarthritis Screening
"""

import os
import uvicorn
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

from app.utils.preprocessing import calculate_bmi, generate_patient_id
from app.services.xray_service import process_xray_upload, UPLOAD_DIR_XRAY
from app.services.gait_service import process_gait_upload, UPLOAD_DIR_MOVEMENT
from app.services.report_service import generate_screening_report, generate_printable_html_report
from app.ai.fusion import fuse_multimodal_assessment

app = FastAPI(
    title="AI-Based Multimodal Osteoarthritis Screening API",
    description=(
        "Research & Educational Prototype for Multimodal Knee Osteoarthritis Screening. "
        "Integrates knee X-ray heuristics, gait/movement analysis, and patient clinical symptoms. "
        "NOTE: Prototype demonstration only. Does not provide a formal medical diagnosis."
    ),
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR_XRAY, exist_ok=True)
os.makedirs(UPLOAD_DIR_MOVEMENT, exist_ok=True)

# Mount static files for uploads
app.mount("/uploads/xray", StaticFiles(directory=UPLOAD_DIR_XRAY), name="uploads_xray")
app.mount("/uploads/movement", StaticFiles(directory=UPLOAD_DIR_MOVEMENT), name="uploads_movement")

# In-memory screening store for demonstration dashboard statistics
SCREENING_RECORDS: Dict[str, Dict[str, Any]] = {}

# Prepopulate a few realistic demo records for the dashboard metrics
_DEMO_INITIAL_RECORDS = [
    {
        "patient_id": "OA-2026-1001",
        "risk_level": "Higher Risk",
        "verification_status": "Referred",
        "created_at": "2026-09-15 10:30:00"
    },
    {
        "patient_id": "OA-2026-1002",
        "risk_level": "Moderate Risk",
        "verification_status": "Reviewed",
        "created_at": "2026-09-16 11:15:00"
    },
    {
        "patient_id": "OA-2026-1003",
        "risk_level": "Lower Risk",
        "verification_status": "Reviewed",
        "created_at": "2026-09-16 14:40:00"
    },
    {
        "patient_id": "OA-2026-1004",
        "risk_level": "Moderate Risk",
        "verification_status": "Pending",
        "created_at": "2026-09-17 09:20:00"
    }
]

for rec in _DEMO_INITIAL_RECORDS:
    SCREENING_RECORDS[rec["patient_id"]] = {
        "patient": {"patient_id": rec["patient_id"], "name": f"Demo Patient {rec['patient_id'][-4:]}"},
        "fusion": {"overall_risk": rec["risk_level"]},
        "verification": {"status": rec["verification_status"], "comments": "Initial baseline record"}
    }


@app.get("/", tags=["General"])
async def root():
    return {
        "system": "AI-Based Multimodal Osteoarthritis Screening and Risk Assessment System",
        "version": "1.0.0",
        "status": "online",
        "type": "Prototype / Demonstration",
        "disclaimer": "AI prototype screening indication for research demonstration only. Not a medical diagnosis.",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["General"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_screenings": len(SCREENING_RECORDS)
    }


@app.get("/api/stats", tags=["Dashboard"])
async def get_dashboard_stats():
    """
    Returns aggregate screening metrics for the healthcare dashboard.
    """
    total = len(SCREENING_RECORDS)
    higher_risk = sum(1 for r in SCREENING_RECORDS.values() if r.get("fusion", {}).get("overall_risk") == "Higher Risk")
    moderate_risk = sum(1 for r in SCREENING_RECORDS.values() if r.get("fusion", {}).get("overall_risk") == "Moderate Risk")
    lower_risk = sum(1 for r in SCREENING_RECORDS.values() if r.get("fusion", {}).get("overall_risk") == "Lower Risk")

    pending_reviews = sum(1 for r in SCREENING_RECORDS.values() if r.get("verification", {}).get("status", "Pending") == "Pending")
    referrals = sum(1 for r in SCREENING_RECORDS.values() if r.get("verification", {}).get("status") == "Referred")

    return {
        "total_screenings": total,
        "higher_risk": higher_risk,
        "moderate_risk": moderate_risk,
        "lower_risk": lower_risk,
        "pending_reviews": pending_reviews,
        "referrals": referrals,
        "risk_distribution": {
            "Higher Risk": higher_risk,
            "Moderate Risk": moderate_risk,
            "Lower Risk": lower_risk
        }
    }


@app.post("/api/xray", tags=["Screening Modules"])
async def screen_xray(xray_file: UploadFile = File(...)):
    """
    Analyze knee X-ray independently.
    """
    return await process_xray_upload(xray_file)


@app.post("/api/gait", tags=["Screening Modules"])
async def screen_gait(movement_file: UploadFile = File(...)):
    """
    Analyze knee movement / walking video independently.
    """
    return await process_gait_upload(movement_file)


@app.post("/api/screen", tags=["Multimodal Screening"])
async def screen_patient(
    # Patient Demographics
    patient_name: str = Form("Demo Patient"),
    patient_id: Optional[str] = Form(None),
    age: int = Form(55),
    sex: str = Form("Female"),
    height: float = Form(165.0),
    weight: float = Form(72.0),
    # Clinical history & duration
    previous_injury: bool = Form(False),
    oa_history: bool = Form(False),
    symptom_duration: str = Form("6-12 months"),
    # Clinical Symptoms
    pain_score: int = Form(6),
    morning_stiffness: bool = Form(True),
    joint_stiffness: bool = Form(True),
    swelling: bool = Form(False),
    walking_difficulty: bool = Form(True),
    stairs_difficulty: bool = Form(True),
    standing_difficulty: bool = Form(False),
    bending_difficulty: bool = Form(True),
    # Uploaded Files
    xray_file: UploadFile = File(...),
    movement_file: UploadFile = File(...)
):
    """
    Comprehensive multimodal screening endpoint.
    Accepts patient information, clinical symptoms, knee X-ray, and gait movement video.
    Returns synthesized multimodal assessment and risk indication.
    """
    # 1. Assign or generate Patient ID
    assigned_id = patient_id if patient_id and patient_id.strip() else generate_patient_id()

    # 2. Calculate BMI
    bmi_value, bmi_category = calculate_bmi(height, weight)

    # 3. Process X-Ray
    xray_response = await process_xray_upload(xray_file)
    xray_result = xray_response["result"]

    # 4. Process Movement Video
    gait_response = await process_gait_upload(movement_file)
    gait_result = gait_response["result"]

    # 5. Compile Clinical Data
    clinical_data = {
        "age": age,
        "sex": sex,
        "height_cm": height,
        "weight_kg": weight,
        "bmi": bmi_value,
        "bmi_category": bmi_category,
        "pain_score": pain_score,
        "morning_stiffness": morning_stiffness,
        "joint_stiffness": joint_stiffness,
        "swelling": swelling,
        "walking_difficulty": walking_difficulty,
        "stairs_difficulty": stairs_difficulty,
        "standing_difficulty": standing_difficulty,
        "bending_difficulty": bending_difficulty,
        "previous_injury": previous_injury,
        "oa_history": oa_history,
        "symptom_duration": symptom_duration
    }

    # 6. Multimodal Fusion
    fusion_result = fuse_multimodal_assessment(
        xray_result=xray_result,
        clinical_data=clinical_data,
        gait_result=gait_result
    )

    # 7. Assemble Record
    screening_record = {
        "screening_id": f"SCR-{assigned_id}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient": {
            "patient_id": assigned_id,
            "name": patient_name,
            "age": age,
            "sex": sex,
            "height_cm": height,
            "weight_kg": weight,
            "bmi": bmi_value,
            "bmi_category": bmi_category
        },
        "clinical": clinical_data,
        "xray": {
            "file_url": xray_response["file_url"],
            "filename": xray_response["filename"],
            "result": xray_result
        },
        "gait": {
            "file_url": gait_response["file_url"],
            "filename": gait_response["filename"],
            "result": gait_result
        },
        "fusion": fusion_result,
        "verification": {
            "status": "Pending",
            "comments": "",
            "verified_by": "Pending Review",
            "verified_at": None
        },
        "disclaimer": "Prototype AI screening indication for research demonstration only. Not a medical diagnosis."
    }

    # Save to in-memory store
    SCREENING_RECORDS[assigned_id] = screening_record

    return screening_record


@app.post("/api/verify", tags=["Healthcare Worker Verification"])
async def verify_screening(
    patient_id: str = Form(...),
    action: str = Form(...),  # 'Reviewed' (Accept), 'Flagged', 'Referred'
    comments: str = Form(""),
    verified_by: str = Form("Healthcare Worker")
):
    """
    Update healthcare worker review and verification status.
    """
    if patient_id not in SCREENING_RECORDS:
        # Create a record if not found (e.g. testing)
        SCREENING_RECORDS[patient_id] = {
            "patient": {"patient_id": patient_id},
            "fusion": {"overall_risk": "Moderate Risk"},
            "verification": {}
        }

    valid_actions = {"Reviewed", "Flagged", "Referred", "Pending"}
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid verification status. Allowed: {valid_actions}")

    SCREENING_RECORDS[patient_id]["verification"] = {
        "status": action,
        "comments": comments.strip(),
        "verified_by": verified_by,
        "verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return {
        "message": f"Verification status updated to '{action}'",
        "patient_id": patient_id,
        "verification": SCREENING_RECORDS[patient_id]["verification"]
    }


@app.post("/api/report", tags=["Digital Report"])
async def generate_report_endpoint(
    patient_id: str = Form(None),
    report_json: Optional[str] = Form(None)
):
    """
    Generate digital screening report. Can return printable HTML or structured JSON.
    """
    import json
    data = None
    if patient_id and patient_id in SCREENING_RECORDS:
        data = SCREENING_RECORDS[patient_id]
    elif report_json:
        try:
            data = json.loads(report_json)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON in report_json")

    if not data:
        raise HTTPException(status_code=404, detail="Screening record not found.")

    report = generate_screening_report(data)
    printable_html = generate_printable_html_report(report)

    return {
        "report_id": report["report_id"],
        "generated_at": report["generated_at"],
        "report_data": report,
        "printable_html": printable_html
    }


@app.get("/api/report/{patient_id}/print", response_class=HTMLResponse, tags=["Digital Report"])
async def print_report_view(patient_id: str):
    """
    Direct printable HTML endpoint for a patient's screening report.
    """
    if patient_id not in SCREENING_RECORDS:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")

    record = SCREENING_RECORDS[patient_id]
    report = generate_screening_report(record)
    return HTMLResponse(content=generate_printable_html_report(report))


# Mount the frontend directory if it exists, so the whole app can run from a single FastAPI server
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend_app")

# Mount demo directory for serving sample assets
DEMO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "demo"))
if os.path.exists(DEMO_DIR):
    app.mount("/demo", StaticFiles(directory=DEMO_DIR), name="demo_files")


if __name__ == "__main__":
    # Support cloud deployment with dynamic $PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting OA Screening System API on 0.0.0.0:{port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
