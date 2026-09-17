/**
 * AI-Based Multimodal Osteoarthritis Screening and Risk Assessment System
 * Frontend Client Application
 */

// ============================================================================
// CONFIGURATION
// Replace this URL when deploying the backend to a cloud host (e.g., Render, Railway, AWS)
// Example: const API_URL = "https://your-backend-service.com";
// ============================================================================
const API_URL = window.location.origin;

// State
let selectedXrayFile = null;
let selectedVideoFile = null;
let currentScreeningResult = null;
let riskChartInstance = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initPatientId();
    initBmiCalculator();
    initPainSlider();
    initFileDropzones();
    initFormHandlers();
    initVerificationHandlers();
    initDashboardStats();
});

// ----------------------------------------------------------------------------
// 1. Patient ID Generation & Helpers
// ----------------------------------------------------------------------------
function generatePatientId() {
    const randomHex = Math.floor(1000 + Math.random() * 9000);
    return `OA-2026-${randomHex}`;
}

function initPatientId() {
    const pIdInput = document.getElementById("patientId");
    pIdInput.value = generatePatientId();

    document.getElementById("btnRegenId").addEventListener("click", () => {
        pIdInput.value = generatePatientId();
    });
}

// ----------------------------------------------------------------------------
// 2. BMI Auto-Calculation
// ----------------------------------------------------------------------------
function calculateBmi() {
    const heightCm = parseFloat(document.getElementById("patientHeight").value) || 0;
    const weightKg = parseFloat(document.getElementById("patientWeight").value) || 0;
    const bmiValEl = document.getElementById("bmiVal");
    const bmiBadgeEl = document.getElementById("bmiBadge");

    if (heightCm > 0 && weightKg > 0) {
        const heightM = heightCm / 100.0;
        const bmi = (weightKg / (heightM * heightM)).toFixed(1);
        bmiValEl.textContent = bmi;

        if (bmi < 18.5) {
            bmiBadgeEl.textContent = "Underweight";
            bmiBadgeEl.className = "badge bg-info text-dark";
        } else if (bmi < 25.0) {
            bmiBadgeEl.textContent = "Normal";
            bmiBadgeEl.className = "badge bg-success";
        } else if (bmi < 30.0) {
            bmiBadgeEl.textContent = "Overweight";
            bmiBadgeEl.className = "badge bg-warning text-dark";
        } else {
            bmiBadgeEl.textContent = "Obese";
            bmiBadgeEl.className = "badge bg-danger";
        }
    } else {
        bmiValEl.textContent = "--";
        bmiBadgeEl.textContent = "Invalid";
        bmiBadgeEl.className = "badge bg-secondary";
    }
}

function initBmiCalculator() {
    document.getElementById("patientHeight").addEventListener("input", calculateBmi);
    document.getElementById("patientWeight").addEventListener("input", calculateBmi);
    calculateBmi();
}

// ----------------------------------------------------------------------------
// 3. Pain Score Slider
// ----------------------------------------------------------------------------
function initPainSlider() {
    const painRange = document.getElementById("painRange");
    const painBadge = document.getElementById("painBadge");

    painRange.addEventListener("input", () => {
        const val = parseInt(painRange.value, 10);
        painBadge.textContent = `${val} / 10`;

        if (val <= 3) {
            painBadge.className = "pain-display bg-success text-white";
        } else if (val <= 6) {
            painBadge.className = "pain-display bg-warning text-dark";
        } else {
            painBadge.className = "pain-display bg-danger text-white";
        }
    });
}

