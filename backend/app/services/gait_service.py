"""
Service for handling Knee Movement / Gait Video uploads, persistence, and AI screening execution.
"""

import os
import uuid
from fastapi import UploadFile, HTTPException
from app.utils.preprocessing import validate_movement_file
from app.ai.gait_model import analyze_gait


UPLOAD_DIR_MOVEMENT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "movement"))
os.makedirs(UPLOAD_DIR_MOVEMENT, exist_ok=True)


async def process_gait_upload(file: UploadFile) -> dict:
    """
    Validate, save, and analyze an uploaded knee movement / walking video.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No movement video provided.")

    content = await file.read()
    file_size = len(content)

    valid, msg = validate_movement_file(file.filename, file_size)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Generate unique filename
    ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"movement_{uuid.uuid4().hex[:10]}{ext}"
    saved_path = os.path.join(UPLOAD_DIR_MOVEMENT, unique_filename)

    with open(saved_path, "wb") as f:
        f.write(content)

    try:
        analysis_result = analyze_gait(saved_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Movement analysis error: {str(e)}")

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": saved_path,
        "file_url": f"/uploads/movement/{unique_filename}",
        "file_size_mb": round(file_size / (1024 * 1024), 2),
        "result": analysis_result
    }
