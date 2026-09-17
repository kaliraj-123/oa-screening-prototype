# Demonstration Samples & Testing Data

This directory contains sample files and instructions for testing the **AI-Based Multimodal Osteoarthritis Screening and Risk Assessment System**.

## Included Demo Files
- `generate_demo_assets.py`: Standalone Python script to regenerate synthetic test assets.
- `sample_knee_xray.png`: A non-copyrighted synthetic knee radiograph illustration depicting femur, tibia plateau, and joint space.
- `sample_movement.mp4`: A synthetic animated gait/walking movement video with cyclic knee flexion-extension.

## Generating or Regenerating Demo Files
To regenerate the sample files at any time, run:
```bash
python demo/generate_demo_assets.py
```

## Adding Your Own Medical Data
To test with real clinical or public research dataset files:
1. **Knee X-Rays**:
   - Acceptable formats: `.jpg`, `.jpeg`, `.png`
   - Image recommendations: Anteroposterior (AP) standing knee radiographs with clear visibility of medial and lateral joint compartments.
   - De-identification: Ensure all Patient Health Information (PHI) such as patient names, birthdates, MRNs, and hospital identifiers are completely stripped prior to upload.
   - Public reference datasets: You may obtain open-access de-identified knee X-rays from the **Osteoarthritis Initiative (OAI)** or **MURA** musculoskeletal dataset for academic evaluation.

2. **Knee Movement / Gait Videos**:
   - Acceptable formats: `.mp4`, `.mov`, `.avi`
   - Recommendations: 3 to 10 seconds of frontal or sagittal plane walking, knee squatting, or flexion-extension movements.
   - Ensure patient face is blurred or obscured to maintain participant privacy.

## Disclaimer
All sample assets provided in this folder are purely synthetic, non-copyrighted computer-generated files designed solely to verify that the video decoder and image pipeline function without errors. They do not represent real patient medical imaging.