// ----------------------------------------------------------------------------
// 4. File Dropzones & Previews (X-Ray and Movement Video)
// ----------------------------------------------------------------------------
function initFileDropzones() {
    // X-Ray Dropzone
    const xrayDropzone = document.getElementById("xrayDropzone");
    const xrayInput = document.getElementById("xrayInput");
    const xrayPreview = document.getElementById("xrayPreview");
    const xrayPreviewContainer = document.getElementById("xrayPreviewContainer");
    const xrayFileName = document.getElementById("xrayFileName");

    xrayInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleXrayFile(e.target.files[0]);
        }
    });

    setupDragDrop(xrayDropzone, handleXrayFile);

    function handleXrayFile(file) {
        const allowedExts = [".jpg", ".jpeg", ".png"];
        const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
        if (!allowedExts.includes(ext)) {
            alert("Please upload a valid knee X-ray image (.jpg, .jpeg, .png).");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert("X-ray image exceeds maximum limit of 10 MB.");
            return;
        }

        selectedXrayFile = file;
        xrayFileName.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        xrayFileName.style.display = "block";

        const reader = new FileReader();
        reader.onload = (e) => {
            xrayPreview.src = e.target.result;
            xrayPreviewContainer.style.display = "flex";
        };
        reader.readAsDataURL(file);
    }

    // Video Dropzone
    const videoDropzone = document.getElementById("videoDropzone");
    const videoInput = document.getElementById("videoInput");
    const videoPreview = document.getElementById("videoPreview");
    const videoPreviewContainer = document.getElementById("videoPreviewContainer");
    const videoFileName = document.getElementById("videoFileName");

    videoInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleVideoFile(e.target.files[0]);
        }
    });

    setupDragDrop(videoDropzone, handleVideoFile);

    function handleVideoFile(file) {
        const allowedExts = [".mp4", ".mov", ".avi"];
        const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
        if (!allowedExts.includes(ext)) {
            alert("Please upload a valid knee movement video (.mp4, .mov, .avi).");
            return;
        }

        if (file.size > 50 * 1024 * 1024) {
            alert("Movement video exceeds maximum limit of 50 MB.");
            return;
        }

        selectedVideoFile = file;
        videoFileName.textContent = `Selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`;
        videoFileName.style.display = "block";

        const fileUrl = URL.createObjectURL(file);
        videoPreview.src = fileUrl;
        videoPreviewContainer.style.display = "flex";
    }

    function setupDragDrop(zone, fileHandler) {
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                zone.classList.remove('dragover');
            }, false);
        });

        zone.addEventListener('drop', (e) => {
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                fileHandler(e.dataTransfer.files[0]);
            }
        }, false);
    }
}

// ----------------------------------------------------------------------------
// 5. Demo Data Auto-Populator
// ----------------------------------------------------------------------------
async function loadDemoSample() {
    document.getElementById("patientName").value = "Margaret Vance";
    document.getElementById("patientAge").value = "62";
    document.getElementById("patientSex").value = "Female";
    document.getElementById("patientHeight").value = "160";
    document.getElementById("patientWeight").value = "76";
    document.getElementById("symptomDuration").value = "1-3 years";
    document.getElementById("prevInjury").checked = true;
    document.getElementById("oaHistory").checked = true;

    // Clinical symptoms
    document.getElementById("painRange").value = 7;
    document.getElementById("painRange").dispatchEvent(new Event("input"));
    document.getElementById("chkMorningStiff").checked = true;
    document.getElementById("chkJointStiff").checked = true;
    document.getElementById("chkSwelling").checked = true;
    document.getElementById("chkBending").checked = true;
    document.getElementById("chkWalking").checked = true;
    document.getElementById("chkStairs").checked = true;
    document.getElementById("chkStanding").checked = true;

    calculateBmi();

    // Fetch demo assets from backend or local relative paths
    try {
        // Fetch synthetic demo knee X-ray
        const xrayRes = await fetch(`${API_URL}/demo/sample_knee_xray.png`).catch(() => fetch(`../demo/sample_knee_xray.png`));
        if (xrayRes && xrayRes.ok) {
            const xrayBlob = await xrayRes.blob();
            const xrayFile = new File([xrayBlob], "sample_knee_xray.png", { type: "image/png" });
            selectedXrayFile = xrayFile;

            const xrayPreview = document.getElementById("xrayPreview");
            xrayPreview.src = URL.createObjectURL(xrayBlob);
            document.getElementById("xrayPreviewContainer").style.display = "flex";
            document.getElementById("xrayFileName").textContent = `Selected: sample_knee_xray.png (Demo Asset)`;
            document.getElementById("xrayFileName").style.display = "block";
        }

        // Fetch synthetic demo movement video
        const vidRes = await fetch(`${API_URL}/demo/sample_movement.mp4`).catch(() => fetch(`../demo/sample_movement.mp4`));
        if (vidRes && vidRes.ok) {
            const vidBlob = await vidRes.blob();
            const vidFile = new File([vidBlob], "sample_movement.mp4", { type: "video/mp4" });
            selectedVideoFile = vidFile;

            const videoPreview = document.getElementById("videoPreview");
            videoPreview.src = URL.createObjectURL(vidBlob);
            document.getElementById("videoPreviewContainer").style.display = "flex";
            document.getElementById("videoFileName").textContent = `Selected: sample_movement.mp4 (Demo Asset)`;
            document.getElementById("videoFileName").style.display = "block";
        }
    } catch (e) {
        console.warn("Could not automatically preload demo media files:", e);
    }
}

