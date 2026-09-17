# PowerShell startup script for AI-Based Multimodal OA Screening System
Set-Location -Path $PSScriptRoot
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host " Starting AI-Based Multimodal OA Screening System" -ForegroundColor Cyan
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "Working Directory: $(Get-Location)"
Write-Host ""

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .venv\Scripts\Activate.ps1
}

Write-Host "Starting FastAPI Server..." -ForegroundColor Yellow
Write-Host "  - Backend URL:    http://127.0.0.1:8000"
Write-Host "  - Swagger Docs:   http://127.0.0.1:8000/docs"
Write-Host "  - Web Frontend:   http://127.0.0.1:8000/app"
Write-Host ""

python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
