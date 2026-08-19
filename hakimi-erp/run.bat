@echo off
echo ====================================================
echo   HAKIMI-ERP: UNIFIED STARTUP SCRIPT
echo ====================================================

:: Detect current directory
set BASE_DIR=%~dp0
cd /d %BASE_DIR%

echo [1/2] Starting Backend (FastAPI)...
start "HAKIMI-BACKEND" cmd /k "cd backend && (if exist venv\Scripts\python.exe (venv\Scripts\python.exe server.py) else if exist D:\Anaconda\python.exe (D:\Anaconda\python.exe server.py) else (python server.py))"

echo [2/2] Starting Frontend (Vue 3 / Vite)...
start "HAKIMI-FRONTEND" cmd /k "cd frontend && npm run dev"

echo.
echo ====================================================
echo   Backend and Frontend are starting in separate windows.
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:5173
echo ====================================================
pause
