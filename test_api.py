"""
Comprehensive API test suite for the OA Screening System.
Verifies all endpoints:
- GET /
- GET /health
- GET /api/stats
- POST /api/xray
- POST /api/gait
- POST /api/screen
- POST /api/verify
- POST /api/report
- GET /api/report/{patient_id}/print
"""

import os
import sys

# Add backend directory to path
backend_dir = os.path.abspath("backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all():
    print("=== Testing FastAPI Endpoints ===")

    # 1. GET / (Redirects to /app/) and GET /api
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (307, 302, 308), f"GET / redirect failed: {r.status_code}"
    print("[PASS] GET / -> Redirects to", r.headers.get("location"))

    r_api = client.get("/api")
    assert r_api.status_code == 200, f"GET /api failed: {r_api.status_code}"
    print("[PASS] GET /api ->", r_api.json().get("system"))

    # 2. GET /health
    r = client.get("/health")
    assert r.status_code == 200, f"GET /health failed: {r.status_code}"
    print("[PASS] GET /health ->", r.json())

    # 3. GET /api/stats
    r = client.get("/api/stats")
    assert r.status_code == 200, f"GET /api/stats failed: {r.status_code}"
    print("[PASS] GET /api/stats -> total:", r.json().get("total_screenings"))

    # 4. POST /api/xray
    with open("demo/sample_knee_xray.png", "rb") as f:
        r = client.post("/api/xray", files={"xray_file": ("sample_knee_xray.png", f, "image/png")})
    assert r.status_code == 200, f"POST /api/xray failed: {r.status_code}, {r.text}"
    xray_data = r.json()
    print("[PASS] POST /api/xray -> Severity:", xray_data["result"]["severity"], "Confidence:", xray_data["result"]["confidence"])

    # 5. POST /api/gait
    with open("demo/sample_movement.mp4", "rb") as f:
        r = client.post("/api/gait", files={"movement_file": ("sample_movement.mp4", f, "video/mp4")})
    assert r.status_code == 200, f"POST /api/gait failed: {r.status_code}, {r.text}"
    gait_data = r.json()
    print("[PASS] POST /api/gait -> Risk:", gait_data["result"]["movement_risk"], "Asymmetry:", gait_data["result"]["asymmetry_percentage"])

    # 6. POST /api/screen
    with open("demo/sample_knee_xray.png", "rb") as fx, open("demo/sample_movement.mp4", "rb") as fv:
        form_data = {
            "patient_name": "Test Patient",
            "patient_id": "OA-2026-TEST",
            "age": "55",
            "sex": "Female",
            "height": "165.0",
            "weight": "72.0",
            "previous_injury": "true",
            "oa_history": "false",
            "symptom_duration": "6-12 months",
            "pain_score": "6",
            "morning_stiffness": "true",
            "joint_stiffness": "true",
            "swelling": "false",
            "walking_difficulty": "true",
            "stairs_difficulty": "true",
            "standing_difficulty": "false",
            "bending_difficulty": "true"
        }
        files = {
            "xray_file": ("sample_knee_xray.png", fx, "image/png"),
            "movement_file": ("sample_movement.mp4", fv, "video/mp4")
        }
        r = client.post("/api/screen", data=form_data, files=files)
    assert r.status_code == 200, f"POST /api/screen failed: {r.status_code}, {r.text}"
    screen_data = r.json()
    print("[PASS] POST /api/screen -> Overall Risk:", screen_data["fusion"]["overall_risk"], "Score:", screen_data["fusion"]["risk_score"])

    # 7. POST /api/verify
    r = client.post("/api/verify", data={
        "patient_id": "OA-2026-TEST",
        "action": "Reviewed",
        "comments": "Patient exhibits typical moderate degenerative indications.",
        "verified_by": "Nurse Clinician"
    })
    assert r.status_code == 200, f"POST /api/verify failed: {r.status_code}"
    print("[PASS] POST /api/verify -> Status:", r.json()["verification"]["status"])

    # 8. POST /api/report
    r = client.post("/api/report", data={"patient_id": "OA-2026-TEST"})
    assert r.status_code == 200, f"POST /api/report failed: {r.status_code}"
    report_json = r.json()
    assert "printable_html" in report_json
    print("[PASS] POST /api/report -> Report ID:", report_json["report_id"])

    # 9. GET /api/report/OA-2026-TEST/print
    r = client.get("/api/report/OA-2026-TEST/print")
    assert r.status_code == 200, f"GET print report failed: {r.status_code}"
    assert "Multimodal Osteoarthritis Screening Report" in r.text
    print("[PASS] GET /api/report/OA-2026-TEST/print -> HTML rendered with length:", len(r.text))

    print("\nALL BACKEND API TESTS PASSED SUCCESSFULLY! 100% OK")

if __name__ == "__main__":
    test_all()
