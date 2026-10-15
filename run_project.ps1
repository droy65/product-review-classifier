# ReviewLens AI - PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  ReviewLens AI - Product Review Classifier Suite" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$PythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Virtual environment python.exe not found at $PythonExe" -ForegroundColor Red
    exit 1
}

$ModelPkl = Join-Path $ScriptDir "model\model.pkl"
if (-not (Test-Path $ModelPkl)) {
    Write-Host "[INFO] Model artifacts missing. Training model on genuine Amazon dataset..." -ForegroundColor Yellow
    & $PythonExe (Join-Path $ScriptDir "model\train.py")
}

Write-Host "[1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PythonExe' -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Launching Streamlit Frontend on http://localhost:8501 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '$PythonExe' -m streamlit run (Join-Path '$ScriptDir' 'frontend\app.py') --server.port 8501"

Write-Host "`nServices Started!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Docs:     http://127.0.0.1:8000/docs" -ForegroundColor White
