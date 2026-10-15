@echo off
title Product Review Classifier - Launching AI Suite...
echo ========================================================
echo   Starting ReviewLens AI - Product Review Classifier
echo ========================================================
echo.

cd /d "%~dp0"

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    echo Please run setup first.
    pause
    exit /b 1
)

echo [1/3] Checking dataset and model artifacts...
IF NOT EXIST "model\model.pkl" (
    echo Model artifacts missing. Training model on genuine Amazon dataset...
    ".venv\Scripts\python.exe" model\train.py
)

echo [2/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "ReviewLens - FastAPI Backend" cmd /k "".venv\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"

echo Waiting 3 seconds for Backend API to initialize...
timeout /t 3 /nobreak >nul

echo [3/3] Launching Streamlit Frontend on http://localhost:8501 ...
start "ReviewLens - Streamlit Frontend" cmd /k "".venv\Scripts\python.exe" -m streamlit run frontend\app.py --server.port 8501"

echo.
echo ========================================================
echo   Services are running!
echo   Frontend: http://localhost:8501
echo   Backend:  http://127.0.0.1:8000
echo   API Docs: http://127.0.0.1:8000/docs
echo ========================================================
echo.
