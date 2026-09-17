"""
Demo Asset Generator for Osteoarthritis Screening System

Generates synthetic, non-copyrighted demonstration assets:
1. sample_knee_xray.png: Synthetic AP knee radiograph proxy
2. sample_movement.mp4: Synthetic knee movement / gait video clip
"""

import os
import numpy as np
import cv2


def generate_synthetic_knee_xray(output_path: str, width: int = 512, height: int = 512):
    """
    Generate a synthetic grayscale knee joint radiograph showing femur condyles,
    tibia plateau, and joint space narrowing proxy.
    """
    img = np.zeros((height, width), dtype=np.uint8)

    # Soft background tissue tone
    background_noise = np.random.normal(45, 12, (height, width)).clip(0, 255).astype(np.uint8)
    img = cv2.addWeighted(img, 0.0, background_noise, 1.0, 0)

    # Femur shaft (top center)
    cv2.rectangle(img, (int(width * 0.35), 0), (int(width * 0.65), int(height * 0.35)), 170, -1)

    # Femur medial and lateral condyles
    cv2.ellipse(img, (int(width * 0.38), int(height * 0.38)), (int(width * 0.14), int(height * 0.12)), 0, 0, 360, 210, -1)
    cv2.ellipse(img, (int(width * 0.62), int(height * 0.38)), (int(width * 0.14), int(height * 0.12)), 0, 0, 360, 210, -1)

    # Joint space gap: Intentionally leave a horizontal band around y = 0.46 to 0.50
    # Tibia plateau (bottom)
    cv2.ellipse(img, (int(width * 0.38), int(height * 0.58)), (int(width * 0.15), int(height * 0.09)), 0, 0, 360, 215, -1)
    cv2.ellipse(img, (int(width * 0.62), int(height * 0.58)), (int(width * 0.15), int(height * 0.09)), 0, 0, 360, 215, -1)
    cv2.rectangle(img, (int(width * 0.34), int(height * 0.58)), (int(width * 0.66), height), 175, -1)

    # Fibula head (lateral side - right)
    cv2.ellipse(img, (int(width * 0.76), int(height * 0.62)), (int(width * 0.06), int(height * 0.10)), 15, 0, 360, 180, -1)

    # Patella shadow overlay
    patella = np.zeros((height, width), dtype=np.uint8)
    cv2.ellipse(patella, (int(width * 0.50), int(height * 0.36)), (int(width * 0.12), int(height * 0.14)), 0, 0, 360, 60, -1)
    img = cv2.add(img, patella)

    # Apply realistic radiographic blur and scattering
    img = cv2.GaussianBlur(img, (11, 11), 0)

    # Add anatomical bone texture grain
    grain = np.random.normal(0, 10, (height, width)).astype(np.int16)
    textured = np.clip(img.astype(np.int16) + grain, 0, 255).astype(np.uint8)

    # Add subtle clinical annotations
    cv2.putText(textured, "R", (width - 45, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, 230, 2)
    cv2.putText(textured, "DEMO-AP-KNEE", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, 140, 1)

    cv2.imwrite(output_path, textured)
    print(f"Synthetic Knee X-Ray created at: {output_path}")


def generate_synthetic_movement_video(output_path: str, width: int = 480, height: int = 640, fps: int = 25, duration_sec: int = 4):
    """
    Generate a synthetic movement video depicting a cyclic gait / knee flexion-extension cycle.
    """
    total_frames = fps * duration_sec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    hip_x, hip_y = width // 2, int(height * 0.25)
    thigh_len = int(height * 0.28)
    shank_len = int(height * 0.28)

    for f in range(total_frames):
        frame = np.ones((height, width, 3), dtype=np.uint8) * 245

        # Background floor and grid line
        cv2.line(frame, (0, int(height * 0.88)), (width, int(height * 0.88)), (180, 180, 180), 2)

        # Cyclic angle for knee flexion during gait cycle (sine wave)
        cycle = (f / fps) * 1.5 * np.pi  # ~1.5 Hz walking cadence
        hip_angle = np.sin(cycle) * 0.35
        knee_flexion = max(0.0, np.sin(cycle + 0.5) * 0.8)

        # Right leg (foreground)
        knee_x = int(hip_x + thigh_len * np.sin(hip_angle))
        knee_y = int(hip_y + thigh_len * np.cos(hip_angle))

        shank_angle = hip_angle - knee_flexion
        ankle_x = int(knee_x + shank_len * np.sin(shank_angle))
        ankle_y = int(knee_y + shank_len * np.cos(shank_angle))

        # Draw thigh
        cv2.line(frame, (hip_x, hip_y), (knee_x, knee_y), (40, 70, 180), 10)
        # Draw shank (shin)
        cv2.line(frame, (knee_x, knee_y), (ankle_x, ankle_y), (50, 100, 210), 8)
        # Knee joint circle
        cv2.circle(frame, (knee_x, knee_y), 12, (20, 40, 150), -1)
        # Foot line
        cv2.line(frame, (ankle_x, ankle_y), (ankle_x + 25, ankle_y), (30, 30, 80), 6)

        # Left leg (dimmer background silhouette for asymmetry)
        left_cycle = cycle + np.pi
        left_hip_angle = np.sin(left_cycle) * 0.32
        left_knee_flex = max(0.0, np.sin(left_cycle + 0.5) * 0.7)

        lknee_x = int(hip_x - 15 + thigh_len * np.sin(left_hip_angle))
        lknee_y = int(hip_y + thigh_len * np.cos(left_hip_angle))
        lshank_angle = left_hip_angle - left_knee_flex
        lankle_x = int(lknee_x + shank_len * np.sin(lshank_angle))
        lankle_y = int(lknee_y + shank_len * np.cos(lshank_angle))

        cv2.line(frame, (hip_x - 15, hip_y), (lknee_x, lknee_y), (140, 160, 200), 7)
        cv2.line(frame, (lknee_x, lknee_y), (lankle_x, lankle_y), (150, 170, 210), 6)
        cv2.circle(frame, (lknee_x, lknee_y), 9, (120, 140, 180), -1)

        # Torso & Head indicator
        cv2.line(frame, (hip_x, hip_y), (hip_x, int(height * 0.12)), (40, 40, 60), 12)
        cv2.circle(frame, (hip_x, int(height * 0.08)), 20, (50, 50, 70), -1)

        # Frame HUD
        cv2.putText(frame, f"GAIT ANALYSIS DEMO - Frame {f+1}/{total_frames}", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)
        cv2.putText(frame, "KNEE FLEXION TRACKING", (15, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 100, 200), 1)

        out.write(frame)

    out.release()
    print(f"Synthetic Movement Video created at: {output_path}")


if __name__ == "__main__":
    demo_dir = os.path.dirname(os.path.abspath(__file__))
    xray_path = os.path.join(demo_dir, "sample_knee_xray.png")
    video_path = os.path.join(demo_dir, "sample_movement.mp4")

    print("Generating demo assets...")
    generate_synthetic_knee_xray(xray_path)
    generate_synthetic_movement_video(video_path)
    print("Demo assets generation complete!")