// ----------------------------------------------------------------------------
// 6. Screening Submission & Multi-Stage Animation
// ----------------------------------------------------------------------------
function initFormHandlers() {
    document.getElementById("btnFillDemo").addEventListener("click", loadDemoSample);

    document.getElementById("btnResetForm").addEventListener("click", () => {
        document.getElementById("screeningForm").reset();
        selectedXrayFile = null;
        selectedVideoFile = null;
        document.getElementById("xrayPreviewContainer").style.display = "none";
        document.getElementById("videoPreviewContainer").style.display = "none";
        document.getElementById("xrayFileName").style.display = "none";
        document.getElementById("videoFileName").style.display = "none";
        document.getElementById("resultsSection").style.display = "none";
        initPatientId();
        calculateBmi();
        document.getElementById("painRange").dispatchEvent(new Event("input"));
    });

    document.getElementById("screeningForm").addEventListener("submit", async (e) => {
        e.preventDefault();

        // Validation
        if (!selectedXrayFile) {
            alert("Please upload a knee X-ray image before starting screening.");
            return;
        }

        if (!selectedVideoFile) {
            alert("Please upload a knee movement video before starting screening.");
            return;
        }

        // Prepare FormData
        const formData = new FormData();
        formData.append("patient_name", document.getElementById("patientName").value.trim());
        formData.append("patient_id", document.getElementById("patientId").value.trim());
        formData.append("age", document.getElementById("patientAge").value);
        formData.append("sex", document.getElementById("patientSex").value);
        formData.append("height", document.getElementById("patientHeight").value);
        formData.append("weight", document.getElementById("patientWeight").value);
        formData.append("symptom_duration", document.getElementById("symptomDuration").value);
        formData.append("previous_injury", document.getElementById("prevInjury").checked);
        formData.append("oa_history", document.getElementById("oaHistory").checked);

        formData.append("pain_score", document.getElementById("painRange").value);
        formData.append("morning_stiffness", document.getElementById("chkMorningStiff").checked);
        formData.append("joint_stiffness", document.getElementById("chkJointStiff").checked);
        formData.append("swelling", document.getElementById("chkSwelling").checked);
        formData.append("walking_difficulty", document.getElementById("chkWalking").checked);
        formData.append("stairs_difficulty", document.getElementById("chkStairs").checked);
        formData.append("standing_difficulty", document.getElementById("chkStanding").checked);
        formData.append("bending_difficulty", document.getElementById("chkBending").checked);

        formData.append("xray_file", selectedXrayFile);
        formData.append("movement_file", selectedVideoFile);

        // Show Staged Animation Modal
        const analysisModal = new bootstrap.Modal(document.getElementById("analysisModal"));
        analysisModal.show();
        resetStepper();

        try {
            // Staged visual progression
            await simulateStep("step1", 700);

            // Trigger actual request concurrently
            const fetchPromise = fetch(`${API_URL}/api/screen`, {
                method: "POST",
                body: formData
            });

            await simulateStep("step2", 700);
            await simulateStep("step3", 600);

            const response = await fetchPromise;
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Server error: ${response.status}`);
            }

            await simulateStep("step4", 400);

            const screeningData = await response.json();
            currentScreeningResult = screeningData;

            // Dismiss modal and render results
            setTimeout(() => {
                analysisModal.hide();
                displayResults(screeningData);
                initDashboardStats(); // Refresh top counters
            }, 300);

        } catch (error) {
            analysisModal.hide();
            console.error("Screening error:", error);
            alert(`Screening Failed: ${error.message}\n\nPlease verify that the FastAPI backend is running at ${API_URL}`);
        }
    });
}

function resetStepper() {
    ["step1", "step2", "step3", "step4"].forEach((id, idx) => {
        const el = document.getElementById(id);
        el.className = idx === 0 ? "stepper-item active" : "stepper-item";
    });
}

function simulateStep(stepId, durationMs) {
    return new Promise(resolve => {
        const el = document.getElementById(stepId);
        el.classList.add("active");
        setTimeout(() => {
            el.classList.remove("active");
            el.classList.add("done");
            resolve();
        }, durationMs);
    });
}

// ----------------------------------------------------------------------------
// 7. Display Results
// ----------------------------------------------------------------------------
function displayResults(data) {
    const resultsSection = document.getElementById("resultsSection");
    resultsSection.style.display = "block";
    resultsSection.scrollIntoView({ behavior: "smooth" });

    // Patient Summary
    const patient = data.patient || {};
    const fusion = data.fusion || {};
    const xray = data.xray?.result || {};
    const gait = data.gait?.result || {};
    const clinical = data.clinical || {};

    document.getElementById("resPatientSummary").textContent = `Patient ID: ${patient.patient_id || 'N/A'}`;
    document.getElementById("resName").textContent = patient.name || 'Demo Patient';
    document.getElementById("resAge").textContent = patient.age || '55';
    document.getElementById("resTimestamp").textContent = data.created_at || new Date().toLocaleString();

    // Multimodal Overall Risk
    const overallRisk = fusion.overall_risk || "Moderate Risk";
    const riskBadge = document.getElementById("resOverallRiskBadge");
    riskBadge.textContent = overallRisk;
    riskBadge.className = `risk-level-badge ${fusion.risk_badge_class || 'warning'}`;
    document.getElementById("resRiskScore").textContent = fusion.risk_score || '50.0';

    // X-Ray Card
    document.getElementById("resXrayQuality").textContent = xray.image_quality || "Good";
    const abnEl = document.getElementById("resXrayAbnormality");
    abnEl.textContent = xray.abnormality_detected ? "Detected" : "None Detected";
    abnEl.className = xray.abnormality_detected ? "value text-danger" : "value text-success";
    document.getElementById("resXraySeverity").textContent = xray.severity || "Moderate";
    document.getElementById("resXrayConfidence").textContent = `${Math.round((xray.confidence || 0.8) * 100)}%`;

    // Movement Card
    document.getElementById("resGaitQuality").textContent = gait.movement_quality || "Fair";
    const asymPercent = gait.asymmetry_percentage || `${Math.round((gait.asymmetry || 0.15) * 100)}%`;
    document.getElementById("resGaitAsymmetry").textContent = asymPercent;
    document.getElementById("resGaitRisk").textContent = gait.movement_risk || "Moderate";
    document.getElementById("resGaitConsistency").textContent = `${Math.round((gait.movement_consistency || 0.75) * 100)}%`;

    // Clinical Card
    document.getElementById("resClinPain").textContent = `${clinical.pain_score || 0}/10`;
    document.getElementById("resClinStiffness").textContent = (clinical.morning_stiffness || clinical.joint_stiffness) ? "Present" : "Absent";
    document.getElementById("resClinWalking").textContent = clinical.walking_difficulty ? "Present" : "None";
    document.getElementById("resClinBmi").textContent = `${clinical.bmi || 25.0} (${clinical.bmi_category || 'Normal'})`;

    // Explanations List
    const expList = document.getElementById("resExplanationsList");
    expList.innerHTML = "";
    (fusion.explanations || []).forEach(exp => {
        const li = document.createElement("li");
        li.textContent = exp;
        expList.appendChild(li);
    });

    // Recommendations List
    const recList = document.getElementById("resRecommendationsList");
    recList.innerHTML = "";
    (fusion.recommendations || []).forEach(rec => {
        const li = document.createElement("li");
        li.textContent = rec;
        recList.appendChild(li);
    });

    // Reset Verification status
    updateVerificationBadge("PENDING");
    document.getElementById("hwComments").value = "";
    document.getElementById("verifFeedback").style.display = "none";
}

// ----------------------------------------------------------------------------
// 8. Healthcare Worker Verification
// ----------------------------------------------------------------------------
function updateVerificationBadge(status) {
    const badge = document.getElementById("badgeVerifStatus");
    badge.textContent = status.toUpperCase();
    if (status === "Reviewed" || status === "Accepted") {
        badge.className = "status-badge reviewed";
    } else if (status === "Referred") {
        badge.className = "status-badge referred";
    } else {
        badge.className = "status-badge pending";
    }
}

function initVerificationHandlers() {
    async function sendVerification(action) {
        if (!currentScreeningResult) {
            alert("Please complete a screening first.");
            return;
        }

        const patientId = currentScreeningResult.patient?.patient_id;
        const comments = document.getElementById("hwComments").value;

        const formData = new FormData();
        formData.append("patient_id", patientId);
        formData.append("action", action);
        formData.append("comments", comments);
        formData.append("verified_by", "Staff Healthcare Worker");

        try {
            const res = await fetch(`${API_URL}/api/verify`, {
                method: "POST",
                body: formData
            });

            if (res.ok) {
                updateVerificationBadge(action);
                const fb = document.getElementById("verifFeedback");
                fb.textContent = `Status successfully updated to ${action.toUpperCase()}`;
                fb.style.display = "block";
                initDashboardStats(); // Refresh stats counters
            } else {
                throw new Error("Failed to record verification status.");
            }
        } catch (e) {
            console.error("Verification error:", e);
            // Fallback for offline demo
            updateVerificationBadge(action);
            const fb = document.getElementById("verifFeedback");
            fb.textContent = `Status updated locally to ${action.toUpperCase()}`;
            fb.style.display = "block";
        }
    }

    document.getElementById("btnAcceptResult").addEventListener("click", () => sendVerification("Reviewed"));
    document.getElementById("btnFlagReview").addEventListener("click", () => sendVerification("Flagged"));
    document.getElementById("btnReferClinician").addEventListener("click", () => sendVerification("Referred"));

    // Report Handlers
    document.getElementById("btnGenerateReport").addEventListener("click", openReportModal);
    document.getElementById("btnPrintDirect").addEventListener("click", openReportModal);
    document.getElementById("btnModalPrint").addEventListener("click", () => {
        const frame = document.getElementById("reportFrame");
        frame.contentWindow.print();
    });
}

function openReportModal() {
    if (!currentScreeningResult) {
        alert("Please complete a screening first to generate a digital report.");
        return;
    }

    const patientId = currentScreeningResult.patient?.patient_id;
    const reportUrl = `${API_URL}/api/report/${patientId}/print`;

    const frame = document.getElementById("reportFrame");
    frame.src = reportUrl;

    const modal = new bootstrap.Modal(document.getElementById("reportModal"));
    modal.show();
}

// ----------------------------------------------------------------------------
// 9. Dashboard Statistics & Chart.js
// ----------------------------------------------------------------------------
async function initDashboardStats() {
    try {
        const res = await fetch(`${API_URL}/api/stats`);
        if (!res.ok) return;

        const data = await res.json();
        document.getElementById("statTotal").textContent = data.total_screenings ?? "--";
        document.getElementById("statHigher").textContent = data.higher_risk ?? "--";
        document.getElementById("statModerate").textContent = data.moderate_risk ?? "--";
        document.getElementById("statLower").textContent = data.lower_risk ?? "--";
        document.getElementById("statPending").textContent = data.pending_reviews ?? "--";
        document.getElementById("statReferrals").textContent = data.referrals ?? "--";

        renderRiskChart(data.risk_distribution || {
            "Higher Risk": data.higher_risk || 1,
            "Moderate Risk": data.moderate_risk || 2,
            "Lower Risk": data.lower_risk || 1
        });
    } catch (e) {
        console.log("Could not load backend stats, showing baseline demo counters:", e);
        // Fallback default demo metrics
        document.getElementById("statTotal").textContent = "4";
        document.getElementById("statHigher").textContent = "1";
        document.getElementById("statModerate").textContent = "2";
        document.getElementById("statLower").textContent = "1";
        document.getElementById("statPending").textContent = "1";
        document.getElementById("statReferrals").textContent = "1";

        renderRiskChart({ "Higher Risk": 1, "Moderate Risk": 2, "Lower Risk": 1 });
    }
}

document.getElementById("btnRefreshStats").addEventListener("click", initDashboardStats);

function renderRiskChart(distData) {
    const ctx = document.getElementById("riskChart");
    if (!ctx) return;

    const labels = ["Higher Risk", "Moderate Risk", "Lower Risk"];
    const values = [
        distData["Higher Risk"] || 0,
        distData["Moderate Risk"] || 0,
        distData["Lower Risk"] || 0
    ];

    if (riskChartInstance) {
        riskChartInstance.data.datasets[0].data = values;
        riskChartInstance.update();
        return;
    }

    riskChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#dc3545', '#f59e0b', '#10b981'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            cutout: '70%'
        }
    });
}
