"""
Preprocessing and validation utilities for X-ray images, movement videos, and clinical data.
"""

import os
import uuid
import numpy as np
import cv2
from PIL import Image

# Maximum allowed file sizes
MAX_XRAY_SIZE_BYTES = 10 * 1024 * 1024      # 10 MB
MAX_VIDEO_SIZE_BYTES = 50 * 1024 * 1024     # 50 MB

ALLOWED_XRAY_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".jfif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm", ".mkv", ".ogv"}


def generate_patient_id(prefix: str = "OA-2026") -> str:
    """
    Generate a standardized patient screening identifier.
    Example: OA-2026-8492
    """
    short_hash = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{short_hash}"


def validate_xray_file(filename: str, file_size: int) -> tuple[bool, str]:
    """
    Validate X-ray file extension and size.
    """
    if not filename:
        return False, "No X-ray image filename provided."

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_XRAY_EXTENSIONS:
        return False, f"Unsupported X-ray format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_XRAY_EXTENSIONS))}"

    if file_size > MAX_XRAY_SIZE_BYTES:
        return False, f"X-ray file exceeds maximum size limit of 10 MB (current: {file_size / (1024*1024):.2f} MB)."

    return True, "Valid"


def validate_movement_file(filename: str, file_size: int) -> tuple[bool, str]:
    """
    Validate movement video file extension and size.
    """
    if not filename:
        return False, "No movement video filename provided."

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        return False, f"Unsupported video format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_VIDEO_EXTENSIONS))}"

    if file_size > MAX_VIDEO_SIZE_BYTES:
        return False, f"Movement video exceeds maximum size limit of 50 MB (current: {file_size / (1024*1024):.2f} MB)."

    return True, "Valid"


def calculate_bmi(height_cm: float, weight_kg: float) -> tuple[float, str]:
    """
    Calculate Body Mass Index (BMI) and classification category.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "Invalid Measurements"

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obese"

    return bmi, category


def preprocess_xray(image_path: str, target_size: tuple[int, int] = (512, 512)) -> dict:
    """
    Load, validate, normalize and extract image quality metrics from knee X-ray.
    Uses OpenCV and CLAHE contrast enhancement.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"X-ray file not found: {image_path}")

    # Read image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        # Fallback to Pillow in case of uncommon color profiles
        try:
            pil_img = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"Could not decode image file: {str(e)}")

    original_h, original_w = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate image sharpness metric (Laplacian variance)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Calculate contrast and brightness metrics
    mean_intensity = float(np.mean(gray))
    std_intensity = float(np.std(gray))

    # Determine image quality heuristic
    if laplacian_var > 120.0 and 30 < mean_intensity < 225 and std_intensity > 35:
        quality = "Good"
    elif laplacian_var > 50.0 and std_intensity > 20:
        quality = "Fair"
    else:
        quality = "Low"

    # Resize to standard model input dimensions
    resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)

    # Apply Contrast Limited Adaptive Histogram Equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(resized)

    return {
        "original_shape": (original_h, original_w),
        "resized_shape": target_size,
        "sharpness_score": round(laplacian_var, 2),
        "mean_intensity": round(mean_intensity, 2),
        "contrast_std": round(std_intensity, 2),
        "quality": quality,
        "enhanced_image": enhanced,
        "raw_gray": resized
    }


def extract_video_frames(video_path: str, max_frames: int = 60, target_size: tuple[int, int] = (360, 480)) -> dict:
    """
    Sample video frames and calculate duration and basic video attributes.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Unable to open video stream from file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    duration_sec = total_frames / fps if fps > 0 else 0.0

    frames = []
    step = max(1, total_frames // max_frames) if total_frames > max_frames else 1

    current_frame = 0
    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if current_frame % step == 0:
            # Resize frame for uniform motion analysis
            h, w = frame.shape[:2]
            scaled = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
            frames.append(scaled)

        current_frame += 1

    cap.release()

    if len(frames) == 0:
        raise ValueError("Video file contained no readable frames or is corrupted.")

    return {
        "frames": frames,
        "fps": round(fps, 1),
        "total_frames": total_frames,
        "sampled_frames_count": len(frames),
        "duration_seconds": round(duration_sec, 2)
    }
