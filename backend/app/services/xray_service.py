"""
Service for handling Knee X-Ray file uploads, persistence, and AI screening execution.
"""

import os
import uuid
from fastapi import UploadFile, HTTPException
from app.utils.preprocessing import validate_xray_file
from app.ai.xray_model import analyze_xray


if os.environ.get("VERCEL"):
    UPLOAD_DIR_XRAY = "/tmp/uploads/xray"
else:
    UPLOAD_DIR_XRAY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "xray"))
os.makedirs(UPLOAD_DIR_XRAY, exist_ok=True)


async def process_xray_upload(file: UploadFile) -> dict:
    """
    Validate, save, and analyze an uploaded knee X-ray image.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No X-ray file provided.")

    # Read content to check file size
    content = await file.read()
    file_size = len(content)

    valid, msg = validate_xray_file(file.filename, file_size)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Generate unique filename to avoid collisions
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"xray_{uuid.uuid4().hex[:10]}{ext}"
    saved_path = os.path.join(UPLOAD_DIR_XRAY, unique_filename)

    # Save to disk
    with open(saved_path, "wb") as f:
        f.write(content)

    # Perform prototype AI analysis
    try:
        analysis_result = analyze_xray(saved_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"X-ray analysis error: {str(e)}")

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": saved_path,
        "file_url": f"/uploads/xray/{unique_filename}",
        "file_size_kb": round(file_size / 1024, 1),
        "result": analysis_result
    }
