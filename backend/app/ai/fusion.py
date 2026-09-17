"""
Multimodal Fusion Engine for Osteoarthritis Screening

Combines evidence from:
1. Knee X-Ray AI Assessment (Structural features)
2. Patient Clinical Symptoms & Risk Factors (Pain, stiffness, mobility, BMI, age)
3. Gait / Movement AI Assessment (Functional biomechanical asymmetry and consistency)

Outputs an overall AI screening risk indication and recommendations.
Does NOT provide a medical diagnosis.
"""

from typing import Dict, Any, List


def fuse_multimodal_assessment(
    xray_result: Dict[str, Any],
    clinical_data: Dict[str, Any],
    gait_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Perform weighted multimodal fusion across X-ray, clinical, and gait findings.
    """
    explanations: List[str] = []

    # -------------------------------------------------------------
    # 1. X-RAY COMPONENT (Weight: 40%)
    # -------------------------------------------------------------
    xray_severity = xray_result.get("severity", "None")
    xray_abnormality = xray_result.get("abnormality_detected", False)
    xray_conf = xray_result.get("confidence", 0.70)

    if xray_severity == "Severe":
        xray_score = 38.0
        explanations.append("X-ray analysis indicated significant joint space narrowing / contour irregularities.")
    elif xray_severity == "Moderate":
        xray_score = 28.0
        explanations.append("X-ray analysis indicated moderate joint space asymmetry and subchondral density changes.")
    elif xray_severity == "Mild":
        xray_score = 16.0
        explanations.append("X-ray analysis detected mild structural irregularities in the joint space.")
    else:
        xray_score = 4.0
        explanations.append("X-ray joint space contours appear preserved with minimal detectable narrowing.")

    # Modulate slightly by model confidence
    xray_score = xray_score * (0.8 + (xray_conf * 0.2))

    # -------------------------------------------------------------
    # 2. CLINICAL COMPONENT (Weight: 35%)
    # -------------------------------------------------------------
    clinical_points = 0.0

    # Pain score (0-10) -> max 12 pts
    pain = float(clinical_data.get("pain_score", 0))
    pain_pts = min(12.0, (pain / 10.0) * 12.0)
    clinical_points += pain_pts
    if pain >= 5:
        explanations.append(f"Elevated self-reported pain score ({int(pain)}/10) during knee loading.")

    # Joint symptoms -> max 7 pts
    morning_stiff = bool(clinical_data.get("morning_stiffness", False))
    joint_stiff = bool(clinical_data.get("joint_stiffness", False))
    swelling = bool(clinical_data.get("swelling", False))

    if morning_stiff:
        clinical_points += 2.5
    if joint_stiff:
        clinical_points += 2.5
    if swelling:
        clinical_points += 2.0
    if morning_stiff or joint_stiff or swelling:
        active_symp = []
        if morning_stiff: active_symp.append("morning stiffness")
        if joint_stiff: active_symp.append("joint stiffness")
        if swelling: active_symp.append("joint swelling")
        explanations.append(f"Active clinical symptoms present: {', '.join(active_symp)}.")

    # Functional mobility restrictions -> max 8 pts
    walk_diff = bool(clinical_data.get("walking_difficulty", False))
    stairs_diff = bool(clinical_data.get("stairs_difficulty", False))
    standing_diff = bool(clinical_data.get("standing_difficulty", False))
    bending_diff = bool(clinical_data.get("bending_difficulty", False))

    mobility_flags = [walk_diff, stairs_diff, standing_diff, bending_diff]
    active_mobility_count = sum(mobility_flags)
    clinical_points += (active_mobility_count * 2.0)
    if active_mobility_count >= 2:
        explanations.append(f"Multiple mobility restrictions reported ({active_mobility_count} functional difficulties).")

    # Demographic and historical risk factors -> max 8 pts
    age = float(clinical_data.get("age", 40))
    bmi = float(clinical_data.get("bmi", 22.0))
    prev_injury = bool(clinical_data.get("previous_injury", False))
    oa_history = bool(clinical_data.get("oa_history", False))

    if age >= 55:
        clinical_points += 2.5
    elif age >= 45:
        clinical_points += 1.5

    if bmi >= 30.0:
        clinical_points += 2.5
        explanations.append(f"Elevated BMI ({bmi}) contributes increased biomechanical knee joint loading.")
    elif bmi >= 25.0:
        clinical_points += 1.0

    if prev_injury:
        clinical_points += 1.5
        explanations.append("Documented history of knee trauma/injury increases post-traumatic OA risk.")
    if oa_history:
        clinical_points += 1.5

    clinical_score = min(35.0, clinical_points)

    # -------------------------------------------------------------
    # 3. GAIT & MOVEMENT COMPONENT (Weight: 25%)
    # -------------------------------------------------------------
    gait_risk_level = gait_result.get("movement_risk", "Lower")
    asymmetry = float(gait_result.get("asymmetry", 0.05))
    consistency = float(gait_result.get("movement_consistency", 0.85))

    if gait_risk_level == "Higher":
        gait_score = 22.0
    elif gait_risk_level == "Moderate":
        gait_score = 14.0
    else:
        gait_score = 5.0

    # Adjust based on asymmetry percentage
    if asymmetry >= 0.15:
        gait_score = min(25.0, gait_score + 3.0)
        explanations.append(f"Gait analysis detected notable bilateral movement asymmetry ({round(asymmetry * 100, 1)}%).")
    elif asymmetry >= 0.10:
        gait_score = min(25.0, gait_score + 1.5)

    if consistency < 0.65:
        gait_score = min(25.0, gait_score + 2.0)
        explanations.append("Irregular movement cadence observed across sampled video frames.")

    # -------------------------------------------------------------
    # 4. OVERALL RISK FUSION
    # -------------------------------------------------------------
    total_risk_score = round(xray_score + clinical_score + gait_score, 1)
    total_risk_score = max(5.0, min(98.0, total_risk_score))

    if total_risk_score >= 65.0:
        overall_risk = "Higher Risk"
        risk_badge_class = "danger"
    elif total_risk_score >= 38.0:
        overall_risk = "Moderate Risk"
        risk_badge_class = "warning"
    else:
        overall_risk = "Lower Risk"
        risk_badge_class = "success"

    # Standard recommendations
    recommendations = [
        "Further clinical evaluation recommended.",
        "Formal radiological assessment by a musculoskeletal specialist or radiologist is advised."
    ]

    if overall_risk in ["Higher Risk", "Moderate Risk"]:
        recommendations.append("Consider clinical physiotherapy consult for quadriceps strengthening and joint mobility.")
    if bmi >= 28.0:
        recommendations.append("Nutritional counseling and weight management strategies to alleviate knee joint stress.")
    if pain >= 6 or walk_diff:
        recommendations.append("Evaluate pain management protocols and temporary use of assistive ambulatory devices if indicated.")

    return {
        "overall_risk": overall_risk,
        "risk_level": overall_risk,
        "risk_score": total_risk_score,
        "risk_badge_class": risk_badge_class,
        "breakdown": {
            "xray_score": round(xray_score, 1),
            "clinical_score": round(clinical_score, 1),
            "gait_score": round(gait_score, 1),
            "max_weights": {"xray": 40, "clinical": 35, "gait": 25}
        },
        "explanations": explanations,
        "recommendations": recommendations,
        "primary_recommendation": "Further clinical evaluation recommended.",
        "disclaimer": "AI prototype screening indication for research demonstration only. This does NOT constitute a formal medical diagnosis."
    }
