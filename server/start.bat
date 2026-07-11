@echo off
title JARVIS Server - Start
color 0A
echo.
echo ========================================
echo   J.A.R.V.I.S. Server - Starting...
echo ========================================
echo.

cd /d "%~dp0..\backend"

echo [INFO] Checking if server is already running...
netstat -ano | findstr :8000 | findstr LISTEN >nul 2>&1
if %errorlevel%==0 (
    echo [WARNING] Server already running on port 8000
    echo [INFO] Access at: https://localhost:8000
    pause
    exit /b
)

echo [INFO] Starting JARVIS server...
echo [INFO] PC: https://localhost:8000
echo [INFO] Android: https://192.168.1.22:8000
echo [INFO] Press Ctrl+C to stop
echo.

"C:\Users\Kimet\AppData\Local\Programs\Python\Python311\python.exe" main.py

pause
