@echo off
title JARVIS Server - Stop
color 0C
echo.
echo ========================================
echo   J.A.R.V.I.S. Server - Stopping...
echo ========================================
echo.

echo [INFO] Looking for JARVIS process...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTEN') do (
    echo [INFO] Found process %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
    echo [INFO] Process terminated
)

echo [INFO] Cleaning up remaining processes...
taskkill /IM python.exe /F >nul 2>&1

echo.
echo [OK] JARVIS server stopped
echo.
pause
