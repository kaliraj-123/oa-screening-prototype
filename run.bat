@echo off
cd /d "%~dp0"
echo ===================================================================
echo  Starting AI-Based Multimodal OA Screening System
echo ===================================================================
echo Working Directory: %CD%
echo.

IF EXIST ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Starting FastAPI Server...
echo   - Backend URL:    http://127.0.0.1:8000
echo   - Swagger Docs:   http://127.0.0.1:8000/docs
echo   - Web Frontend:   http://127.0.0.1:8000/app
echo.
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
pause
