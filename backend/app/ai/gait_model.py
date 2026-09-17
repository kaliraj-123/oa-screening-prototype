"""
Knee Movement and Gait AI Analysis Module (Prototype / Demonstration Model)

IMPORTANT NOTICE:
This module is a prototype computer-vision motion analyzer for demonstration and research purposes.
It does NOT provide a medical diagnosis.
In production, this module can be extended with full-body 3D pose estimation (e.g., MediaPipe Pose or OpenPose)
to measure precise knee flexion angles, ground reaction forces, and spatiotemporal gait parameters.
"""

from typing import Dict, Any, List
import numpy as np
import cv2
from app.utils.preprocessing import extract_video_frames


class BaseGaitModel:
    """
    Abstract interface for Gait / Movement AI models.
    Can be subclassed by MediaPipe Pose or deep sequence models (LSTM / Transformer).
    """
    def predict(self, video_path: str) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement predict()")


class PrototypeOpenCVGaitModel(BaseGaitModel):
    """
    OpenCV-based gait and movement feature extraction prototype.
    Analyzes bilateral motion asymmetry, movement velocity smoothness,
    and movement consistency across sampled video frames.
    """

    def __init__(self):
        self.model_name = "Prototype-OpenCV-GaitAnalyzer-v1.0"

    def _compute_motion_metrics(self, frames: List[np.ndarray]) -> Dict[str, float]:
        """
        Compute frame-to-frame optical flow / motion energy and bilateral asymmetry.
        """
        if len(frames) < 2:
            return {
                "asymmetry": 0.05,
                "consistency": 0.90,
                "mean_motion": 0.0
            }

        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
        left_energies = []
        right_energies = []
        frame_diff_magnitudes = []

        for i in range(1, len(frames)):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

            # Compute absolute difference between successive frames
            diff = cv2.absdiff(curr_gray, prev_gray)
            _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

            h, w = thresh.shape
            mid_x = w // 2

            left_motion = float(np.sum(thresh[:, :mid_x]))
            right_motion = float(np.sum(thresh[:, mid_x:]))

            left_energies.append(left_motion)
            right_energies.append(right_motion)
            frame_diff_magnitudes.append(left_motion + right_motion)

            prev_gray = curr_gray

        total_left = sum(left_energies) + 1e-5
        total_right = sum(right_energies) + 1e-5

        # Bilateral asymmetry ratio: |Left - Right| / (Left + Right)
        asymmetry = abs(total_left - total_right) / (total_left + total_right)
        asymmetry = min(0.60, max(0.02, asymmetry))

        # Motion consistency metric: coefficient of variation of frame differences
        diff_arr = np.array(frame_diff_magnitudes)
        if len(diff_arr) > 0 and np.mean(diff_arr) > 0:
            coef_var = float(np.std(diff_arr) / np.mean(diff_arr))
            # Lower variance in periodic walking implies higher cadence consistency
            consistency = max(0.40, min(0.98, 1.0 - (coef_var * 0.3)))
        else:
            consistency = 0.75

        mean_motion = float(np.mean(frame_diff_magnitudes)) if len(frame_diff_magnitudes) > 0 else 0.0

        return {
            "asymmetry": round(float(asymmetry), 3),
            "consistency": round(float(consistency), 2),
            "mean_motion": round(mean_motion, 1)
        }

    def predict(self, video_path: str) -> Dict[str, Any]:
        """
        Perform movement analysis on the uploaded video.
        """
        extracted = extract_video_frames(video_path, max_frames=60)
        frames = extracted["frames"]
        fps = extracted["fps"]
        duration = extracted["duration_seconds"]

        metrics = self._compute_motion_metrics(frames)
        asymmetry = metrics["asymmetry"]
        consistency = metrics["consistency"]

        # Risk categorization based on asymmetry & consistency heuristics
        # Individuals with symptomatic knee OA frequently exhibit antalgic gait with asymmetry > 12-15%
        if asymmetry > 0.20 or consistency < 0.60:
            movement_risk = "Higher"
            movement_quality = "Poor"
        elif asymmetry > 0.10 or consistency < 0.75:
            movement_risk = "Moderate"
            movement_quality = "Fair"
        else:
            movement_risk = "Lower"
            movement_quality = "Good"

        return {
            "model_version": self.model_name,
            "movement_risk": movement_risk,
            "movement_quality": movement_quality,
            "asymmetry": asymmetry,
            "asymmetry_percentage": f"{round(asymmetry * 100, 1)}%",
            "movement_consistency": consistency,
            "frames_analyzed": len(frames),
            "video_duration_seconds": duration,
            "fps": fps,
            "metrics": metrics,
            "disclaimer": "Prototype movement indication. Not a medical diagnosis. Clinician review required."
        }


# Singleton instance
_gait_model_instance = PrototypeOpenCVGaitModel()


def analyze_gait(video_path: str) -> Dict[str, Any]:
    """Public helper function to analyze knee movement video."""
    return _gait_model_instance.predict(video_path)
