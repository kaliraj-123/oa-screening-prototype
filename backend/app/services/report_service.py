"""
Digital Screening Report Generator Service
Generates structured JSON report and printable HTML screening summary.
"""

from datetime import datetime
from typing import Dict, Any


def generate_screening_report(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive structured digital report object.
    """
    patient = data.get("patient", {})
    clinical = data.get("clinical", {})
    xray = data.get("xray", {})
    gait = data.get("gait", {})
    fusion = data.get("fusion", {})
    verification = data.get("verification", {
        "status": "Pending",
        "comments": "",
        "verified_by": "Healthcare Worker (Unassigned)",
        "verified_at": None
    })

    screening_date = data.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "report_id": f"REP-{patient.get('patient_id', 'UNKNOWN')}",
        "generated_at": screening_date,
        "facility": "Community Health & Mobility Screening Hub",
        "system_version": "AI-Multimodal-OA-v1.0-Prototype",
        "patient": patient,
        "clinical": clinical,
        "xray": xray,
        "gait": gait,
        "fusion": fusion,
        "verification": verification,
        "disclaimer": (
            "NOTICE: This document is a prototype AI-assisted screening assessment generated for research "
            "and demonstration purposes only. It does NOT constitute a formal medical diagnosis. "
            "Further clinical evaluation by a licensed healthcare professional is recommended."
        )
    }


def generate_printable_html_report(report_data: Dict[str, Any]) -> str:
    """
    Generate a standalone, styled, printable HTML document for the screening report.
    """
    patient = report_data.get("patient", {})
    clinical = report_data.get("clinical", {})
    xray = report_data.get("xray", {}).get("result", report_data.get("xray", {}))
    gait = report_data.get("gait", {}).get("result", report_data.get("gait", {}))
    fusion = report_data.get("fusion", {})
    verification = report_data.get("verification", {})

    p_id = patient.get("patient_id", "N/A")
    p_name = patient.get("name", "Anonymous")
    p_age = patient.get("age", "N/A")
    p_sex = patient.get("sex", "N/A")
    p_bmi = patient.get("bmi", "N/A")
    p_height = patient.get("height_cm", "N/A")
    p_weight = patient.get("weight_kg", "N/A")

    risk_level = fusion.get("overall_risk", "Moderate Risk")
    risk_score = fusion.get("risk_score", "50.0")

    badge_color = "#dc3545" if "Higher" in risk_level else ("#ffc107" if "Moderate" in risk_level else "#198754")
    badge_text_color = "#ffffff" if "Moderate" not in risk_level else "#000000"

    v_status = verification.get("status", "Pending")
    v_comments = verification.get("comments", "No comments entered.")
    timestamp = report_data.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    explanations_html = "".join([f"<li>{item}</li>" for item in fusion.get("explanations", [])]) or "<li>Standard baseline screening features observed.</li>"
    recommendations_html = "".join([f"<li>{item}</li>" for item in fusion.get("recommendations", ["Further clinical evaluation recommended."])])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OA Screening Report - {p_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #2b2d42;
            background-color: #f8f9fa;
            margin: 0;
            padding: 24px;
        }}
        .report-container {{
            max-width: 820px;
            margin: 0 auto;
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 36px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0d6efd;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 22px;
            color: #0f2e59;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .header .subtitle {{
            margin: 4px 0 0;
            font-size: 13px;
            color: #6c757d;
        }}
        .report-id-badge {{
            text-align: right;
            font-size: 13px;
        }}
        .report-id-badge strong {{
            font-size: 16px;
            color: #0d6efd;
        }}
        .disclaimer-box {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 14px;
            font-size: 12px;
            color: #664d03;
            margin-bottom: 24px;
            border-radius: 4px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #0f2e59;
            border-bottom: 1px solid #e9ecef;
            padding-bottom: 6px;
            margin-top: 20px;
            margin-bottom: 12px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 12px;
        }}
        .grid-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 16px;
            margin-bottom: 12px;
        }}
        .data-card {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px 14px;
        }}
        .data-card h4 {{
            margin: 0 0 8px;
            font-size: 13px;
            color: #475569;
        }}
        .data-item {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 4px;
        }}
        .data-item span:first-child {{
            color: #64748b;
        }}
        .data-item span:last-child {{
            font-weight: 600;
        }}
        .risk-banner {{
            background: #f1f5f9;
            border: 2px solid {badge_color};
            border-radius: 8px;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 16px 0;
        }}
        .risk-badge {{
            display: inline-block;
            background: {badge_color};
            color: {badge_text_color};
            font-size: 18px;
            font-weight: 700;
            padding: 8px 18px;
            border-radius: 20px;
        }}
        ul {{
            margin: 6px 0 12px 20px;
            padding: 0;
            font-size: 13px;
            color: #334155;
            line-height: 1.5;
        }}
        .verification-block {{
            background: #eef2f6;
            border-radius: 6px;
            padding: 14px;
            margin-top: 16px;
            font-size: 13px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 16px;
            border-top: 1px solid #dee2e6;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
        .actions {{
            text-align: center;
            margin-top: 20px;
        }}
        .btn-print {{
            background: #0d6efd;
            color: #ffffff;
            border: none;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
        }}
        @media print {{
            body {{
                background: #ffffff;
                padding: 0;
            }}
            .report-container {{
                border: none;
                box-shadow: none;
                padding: 0;
                max-width: 100%;
            }}
            .actions {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>

<div class="report-container">
    <div class="header">
        <div>
            <h1>Multimodal Osteoarthritis Screening Report</h1>
            <div class="subtitle">AI-Assisted X-Ray, Clinical &amp; Movement Assessment Prototype</div>
        </div>
        <div class="report-id-badge">
            <div>Patient ID: <strong>{p_id}</strong></div>
            <div>Date: {timestamp}</div>
        </div>
    </div>

    <div class="disclaimer-box">
        <strong>IMPORTANT MEDICAL DISCLAIMER:</strong> This document is a prototype AI-assisted screening assessment for research and demonstration only. It does <strong>NOT</strong> provide a medical diagnosis. Further clinical evaluation is recommended.
    </div>

    <div class="section-title">1. Patient Information</div>
    <div class="grid-3">
        <div class="data-card">
            <h4>Demographics</h4>
            <div class="data-item"><span>Full Name:</span> <span>{p_name}</span></div>
            <div class="data-item"><span>Age:</span> <span>{p_age} yrs</span></div>
            <div class="data-item"><span>Sex:</span> <span>{p_sex}</span></div>
        </div>
        <div class="data-card">
            <h4>Anthropometrics</h4>
            <div class="data-item"><span>Height:</span> <span>{p_height} cm</span></div>
            <div class="data-item"><span>Weight:</span> <span>{p_weight} kg</span></div>
            <div class="data-item"><span>BMI:</span> <span>{p_bmi} kg/m²</span></div>
        </div>
        <div class="data-card">
            <h4>History</h4>
            <div class="data-item"><span>Target Joint:</span> <span>Knee</span></div>
            <div class="data-item"><span>Prior Trauma:</span> <span>{"Yes" if clinical.get("previous_injury") else "No"}</span></div>
            <div class="data-item"><span>OA History:</span> <span>{"Yes" if clinical.get("oa_history") else "No"}</span></div>
        </div>
    </div>

    <div class="section-title">2. Clinical Symptoms</div>
    <div class="grid-2">
        <div class="data-card">
            <h4>Symptom Severity</h4>
            <div class="data-item"><span>Reported Pain Score:</span> <span>{clinical.get("pain_score", 0)} / 10</span></div>
            <div class="data-item"><span>Morning Stiffness:</span> <span>{"Present" if clinical.get("morning_stiffness") else "Absent"}</span></div>
            <div class="data-item"><span>Joint Stiffness:</span> <span>{"Present" if clinical.get("joint_stiffness") else "Absent"}</span></div>
            <div class="data-item"><span>Visible Swelling:</span> <span>{"Present" if clinical.get("swelling") else "Absent"}</span></div>
        </div>
        <div class="data-card">
            <h4>Functional Impairments</h4>
            <div class="data-item"><span>Walking Difficulty:</span> <span>{"Reported" if clinical.get("walking_difficulty") else "None"}</span></div>
            <div class="data-item"><span>Stair Climbing:</span> <span>{"Difficulty" if clinical.get("stairs_difficulty") else "Normal"}</span></div>
            <div class="data-item"><span>Prolonged Standing:</span> <span>{"Difficulty" if clinical.get("standing_difficulty") else "Normal"}</span></div>
            <div class="data-item"><span>Knee Bending:</span> <span>{"Difficulty" if clinical.get("bending_difficulty") else "Normal"}</span></div>
        </div>
    </div>

    <div class="section-title">3. Objective Prototype AI Assessments</div>
    <div class="grid-2">
        <div class="data-card">
            <h4>Knee X-Ray Assessment</h4>
            <div class="data-item"><span>Image Quality:</span> <span>{xray.get("image_quality", "Good")}</span></div>
            <div class="data-item"><span>Abnormality:</span> <span>{"Detected" if xray.get("abnormality_detected") else "None Detected"}</span></div>
            <div class="data-item"><span>Estimated Severity:</span> <span>{xray.get("severity", "None")}</span></div>
            <div class="data-item"><span>Model Confidence:</span> <span>{int(float(xray.get("confidence", 0.8)) * 100)}%</span></div>
        </div>
        <div class="data-card">
            <h4>Movement &amp; Gait Assessment</h4>
            <div class="data-item"><span>Movement Quality:</span> <span>{gait.get("movement_quality", "Fair")}</span></div>
            <div class="data-item"><span>Bilateral Asymmetry:</span> <span>{gait.get("asymmetry_percentage", f"{round(float(gait.get('asymmetry', 0.12))*100, 1)}%")}</span></div>
            <div class="data-item"><span>Movement Risk:</span> <span>{gait.get("movement_risk", "Moderate")}</span></div>
            <div class="data-item"><span>Movement Consistency:</span> <span>{int(float(gait.get("movement_consistency", 0.75)) * 100)}%</span></div>
        </div>
    </div>

    <div class="section-title">4. Multimodal Fusion Screening Result</div>
    <div class="risk-banner">
        <div>
            <div style="font-size: 13px; color: #64748b; margin-bottom: 4px;">COMBINED OA SCREENING RISK</div>
            <div class="risk-badge">{risk_level}</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 28px; font-weight: 800; color: #0f2e59;">{risk_score}<span style="font-size: 15px; font-weight: 400; color: #64748b;">/100</span></div>
            <div style="font-size: 12px; color: #64748b;">Multimodal Risk Index</div>
        </div>
    </div>

    <div>
        <h4 style="font-size: 13px; margin: 10px 0 4px; color: #475569;">Contributing Clinical Indications:</h4>
        <ul>{explanations_html}</ul>
    </div>

    <div>
        <h4 style="font-size: 13px; margin: 10px 0 4px; color: #475569;">Suggested Clinical Next Steps:</h4>
        <ul>{recommendations_html}</ul>
    </div>

    <div class="section-title">5. Healthcare Worker Review &amp; Verification</div>
    <div class="verification-block">
        <div class="data-item"><span>Verification Status:</span> <strong>{v_status.upper()}</strong></div>
        <div class="data-item"><span>Healthcare Worker Comments:</span> <span>{v_comments}</span></div>
        <div class="data-item"><span>Referral Recommendation:</span> <strong>{"Orthopedic / Rheumatology Referral Recommended" if "Higher" in risk_level or v_status == "Referred" else "Routine Primary Care Follow-up"}</strong></div>
    </div>

    <div class="actions">
        <button class="btn-print" onclick="window.print()">Print Screening Report</button>
    </div>

    <div class="footer">
        Generated by AI-Based Multimodal Osteoarthritis Screening System &bull; Research &amp; Educational Prototype &bull; {timestamp}
    </div>
</div>

</body>
</html>
"""
